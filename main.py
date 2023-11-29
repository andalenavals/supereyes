import requests
import json
import os
from emergencytext import generate_emergency_text
import base64
from transformers import AutoImageProcessor, ResNetForImageClassification, ResNetConfig
from PIL import Image

# Your OpenAI API key
with open('apikey.txt', 'r') as f:
    KEY = f.read()

api_key = KEY

transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Adjust size as needed
    transforms.ToTensor(),
])

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Function to transcribe audio using Whisper
def transcribe_audio(file_path):
    url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'multipart/form-data'
    }
    files = {
        'file': open(file_path, 'rb'),
        'model': (None, 'whisper-1')
    }
    response = requests.post(url, headers=headers, files=files)
    return response.json()


# Function to analyze image using GPT-4 Vision
def analyze_image(base64_image):
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
    return response.json()

def analyze_image_resnet(imgage_path):

    processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
    model = ResNetForImageClassification.from_pretrained()

    image = Image.open(img_name).convert("RGB")
    image = transform(image)



# Example usage
audiopath = os.path.join('assets', 'audio.mp3')
imagepath = os.path.join('assets', 'chest-pain.jpg')
audio_transcription = transcribe_audio(audiopath)
image_analysis = analyze_image(imagepath)
emergency_text = generate_emergency_text()

print(audio_transcription)
print(image_analysis)
print(emergency_text)


# Constructing the prompt for ChatGPT
prompt = f"Given the following inputs:\n\n" \
         f"Image Content Description: {image_analysis['choices'][0]['message']['content']}\n" \
         f"Chat Transcript: {emergency_text}\n" \
         f"Call Transcript (TTS): {audio_transcription['choices'][0]['message']['content']}\n\n" \
         "Please analyze the emergency situation and provide an analysis based on these parameters:\n\n" \
         "Sentiment: Evaluate and describe the overall sentiment of the individuals involved in the emergency situation based on the provided texts.\n" \
         "NACA Score: Based on the severity and urgency indicated in the texts, assign a NACA (National Advisory Committee for Aeronautics) score to the situation.\n" \
         "Resources to Deploy: Recommend the appropriate emergency resources (e.g., medical, fire, police) that should be deployed in this situation.\n" \
         "Immediate Suggestions: Provide practical advice or instructions that can be suggested to the person in the emergency to do in the meantime while rescue services are en route."
