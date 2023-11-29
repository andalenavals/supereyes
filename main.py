import os
from emergencytext import generate_emergency_text
from openai import OpenAI
import base64
import requests
import json
# Your OpenAI API key
client = OpenAI()
#client.api_key_path="apikey.txt"

with open('apikey.txt', 'r') as f:
    KEY= f.read()

api_key = KEY

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Function to transcribe audio using Whisper
def transcribe_audio(file_path):
    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create( model="whisper-1", file=audio_file)

    """ url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'multipart/form-data'
    }
    files = {
        'file': open(file_path, 'rb'),
        'model': ("base", 'whisper-1')
    }
    response = requests.post(url, headers=headers, files=files) """
    return transcript.text


# Function to analyze image using GPT-4 Vision
def analyze_image(image_path):
    base64_image=encode_image(image_path)

    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    payload = {
        'model': 'gpt-4-vision-preview',
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': 'What’s in this image?'
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{base64_image}'
                        }
                    }
                ]
            }
        ],
        'max_tokens': 300
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# Function to call ChatGPT-4 with the prompt
def call_chatgpt(prompt):
    url = 'https://api.openai.com/v1/chat/completions'  # URL for the ChatGPT API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': 'gpt-4',  # Replace with the correct ChatGPT model name if different
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful assistant.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 500
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
def send_to_local_server(json_data):
    url = 'http://localhost:8081/api/emergency'  # Change to the correct URL of your local server
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(json_data))  # Convert JSON data to a string
    return response
# Example usage
audiopath1 = os.path.join('assets', 'audio.mp3')
imagepath1 = os.path.join('assets', 'chest-pain.jpg')
ckptpath = 'ckpt/pytorch_model.bin'

audio_transcription = transcribe_audio(audiopath1)
image_analysis = analyze_image(imagepath1)
emergency_text = generate_emergency_text()

print(audio_transcription)
print(image_analysis)
print(emergency_text)

json_structure = {
    "sentiment": "write here the sentiment analysis and human readable description of NACA SCORE",
    "nacaScore": 1,
    "resources": ["AMBULANCE", "POLICE","FIREFIGHTER"],
    "firstAid": "write here the first aid suggestions"
}
# Constructing the prompt for ChatGPT
prompt = f"Given the following inputs:\n\n" \
         f"Image Content Description: {image_analysis}\n" \
         f"Chat Transcript: {emergency_text}\n" \
         f"Call Transcript (TTS): {audio_transcription}\n\n" \
         f"Please analyze the emergency situation and provide a brief analysis preparing a JSON body with this structure: {json_structure} PAY ATTENTION: JUST WRITE DOWN INSIDE THE JSON STRUCTURE, DON'T WRITE ANY OTHER THINGS. based on these parameters:\n\n" \
         "Sentiment + NACA Score: Evaluate and describe the overall sentiment of the individuals involved in the emergency situation based on the provided texts. max 35 words for sentiment and NACA score\n" \
         "Resources to Deploy: Recommend the appropriate emergency resources (choose only between AMBULANCE, POLICE, FIREFIGHTER) that should be deployed in this situation.\n" \
         "First Aid: Provide practical advice or instructions that can be suggested to the person in the emergency to do in the meantime while rescue services are en route. 30 words for immediate suggestions"
# Call ChatGPT-4 with the prompt

chatgpt_response = call_chatgpt(prompt)
print(prompt)

# Extract the JSON content from ChatGPT's response
chatgpt_content = chatgpt_response['choices'][0]['message']['content']

# Assuming chatgpt_content is a string in JSON-like format, let's parse and reformat it
try:
    # Parse the string to a Python dictionary
    # It's important to replace single quotes with double quotes for valid JSON
    chatgpt_content_dict = json.loads(chatgpt_content.replace("'", "\""))

    # Construct a new dictionary that matches the structure of your Emergency class
    emergency_data = {
        "sentiment": chatgpt_content_dict.get("sentiment", ""),
        "nacaScore": chatgpt_content_dict.get("nacaScore", ""),
        "firstAid": chatgpt_content_dict.get("firstAid", ""),
        "resources": chatgpt_content_dict.get("resources", [])
    }

    # Serialize the Python dictionary to a JSON string
    json_data = json.dumps(emergency_data)

    # Send the JSON data to the local server
    local_server_response = send_to_local_server(json_data)
    print("Local Server Response:")
    print(local_server_response.text)

except json.JSONDecodeError as e:
    print(f"JSON decoding error: {e}")
# Print the result
print(chatgpt_response)
