import time
import pygame
import pygame_gui
import openai
import threading
import pyaudio
import wave
import threading
import deepl
from personal_key import OPENAI_API_KEY, DEEPL_API_KEY
from socketClient import stablePicture
from pygame.locals import K_LALT
from pygame_gui.elements import UIWindow, UITextEntryBox, UITextBox
from prompting import storyGen1, imageGen10, imageGenForcedPreface, scenario, correctionGER

useWindowsSound = True
if(useWindowsSound):
    import win32com.client as wincl
else:
    from gtts import gTTS


openai.api_key = OPENAI_API_KEY

translator = deepl.Translator(DEEPL_API_KEY)

messages = []
storyGen = storyGen1
imageGen = imageGen10 
useImageGenPreface = False

outputLinkText = ""
output_Text = ""

running = True
promptSet = False
iteration = 0

background_image = None

audio_frames = []
is_recording = False
isTextInputVisible = False

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

def stablediff_thread(iteration, imageGen, preface, storyGen, userInput):
    if (storyGen == ""):
        stablePicture(iteration, askGPT(imageGen, preface, userInput, "Image generation"))
    else: 
        stablePicture(iteration, askGPT(imageGen, preface, askGPT(storyGen,"", userInput, "Story generation"), "Image generation"))
    print("Image is loading...")
    loadImage("output_"+str(iteration))
    

# Initialize Pygame
pygame.init()
pygame.mixer.init()

#add feedback sound
feedbackSound = pygame.mixer.Sound('Click.mp3')

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
window_size = (screen_width, screen_height)
image_size = (384,768)
screen = pygame.display.set_mode(window_size)

# Set the title of the window
pygame.display.set_caption("ChatWindow")

# Initialize the pygame_gui UIManager
UI_MANAGER = pygame_gui.UIManager(window_size, 'themes.json')

# Setup Background 
background = pygame.Surface(window_size)
background.fill(UI_MANAGER.ui_theme.get_colour('dark_bg'))

# Set up the game clock
CLOCK = pygame.time.Clock()

# Create a "Record" button
button_size = (80, 80)

TEXT_INPUT_HEIGHT = 50
TEXT_INPUT_WIDTH = (screen_width / 3)*2

TEXT_INPUT_X = (screen_width) / 3
TEXT_INPUT_Y = (screen_height - button_size[1]) - 20-TEXT_INPUT_HEIGHT
button_x = (TEXT_INPUT_X + (TEXT_INPUT_WIDTH/2) - (button_size[0]/2))
button_y = (screen_height - button_size[1]) - 10
TEXT_OUTPUT_Y = -10 

TEXT_OUTPUT_HEIGHT = TEXT_INPUT_Y - TEXT_OUTPUT_Y

PANEL_HEIGHT = screen_height
PANEL_WIDTH = TEXT_INPUT_X

PANEL_X = 0
PANEL_Y = TEXT_OUTPUT_Y

# Create a Textfield
TEXT_OUTPUT = pygame_gui.elements.UITextBox("",
                                               relative_rect=pygame.Rect((TEXT_INPUT_X, TEXT_OUTPUT_Y+10), 
                                                                          (TEXT_INPUT_WIDTH, TEXT_OUTPUT_HEIGHT)),
                                                manager=UI_MANAGER, 
                                                object_id='#text_output')

# Create a Textfield
TEXT_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((TEXT_INPUT_X, TEXT_INPUT_Y+5),
                                                                            (TEXT_INPUT_WIDTH, TEXT_INPUT_HEIGHT)),
                                                                              manager=UI_MANAGER, object_id='#text_entry')



BUTTON_RECORD = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((button_x, button_y), button_size),
                                             text="",
                                             object_id='#record_button',
                                             manager=UI_MANAGER)

# Button to expand Textfield
BUTTON_TEXT_INPUT = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((button_x+(button_size[0]), button_y+(button_size[0]/2)-(button_size[0]/4)), ((button_size[0]/2),(button_size[1]/2))),
                                             text="",
                                             object_id='#text_button',
                                             manager=UI_MANAGER)

#PANEL = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((0, 0), (PANEL_WIDTH, PANEL_HEIGHT)), 
#                                    object_id='#panel',
#                                    manager=UI_MANAGER)

# Define the color of the line (in RGB format)
line_color = (255, 255, 255)  # White color

# Define the start and end points of the line
start_pos = (TEXT_INPUT_X, 0)
end_pos = (TEXT_INPUT_X, screen_height)

