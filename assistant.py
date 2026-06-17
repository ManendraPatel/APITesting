import os
import json
import datetime
import speech_recognition as sr
from google import genai
from gtts import gTTS
import pygame

# API Configuration
API_KEY = "AQ.Ab8RN6Kqbo_souRsA6gKahMuwnVnY1BIFSzer1I67MbBWfoGfw"
client = genai.Client(api_key=API_KEY)

pygame.mixer.init()

def speak(text):
    print(f"🤖 Assistant: {text}\n")
    clean_text = text.replace("*", "").replace("#", "").replace("_", "")
    try:
        tts = gTTS(text=clean_text, lang='hi', slow=False)
        filename = "temp_voice.mp3"
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove(filename)
    except Exception as e:
        print(f"Speaking error: {e}")

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        print("🧠 Processing...")
        query = r.recognize_google(audio, language='hi-IN')
        print(f"User said: {query}\n")
        return query
    except Exception:
        return "None"

def analyze_intent_with_gemini(user_input):
    """
    Ye function Gemini AI ko use karke user ka Intent pehchanega.
    """
    prompt = f"""
    Analyze the user input and categorize it into one of these actions: 'open', 'close', 'time', or 'chat'.
    Also extract the application name if the action is 'open' or 'close' (convert app name to standard English like 'chrome', 'msedge', 'notepad', 'calculator').
    
    Respond ONLY with a valid JSON object matching this structure:
    {{"action": "action_name", "app": "app_name_or_null"}}

    Examples:
    "chrome khol do" -> {{"action": "open", "app": "chrome"}}
    "edge browser band karo" -> {{"action": "close", "app": "msedge"}}
    "bhai samay kya hua hai" -> {{"action": "time", "app": null}}
    "india ki capital kya hai" -> {{"action": "chat", "app": null}}

    User Input: "{user_input}"
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Ekdam safe tarike se code blocks ko remove kar rahe hain
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        
        return json.loads(clean_text.strip())
    except Exception as e:
        print(f"Intent Error: {e}")
        return {"action": "chat", "app": None}

def voice_assistant():
    speak("Aadesh kijiye, main aapki kya madad kar sakta hoon?")
    
    while True:
        user_input = take_command()
        if user_input == "None":
            continue
            
        user_input_lower = user_input.lower()
        
        # Hardcoded Stop Command
        if user_input_lower in ["bye", "alvida", "exit", "band karo", "stop"]:
            speak("Khuda hafiz! System shutting down.")
            break
            
        # Intent Processing
        intent = analyze_intent_with_gemini(user_input)
        action = intent.get("action")
        app = intent.get("app")
        
        # 1. TIME
        if action == "time":
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"Abhi waqt ho raha hai {current_time}.")
            
        # 2. OPEN APPLICATION
        elif action == "open" and app:
            speak(f"Sure, main {app} open kar raha hoon.")
            if app in ["chrome", "google chrome"]:
                os.system("start chrome")
            elif app in ["msedge", "edge", "microsoft edge"]:
                os.system("start msedge")
            elif app == "notepad":
                os.system("start notepad")
            elif app == "calculator":
                os.system("start calc")
            else:
                os.system(f"start {app}")
                
        # 3. CLOSE APPLICATION
        elif action == "close" and app:
            speak(f"Theek hai, main {app} ko close kar raha hoon.")
            if app in ["chrome", "google chrome"]:
                os.system("taskkill /f /im chrome.exe")
            elif app in ["msedge", "edge", "microsoft edge"]:
                os.system("taskkill /f /im msedge.exe")
            elif app == "notepad":
                os.system("taskkill /f /im notepad.exe")
            else:
                os.system(f"taskkill /f /im {app}.exe")
                
        # 4. CHAT / GENERAL KNOWLEDGE
        else:
            try:
                chat_prompt = f"Answer this in a short, professional, and natural sentence for a voice assistant. Do not use any bullet points or symbols: {user_input}"
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=chat_prompt,
                )
                speak(response.text)
            except Exception as e:
                if "429" in str(e):
                    speak("Main thoda thak gaya hoon, kripya ek minute baad dobara puchiye.")
                else:
                    print(f"⚠️ Chat Error: {e}")

if __name__ == "__main__":
    voice_assistant()