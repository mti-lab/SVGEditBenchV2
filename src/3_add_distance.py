import pandas as pd
import pickle
import sys
import torch
from tqdm import tqdm

assert len(sys.argv) % 2 == 0 and len(sys.argv) >= 6
out_file = sys.argv[1]
dist_files = sys.argv[2::2]
weights = list(map(float, sys.argv[3::2]))

datas = []
for i, dist_file in enumerate(dist_files):
  with open(dist_file, "rb") as f:
    dists, file_names = pickle.load(f)
    df = pd.DataFrame(dists.cpu(), index=file_names, columns=file_names)
    datas.append(df)
  
  if i == 0:
    new_files = set(file_names)
  else:
    new_files &= set(file_names)

new_files = list(new_files)
new_df = pd.DataFrame(columns=new_files, index=new_files, dtype=float)
for row in tqdm(new_files):
  for column in new_files:
    value = 0
    for table_id in range(len(datas)):
      value += weights[table_id] * datas[table_id].loc[row,column].item()
    new_df.loc[row, column] = value

with open(out_file, "wb") as f:
  pickle.dump((torch.tensor(new_df.values), new_files), f)
