import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os
import subprocess
import sys

SCRIPTS_DIRECTORY = r"C:\Users\end user\Desktop\Projects\RALPH\Second draft"

print("Current working directory:", os.getcwd())
print("Files in the scripts directory:", os.listdir(SCRIPTS_DIRECTORY))

WAKE_WORDS = {
    "ralph": os.path.join(SCRIPTS_DIRECTORY, "claude_sonnet_assistant.py"),
    "pixie": os.path.join(SCRIPTS_DIRECTORY, "claude_haiku_assistant.py"),
    "gpt": os.path.join(SCRIPTS_DIRECTORY, "gpt4_assistant.py"),
    "mini": os.path.join(SCRIPTS_DIRECTORY, "gpt4_mini_assistant.py")
}

def detect_wake_words(wake_words):
    model_path = r"C:\Users\end user\Desktop\Projects\RALPH\vosk\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
    
    print(f"Checking for Vosk model in: {model_path}")
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return None

    try:
        model = Model(model_path=model_path)
        rec = KaldiRecognizer(model, 16000)
    except Exception as e:
        print(f"Error creating Vosk model: {str(e)}")
        return None

    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
    except OSError as e:
        print(f"Error opening audio stream: {str(e)}")
        p.terminate()
        return None

    print("Listening for wake words...")
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print(f"Detected: {result['text']}")
                for wake_word, script in wake_words.items():
                    if wake_word in result["text"].lower():
                        print(f"Wake word '{wake_word}' detected!")
                        return script
    except KeyboardInterrupt:
        print("Stopping wake word detection.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    return None

def main():
    while True:
        script_to_run = detect_wake_words(WAKE_WORDS)
        if script_to_run:
            print(f"Running script: {script_to_run}")
            try:
                result = subprocess.run([sys.executable, script_to_run], capture_output=True, text=True, check=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error running script {script_to_run}:")
                print(f"Exit code: {e.returncode}")
                print(f"Standard output:\n{e.stdout}")
                print(f"Standard error:\n{e.stderr}")
            except FileNotFoundError:
                print(f"Script {script_to_run} not found.")

if __name__ == "__main__":
    main()
