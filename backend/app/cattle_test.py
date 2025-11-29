from ml_service.cattle_predictor_s3 import CattleWeightPredictorS3

p = CattleWeightPredictorS3("ml_models/best_seg_model.keras", "ml_models/best_reg_model.keras")
res = p.predict_from_file("tests/test_image.jpg", return_mask_b64=False)
print(res)