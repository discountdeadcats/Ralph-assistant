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
    speak("How can I help you? I'm Claude Sonnet.")
    user_input = recognize_speech()
    if user_input:
        print(f"You said: {user_input}")
        
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=500,
                temperature=0,
                system="You are a voice-activated AI assistant named Claude Sonnet. Your responses will be spoken, so they should be concise and formatted appropriately.",
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
            speak("I'm sorry, I encountered an error while processing your request.")

if __name__ == "__main__":
    main()
