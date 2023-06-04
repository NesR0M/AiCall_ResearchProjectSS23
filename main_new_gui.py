import pygame
import pygame_gui
import openai
import threading
import pyaudio
import wave
import threading
from personal_key import API_KEY
from socketClient import stablePicture
from pygame.locals import K_LALT
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui import UI_TEXT_ENTRY_CHANGED
from prompting import imageGen4, imageGen8, imageGen6_1, imageGenForcedPreface, scenario, scenarioGER, correctionGER

useWindowsSound = True
if(useWindowsSound):
    import win32com.client as wincl
else:
    from gtts import gTTS


openai.api_key = API_KEY

messages = []
imageGen = imageGen8 
useImageGenPreface = False

output_Text = ""


def tts_thread(output, useWindowsSound):
    if useWindowsSound:
        # TTS Windows:
        tts_engine.Speak(output)
    else:
        # TTS Google:
        mp3_fp = BytesIO()
        tts = gTTS(output, lang='en')
        tts.save_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()

def stablediff_thread(iteration, imageGen, preface, userInput):
    stablePicture(iteration, askGPT(imageGen, preface, userInput))
    loadImage("output_"+str(iteration))



# Initialize Pygame
pygame.init()
pygame.mixer.init()

# create a TTS engine using Windows 10 integrated TTS
if(useWindowsSound):
    tts_engine = wincl.Dispatch("SAPI.SpVoice")
    for voice in tts_engine.GetVoices():
        if voice.GetDescription().startswith('Microsoft Katja'):
            tts_engine.Voice = voice
            break
    tts_engine.Rate = 0
    tts_engine.Volume = 100


# Set up the display
screen_width = 1152
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title of the window
pygame.display.set_caption("ChatWindow")

# Set up the game clock
CLOCK = pygame.time.Clock()

# Initialize the pygame_gui UIManager
UI_MANAGER = pygame_gui.UIManager((screen_width, screen_height))

# Create a "Record" button
button_size = (80, 80)
button_x = (screen_width - button_size[0]) / 2
button_y = (screen_height - button_size[1]) - 30

TEXT_INPUT_HEIGHT = 50
TEXT_INPUT_WIDTH = screen_width / 2

TEXT_INPUT_X = (screen_width - TEXT_INPUT_WIDTH) / 2
TEXT_INPUT_Y = button_y-TEXT_INPUT_HEIGHT
TEXT_OUTPUT_Y = button_y - screen_height / 4 

TEXT_OUTPUT_HEIGHT = TEXT_INPUT_Y - TEXT_OUTPUT_Y

# Create a Textfield
output_Textbox = pygame_gui.elements.UITextBox("",
                                               relative_rect=pygame.Rect((TEXT_INPUT_X, TEXT_OUTPUT_Y+10), 
                                                                          (TEXT_INPUT_WIDTH, TEXT_OUTPUT_HEIGHT)),
                                                manager=UI_MANAGER, 
                                                object_id='#text_entry')

# Create a Textfield
TEXT_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((TEXT_INPUT_X, TEXT_INPUT_Y+5),
                                                                            (TEXT_INPUT_WIDTH, TEXT_INPUT_HEIGHT)),
                                                                              manager=UI_MANAGER, object_id='#text_entry')



record_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((button_x, button_y), button_size),
                                             text="Record",
                                             object_id='#record_button',
                                             manager=UI_MANAGER)

TEXT_INPUT.focus()


# Set up background
window_size = (screen_width, screen_height)
background_color = (0, 0, 0)
screen.fill(background_color)


pygame.display.flip()


# One time GPT stable Call:
def askGPT(structure, preface, prompt):
    task = []
    task.append({"role": "user", "content": structure+prompt+" happy"}) # task: "Create a stable diffusion prompt out of this: "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=task)
    output = response["choices"][0]["message"]["content"]
    usedprompt = preface + output
    print("The Stable prompt is: " + usedprompt)
    return usedprompt

# One time GPT correction Call:
def askGPTforCorrection(structure, prompt):
    task = []
    task.append({"role": "user", "content": structure+prompt}) # task: "Correct this sentence: "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=task)
    output = response["choices"][0]["message"]["content"]
    print("Die Korrektur lautet: " + output)
    return output

