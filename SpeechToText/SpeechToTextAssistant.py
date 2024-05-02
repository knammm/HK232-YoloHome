import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
import os


def recognize_speech_from_microphone():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use default microphone as the audio source
    with sr.Microphone() as source:
        print("Listening...")
        # Adjust for ambient noise, capture the audio input
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        # Use Google Web Speech API to convert audio to text
        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        pass

    except sr.RequestError as e:
        print(f"Sorry, there was an error accessing the Google Web Speech API: {e}")

    return ""


def speak(text):
    # Initialize gTTS
    tts = gTTS(text=text, lang='en')

    # Save the audio to a temporary file
    audio_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    audio_file_path = audio_file.name
    audio_file.close()  # Close the file to allow loading with pygame

    tts.save(audio_file_path)

    # Initialize pygame mixer and load the audio file
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file_path)

    # Play the audio
    pygame.mixer.music.play()

    # Wait until the audio finishes playing
    while pygame.mixer.music.get_busy():
        continue

    # Clean up
    pygame.mixer.quit()
    os.remove(audio_file_path)

# if __name__ == "__main__":
#     lights_on = False
#     while True:
#         # Listen for speech input and convert it to text
#         speech_text = recognize_speech_from_microphone()
#
#         # Check if the phrase "Turn on the light" is detected
#         if "turn on the light" in speech_text.lower():
#             if not lights_on:
#                 lights_on = True
#                 print("Which light, master?")
#                 speak("Which light, master?")
#             else:
#                 print("Lights are already on, master.")
#                 speak("Lights are already on, master.")
