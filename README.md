# SVGEditBenchV2
We will publish the code for the experiment soon.
## Steps to restore the dataset
1. Clone this repository along with the submodules
```bash
git clone --recursive https://github.com/mti-lab/SVGEditBenchV2.git
```

2. Install the packages
- You may have to install additional packages for cairo to work (https://cairosvg.org/documentation/#installation)
```bash
pip install -r requirements.txt
```

3. Restore the dataset with the following command
```bash
python src/1_rasterize_images.py data 64
python src/restore_dataset.py data
```

## Steps to run the pipelines
1. Follow steps 1 and 2 from the previous section
2. Run the following command to run the pipeline
```bash
python src/1_rasterize_images.py data 64
wget https://unicode.org/Public/emoji/16.0/emoji-zwj-sequences.txt
python src/2_calculate_distance.py data lpips.pkl lpips
python src/2_calculate_distance.py data clip-cos.pkl clip-cos
python src/3_add_distance.py lpips+cos.pkl lpips.pkl 1 clip-cos.pkl 1
python src/4_extract_pairs.py lpips+cos.pkl data triplets 3000 3
```
