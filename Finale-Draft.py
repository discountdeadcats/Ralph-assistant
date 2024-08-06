import speech_recognition as sr
import pyttsx3
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import anthropic
import os
import time
import re


# Initialize the speech recognizer, text-to-speech engine, and Anthropic client
recognizer = sr.Recognizer()
engine = pyttsx3.init()
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)
# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech
def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return ""

# Function to detect wake word
def detect_wake_word(wake_word="hey ralph"):
    model_path = r"C:\Users\end user\Desktop\Projects\RALPH\vosk\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
    
    print(f"Checking for Vosk model in: {model_path}")
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return False

    try:
        model = Model(model_path=model_path)
        rec = KaldiRecognizer(model, 16000)
    except Exception as e:
        print(f"Error creating Vosk model: {str(e)}")
        return False

    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
    except OSError as e:
        print(f"Error opening audio stream: {str(e)}")
        p.terminate()
        return False

    print("Listening for wake word...")
    try:
        while True:
            try:
                data = stream.read(4000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    print(f"Detected: {result['text']}")
                    if wake_word in result["text"].lower():
                        print("Wake word detected!")
                        return True
            except OSError as e:
                print(f"Error reading from stream: {str(e)}")
                time.sleep(0.1)  # Add a small delay before retrying
    except KeyboardInterrupt:
        print("Stopping wake word detection.")
    finally:
        try:
            stream.stop_stream()
            stream.close()
        except OSError as e:
            print(f"Error closing stream: {str(e)}")
        p.terminate()

    return False

def clean_text(text):
    if isinstance(text, str):
        # Remove newline characters
        text = text.replace('\n', ' ')
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
    return text

def main():
    while True:
        if detect_wake_word():
            speak("How can I help you?")
            user_input = recognize_speech()
            if user_input:
                print(f"You said: {user_input}")
                
                # Send the user's input to Anthropic API
                try:
                    message = client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=500,
                        temperature=0,
                        system="You are a Chatbot like Amazon Alexa, or google home. Your responses will be spoken so they should be formatted appropriately.",
                        messages=[
                            {
                                "role": "user",
                                "content": user_input
                            }
                        ]
                    )
                    
                    # Print the entire message object for debugging
                    print("Raw API response:", message)
                    
                    # Extract the text content from the message
                    if message.content and isinstance(message.content, list) and len(message.content) > 0:
                        ai_response = message.content[0].text
                    else:
                        ai_response = str(message.content)
                    
                    cleaned_response = clean_text(ai_response)
                    print(f"AI response: {cleaned_response}")
                    speak(cleaned_response)
                except Exception as e:
                    print(f"Error communicating with Anthropic API: {str(e)}")
                    speak("I'm sorry, I encountered an error while processing your request.")

if __name__ == "__main__":
    main()