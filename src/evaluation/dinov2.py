from glob import glob
from PIL import Image
from torchvision.transforms.functional import pil_to_tensor
from tqdm import tqdm
import os
import torch

dino = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitg14')
dino.eval()
if torch.cuda.is_available():
  dino.cuda()
cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

def dinov2_cos(prediction: str, reference: str) -> dict[str, float]:
  metric = {}
  for file in tqdm(glob(f"{prediction}/*.png")):
    img_ref = os.path.join(reference, os.path.basename(file))

    i1 = pil_to_tensor(Image.open(img_ref)).unsqueeze(0)/255
    i2 = pil_to_tensor(Image.open(file)).unsqueeze(0)/255

    if torch.cuda.is_available():
      i1 = i1.cuda()
      i2 = i2.cuda()
    
    with torch.no_grad():
      image_features1 = dino(i1)[0]
      image_features2 = dino(i2)[0]

    metric[os.path.basename(file).removesuffix(".png")] = cos(image_features1, image_features2).item()
  return metric