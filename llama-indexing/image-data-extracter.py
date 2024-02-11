import base64
import requests
import os
import json
from urllib.parse import urlparse

# OpenAI API Key
api_key = os.environ['OPENAI_API_KEY']

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
def fetch_files_with_path(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith("json"):
                # Join the directory path with the file name to get the relative path
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    return file_paths

image_paths = fetch_files_with_path("./data/Training_images")

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

for image in image_paths:

    encoded_image = encode_image(image)
    print(f"Fetching metadata for {image}")
    
    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Generate a detailed JSON document outlining every visible component in the provided image, which depicts an equity management website interface. The objective is to capture an exhaustive inventory of the interface elements. This includes identifying and describing each element's type and function, such as text labels, buttons, input fields, and graphical elements. The structure and arrangement of these elements within the image should be clearly articulated. Ensure that the final output is strictly in JSON format, focusing solely on the descriptive metadata of the interface elements, without any additional explanatory or narrative text."
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 4096
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())

    response_data = response.json()
    json_string = response_data['choices'][0]['message']['content']
    json_string = json_string.replace("```json\n", "").replace("\n```", "")

    # Parse the string into a JSON object
    json_data = json.loads(json_string)

    filename_without_extension = os.path.splitext(os.path.basename(urlparse(image).path))[0] #for URL image
    #filename_without_extension = os.path.splitext(os.path.basename(image_local))[0] #for local image

    # Add .json extension to the filename
    json_filename = f"{filename_without_extension}.json"

    # Save the JSON data to a file with proper formatting
    with open("./data/Training_images/MetaData/" + json_filename, 'w') as file:
        json.dump(json_data, file, indent=4)

    print(f"JSON data saved to {json_filename}")

