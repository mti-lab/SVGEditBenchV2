# SVGEditBenchV2
This is the repository for the paper, [SVGEditBench V2: A Benchmark for Instruction-based SVG Editing](https://arxiv.org/abs/2502.19453).
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
2. Run the following command to extract the image pairs
```bash
python src/1_rasterize_images.py data 64
wget https://unicode.org/Public/emoji/16.0/emoji-zwj-sequences.txt
python src/2_calculate_distance.py data lpips.pkl lpips
python src/2_calculate_distance.py data clip-cos.pkl clip-cos
python src/3_add_distance.py lpips+cos.pkl lpips.pkl 1 clip-cos.pkl 1
python src/4_extract_pairs.py lpips+cos.pkl data triplets 3000 3
```

3. Add the API keys to the environment variable
```
OPENAI_API_KEY="(YOUR OPENAI API KEY)"
GEMINI_API_KEY="(YOUR GEMINI API KEY)"
```

4. Run the following command to retrieve the editing prompts
```bash
python src/5_create_batch.py triplets batch.jsonl
python src/6_send_batch.py batch.jsonl batch_output.jsonl
python src/7_add_edit_instruction.py triplets batch_output.jsonl
```

5. Run the following command for the evaluation experiment
```bash
python src/8_inference.py triplets (Model) (Output Folder)
python src/9_calculate_metrics.py triplets (Output Folder) (Output File)
```
