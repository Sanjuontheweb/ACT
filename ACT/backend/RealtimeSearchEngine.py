from googlesearch import search
from groq import Groq
from json import load, dump
from dotenv import dotenv_values
import datetime

env_vars = dotenv_values(".env")

#get the username, assistant name and api ey
Username = env_vars.get("username")
Assistant_Name = env_vars.get("assistant_name")
GroqAPIKey = env_vars.get("groqapikey")

#initialize the groq client
client = Groq(api_key=GroqAPIKey)

# define a system message which instructs the AI
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistant_Name} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a polite and professional way. ***
*** Answer without extra notes and keep the response short and to the point. ***"""

#try to load the chat from a jSON file
try:
    with open(r"data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError as e:
    # if the file doesn't exist, create a new one
    with open(r"data/ChatLog.json", "w") as f:
        dump([], f)

def Google_search(query):
    results = list(search(query, advanced=True, num_results=7))
    answer = f"The result for the '{query}' is: \n[start]\n"

    for i in results:
        answer += f"Title:{i.title}\n Description:{i.description}\n\n"
    
    answer += "[end]"
    return answer

def ModifyAnswer(Answer):
    lines = Answer.split('\n')
    non_empty_line = [line for line in lines if line.strip()]
    modified_ans = '\n'.join(non_empty_line)  # joining the clear lines
    return modified_ans

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "HI"},
    {"role": "assistant", "content": "How will i help you now?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")  # 24-hour format
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data += f"Use this real-time information when required:\n"
    data += f"Day:{day}\n"
    data += f"Date:{date}\n"
    data += f"Month:{month}\n"
    data += f"Year:{year}\n"
    data += f"Time:{hour}hours, {minute} minutes & {second} seconds\n"
    return data

#functio for getting real-time response ans result generation
def RealTimeSearchEngine(prompt):
    global SystemChatBot, messages

    #load the chat log
    with open(r"data/ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role" : "user", "content": f"{prompt}"})

    SystemChatBot.append({"role" : "system", "content": Google_search(prompt)})

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages= SystemChatBot + [{"role" : "system", "content": Information()}] + messages,
        top_p=1, # using nuclear sampling to control diversity
        stream=True,
        max_tokens=2048,
        stop=None,   #letting the model decide when to quit
        temperature=0.7
    )

    #initializing answer 
    Answer = ""

    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    #clean up any unwanted tokens
    Answer = Answer.replace("</s>", "")

    #update the chatbot's response to messgae list
    messages.append({"role": "assistant", "content": Answer})

    #save the updated chat log
    with open(r"data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

    # remove the most recend system message from chatbot conversation
    SystemChatBot.pop()
    return ModifyAnswer(Answer=Answer)

# main point for interaction querying
if __name__ == "__main__":
    while True:
        prompt = input("Prompt me: ")
        print(RealTimeSearchEngine(prompt))