# Define the width of the line
line_width = 1

# Draw the line
pygame.draw.line(screen, line_color, start_pos, end_pos, line_width)

pygame.display.flip()

#isTextInputVisible = False //already set
TEXT_INPUT.disable()
TEXT_INPUT.hide()


# One time GPT stable Call:
def askGPT(structure, preface, prompt, reason):
    task = []
    task.append({"role": "user", "content": prompt+structure}) # task: "Create a stable diffusion prompt out of this: "
    try:
        response = openai.ChatCompletion.create(
        model="gpt-4-0314",
        messages=task)
        output = response["choices"][0]["message"]["content"]
        usedprompt = ""
        if(preface != ""):
            usedprompt = preface + output + ",happy"
        else: 
            usedprompt = preface + output   
        print("ASKGPT "+reason+": " + usedprompt)
        return usedprompt

    except openai.error.RateLimitError as e:
        # Retry the request after waiting for some time
        print("Rate limit exceeded. Retrying after 15 seconds...")
        time.sleep(15)
        return askGPT(structure, preface, prompt, reason)
    
    

# One time GPT correction Call:
def askGPTForCorrection(structure, prompt):
    task = []
    task.append({"role": "user", "content": structure+prompt}) # task: "Correct this sentence: "
    try:
        response = openai.ChatCompletion.create(
        model="gpt-4-0314",
        messages=task)
        output = response["choices"][0]["message"]["content"]
        print("Die Korrektur lautet: " + output)
        return output
    
    except openai.error.RateLimitError as e:
        # Retry the request after waiting for some time
        print("Rate limit exceeded. Retrying after 15 seconds...")
        time.sleep(15)
        return askGPTForCorrection(structure, prompt)
    

def highlightDifferences(original, corrected):
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
    # Replace 'NOT OK' with 'corrected sentence' in string2
    string2 = string2.replace('NOT OK.', '//')
    # Then remove 'OK' from string2
    string2 = string2.replace('OK', '')
    string2 = string2.replace('.', '')
    result = string1 +" "+ "<u><font color=\"#ecb20b\">" + string2 + "</font></u>"
    return result


# Load an image:
def loadImage(name):
    global background_image
    background_image = pygame.image.load("images/"+name+".png")
    background_image = pygame.transform.scale(background_image, image_size)
    print("Image is loaded")
    screen.blit(background_image, (0, 0))
    pygame.display.update()
    

# Set up audio recording parameters
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100
filename = 'sound/output.wav'

def recordAudio():
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

def saveAudioToFile():
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(audio_frames))
    wf.close()

#Create a Link for DeepL HTML interface. This function is not in use.
def httpsDeepLString(input_string):
    url = "https://www.deepl.com/translator#de/en/"
    formatted_string = input_string.replace(" ", "%20")
    return url + formatted_string

#Use DeepL API to translate the string into english
def translateWithDeepLAPI(toTranslateString):
    return translator.translate_text(toTranslateString, target_lang="EN-US")

def changeTextInputVisability(makeVisible):
    global isTextInputVisible
    if(makeVisible):
        if(not isTextInputVisible):
            isTextInputVisible = True
            TEXT_INPUT.enable()
            TEXT_INPUT.show()
            BUTTON_TEXT_INPUT.select()
    else:
        if(isTextInputVisible):
            isTextInputVisible = False
            TEXT_INPUT.disable()
            TEXT_INPUT.hide()

def switchTextInputVisibility():
    global isTextInputVisible
    if isTextInputVisible:
        isTextInputVisible = False
        TEXT_INPUT.disable()
        TEXT_INPUT.hide()
    else:
        isTextInputVisible = True
        TEXT_INPUT.enable()
        TEXT_INPUT.show()
        BUTTON_TEXT_INPUT.select()


#microphone icon
#mic_icon = pygame.image.load('microphone.jpg')
#mic_icon = pygame.transform.scale(mic_icon, button_size)
#screen.blit(mic_icon, (button_x, button_y))


