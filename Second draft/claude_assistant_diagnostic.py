import sys
import subprocess

def check_installation(package):
    try:
        __import__(package)
        print(f"{package} is installed.")
        return True
    except ImportError:
        print(f"{package} is NOT installed.")
        return False

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

required_packages = ['speech_recognition', 'pyttsx3', 'anthropic']

all_installed = True
for package in required_packages:
    if not check_installation(package):
        all_installed = False

if not all_installed:
    print("Please install missing packages using:")
    print(f"{sys.executable} -m pip install SpeechRecognition pyttsx3 anthropic")
    sys.exit(1)

# If all packages are installed, proceed with imports
import speech_recognition as sr
import pyttsx3
import anthropic
import re

# Initialize the speech recognizer, text-to-speech engine, and Anthropic client
recognizer = sr.Recognizer()
engine = pyttsx3.init()
client = anthropic.Anthropic()

def speak(text):
    engine.say(text)
    engine.runAndWait()

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

def clean_text(text):
    if isinstance(text, str):
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
    return text

def main():
    try:
        speak("Hello, I'm your Claude assistant. How can I help?")
        user_input = recognize_speech()
        if user_input:
            print(f"You said: {user_input}")
            
            try:
                message = client.messages.create(
                    model="claude-3-opus-20240229",  # Update this for specific Claude versions
                    max_tokens=500,
                    temperature=0,
                    system="You are a helpful AI assistant.",  # Customize this for specific assistants
                    messages=[
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                )
                
                if message.content and isinstance(message.content, list) and len(message.content) > 0:
                    ai_response = message.content[0].text
                else:
                    ai_response = str(message.content)
                
                cleaned_response = clean_text(ai_response)
                print(f"AI response: {cleaned_response}")
                speak(cleaned_response)
            except Exception as e:
                print(f"Error communicating with Anthropic API: {str(e)}")
                speak("Sorry, I ran into a problem while processing your request.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        speak("I'm sorry, but I encountered an unexpected error. Please try again later.")

if __name__ == "__main__":
    main()
