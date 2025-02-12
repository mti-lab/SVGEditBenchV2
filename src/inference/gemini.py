import asyncio
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv
from glob import glob
from tqdm import tqdm

load_dotenv()

class Gemini:
  def __init__(self, model: str):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    self.model = genai.GenerativeModel(model, 
      generation_config=genai.types.GenerationConfig(
        max_output_tokens=8192
      )
    )
    self.called = 0
  
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
  
  def update_counter(self):
    self.called+=1
    self.pbar.set_description(f"#Called: {self.called}")

  async def call_API(self, triplet: str, output_folder: str):
    with open(os.path.join(triplet, "before.svg")) as f:
      before_svg = f.read()
    with open(os.path.join(triplet, "instruction.txt")) as f:
      instruction = f.read()
    
    triplet_id = os.path.basename(triplet)
    while self.called - self.pbar.n > 15:
      await asyncio.sleep(0.1)
    self.update_counter()
    content = await self.model.generate_content_async(f"The following is the SVG code representing an image. {instruction} Only return the output SVG code.\n\n```svg\n{before_svg}\n```")

    response = content.text
    with open(os.path.join(output_folder, triplet_id+".txt"), "w") as out:
      out.write(response)
    try:
      parsed = self.parse_response(response)
      with open(os.path.join(output_folder, triplet_id+".svg"), "w") as out:
        out.write(parsed)
    except ValueError:
      print(f"Parser Error at {triplet_id}")

  def inference(self, triplets: str, output_folder: str = "output") -> str:
    os.makedirs(output_folder)

    folder_list = glob(os.path.join(triplets, "*"))
    self.pbar = tqdm(total = len(folder_list))

    def progress(task):
      self.pbar.update(1)

    async def tasks():
      tasks = [
        asyncio.create_task(self.call_API(triplet, output_folder))
        for triplet in folder_list
      ]
      for task in tasks:
        task.add_done_callback(progress)
      await asyncio.wait(tasks)

    asyncio.run(tasks())
    return output_folder