while running:
    UI_REFRESH_RATE = CLOCK.tick(60)/1000.0

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
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, imageGenForcedPreface, storyGen, event.text))
                thread.start()
            else:
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, "", storyGen, event.text))
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
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, imageGenForcedPreface, storyGen, event.text))
                thread.start()
            else:
                thread = threading.Thread(target=stablediff_thread, args=(iteration, imageGen, "", storyGen, event.text))
                thread.start()
            

        elif (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
            event.ui_object_id == '#text_entry' and promptSet and event.text and event.text[0] != "#"):

            if event.text == "":
                print("Empty input is skipped")
            else:
                print("Answer is triggerd")

                text = event.text

                feedbackSound.play()
                TEXT_INPUT.set_text("")
                TEXT_INPUT.redraw()

                correctText = correctOutput(text, askGPTForCorrection(correctionGER, text))
                print(correctText)

                output_Text += "\n<font color=\"#FF0000\">YOU:</font>" +" "+ "<font color=\"#ffeeee\">" + correctText+"</font>"
                TEXT_OUTPUT.set_text(output_Text) #Write into Textbox_Output

                UI_MANAGER.draw_ui(screen) 
                pygame.display.update()

                if event.text == "stop":
                    running = False
                    break
                messages.append({"role": "user", "content": text})


                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    # max_tokens= 30,
                    messages=messages)
                outputLinkText = response["choices"][0]["message"]["content"]
                messages.append({"role": "assistant", "content": outputLinkText})
                print("\n" + outputLinkText + "\n")

                outputLink = outputLinkText.replace(' ', '_')

                output_Text += "\n<font color=\"#209de0\">AI:</font>"+ " "+ "<font color=\"#76b8db\">" + "<a href="+outputLink+">"+outputLinkText+"</a></font>"
                TEXT_OUTPUT.set_text(output_Text) #Write into Textbox_Output
                UI_MANAGER.draw_ui(screen)  # Draw the UI elements
                pygame.display.update()  # Update the display

                thread = threading.Thread(target=tts_thread, args=(outputLinkText, useWindowsSound))
                thread.start()
        
        if ((event.type == pygame_gui.UI_BUTTON_PRESSED and
            event.ui_object_id == '#record_button') or (event.type == pygame.KEYDOWN and event.key == K_LALT)):

            # Button pressed, perform the desired action
            if not is_recording:
                #BUTTON_RECORD.set_text("STOP")
                BUTTON_RECORD.select()
                is_recording = True
                recording_thread = threading.Thread(target=recordAudio)
                recording_thread.start()
            else:
                #BUTTON_RECORD.set_text("Record")
                is_recording = False
                recording_thread.join()
                saveAudioToFile()

                duration = 0
                with wave.open("sound/output.wav") as currentA:
                    duration = currentA.getnframes() / currentA.getframerate()
                
                #send file to whisper
                audio_file = open("sound/output.wav", "rb")
                if  duration > 1:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)

                    changeTextInputVisability(True)


                    TEXT_INPUT.set_text(transcript.text)
                    TEXT_INPUT.focus()
                    print(transcript.text)
                else:
                    print("Audio duration under limit")
                
        if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id == '#text_button'):
            switchTextInputVisibility()
            TEXT_INPUT.redraw()

        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if event.ui_element is TEXT_OUTPUT:

                linkText = event.link_target
                translation = str(translateWithDeepLAPI(linkText.replace('_', ' ')))
                
                #External Window
                #notepad_window = UIWindow(pygame.Rect(50, 20, 300, 400), window_display_title="English translation:")
                #text_output_box = UITextBox(
                #    relative_rect=pygame.Rect((0, 0), notepad_window.get_container().get_size()),
                #    html_text="",
                #    container=notepad_window)
                #text_output_box.set_text(translation)
                
                print("DeepL translation: "+ translation)     

    
                output_Text += "\n\n\n<font color=\"#d77aff\">" + "Translation: "+translation+"</font>"
                TEXT_OUTPUT.set_text(output_Text) #Write into Textbox_Output
                UI_MANAGER.draw_ui(screen)  # Draw the UI elements
                pygame.display.update()  # Update the display


        UI_MANAGER.process_events(event)

    UI_MANAGER.update(UI_REFRESH_RATE)

    if background_image is None:
        screen.blit(background, (0, 0))
        pygame.draw.line(screen, line_color, start_pos, end_pos, line_width)
    else:
        screen.blit(background_image, (0, 0))
        pygame.draw.line(screen, line_color, start_pos, end_pos, line_width)

    UI_MANAGER.draw_ui(screen) 

    pygame.display.update()

    # Cap the frame rate to 60 FPS
    # CLOCK.tick(60)

# Quit Pygame
pygame.mixer.quit()
pygame.quit()