""" Just type the images you want to create in the ImageGeneration.data file ',True' next to it in frontend/files/ImageGeneration.data and run this program """

import asyncio
from random import randint
import os
from dotenv import get_key
from PIL import Image
from time import sleep
import requests

# function to open and dsiplay images based on prompt
def open_images(prompt):
    folder_path = r"data/images/"
    prompt = prompt.replace(" ", "_")

    #generate the file names for images
    File = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    #generating the image path
    for jpg_file in File:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(2)  # pause for 2 sec before showing the next image
        except IOError as e:
            print(f"{e}")

# API details for hugging face
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# function to send a query to the hugging face api
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# function to generate images based on the query
async def generate_image(prompt: str):
    
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if not image_bytes or len(image_bytes) < 100:
            print(f"{i+1} is empty or corrupted, skip")
        try:
            with open(fr"data/images/{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
                f.write(image_bytes)
        except Exception as e:
            print(f"{e}")

# to generate the images
def GenerateImage(prompt: str):
    asyncio.run(generate_image(prompt))
    open_images(prompt)

# main loop to monitor the image generation response
while True:

    try:
        with open(r"frontend/files/ImageGeneration.data", "r") as f:
            Data :str = f.read()

        Prompt, status = Data.split(",")

        if status == "True":
            print("generating images....")
            ImageStatus = GenerateImage(prompt=Prompt)

            with open(r"frontend/files/ImageGeneration.data", "w") as f:
                f.write("False,False")
                break

        else:
            sleep(2)   # wait for 2 seconds before checking again

    except Exception as e:
        print(f"Exception {e}")