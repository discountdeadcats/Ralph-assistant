import sys

try:
    import speech_recognition as sr
    import pyttsx3
    import openai
    import re
except ImportError as e:
    print(f"Error: Could not import required module. {str(e)}")
    print("Please ensure you have installed all required libraries.")
    print("You can install them using pip:")
    print("pip install SpeechRecognition pyttsx3 openai")
    sys.exit(1)

# Initialize the speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set a more feminine, child-like voice
voices = engine.getProperty('voices')
for voice in voices:
    if "child" in voice.name.lower() or "female" in voice.name.lower():
        engine.setProperty('voice', "com.apple.speech.synthesis.voice.samantha")
        break

# Set up OpenAI API client

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
        speak("Hi, I'm micky , your GPT-4 assistant. How can I help?")
        user_input = recognize_speech()
        if user_input:
            print(f"You said: {user_input}")
            
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",  # Use "gpt-4" for GPT-4, or "gpt-3.5-turbo" for GPT-3.5
                    messages=[
                        {"role": "system", "content": "You are Pixie, a quick and efficient voice-activated AI assistant powered by GPT-4. Your responses should be concise, practical, and to the point. Focus on providing fast, accurate information for everyday tasks and queries."},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=500,
                    temperature=0
                )
                
                ai_response = response.choices[0].message.content
                cleaned_response = clean_text(ai_response)
                print(f"AI response: {cleaned_response}")
                speak(cleaned_response)
            except Exception as e:
                print(f"Error communicating with OpenAI API: {str(e)}")
                speak("Sorry, I ran into a problem while processing your request.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        speak("I'm sorry, but I encountered an unexpected error. Please try again later.")

if __name__ == "__main__":
    main()