import pygame
import pygame_gui
import openai
import threading
import pyaudio
import wave
from personal_key import API_KEY
from socketClient import stablePicture
from pygame_gui.elements.ui_text_box import UITextBox
from prompting import imageGen4, imageGen8, imageGen6_1, imageGenForcedPreface, scenario, scenarioGER


useWindowsSound = True
if(useWindowsSound):
    import win32com.client as wincl
else:
    from gtts import gTTS


openai.api_key = API_KEY

messages = []
imageGen = imageGen8 
useImageGenPreface = False

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# create a TTS engine using Windows 10 integrated TTS
tts_engine = wincl.Dispatch("SAPI.SpVoice")
for voice in tts_engine.GetVoices():
    if voice.GetDescription().startswith('Microsoft Katja'):
        tts_engine.Voice = voice
        break
tts_engine.Rate = 0
tts_engine.Volume = 100


# Set up the display
#original screen_width = 768
#original screen_height = 512
screen_width = 1152
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title of the window
pygame.display.set_caption("Research Project Pygame")

# Set up the game clock
CLOCK = pygame.time.Clock()

# Initialize the pygame_gui UIManager
UI_MANAGER = pygame_gui.UIManager((screen_width, screen_height))

# Create a "Record" button
button_size = (100, 50)
button_x = screen_width - button_size[0] - 20
button_y = screen_height - 70
record_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((button_x, button_y), button_size),
                                             text="Record",
                                             object_id='#record_button',
                                             manager=UI_MANAGER)

# Create a Textfield
TEXT_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20, screen_height - 70),
                                                                            (screen_width - 40 - button_size[0], 50)),
                                                                              manager=UI_MANAGER, object_id='#text_entry')
TEXT_INPUT.focus()

# Create a Output Textfield

textbox_test = ""

output_Textbox = UITextBox(textbox_test,                                            #if html'<font face=fira_code size=2 color=#000000>'
                             pygame.Rect((20, screen_height - 280), (250, 200)),    #left: float, top: float, width: float, height
                             manager=UI_MANAGER,
                                                                                    #object_id=ObjectID(class_id="@white_text_box",
                                                                                    #object_id="#text_box_2")
                            )
output_Textbox.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)

# Set up background
window_size = (screen_width, screen_height)
background_color = (0, 0, 0)
screen.fill(background_color)


# Set up textfield variables
# textfield_rect = pygame.Rect(20, screen_height - 70, screen_width - 40 - button_size[0] - 10, 50)
# textfield_color = (255, 255, 255)
# textfield_text = ""
# textfield_font = pygame.font.Font(None, 40)

# Load the image
# image = pygame.image.load("image.png")

# Get the dimensions of the image
# image_width = image.get_width()
# image_height = image.get_height()

# Calculate the center of the screen
# center_x = screen_width // 2
# center_y = screen_height // 2

# Calculate the top-left corner of the image
# image_x = center_x - (image_width // 2)
# image_y = center_y - (image_height // 2)

# Blit the image to the screen
# screen.blit(image, (image_x, image_y))

# Update the screen
pygame.display.flip()


# One time GPT Call:
def askGPT(structure, preface, prompt):
    task = []
    task.append({"role": "user", "content": structure+prompt}) # task: "Create a stable diffusion prompt out of this: "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=task)
    output = response["choices"][0]["message"]["content"]
    usedprompt = preface + output
    print("The Stable prompt is: " + usedprompt)
    return usedprompt

# Load an image:
def loadImage(name):
    background_image = pygame.image.load("images/"+name+".png")
    background_image = pygame.transform.scale(background_image, window_size)
    screen.blit(background_image, (0, 0))
    pygame.display.update()

# Set up audio recording parameters
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100
filename = 'sound/output.wav'

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


running = True
promptSet = False
iteration = 0

audio_frames = []
is_recording = False

while running:
    UI_REFRESH_RATE = CLOCK.tick(60)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
            event.ui_object_id == '#text_entry' and not promptSet):

            # Process the entered text
            print("The prompt is: "+ event.text)
            messages.append({"role": "system", "content": scenario + event.text}) # Prompt
            promptSet = True

            # Let Stable Diffusion create an Image
            if useImageGenPreface:
                stablePicture(iteration,askGPT(imageGen, imageGenForcedPreface,event.text))
            else:
                stablePicture(iteration,askGPT(imageGen, "",event.text))

            # Set background Image:
            loadImage("output_"+str(iteration))

            TEXT_INPUT.set_text("")
            TEXT_INPUT.redraw()
            iteration += 1

            print("The conversation is starting...")

        if(event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
            event.ui_object_id == '#text_entry' and promptSet and event.text[0] == "#"):
            
            #Regenerate Picture (same code as above)
            if useImageGenPreface:
                stablePicture(iteration,askGPT(imageGen, imageGenForcedPreface,event.text))
            else:
                stablePicture(iteration,askGPT(imageGen, "",event.text))

            # Set background Image:
            loadImage("output_"+str(iteration))

            TEXT_INPUT.set_text("")
            TEXT_INPUT.redraw()
            iteration += 1
            

        elif (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
            event.ui_object_id == '#text_entry' and promptSet):

            print("Answer is triggerd")

            if event.text == "stop":
                   running = False
                   break
            messages.append({"role": "user", "content": event.text})

            TEXT_INPUT.set_text("")
            TEXT_INPUT.redraw()

            UI_MANAGER.draw_ui(screen)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                # max_tokens= 30,
                messages=messages)
            output = response["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": output})
            print("\n" + output + "\n")

            textbox_test = output; #Write into Textbox_Output
            pygame.display.flip()

            if(useWindowsSound):
                #TTS Windows:
                tts_engine.Speak(output)
            else:
                #TTS Google:
                mp3_fp = BytesIO()
                tts = gTTS(output, lang='en')
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                pygame.mixer.music.load(mp3_fp, 'mp3')
                pygame.mixer.music.play()

        
        if (event.type == pygame_gui.UI_BUTTON_PRESSED and
            event.ui_object_id == '#record_button'):

            # Button pressed, perform the desired action
            if not is_recording:
                record_button.set_text("Recording...")
                is_recording = True
                recording_thread = threading.Thread(target=record_audio)
                recording_thread.start()
            else:
                record_button.set_text("Record")
                is_recording = False
                recording_thread.join()
                save_audio_to_file()
                
                #send file to whisper
                audio_file= open("sound/output.wav", "rb")
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                TEXT_INPUT.set_text(transcript.text)
                TEXT_INPUT.focus()
                #TODO event.type = pygame_gui.UI_TEXT_ENTRY_FINISHED


                print(transcript.text)
              
                # messages.append({"role": "user", "content": transcript.text})
                # response = openai.ChatCompletion.create(
                #     model="gpt-3.5-turbo",
                #     messages=messages)
                # output = response["choices"][0]["message"]["content"]
                # messages.append({"role": "assistant", "content": output})

    UI_MANAGER.process_events(event)
    
    UI_MANAGER.update(UI_REFRESH_RATE)
    UI_MANAGER.draw_ui(screen)  # Draw the UI elements

    # Update the display
    pygame.display.update()

    # Cap the frame rate to 60 FPS
    # CLOCK.tick(60)


# Quit Pygame
pygame.mixer.quit()
pygame.quit()