def highlight_differences(original, corrected):
    original = original.replace('.', '')  # Remove periods from original sentence
    corrected = corrected.replace('.', '')  # Remove periods from corrected sentence

    original_words = original.split()
    corrected_words = corrected.split()

    result = ""
    i = 0
    j = 0
    while i < len(original_words) and j < len(corrected_words):
        if original_words[i] != corrected_words[j]:
            incorrect = []
            correct = []
            while (i < len(original_words) and j < len(corrected_words) and 
                   original_words[i] != corrected_words[j]):
                incorrect.append(original_words[i])
                correct.append(corrected_words[j])
                i += 1
                j += 1
            
            result += "<u><font color=\"#FF0000\">" + " ".join(incorrect) + "</font></u> "
            result += "<i><font color=\"#ecb20b\">" + " ".join(correct) + "</font></i> "
        else:
            result += original_words[i] + " "
            i += 1
            j += 1

    # If there are remaining words in original sentence
    while i < len(original_words):
        result += "<u>" + original_words[i] + "</u> "
        i += 1

    # If there are remaining words in corrected sentence
    while j < len(corrected_words):
        result += "<i>" + corrected_words[j] + "</i> "
        j += 1

    return result

def correctOutput(string1, string2):
    result = string1 + " // " +"<u><font color=\"#ecb20b\">" + string2 + "</font></u>"
    return result

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
    UI_REFRESH_RATE = CLOCK.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
            event.ui_object_id == '#text_entry' and not promptSet):

            # Process the entered text
            print("The prompt is: "+ event.text)
            messages.append({"role": "system", "content": scenarioGER + event.text}) # Prompt
            promptSet = True

            # Let Stable Diffusion create an Image
            if useImageGenPreface:
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, imageGenForcedPreface, event.text))
                thread.start()
            else:
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, "", event.text))
                thread.start()

            TEXT_INPUT.set_text("")
            TEXT_INPUT.redraw()
            iteration += 1

            print("The conversation is starting...")

        if(event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
            event.ui_object_id == '#text_entry' and promptSet and event.text and event.text[0] == "#"):

            text = event.text

            TEXT_INPUT.set_text("")
            TEXT_INPUT.redraw()
            iteration += 1

            #Regenerate Picture (same code as above)
            if useImageGenPreface:
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, imageGenForcedPreface, event.text))
                thread.start()
            else:
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, "", event.text))
                thread.start()
            

        elif (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
            event.ui_object_id == '#text_entry' and promptSet):

            if event.text == "":
                print("Empty input is skipped")
            else:
                print("Answer is triggerd")

                text = event.text
                correctText = correctOutput(text, askGPTforCorrection(correctionGER, text))
                print(correctText)

                output_Text += "\n<font color=\"#FF0000\">YOU:</font>" +" "+ "<font color=\"#ffeeee\">" + correctText+"</font>"
                output_Textbox.set_text(output_Text) #Write into Textbox_Output

                if event.text == "stop":
                    running = False
                    break
                messages.append({"role": "user", "content": text})

                TEXT_INPUT.set_text("")
                TEXT_INPUT.redraw()
                UI_MANAGER.draw_ui(screen)
                pygame.display.update()

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    # max_tokens= 30,
                    messages=messages)
                output = response["choices"][0]["message"]["content"]
                messages.append({"role": "assistant", "content": output})
                print("\n" + output + "\n")

                output_Text += "\n<font color=\"#209de0\">AI:</font>"+ " "+ "<font color=\"#76b8db\">" + output +"</font>"
                output_Textbox.set_text(output_Text) #Write into Textbox_Output
                UI_MANAGER.draw_ui(screen)  # Draw the UI elements
                pygame.display.update()  # Update the display

                thread = threading.Thread(target=tts_thread, args=(output, useWindowsSound))
                thread.start()
        
        if ((event.type == pygame_gui.UI_BUTTON_PRESSED and
            event.ui_object_id == '#record_button') or (event.type == pygame.KEYDOWN and event.key == K_LALT)):

            # Button pressed, perform the desired action
            if not is_recording:
                record_button.set_text("STOP")
                is_recording = True
                recording_thread = threading.Thread(target=record_audio)
                recording_thread.start()
            else:
                record_button.set_text("Record")
                is_recording = False
                recording_thread.join()
                save_audio_to_file()

                duration = 0
                with wave.open("sound/output.wav") as currentA:
                    duration = currentA.getnframes() / currentA.getframerate()
                
                #send file to whisper
                audio_file = open("sound/output.wav", "rb")
                if  duration > 1:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)
                    TEXT_INPUT.set_text(transcript.text)
                    TEXT_INPUT.focus()
                    print(transcript.text)
                else:
                    print("Audio duration under limit")

        UI_MANAGER.process_events(event)
    UI_MANAGER.update(UI_REFRESH_RATE)
    UI_MANAGER.draw_ui(screen) 
    pygame.display.update()

    # Cap the frame rate to 60 FPS
    # CLOCK.tick(60)


# Quit Pygame
pygame.mixer.quit()
pygame.quit()