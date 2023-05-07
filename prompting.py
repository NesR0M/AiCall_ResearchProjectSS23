imageGen = "Give me a description of objects in the background in single words, delimited by comma, in this style: portrait of beautiful girl, ethereal, realistic anime, trending on pixiv, detailed, clean lines, sharp lines, crisp lines, award winning illustration, masterpiece, eugene de blaas and ross tran, vibrant color scheme, intricately detailed from this prompt: "
imageGen2 = "Give me a description of objects for an image in single words, delimited by comma, in this style: portrait of beautiful girl, ethereal, realistic anime, trending on pixiv, detailed, clean lines, sharp lines, crisp lines, award winning illustration, masterpiece, eugene de blaas and ross tran, vibrant color scheme, intricately detailed from this prompt: "
imageGen3 = "As a writer, you're seeking inspiration for a coffee shop scene in your story. You need GPT-3 to generate a prompt for an image of a person (either a beautiful girl or boy), with objects like coffee, cups, saucers, tables, chairs, and a menu. However, it's important that the answer is provided in single words, delimited by comma, to make it easier to incorporate into your writing. Can you provide a list of objects that would help bring the scene to life? Get the location from this sentence: "
imageGen4 = "Limit your response to only the answer. As a writer, you're seeking inspiration for a scene in your story. You need GPT-3 to generate a prompt for an image of a person (either a beautiful girl or boy). Generate 30 single words, delimited by comma, for objects related to this sentence to make it as descriptive as possible: "
imageGen5 = "I am a professional artist seeking assistance in creating an engaging image with the illusion of conversation. Please provide single-word responses, separated by commas. The viewer should feel as though they are conversing with either a '1girl' or '1boy' (your choice) in a cowboy shot (camera perspective) that remains central in the image that is always looking at the viewer. Additionally, provide 40 descriptive words to enhance the background and contribute to the conversational atmosphere inspired by the phrase: "
imageGen5_1 = "I am a professional artist seeking assistance in creating an engaging image with the illusion of conversation. Please provide single-word responses, separated by commas. The viewer should feel as though they are conversing with either a person in the center in a cowboy shot (camera perspective) that is always looking at the viewer. Additionally, provide 35 descriptive words to enhance the background and contribute to the conversational atmosphere inspired by the phrase: "
imageGen6 = "I am a professional artist seeking single-word responses, separated by commas, for an engaging image with the illusion of conversation. The subject should be either a '1girl' or '1boy' (your choice) in a cowboy shot, always looking at the viewer. Please provide 35 descriptive words to create a conversational atmosphere. Example: '1girl, cowboy shot, looking at viewer, Engaging, Conversation, Vodka, Borscht, Embroidery, Red Square, Folk Music, Onion Domes, Caviar, Matryoshka Dolls, Kremlin, Samovar, Cyrillic Alphabet, Traditions, Bolshoi Ballet, St. Basil's Cathedral, Blini, Russian Vodka Room, Zakuski, Balalaika, Pushkin, Soviet Union, Bear, Faberge Eggs, Siberia, St. Petersburg, Winter Palace, Taiga Forest, Tsar, Peterhof Palace, Russian Orthodox Church, Tchaikovsky, Rasputin, Hermitage Museum, Russian Federation.' The new sentence inspired by the following phrase:"
imageGenForcedPreface = "1girl, cowboy shot, looking at viewer"
scenario ="converse with me. dont narrate. I will answer in the following texts. You are a girl named Emila. You start talking. Answer in a maximum of four sentences. The scenario is: "

def stableDifpayload(prompt):
    payload = {
                "enable_hr": True,
                "denoising_strength": 0.58,
                "firstphase_width": 768,
                "firstphase_height": 512,
                "hr_scale": 2,
                "hr_upscaler": "Latent (nearest-exact)",
                "hr_second_pass_steps": 20,
                "prompt": prompt,
                "seed": -1,
                "sampler_name": "DPM++ 2M Karras",
                "steps": 25,
                "cfg_scale": 7,
                "width": 768,
                "height": 512,
                "negative_prompt": "EasyNegative, badhandv4, nsfw, signature, patreon",
                "eta": 31337,
            }
    return payload