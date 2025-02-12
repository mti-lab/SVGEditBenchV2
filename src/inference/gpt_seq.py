import asyncio
import os
import re
from dotenv import load_dotenv
from glob import glob
from openai import AsyncOpenAI
from tqdm import tqdm

load_dotenv()

class SequentialOpenAI:
  def __init__(self, model: str):
    self.model = model
    self.client = AsyncOpenAI()
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

    completion = await self.client.chat.completions.create(
      model=self.model,
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": f"The following is the SVG code representing an image. {instruction} Only return the output SVG code.\n\n```svg\n{before_svg}\n```"
            }
          ]
        }
      ]
    )

    response = completion.choices[0].message.content
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