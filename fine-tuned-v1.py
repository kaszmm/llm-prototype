from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
# model_name = "ft:gpt-3.5-turbo-0613:personal::8q3apor4"
# model_name = "ft:gpt-3.5-turbo-0613:personal::8rm3JVLZ"
model_name = "ft:gpt-3.5-turbo-1106:personal::8roO1D24"

response = client.chat.completions.create(
  model= model_name,
  messages=[
    {"role": "system", "content": "You are helpful assistant"},
    {"role": "user", "content": "WHo are you?"}
  ]
)
print(response.choices[0].message)