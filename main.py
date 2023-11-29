import requests
import json
import os
from emergencytext import generate_emergency_text
from openai import OpenAI
import base64
from transformers import AutoImageProcessor, ResNetForImageClassification, ResNetConfig
from PIL import Image
import requests

# Your OpenAI API key
client = OpenAI()
#client.api_key_path="apikey.txt"

with open('apikey.txt', 'r') as f:
    KEY= f.read()

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
    url = 'https://api.openai.com/v1/chat/completions'  # This URL might be different for GPT-4
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': 'gpt-4',  # Model name might be different for ChatGPT-4
        'prompt': prompt,
        'max_tokens': 500  # Adjust as needed
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def analyze_image_resnet(image_path, ckpt_path):

    processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
    model = load_model_from_ckpt(ckpt_path)

    image = Image.open(image_path).convert("RGB")
    image = transform(image)
    image = image.unsqueeze(0).to(torch.device('cuda:0'))
    # Tokenize inputs and perform inference
    inputs = processor(images=image, return_tensors="pt", padding=True)
    inputs.to(torch.device('cuda:0'))
    outputs = model(**inputs)

    # Get the predicted class probabilities
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits.to(torch.device('cpu')), dim=1).detach().numpy()

    return probabilities[0].argmax()


def load_model_from_ckpt(ckpt_path):
    model = ResNetForImageClassification.from_pretrained("microsoft/resnet-50")

    device = torch.device("cpu")
    model.classifier = torch.nn.Sequential(
        torch.nn.Flatten(start_dim=1, end_dim=-1),
        torch.nn.Linear(in_features=2048, out_features=5, bias=True))
    model.to(torch.device(device))

    # Load the model state_dict
    state_dict = torch.load(ckpt_path, map_location="cpu" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(state_dict)

    return model


# Example usage
audiopath = os.path.join('assets', 'audio.mp3')
imagepath = os.path.join('assets', 'chest-pain.jpg')
ckptpath = 'ckpt/pytorch_model.bin'
audiopath=os.path.join('assets', 'audio.mp3')
imagepath=os.path.join('assets', 'chest-pain.jpg')
assert os.path.isfile(audiopath)
assert os.path.isfile(imagepath)

audio_transcription = transcribe_audio(audiopath)
image_analysis = analyze_image(imagepath)
severity_score = analyze_image_resnet(imagepath, ckpt_path=ckptpath)
emergency_text = generate_emergency_text()

print(audio_transcription)
print(image_analysis)
print(severity_score)
print(emergency_text)


# Constructing the prompt for ChatGPT
prompt = f"Given the following inputs:\n\n" \
         f"Image Content Description: {image_analysis}\n" \
         f"Chat Transcript: {emergency_text}\n" \
         f"Call Transcript (TTS): {audio_transcription}\n\n" \
         "Please analyze the emergency situation and provide an analysis based on these parameters:\n\n" \
         "Sentiment: Evaluate and describe the overall sentiment of the individuals involved in the emergency situation based on the provided texts.\n" \
         "NACA Score: Based on the severity and urgency indicated in the texts, assign a NACA (National Advisory Committee for Aeronautics) score to the situation.\n" \
         "Resources to Deploy: Recommend the appropriate emergency resources (e.g., medical, fire, police) that should be deployed in this situation.\n" \
         "Immediate Suggestions: Provide practical advice or instructions that can be suggested to the person in the emergency to do in the meantime while rescue services are en route."
# Call ChatGPT-4 with the prompt

chatgpt_response = call_chatgpt(prompt)
print(prompt)


# Print the result
print(chatgpt_response)
