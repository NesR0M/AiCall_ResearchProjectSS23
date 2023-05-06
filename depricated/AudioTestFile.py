import pygame
import pygame_gui
import pyaudio
import numpy as np
import wave
import threading

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Set up the display
window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Audio Recorder')

# Set up the GUI manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

# Set up the record button
record_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 25), (100, 50)),
    text='Record',
    manager=manager,
)

# Set up audio recording parameters
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100
filename = 'output.wav'

# Initialize recording variables
is_recording = False
audio_frames = []

def record_audio():
    global audio_frames, is_recording
    audio_frames = []
    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    while is_recording:
        data = stream.read(chunk)
        audio_frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

def save_audio_to_file():
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(audio_frames))
    wf.close()

clock = pygame.time.Clock()

running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == record_button:
                    if not is_recording:
                        record_button.set_text("Recording...")
                        is_recording = True
                        audio_frames = []
                        recording_thread = threading.Thread(target=record_audio)
                        recording_thread.start()
                    else:
                        record_button.set_text("Record")
                        is_recording = False
                        recording_thread.join()
                        save_audio_to_file()

        manager.process_events(event)

    manager.update(time_delta)
    window_surface.fill((0, 0, 0))
    manager.draw_ui(window_surface)
    pygame.display.update()

pygame.quit()