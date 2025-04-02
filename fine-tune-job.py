from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

file_id = "file-lEVLDG4hl813SPrSuOu1ImaC"

# response = client.fine_tuning.jobs.create(
#   training_file=file_id, 
#   model="gpt-3.5-turbo"
# )

# get state of job
# response = client.fine_tuning.jobs.retrieve("ftjob-kfilnUM7rwNDXI8EZSFFDDyp")

# get last 20 events of job
response = client.fine_tuning.jobs.list_events(fine_tuning_job_id="ftjob-kfilnUM7rwNDXI8EZSFFDDyp", limit=20)

print(response)


