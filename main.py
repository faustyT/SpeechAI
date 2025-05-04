import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
import pyttsx3

# === OpenRouter settings ===
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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"  # <-- Replace this!
MODEL = "google/gemma-3-1b-it:free"  # You can also try "meta-llama/llama-3-8b-instruct"

# === Initialize TTS engine ===
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    print(f"\n[Octo]: {text}")
    engine.say(text)
    engine.runAndWait()

def record_audio(filename="input.wav", duration=5, fs=44100):
    print(" Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wav.write(filename, fs, audio)

def speech_to_text(filename="input.wav"):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "[Couldn't understand speech]"
    except sr.RequestError:
        return "[Speech recognition failed]"

def listen_to_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak now or press Enter to type.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing speech...")
            text = recognizer.recognize_google(audio)
            print(f"You said (voice): {text}")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError:
            print("Speech recognition service error.")
            return None

def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Octa, an AI assistant that responds with kindness, emotional intelligence, "
                    "spiritual wisdom, and physical/health advice. You are great at answering educational "
                    "questions for students in Nigeria. Always provide thoughtful and detailed responses."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"[OpenRouter error {response.status_code}: {response.text}]"
    except Exception as e:
        return f"[Request failed: {e}]"

def main():
    print("Hi! I’m Octa — your smart assistant. Ask me anything by voice or text.")
    print("Say 'exit', 'bye', or press Ctrl+C to stop.")

    while True:
        try:
            print("\nPress [Enter] to type, or wait 5 seconds to speak.")
            typed = input("You (press Enter to speak instead): ").strip()

            if typed.lower() in ['bye', 'exit', 'quit']:
                print("Goodbye!")
                break

            if typed:
                user_input = typed
            else:
                user_input = listen_to_speech()
                if not user_input:
                    continue

            response = ask_openrouter(user_input)
            speak(response)

        except KeyboardInterrupt:
            print("\nExiting. Thanks for chatting!")
            break

if __name__ == "__main__":
    main()
