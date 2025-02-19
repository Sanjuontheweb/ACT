import os
import asyncio
import keyboard
import requests
import webbrowser
import subprocess

from AppOpener import close, open as appopen
from webbrowser import open as webopen
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from pywhatkit import playonyt, search
from groq import Groq
from rich import print

#loading environmet vars
env_vars = dotenv_values('.env')
GroqAPIKey = env_vars.get("groqapikey")

#define css classes for parsing specific elements in HTML content
classes = ["zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLCW", "gsrt vk_bk FzvWSb YwPhpf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# for making web requests
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my atmost priority, feel free to reach out to me if there's anything else i can help you with.",
    "I'm at your service at any additional requests or support, don't hesistate to ask me."
]

# list to storechatbot message
messages = []

# system msg to give context
SystemChatBot = [
  {"role" : "system", "content": f"Hey, I am {os.environ['username']}. You are a content writer. You have to write content like letters, articles, blogs, codes, applications, essays, notes, songs, poems etc."}
]

# for searching google
def GoogleSearch(Topic):
    search(Topic)
    return True

# func to generate content and save it in a file
def Content(Topic):

    def NotepadOpen(File):
       default_text_editor = "notepad.exe"
       subprocess.Popen([default_text_editor, File])

    # to generate content using AI [mixtral]
    def ContentGeneratorAI(prompt):
        messages.append({"role" : "user", "content" : f"{prompt}"})

        completions = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens= 2048,
            temperature=0.7,
            stop=None,
            stream=True,
            top_p=1   #use nuclear sampling for response diversity
       )

        #initialize answer var
        Answer = ""

        for chunk in completions:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role":"assistant", "content": Answer})
        return Answer
    
    # removes content from the topic
    Topic: str = Topic.replace("Content ", "")
    content_by_AI = ContentGeneratorAI(Topic)

    # write the content to a file
    with open(rf"data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as f:
        f.write(content_by_AI)
        f.close()

    NotepadOpen(rf"data\{Topic.lower().replace(' ', '')}.txt")
    return True

#func to search a topic on yt
def SearchYT(Topic):
    URL4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(URL4Search)
    return True  #success

# func to play a yt video
def PlayVid(query):
    playonyt(query)
    return True

#function to open app or perform a googlesearch for the app name
def OpenApp(app, sess=requests.session()):

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True

    except:
        GoogleSearch(app)

# to close an app
def CloseApp(app):

    # skip if its chrome
    if app == "Chrome":
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False
        
# function to execute system level commands
def System(command):

    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume unmute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    # to execute the up 4 commands
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

# function to translate and execute user commands
async def Translatnexe(commands: list[str]):
    
    funcs = []

    # translate the commands to the native language of the system
    for command in commands:
            
        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file" in command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayVid, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(SearchYT, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No result found for {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# async func to automate command execution
async def Automation(commands: list[str]):

    async for result in Translatnexe(commands):
        pass

    return True

    
        