#while running:
#    # Handle events
#    for event in pygame.event.get():
#        if event.type == pygame.QUIT:
#            running = False
#        elif event.type == pygame.USEREVENT:
#            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
#                if event.ui_element == record_button:
#                    # Button pressed, perform the desired action
#                    print("Record button pressed.")
#        elif event.type == pygame.KEYDOWN:
#            if event.key == pygame.K_BACKSPACE:
#                # Remove the last character from the textfield
#                textfield_text = textfield_text[:-1]
#            elif event.key == pygame.K_RETURN and not promptSet:
#                # Process the entered text
#                print("The prompt is: "+ textfield_text)
#                messages.append({"role": "system", "content": textfield_text}) # Prompt
#                promptSet = True
#
#                # Let Stable Diffusion create an Image
#                stablePicture(iteration,askGPT(imageGen4, ",cowboy shot",textfield_text))
#                # Set background Image:
#                loadImage("output_"+str(iteration))
#
#                textfield_text = ""
#                iteration += 1
#
#                print("The conversation is starting...")
#            elif event.key == pygame.K_RETURN and promptSet:
#                if textfield_text == "stop":
#                   running = False
#                   break
#                messages.append({"role": "user", "content": textfield_text})
#                textfield_text = ""
#                response = openai.ChatCompletion.create(
#                    model="gpt-3.5-turbo",
#                    messages=messages)
#                output = response["choices"][0]["message"]["content"]
#                messages.append({"role": "assistant", "content": output})
#                print("\n" + output + "\n")
#                #TODO Add text to Textfield
#
#                #TTS:
#                mp3_fp = BytesIO()
#                tts = gTTS(output, lang='en')
#                tts.write_to_fp(mp3_fp)
#                mp3_fp.seek(0)
#                pygame.mixer.music.load(mp3_fp, 'mp3')
#                pygame.mixer.music.play()
#
#                while pygame.mixer.music.get_busy():
#                    pygame.time.wait(100)
#
#            else:
#                # Add the entered character to the textfield
#                textfield_text += event.unicode
#
#        # Pass events to the UI manager
#        UI_MANAGER.process_events(event)
#
#    # Update game logic
#
#    # Update the UI manager
#    UI_MANAGER.update(UI_REFRESH_RATE)
#
#    # Draw to the screen
#    #TODO DEL old: screen.blit(image, (image_x, image_y))
#    # pygame.draw.rect(screen, (255, 255, 255), textfield_rect)  # Draw the textfield background
#    # pygame.draw.rect(screen, (0, 0, 0), textfield_rect, 2)  # Draw the textfield border
#    # text_surface = textfield_font.render(textfield_text, True, (0, 0, 0))  # Render the text
#    # screen.blit(text_surface, (textfield_rect.x + 10, textfield_rect.y + 10))  # Draw the text to the screen
#    UI_MANAGER.draw_ui(screen)  # Draw the UI elements
#
#    # Update the display
#    pygame.display.update()
#
#    # Cap the frame rate to 60 FPS
#    CLOCK.tick(60)