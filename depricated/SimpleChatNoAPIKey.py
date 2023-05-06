import openai
import pyaudio
import wave
import os
import threading
import sys
import queue
from gtts import gTTS
from io import BytesIO

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

openai.api_key = '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'

WAVE_OUTPUT_FILENAME = "output.wav"

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000
CHUNK = 1024

p = pyaudio.PyAudio()
    
stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

audio_queue = queue.Queue()


def record_audio(stop_event):
    
    audio_queue = queue.Queue()

    while True:
        if stop_event.is_set():
            break
        data = stream.read(CHUNK)
        audio_queue.put(data)

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(list(audio_queue.queue)))
        wf.close()

def main():
    messages = []
    system_prompt = input("Enter system prompt:\n")
    messages.append({"role": "system", "content": system_prompt})
    
    print("\n______________________________\n")

    stop_event = threading.Event()

    pygame.init()
    pygame.mixer.init()
    
    while True:
        input("(Enter to start recording)\n")
        
        record_thread = threading.Thread(target=record_audio, args=(stop_event,))
        record_thread.start()

        stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

        input("(Enter to stop recording)\n")
        stop_event.set()
        record_thread.join()
        
        audio_file= open("output.wav", "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

        print(transcript.text)

        if transcript.text == "End conversation.":
          break

        messages.append({"role": "user", "content": transcript.text})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages)
        output = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": output})
        
        print("\n" + output + "\n")

        mp3_fp = BytesIO()
        tts = gTTS(output, lang='en')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.music.load(mp3_fp, 'mp3')
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        stop_event.clear()

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\nYou quit")

if __name__ == "__main__":
    main()
