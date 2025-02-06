from cairosvg import svg2png
from glob import glob
from tqdm import tqdm
import os
import shutil
import sys

sources = {
  "twemoji": "datasets/twemoji/assets/svg/",
  "noto-emoji": "datasets/noto-emoji/svg/",
  "fluentui_flat": "datasets/fluentui-emoji/assets/*/Flat/",
  "fluentui_highcontrast": "datasets/fluentui-emoji/assets/*/High Contrast/",
}
out_folder = sys.argv[1] # Output Folder
size = int(sys.argv[2]) # Size of the output image

os.makedirs(out_folder)
for name in sources.keys():
  print(name)
  path = sources[name]
  for file in tqdm(glob(os.path.join(path, "*.svg"))):
    include = True
    exclude = [f"{c:x}" for c in range(0x1F3FB, 1+0x1F3FF)] # EMOJI MODIFIER FITZPATRICK (Skin color)
    exclude += [f"{c:x}" for c in range(0x1F1E6, 1+0x1F1FF)] # REGIONAL INDICATOR SYMBOL LETTER (Flags)
    exclude += [f"{c:x}" for c in range(0xE0061, 1+0xE007A)] # Tag components used for subdivision flags
    match name:
      case "twemoji":
        basename = os.path.basename(file)
        for ex in exclude:
          if ex in basename:
            include = False
      case "noto-emoji":
        basename = os.path.basename(file)
        for ex in exclude:
          if ex in basename:
            include = False
      case "fluentui_color" | "fluentui_flat" | "fluentui_highcontrast":
        include = True
    
    if include:
      svg2png(url=file, write_to = os.path.join(out_folder, name + "_" + os.path.basename(file).replace(".svg", ".png")), output_width=size, output_height=size, parent_width=size, parent_height=size, background_color="white")
      shutil.copy(file, os.path.join(out_folder, name + "_" + os.path.basename(file)))
