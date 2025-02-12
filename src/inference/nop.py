from glob import glob
from tqdm import tqdm
import os
import shutil

def nop_inference(triplets: str, output_folder: str):
  os.makedirs(output_folder)

  folder_list = glob(os.path.join(triplets, "*"))

  for triplet in tqdm(folder_list):
    triplet_id = os.path.basename(triplet)
    shutil.copy(os.path.join(triplet, "before.svg"), os.path.join(output_folder, triplet_id+".svg"))
  
  return output_folder

def pefect_inference(triplets: str, output_folder: str):
  os.makedirs(output_folder)

  folder_list = glob(os.path.join(triplets, "*"))

  for triplet in tqdm(folder_list):
    triplet_id = os.path.basename(triplet)
    shutil.copy(os.path.join(triplet, "after.svg"), os.path.join(output_folder, triplet_id+".svg"))
  
  return output_folder