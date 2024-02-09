from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
model_name = "ft:gpt-3.5-turbo-0613:personal::8q3apor4"

response = client.chat.completions.create(
  model= model_name,
  messages=[
    {"role": "system", "content": "You are a helpful and knowledgeable assistant specializing in equity award grants, particularly for Qapita Fintech Pvt Ltd. Your expertise is in understanding and explaining Qapita's services, which include a SaaS platform for ESOPs and cap table management, and QapMap, a digital platform for managing equity awards. Focus on grants, their workflows, and related queries. If asked about topics outside your expertise, respond with, 'I don’t have enough data to answer it, but you can check out our support website: https://qapita-fintech.freshdesk.com/support/home'. Aim to explain concepts clearly and understandably for users. Also go through the entire website for things you get confused with https://qapita-fintech.freshdesk.com/support/home"},
    {"role": "user", "content": "What are the things required to create the grants?"}
  ]
)
print(response.choices[0].message)