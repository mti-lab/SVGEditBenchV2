from glob import glob
from tqdm import tqdm
import cv2
import os

def calculate_MSE(prediction: str, reference: str) -> dict[str, float]:
  metric = {}
  for file in tqdm(glob(f"{prediction}/*.png")):
    img_ref = os.path.join(reference, os.path.basename(file))

    image_ref = cv2.imread(img_ref) / 255
    image_pred = cv2.imread(file) / 255
    mse_score = ((image_ref-image_pred) ** 2).mean().item()

    metric[os.path.basename(file).removesuffix(".png")] = mse_score
  return metric