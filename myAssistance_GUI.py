import tkinter as tk
from tkinter import filedialog
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

# Subject Pretext Dictionary (expand and customize as needed)
subject_pretexts = {
    "math": "In mathematics, ",
    "science": "From a scientific perspective, ",
    "history": "Throughout history, ",
    "english": "In the realm of language arts, ",
    "geography": "When exploring the world, ",
    "social studies": "Within the social sciences, "
}

# Function to get user's subject choice
def get_subject(window):
    subject_choice_var = tk.StringVar(window)
    subject_dropdown = tk.OptionMenu(window, subject_choice_var, *subject_pretexts.keys())
    subject_dropdown.pack()
    subject_choice = subject_choice_var.get().lower()
    subject_dropdown.destroy()  # Remove dropdown after selection
    return subject_choice

# Function to get user input (text or voice)
def get_user_input(window, input_method):
    user_input_text = tk.StringVar(window)
    if input_method == "text":
        user_input_entry = tk.Entry(window, textvariable=user_input_text)
        user_input_entry.pack()
        window.wait_for(user_input_entry)  # Wait for user input
        user_input = user_input_text.get()
        user_input_entry.destroy()  # Remove entry after input
    elif input_method == "voice":
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
        try:
            user_input = r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Could not understand audio")
            user_input = None
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            user_input = None
    return user_input

# Function to provide response (text or voice)
def provide_response(text_response, window, output_method):
    output_text = tk.Text(window, height=5, width=50)
    output_text.insert(tk.END, text_response)
    output_text.pack()
    if output_method == "voice":
        engine = pyttsx3.init()
        engine.say(text_response)
        engine.runAndWait()

# Function to handle image upload and preview
def handle_image_upload(window):
    image_path = filedialog.askopenfilename(
        initialdir="/", title="Select image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")]
    )
    if image_path:
        image_label = tk.Label(window, text="Uploaded Image:")
        image_label.pack()
        image = tk.PhotoImage(file=image_path)
        image_preview = tk.Label(window, image=image)
        image_preview.image = image  # Keep a reference to avoid garbage collection
        image_preview.pack()
        return image_path
    else:
        return None

# Function to configure and use Google Generative AI
def get_response(model_input, stream, model):
    response = model.generate_content(model_input, stream=stream)
    response.resolve()
    try:
        response.text
    except Exception as e:
        print(f'{type(e).__name__}: {e}')
    return response.text

def myAssistant(window):
    # Input Method Selection (Radio Buttons)
    input_method_var = tk.StringVar(window)
    input_method_text_radio = tk.Radiobutton(window, text="Text Input", variable=input_method_var, value="text")
    input_method_text_radio.pack()
    input_method_voice_radio = tk.Radiobutton(window, text="Voice Input", variable=input_method_var, value="voice")
    input_method_voice_radio.pack()
    input_method_var.set("text")  # Pre-select text input

    # Output Method Selection (Radio Buttons)
    output_method_var = tk.StringVar(window)
    output_method_text_radio = tk.Radiobutton(window, text="Text Output", variable=output_method_var, value="text")
    output_method_text_radio.pack()
    output_method_voice_radio = tk.Radiobutton(window, text="Voice Output", variable=output_method_var, value="voice")
    output_method_voice_radio.pack()
    output_method_var.set("text")  # Pre-select text output

    # Subject Selection (Dropdown Menu)
    subject = get_subject(window)

    # User Input Field and Button
    user_input_text = tk.StringVar(window)
    user_input_entry = tk.Entry(window, textvariable=user_input_text)
    user_input_entry.pack()
    user_input_button = tk.Button(window, text="Ask", command=lambda: get_assistant_response(window))
    user_input_button.pack()

    # Microphone Button for Voice Input
    microphone_button = tk.Button(window, text="", command=lambda: get_assistant_response(window, input_method="voice"))
    microphone_button.pack()

    # Image Upload Button and Preview Label
    image_path = None
    image_upload_button = tk.Button(window, text="️", command=lambda: handle_image_upload(window))
    image_upload_button.pack()
    image_preview_label = tk.Label(window)
    image_preview_label.pack()

    # Output Text Box
    output_text = tk.Text(window, height=8, width=80)
    output_text.pack()

    def get_assistant_response(window, input_method="text"):
        """
        Processes user input and provides response based on selected methods.
        """
        nonlocal image_path  # Access the non-local image_path variable

        user_input = get_user_input(window, input_method)
        model_input = f"{subject_pretexts[subject]}{user_input}"

        if image_path:
            model_input = [model_input]
            model_input.append(image_path)
            model = genai.GenerativeModel('gemini-pro-vision')  # For text+image query
            stream = True
        else:
            model = genai.GenerativeModel('gemini-pro')  # For text-only query
            stream = False

        response_text = get_response(model_input, stream, model)
        output_text.delete("1.0", tk.END)  # Clear previous output
        output_text.insert(tk.END, response_text)
        provide_response(response_text, window, output_method_var.get())

    window.mainloop()

if __name__ == "__main__":
    window = tk.Tk()
    window.title("My Personal Assistant")
    myAssistant(window)
