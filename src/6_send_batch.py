from dotenv import load_dotenv
from openai import OpenAI
import sys
import time

load_dotenv()

client = OpenAI()
input_file = sys.argv[1] # Output file from 5_create_batch.py
output_file = sys.argv[2] # Output file from OpenAI API

batch_input_file = client.files.create(
  file=open(input_file, "rb"),
  purpose="batch"
)
batch_input_file_id = batch_input_file.id
print("File id:",batch_input_file_id)

batch_req = client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
batch_id = batch_req.id

print("Starting batch processing")
while True:
  info = client.batches.retrieve(batch_id)
  status = info.status
  
  if (status == "completed"):
    print("Batch successfully completed")
    output_file_id = info.output_file_id
    with open(output_file, "w") as f:
      file_response = client.files.content(output_file_id)
      f.write(file_response.text)
    break
  elif (status in ["validating", "in_progress", "finalizing", "completed"]):
    time.sleep(2)
  else:
    raise Exception("Batch failed")