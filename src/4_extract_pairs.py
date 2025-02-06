from tqdm import tqdm
import json
import os
import pandas as pd
import pickle
import random
import shutil
import sys

distances = sys.argv[1] # Output file from 3_add_distance.py
image_path = sys.argv[2]
OUT_PATH = sys.argv[3] # Output folder path
nPairs = int(sys.argv[4]) # Number of image pairs to generate
max_duplitcates = int(sys.argv[5]) # Maximum times that a single image can be used in the triplets
random.seed(42)

with open(distances, "rb") as f:
  dists, file_names = pickle.load(f)
  df = pd.DataFrame(dists.cpu(), index=file_names, columns=file_names)

df_stacked = df.stack()
df_sorted = df_stacked.sort_values()
os.makedirs(OUT_PATH)

pbar = tqdm(total = nPairs)
count = 0

occurence_count = {}
for key, dist in df_sorted.items():
  if key[0] == key[1] or dist < 0.1:
    pbar.set_description("Ignoring too similar pairs")
    continue
  if key[0] > key[1]:
    continue
  if occurence_count.get(key[0],0) >= max_duplitcates or occurence_count.get(key[1],0) >= max_duplitcates:
    continue
  pbar.set_description("")

  data_path = os.path.join(OUT_PATH, str(count).zfill(3))
  os.makedirs(data_path)
  
  if(random.random()< 0.5):
    shutil.copy(os.path.join(image_path, key[0]), os.path.join(data_path, "before.png"))
    shutil.copy(os.path.join(image_path, key[0].replace(".png", ".svg")), os.path.join(data_path, "before.svg"))
    shutil.copy(os.path.join(image_path, key[1]), os.path.join(data_path, "after.png"))
    shutil.copy(os.path.join(image_path, key[1].replace(".png", ".svg")), os.path.join(data_path, "after.svg"))
    meta = {
      "before": key[0],
      "after": key[1],
      "distance": dist
    }
  else:
    shutil.copy(os.path.join(image_path, key[0]), os.path.join(data_path, "after.png"))
    shutil.copy(os.path.join(image_path, key[0].replace(".png", ".svg")), os.path.join(data_path, "after.svg"))
    shutil.copy(os.path.join(image_path, key[1]), os.path.join(data_path, "before.png"))
    shutil.copy(os.path.join(image_path, key[1].replace(".png", ".svg")), os.path.join(data_path, "before.svg"))
    meta = {
      "after": key[0],
      "before": key[1],
      "distance": dist
    }
  
  with open(os.path.join(data_path, "metadata.json"), "w") as f:
    f.write(json.dumps(meta))

  if key[0] in occurence_count:
    occurence_count[key[0]] += 1
  else:
    occurence_count[key[0]] = 1
  if key[1] in occurence_count:
    occurence_count[key[1]] += 1
  else:
    occurence_count[key[1]] = 1
  count += 1
  pbar.update(1)

  if count >= nPairs:
    break