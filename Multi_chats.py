chats = {"Chat_title": "chat_no"}
history = []
model = genai.GenerativeModel('gemini-pro-vision')
chat_no = 0
name = "User" #Change your name here!

def CreateNewChat():
    chat_title = str(input("Enter the chat Title to start conversation: "))
    chats[chat_title] = chat_no
    history[chat_no] = []
    chat_no += 1
    return chat_title

def main():
    selectChat = input("Enter chat title to dive in {chats} or \n Enter [new]: ")
    if selectChat.lower() == "new":    
        chat = model.start_chat(history[chats[CreateNewChat()]])
        chat.send_message(f"Hi, Iam {name}")
    else:
        chat = model.start_chat(history[chats[selectChat]])
    myAssistant()

def ShowChat():
    for message in chat.history:
        display(Markdown(f'**{message.role}**: {message.parts[0].text}'))
