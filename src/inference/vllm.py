import os
import re
from glob import glob
from tqdm import tqdm
from vllm import LLM, SamplingParams

class VLLM:
  def __init__(self, model: str, llm_params: dict = {}, **sampling_params):
    self.llm = LLM(model = model, **llm_params)
    self.params = SamplingParams(**sampling_params)

  def parse_response(self, response: str) -> str:
    svg_string = re.findall(r"```svg\n[^`]+?```", response)
    if len(svg_string) > 1:
      raise ValueError("The LLM returned more than one SVG string")
    elif len(svg_string) != 1:
      svg_string = re.findall(r"<svg[\s\S]+?<\/svg>", response)
      if len(svg_string) != 1:
        raise ValueError("The LLM returned no or more than one SVG string")
      else:
        svg = svg_string[0]
    else:
      svg = svg_string[0][7:-3]
    
    return svg
  
  def inference(self, triplets: str, output_folder: str):
    os.makedirs(output_folder)

    folder_list = glob(os.path.join(triplets, "*"))

    prompts = []
    for triplet in tqdm(folder_list, desc="Generating prompts..."):
      triplet_id = os.path.basename(triplet)
      with open(os.path.join(triplet, "before.svg")) as f:
        before_svg = f.read()
      with open(os.path.join(triplet, "instruction.txt")) as f:
        instruction = f.read()

      prompts.append([
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": f"The following is the SVG code representing an image. {instruction} Only return the output SVG code.\n\n```svg\n{before_svg}\n```"
            }
          ]
        }
      ])
    responses = self.llm.chat(prompts, sampling_params=self.params)

    for i, triplet in enumerate(tqdm(folder_list, desc="Writing responses...")):
      response = responses[i].outputs[0].text
      triplet_id = os.path.basename(triplet)
      with open(os.path.join(output_folder, triplet_id+".txt"), "w") as out:
        out.write(response)
      try:
        parsed = self.parse_response(response)
        with open(os.path.join(output_folder, triplet_id+".svg"), "w") as out:
          out.write(parsed)
      except ValueError:
        print(f"Parser Error at {triplet_id}")
    
    return output_folder