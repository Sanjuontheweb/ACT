# ACT : A Cool Thing

from frontend.GUI import (
GraphicalUserInterface,
SetAssistantStatus,
SetMicStatus,
TempWorkingDirectory,
ModifyAnswer,
QueryModifier,
ShowTexttOScreen,
GetAssistantStatus,
GetMicStatus
)
from backend.Model import FirstLayerDMM
from backend.RealtimeSearchEngine import RealTimeSearchEngine
from backend.Automation import Automation
from backend.Chatbot import ChatBot
from backend.TextToSpeech import TextToSpeech
from backend.SpeechToText import SpeechRecognition
from time import sleep
from dotenv import dotenv_values
from asyncio import run
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

import subprocess
import threading
import json
import sys
import os

env_vars = dotenv_values('.env')
Username = env_vars.get("username")
Assistant_name = env_vars.get("assistant_name")
default_messages = f"""{Username} : How are ya?
{Assistant_name} : Hello there! I'm doing fine. How may i help you?"""
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

app = QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon("icon.png"))

def showDefChatsifNoChats():
    File = open(r"data/ChatLog.json", "r", encoding='utf-8')
    if len(File.read()) <=5:
        with open(TempWorkingDirectory('database.data'), "w", encoding='utf-8')as file:
            file.write("")

        with open(TempWorkingDirectory('responses.data'), "w", encoding='utf-8')as file:
            file.write(default_messages)

def ReadChatLogdata():
    with open(r"data/ChatLog.json", "r", encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def IntegrateChatLog():
    json_data = ReadChatLogdata()
    formatted_content = ''
    for entry in json_data:
        if entry["role"] == "user":
            formatted_content += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_content += f"Assistant : {entry['content']}\n"
    formatted_content = formatted_content.replace("User", Username + " ")
    formatted_content = formatted_content.replace("Assistant", Assistant_name + " ")

    with open(TempWorkingDirectory('database.data'), "w", encoding='utf-8') as file:
        file.write(ModifyAnswer(formatted_content))

def ShowChatsonGUI():
    File = open(TempWorkingDirectory('database.data'), "r", encoding='utf-8')
    data = File.read()
    if len(str(data)) > 0:
        lines = data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempWorkingDirectory('responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicStatus("False")
    ShowTexttOScreen("")
    showDefChatsifNoChats()
    IntegrateChatLog()
    ShowChatsonGUI()
    SetAssistantStatus("Available..")

InitialExecution()

def MainExecution():
    TasksExecution = "False"
    ImageExecution = "False"
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening..")
    Query = SpeechRecognition()
    ShowTexttOScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking..")
    Decision = FirstLayerDMM(Query)

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:])for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageGenerationQuery = ImageGenerationQuery.replace("generate image ", "")
            ImageExecution = "True"

    for queries in Decision:
        if TasksExecution == "False":
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TasksExecution = True

    if ImageExecution == "True":

        with open(r"frontend/files/ImageGeneration.data", "w")as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            p1 = subprocess.Popen(['python', r"backend/ImageGeneration.py"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE,  shell=False
                            )
            subprocesses.append(p1)

        except Exception as e:
            print(f"Couldn't generate image: {e}")

    if G and R or R:

        SetAssistantStatus("Searching..")
        Answer = RealTimeSearchEngine(QueryModifier(Mearged_query))
        ShowTexttOScreen(f"{Assistant_name} : {Answer}")
        SetAssistantStatus("Answering..")
        TextToSpeech(Answer)
        return True
    
    else:

        for Queries in Decision:
            
            if "general" in Queries:
                SetAssistantStatus("Thinking..")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTexttOScreen(f"{Assistant_name} : {Answer}")
                SetAssistantStatus("Answering..")
                TextToSpeech(Answer)
                return True
            
            elif "realtime" in Queries:
                SetAssistantStatus("Searching..")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealTimeSearchEngine(QueryModifier(QueryFinal))
                ShowTexttOScreen(f"{Assistant_name} : {Answer}")
                SetAssistantStatus("Answering..")
                TextToSpeech(Answer)
                return True
            
            elif "exit" in Queries:
                QueryFinal = "Ok, bye!🙌"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTexttOScreen(f"{Assistant_name} : {Answer}")
                SetAssistantStatus("Answering..")
                TextToSpeech(Answer)
                os._exit(1)
                break

# this is running the backend of the AI
def FirstThread():

    while True:

        currentStatus = GetMicStatus()

        if currentStatus == "True":
            MainExecution()

        else: 
            AIstatus = GetAssistantStatus()

            if "Available.." in AIstatus:
                sleep(0.1)

            else:
                SetAssistantStatus("Available..")

# this is the frontend of the AI
def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()

        
