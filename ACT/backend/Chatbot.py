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

#initialize an empty message list
messages = []

# define a system message which instructs the AI about its roles and behaviours

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistant_Name} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, French, Spanish or any other language reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

#defining the system structure
SystemChatBot = [
  {"role": "system", "content": System}
]

#try to load the chat from a jSON file
try:
    with open(r"data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError as e:
    # if the file doesn't exist, create a new one
    with open(r"data/ChatLog.json", "w") as f:
        dump([], f)


# func to get real time data and time info
def RealTimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")  # 24-hour format
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this data for realtime date and time, \n"
    data += f"Date:{date}\n Day: {day}\n Month:{month}\n Year:{year}\n"
    data += f"Hour:{hour}\n Minute:{minute}\n second:{second}\n"

    return data

#Function to modify the answer
def ModifyAnswer(Answer):
    lines = Answer.split('\n') # split into lines
    non_empty_lines = [line for line in lines if line.strip()] # remove empty lines
    modified_lines = "\n".join(non_empty_lines) # join the clean lines
    return modified_lines

def ChatBot(query):
    """This func gives the query and returns an AI response"""

    try:
        with open(r"data/ChatLog.json", "r") as f:
            messages = load(f)
    
        # append the user's query to messages list
        messages.append({"role": "user", "content": f"{query}"})

        #get the api resonse
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role" : "system", "content": RealTimeInformation()}] + messages,
            top_p=1, # using nuclear sampling to control diversity
            stream=True,
            max_tokens=1024,
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

        with open(r"data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return ModifyAnswer(Answer=Answer)
    
    except Exception as e:
        print(f"Error {e}")
        # reset the chatlog
        with open(r"data/ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(query)
        
if __name__ == "__main__":
    while True:
        user_input = input("Prompt me: " )
        print(ChatBot(user_input))

    