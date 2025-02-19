import cohere
from dotenv import dotenv_values
from rich import print

# get the environmet variables
env_vars = dotenv_values(".env")

#get the cohere api key
CohereAPIKey = env_vars.get('CohereApiKey')

#create a cohere client
co = cohere.Client(api_key=CohereAPIKey)

# set predefined func keywords for task recognition
funcs = [
  "exit", "general", "realtime", "open", "close", "play",
  "generate image", "system", "content", "google search",
  "youtube search", "remainder"
]

#initialize messages
messages = []

#preamble
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was Akbar?' respond with 'general who was Akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye act.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# a pre-defined random user-chatbox interactions for context 
Chat_History = [
    {"role": "User", "message" : "how are you doing?"},
    {"role": "Chatbot", "message" : "general how are you doing?"},
    {"role": "User", "message" : "do you like pizza?"},
    {"role": "Chatbot", "message" : "general do you like pizza?"},
    {"role": "User", "message" : "open chrome and search for trending anime, and list the top 5"},
    {"role": "Chatbot", "message" : "open chrome, google search trending anime, google search list the top 5 anime"},
    {"role": "User", "message" : "Tell me about today's weather"},
    {"role": "Chatbot", "message" : "general tell me about todays weather"},
    {"role": "User", "message" : "Set a remainder for appointment with doctor at 6pm tomorrow"},
    {"role": "Chatbot", "message" : "remainder appointment with doctor at 6pm tomorrow"},
    {"role": "User", "message" : "what is today's date?"},
    {"role": "Chatbot", "message" : "general what is today's date?"},
    {"role": "User", "message" : "Brief me about naruto anime"},
    {"role": "Chatbot", "message" : "general brief me about naruto anime"},
    {"role": "User", "message" : "Not bad"},
    {"role": "Chatbot", "message" : "general not bad"},
]
def FirstLayerDMM(prompt: str):
    
    # add the user's query to message list
    messages.append({"role" : "user", "content": f"{prompt}"})

    # creating a streaming chat session
    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=Chat_History,
        prompt_truncation='OFF',
        preamble=preamble,
        connectors=[]
    )

    # an empty string for responses
    response = ""

    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    # remove the nwline chaacters nd split responses into individual tasks
    response = response=response.replace("\n", "")
    response = response.split(",")

    #remove trailing whitespaces
    response = [i.strip() for i in response]

    #initializing a new list for valid tasks
    temp = []

    # filte the tasksbased on recognized keywords
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
                break

    #update response with filtered tasks
    response = temp

    #if "query" is in response, recurse the response for further classification
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        return response

if __name__ == "__main__":

    #continuously prompt the user for inputs
    while True:
        print(FirstLayerDMM(input(">>> ")))
