"""
CattleWeightPredictor adapted to load images from S3 via boto3,
preprocess in-memory with TensorFlow and provide json-serializable results.
"""

import io
import base64
from typing import Dict, Optional, Tuple

import boto3
import numpy as np
import tensorflow as tf
from PIL import Image  # used only for optional mask->png conversion


class CattleWeightPredictorS3:
    """
    Production-ready cattle weight predictor that fetches image bytes from S3,
    runs segmentation + regression pipeline, and returns JSON-serializable output.
    """

    def __init__(self, seg_model_path: str, reg_model_path: str, s3_client: Optional[boto3.client] = None):
        """
        Load models and set up S3 client (or use provided one).

        Args:
            seg_model_path: path to segmentation model (SavedModel or .keras/.h5)
            reg_model_path: path to regression model
            s3_client: optional boto3 client (useful for tests / dependency injection)
        """

        # custom metric for segmentation model (must match what used in training)
        def dice_coef(y_true, y_pred, smooth=1e-6):
            y_true_f = tf.reshape(y_true, [-1])
            y_pred_f = tf.reshape(y_pred, [-1])
            intersection = tf.reduce_sum(y_true_f * y_pred_f)
            return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

        # Load TF models
        self.seg_model = tf.keras.models.load_model(seg_model_path, custom_objects={"dice_coef": dice_coef})
        self.reg_model = tf.keras.models.load_model(reg_model_path)

        # Create boto3 client if not provided (uses env AWS creds)
        self.s3 = s3_client or boto3.client("s3")

        # Optionally do a warmup to reduce first-call latency
        try:
            # attempt to infer input shape and warm up
            seg_input_shape = self.seg_model.input_shape
            if isinstance(seg_input_shape, list):
                seg_input_shape = seg_input_shape[0]
            batch_shape = (1,) + tuple(seg_input_shape[1:])  # (1, H, W, C)
            dummy = np.zeros(batch_shape, dtype=np.float32)
            self.seg_model.predict(dummy, verbose=0)
            # reg model warmup (if expects mask channel)
            reg_input_shape = self.reg_model.input_shape
            if isinstance(reg_input_shape, list):
                reg_input_shape = reg_input_shape[0]
            dummy2 = np.zeros((1,) + tuple(reg_input_shape[1:]), dtype=np.float32)
            self.reg_model.predict(dummy2, verbose=0)
        except Exception:
            # warmup best-effort; ignore failures
            pass

        print("✅ Segmentation and regression models loaded")

    # --------------------------
    # S3 image loading utilities
    # --------------------------
    def _get_bytes_from_s3(self, bucket: str, key: str) -> bytes:
        """
        Download object bytes from S3. Uses boto3 client configured in the environment.
        Raises botocore.exceptions.ClientError if object missing / credentials invalid.
        """
        obj = self.s3.get_object(Bucket=bucket, Key=key)
        return obj["Body"].read()

    # --------------------------
    # Preprocess helpers
    # --------------------------
    def _decode_and_preprocess(self, image_bytes: bytes, target_size: Tuple[int, int] = (224, 224)) -> tf.Tensor:
        """
        Decode JPEG/PNG bytes to TF tensor, resize and normalize to [0,1].
        Returns a float32 tensor shape (H, W, 3).
        """
        img = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
        # ensure static shape (H,W,3)
        img = tf.image.resize(img, target_size)
        img = tf.cast(img, tf.float32) / 255.0
        return img  # shape (H, W, 3)

    # --------------------------
    # Optional: convert mask -> base64 PNG for easier transport (if needed)
    # --------------------------
    @staticmethod
    def _mask_to_base64_png(mask: np.ndarray) -> str:
        """
        Convert single-channel float mask (H, W) in [0,1] to grayscale PNG and base64 encode.
        """
        # Rescale mask to 0..255 uint8
        m_uint8 = (np.clip(mask, 0.0, 1.0) * 255.0).astype("uint8")
        img = Image.fromarray(m_uint8, mode="L")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode("utf-8")
        return b64

    # --------------------------
    # Public predict methods
    # --------------------------
    def predict_from_s3(self, bucket: str, key: str, target_size: Tuple[int, int] = (224, 224),
                        return_mask_b64: bool = False) -> Dict:
        """
        High-level convenience method:
        - downloads image from S3,
        - preprocesses,
        - runs segmentation and regression,
        - returns JSON-serializable dict.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            target_size: model input size (H,W)
            return_mask_b64: if True, includes 'mask_b64' in result (base64 PNG). Beware of large size.

        Returns:
            {
                "predicted_weight": float,
                "cattle_percentage": float,  # 0..100
                "confidence": "high"/"low",
                optionally "mask_b64": str (base64 PNG)
            }
        """
        # 1) download bytes from S3
        image_bytes = self._get_bytes_from_s3(bucket, key)

        # 2) decode & preprocess into TF tensor
        img = self._decode_and_preprocess(image_bytes, target_size=target_size)  # (H,W,3)
        img_batch = tf.expand_dims(img, axis=0)  # (1,H,W,3)

        # 3) segmentation (model returns e.g. (1,H,W,1) or (1,H,W) depending on architecture)
        seg_pred = self.seg_model.predict(img_batch, verbose=0)[0]  # remove batch dim

        # If seg_pred has channel dim, squeeze it
        if seg_pred.ndim == 3 and seg_pred.shape[-1] == 1:
            seg_mask = np.squeeze(seg_pred, axis=-1)
        else:
            seg_mask = seg_pred  # assume already (H,W)

        # 4) cattle ratio (how much of image is cattle per mask average)
        cattle_ratio = float(np.mean(seg_mask))  # 0..1

        # 5) prepare input for regression: concat along channel axis (H,W,3 + 1 => H,W,4)
        # Ensure both are float32 numpy arrays
        img_np = img.numpy()  # shape (H,W,3)
        # If seg_mask might be not same size, resize (shouldn't be)
        if seg_mask.shape[:2] != img_np.shape[:2]:
            seg_mask = tf.image.resize(seg_mask[..., np.newaxis], img_np.shape[:2]).numpy()[..., 0]

        img_with_mask = np.concatenate([img_np, seg_mask[..., np.newaxis]], axis=-1)  # (H,W,4)
        img_with_mask_batch = np.expand_dims(img_with_mask, axis=0).astype("float32")

        # 6) regression
        reg_out = self.reg_model.predict(img_with_mask_batch, verbose=0)[0]  # e.g. [weight]
        weight = float(reg_out[0]) if isinstance(reg_out, (list, np.ndarray)) else float(reg_out)

        # 7) prepare result
        result = {
            "predicted_weight": weight,
            "cattle_percentage": cattle_ratio * 100.0,
            "confidence": "high" if cattle_ratio > 0.3 else "low"
        }

        # option to include base64-encoded mask image (careful: large)
        if return_mask_b64:
            result["mask_b64"] = self._mask_to_base64_png(seg_mask)

        return result

    # Convenience wrapper to use local file path (keeps API compatible)
    def predict_from_file(self, image_path: str, target_size: Tuple[int, int] = (224, 224),
                          return_mask_b64: bool = False) -> Dict:
        """Allows testing locally with a file path."""
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        return self._predict_from_bytes(image_bytes, target_size=target_size, return_mask_b64=return_mask_b64)

    def _predict_from_bytes(self, image_bytes: bytes, target_size=(224, 224), return_mask_b64: bool = False) -> Dict:
        img = self._decode_and_preprocess(image_bytes, target_size=target_size)
        img_batch = tf.expand_dims(img, axis=0)

        seg_pred = self.seg_model.predict(img_batch, verbose=0)[0]
        if seg_pred.ndim == 3 and seg_pred.shape[-1] == 1:
            seg_mask = np.squeeze(seg_pred, axis=-1)
        else:
            seg_mask = seg_pred
        cattle_ratio = float(np.mean(seg_mask))
        img_np = img.numpy()
        if seg_mask.shape[:2] != img_np.shape[:2]:
            seg_mask = tf.image.resize(seg_mask[..., np.newaxis], img_np.shape[:2]).numpy()[..., 0]
        img_with_mask = np.concatenate([img_np, seg_mask[..., np.newaxis]], axis=-1)
        img_with_mask_batch = np.expand_dims(img_with_mask, axis=0).astype("float32")
        reg_out = self.reg_model.predict(img_with_mask_batch, verbose=0)[0]
        weight = float(reg_out[0]) if isinstance(reg_out, (list, np.ndarray)) else float(reg_out)
        result = {
            "predicted_weight": weight,
            "cattle_percentage": cattle_ratio * 100.0,
            "confidence": "high" if cattle_ratio > 0.3 else "low"
        }
        if return_mask_b64:
            result["mask_b64"] = self._mask_to_base64_png(seg_mask)
        return result
