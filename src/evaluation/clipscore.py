from glob import glob
import json
import os
from tqdm import tqdm

from PIL import Image
from torchmetrics.multimodal.clip_score import CLIPScore
from torchvision.transforms.functional import pil_to_tensor

from emojinames import get_name

model = CLIPScore(model_name_or_path="openai/clip-vit-base-patch32")

def clipscore(prediction: str, dataset: str) -> dict[str, float]:
  metric = {}
  for file in tqdm(glob(os.path.join(prediction, "*.png"))):
    triplet_id = os.path.basename(file).removesuffix(".png")
    text_ref = os.path.join(dataset, triplet_id, "metadata.json")

    with open(text_ref) as f:
      metadata = json.loads(f.read())
    try:
      description = get_name(metadata["after"])
    except ValueError:
      breakpoint()
    
    image = pil_to_tensor(Image.open(file))
    score = model(image, description)

    metric[triplet_id] = score.item()
  return metric