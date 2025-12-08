# backend/ml_service/cattle_adapter.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .cattle_predictor_s3 import CattleWeightPredictorS3

# class CattleAdapter:
#     def __init__(self, seg_model_path, reg_model_path, max_workers=2):
#         self.predictor = CattleWeightPredictorS3(seg_model_path, reg_model_path)
#         self.executor = ThreadPoolExecutor(max_workers=max_workers)

#     def predict_sync(self, bucket, key):
#         return self.predictor.predict_from_s3(bucket, key)

#     async def predict_async(self, bucket, key):
#         loop = asyncio.get_event_loop()
#         return await loop.run_in_executor(self.executor, self.predict_sync, bucket, key)

class CattleAdapter:
    def __init__(self, seg_model_path, reg_model_path, max_workers=2):
        self.predictor = CattleWeightPredictorS3(seg_model_path, reg_model_path)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def predict_sync(self, image_path):
        return self.predictor.predict_from_file(image_path)

    async def predict_async(self, image_path):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.predict_sync, image_path)
    