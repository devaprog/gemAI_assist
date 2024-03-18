import pathlib
import textwrap
import speech_recognition as sr
import pyttsx3

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

from google.colab import files

# Define functions for handling speech and text input/output
def get_user_input(input_method):
    if input_method == "text":
        return input("What's your query?: ")
    elif input_method == "voice":
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            return None

def provide_response(text_response, output_method):
    if output_method == "text":
        display(to_markdown(text_response))
    elif output_method == "voice":
        engine = pyttsx3.init()
        engine.say(text_response)
        engine.runAndWait()

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
GOOGLE_API_KEY = "AIzaSyCrUCzO2suUkeiwLR3NYXG85Erw1X4Zh00"

genai.configure(api_key=GOOGLE_API_KEY)

def get_supported_models(genai):
    return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

print(get_supported_models(genai))

def get_response(model_input, stream, model):
    print((model_input, stream),"len:",len(model_input))
    response = model.generate_content(model_input, stream=stream)
    response.resolve()
    try:
      response.text
    except Exception as e:
      print(f'{type(e).__name__}: {e}')
    return response.text

def myAssistant():
    # Get user input preferences
    input_method = input("Choose input method (voice or text): ").lower()
    output_method = input("Choose output method (voice or text): ").lower()

    model = genai.GenerativeModel('gemini-pro')        # gemini-pro-vision for text query
    stream = False

    model_input = get_user_input(input_method)
    if input("Do you wish to incorporate an image? [Y/N]: ").lower() == 'y':
        model_input = [model_input]
        model_input.append(files.upload())
        model = genai.GenerativeModel('gemini-pro-vision')        # gemini-pro-vision for text+img query
        stream = True
    if input("Do you wish to fix max_limit for output? [Y/N]: ").lower() == 'y':
        if type(model_input) != "list":
          model_input = [model_input]
        model_input.append(genai.types.GenerationConfig(max_output_tokens=input("fix max_limit: ")))
        stream = True
    provide_response(get_response(model_input, stream, model), output_method)

myAssistant()
