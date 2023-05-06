import pygame
import pygame_gui
import openai
from gtts import gTTS
from io import BytesIO
from personal_key import API_KEY
from socketClient import stablePicture
from prompting import imageGen

openai.api_key = API_KEY

# 62.116.57.179
# PORT

messages = []

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title of the window
pygame.display.set_caption("Sex II")

# Set up the game clock
clock = pygame.time.Clock()

# Initialize the pygame_gui UIManager
ui_manager = pygame_gui.UIManager((screen_width, screen_height))

# Create a "Record" button
button_size = (100, 50)
button_x = screen_width - button_size[0] - 20
button_y = screen_height - 70
record_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((button_x, button_y), button_size),
                                             text="Record",
                                             manager=ui_manager)

# Set up image as background
# def setbackground(iteration):
background_image = pygame.image.load("background.jpg")
window_size = (800, 600)
background_image = pygame.transform.scale(background_image, window_size)
screen.blit(background_image, (0, 0))
pygame.display.update()

# Set up textfield variables
textfield_rect = pygame.Rect(20, screen_height - 70, screen_width - 40 - button_size[0] - 10, 50)
textfield_color = (255, 255, 255)
textfield_text = ""
textfield_font = pygame.font.Font(None, 40)

# Load the image
image = pygame.image.load("image.png")

# Get the dimensions of the image
image_width = image.get_width()
image_height = image.get_height()

# Calculate the center of the screen
center_x = screen_width // 2
center_y = screen_height // 2

# Calculate the top-left corner of the image
image_x = center_x - (image_width // 2)
image_y = center_y - (image_height // 2)

# Blit the image to the screen
screen.blit(image, (image_x, image_y))

# Update the screen
pygame.display.flip()


# One time GPT Call:
def askGPT(structure,prompt):
    task = []
    task.append({"role": "user", "content": structure+prompt}) # task: "Create a stable diffusion prompt out of this: "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=task)
    output = response["choices"][0]["message"]["content"]
    print("The Stable prompt is: " + output)
    return output


running = True
promptSet = False

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == record_button:
                    # Button pressed, perform the desired action
                    print("Record button pressed.")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                # Remove the last character from the textfield
                textfield_text = textfield_text[:-1]
            elif event.key == pygame.K_RETURN and not promptSet:
                # Process the entered text
                print("The prompt is: "+ textfield_text)
                messages.append({"role": "system", "content": textfield_text}) # Prompt
                promptSet = True

                stablePicture(0,askGPT(imageGen, textfield_text))
                textfield_text = ""
                # TODO ADD setbackground(0)
                print("The conversation is starting...")
            elif event.key == pygame.K_RETURN and promptSet:
                if textfield_text == "stop":
                   running = False
                   break
                messages.append({"role": "user", "content": textfield_text})
                textfield_text = ""
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages)
                output = response["choices"][0]["message"]["content"]
                messages.append({"role": "assistant", "content": output})
                print("\n" + output + "\n")
                #TODO Add text to Textfield

                #TTS:
                mp3_fp = BytesIO()
                tts = gTTS(output, lang='en')
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                pygame.mixer.music.load(mp3_fp, 'mp3')
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)

            else:
                # Add the entered character to the textfield
                textfield_text += event.unicode

        # Pass events to the UI manager
        ui_manager.process_events(event)

    # Update game logic

    # Update the UI manager
    ui_manager.update(clock.tick(60))

    # Draw to the screen
    #TODO DEL old: screen.blit(image, (image_x, image_y))
    pygame.draw.rect(screen, (255, 255, 255), textfield_rect)  # Draw the textfield background
    pygame.draw.rect(screen, (0, 0, 0), textfield_rect, 2)  # Draw the textfield border
    text_surface = textfield_font.render(textfield_text, True, (0, 0, 0))  # Render the text
    screen.blit(text_surface, (textfield_rect.x + 10, textfield_rect.y + 10))  # Draw the text to the screen
    ui_manager.draw_ui(screen)  # Draw the UI elements

    # Update the display
    pygame.display.update()

    # Cap the frame rate to 60 FPS
    clock.tick(60)

# Quit Pygame
pygame.quit()
