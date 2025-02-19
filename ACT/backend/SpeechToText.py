import os
import mtranslate as mt
from dotenv import dotenv_values

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

#load the env variables from .env
env_vars = dotenv_values('.env')

#get the input language from env variables
Input_Langauge = env_vars.get("inputLanguage")

# get the html code for the speech recognition interface
HTMLcode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
    <style>
        body{
            font-family: Arial, sans-serif;
            background-color: black;
            color: white;
        }

        .start{
            background-color: rgb(0, 174, 255);
            position: absolute;
            top: 50%;
            left: 32%;
            color: white;
            font-size: 27px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .stop{
            background-color: rgb(255, 0, 13);
            position: absolute;
            top: 50%;
            left: 55%;
            color: white;
            font-size: 27px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

#replace the input language in the HTML code with given lang from the env variable
HTMLcode = str(HTMLcode).replace("recognition.lang = '';", f"recognition.lang = '{Input_Langauge}';")

# write the HTML code to a file
with open(r"data/voice.html", "w") as f:
    f.write(HTMLcode)

current_dir = os.getcwd()
# generate a file path for the html file
Link = f"{current_dir}/data/voice.html"

# get the chrome options
chrome_options = Options()

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument (f'user-agent={user_agent}')
chrome_options.add_argument("-use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
# Initialize the Chrome WebDriver using the ChromeDriverManager. 
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# defining the path fr temporary files
temp_dir_path = rf"{current_dir}/frontend/files"

def SetAssistantStatus(Status):
    with open(rf"{temp_dir_path}/status.data", "w", encoding="utf-8") as file:
        file.write(Status)

# function to modify query for proper punctuation and formating
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    questions_words = ["how", "why", "where", "where's", "when", "when's", "who", "whom", "whose", "how's", "can you", "what", "which"]

    #check if a query is a question and add question mrk if necessary
    if any(word + "" in new_query for word in questions_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?'
        else:
            new_query += '?'
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()

# function to translate the text into english (using mtranslate)
def universalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# func to recognize the speech by clicking the button
def SpeechRecognition():
    #get the html file in browser
    driver.get('file:///' + Link)

    # start the speech recognition clicking the button
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            #get the recognized text from html
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                #stop recognition by clicking button
                driver.find_element(by=By.ID, value="end").click()

                if Input_Langauge.lower() == "en" or "en" in Input_Langauge.lower():
                    return QueryModifier(Text)
                else:
                    #if the text is not english, give the translated one
                    SetAssistantStatus("translating...")
                    return QueryModifier(universalTranslator(Text))
        except Exception as e:
            pass

if __name__ == "__main__":
    while True:
        # continuosly do speech recognition and get the text
        Text = SpeechRecognition()
        print(Text)
