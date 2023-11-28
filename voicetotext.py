import whisper
import os


def get_audio_features(audiofile):
    
    model = whisper.load_model("base")
    result = model.transcribe(audiofile)
    #print(result["text"])

    '''
    audio = whisper.load_audio(audiofile)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    #print(f"Detected language: {max(probs, key=probs.get)}")
    '''
    return [result['text'], result['language'] ]
    
audiofile=os.path.join("assets", "audio.mp3")
print(get_audio_features(audiofile))
