from emojinames import get_name
from glob import glob
from tqdm import tqdm
import clip
import lpips
import os
import pickle
import sys
import torch

image_folder = sys.argv[1] # Folder containing rasterized images
out_file_path = sys.argv[2] # Output File Path
metric = sys.argv[3] # Metric to use

assert not os.path.exists(out_file_path), "Output file already exists"

files = glob(os.path.join(image_folder, "*.png"))

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

# Calculate distance
match metric:    
  case "lpips":
    loss_fn = lpips.LPIPS(net='alex',version='0.1').to(device)
    
    image_tensors = []
    print("Converting images to tensor...")
    for file in tqdm(files):
      image = lpips.im2tensor(lpips.load_image(file))
      image_tensors.append(image)
    image_tensor = torch.cat(image_tensors, dim=0).to(device)
    
    print("Calculating distances...")
    BATCH_SIZE = 2048
    distance = torch.zeros((len(image_tensors),len(image_tensors)))
    for ref in tqdm(range(len(image_tensors)-1)):
      for i in range(ref+1, len(image_tensors), BATCH_SIZE):
        with torch.no_grad():
          tensor_batch = image_tensor[i:i+BATCH_SIZE]
          tensor_ref = image_tensor[ref].unsqueeze(0).expand(tensor_batch.shape[0], -1, -1, -1).to(device)
          dists = loss_fn.forward(tensor_ref, tensor_batch).squeeze(1,2,3)
          distance[i:i+BATCH_SIZE, ref] = dists
    diag = distance.diag().diag()
    distance = distance + distance.T - diag

    basenames = [os.path.basename(file) for file in files]
    with open(out_file_path, "wb") as f:
      pickle.dump((distance, basenames), f)

  case "clip-cos":
    descriptions = []
    errors = []
    files_with_names = []
    print("Retrieving text embeddings")
    for file in tqdm(files):
      try:
        descriptions.append(get_name(os.path.basename(file)))
        files_with_names.append(os.path.basename(file))
      except Exception as e:
        errors.append((file, e))
    
    with torch.no_grad():
      tokens = clip.tokenize(descriptions).to(device)
      text_embeddings = model.encode_text(tokens)
      text_embeddings_norm = torch.linalg.vector_norm(text_embeddings, dim=(1,), keepdim=True)
      text_embeddings_unit = text_embeddings / text_embeddings_norm
    print("# Name Errors: ", len(errors), errors)

    print("Calculating distances...")
    cos_sim = 1-torch.mm(text_embeddings_unit, text_embeddings_unit.T)
    with open(out_file_path, "wb") as f:
      pickle.dump((cos_sim, files_with_names), f)

  case _:
    raise ValueError("Invalid metric")