from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Path to your .jsonl file
file_path = "fine-tune-prompts.jsonl"

response = client.files.create(
  file=open(file_path, "rb"),
  purpose="fine-tune"
)

# The response will include details about the uploaded file, including its ID
# file_id = response['id']
# print(file_id)
print(response)