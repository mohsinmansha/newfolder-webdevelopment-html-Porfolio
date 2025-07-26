import os
import re
from openai import OpenAI

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

# ✅ Try to load API key from .env first
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("No API key found in .env")
except:
    # ✅ Fallback for mobile
    api_key = "YOUR_OPENAI_API_KEY"  # <-- put your real key here!

client = OpenAI(api_key=api_key)

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are an intelligent, reliable AI assistant. "
            "Your tasks include writing clear and efficient code, answering questions accurately, "
            "providing helpful personal assistance, and creating safe, appropriate images when requested. "
            "If a user asks for any image that is unsafe or not allowed, you must decline the request politely "
            "and suggest a safe, suitable alternative instead. "
            "Always respond in a friendly, respectful, and professional manner."
        )
    }
]


class ChatBot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Chat history display
        self.history = Label(size_hint_y=None, text_size=(400, None))
        self.history.bind(texture_size=self.history.setter('size'))

        # Scroll view
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.scroll.add_widget(self.history)
        self.add_widget(self.scroll)

        # User input field
        self.input = TextInput(size_hint_y=None, height=50, multiline=False)
        self.add_widget(self.input)

        # Send button
        self.button = Button(text='Send', size_hint_y=None, height=50)
        self.button.bind(on_press=self.send_message)
        self.add_widget(self.button)

    def send_message(self, instance):
        user_input = self.input.text.strip()
        if not user_input:
            return

        self.append_message(f"You: {user_input}\n")
        self.input.text = ''

        # Check if it's an image request
        if re.search(r"(generate|genrate|create|make|draw).*?(image|picture|photo|art|drawing)", user_input, re.IGNORECASE):
            prompt = user_input
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size="1024x1024"
                )
                image_url = response.data[0].url
                self.append_message(f"AI (Image URL): {image_url}\n")
            except Exception as e:
                self.append_message("AI: Sorry, I can't generate that image due to policy or an error.\n")
                self.append_message("AI: How about an image of a peaceful landscape, sunset, or cute animals instead?\n")
        else:
            conversation_history.append({"role": "user", "content": user_input})
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation_history
            )
            reply = response.choices[0].message.content
            self.append_message(f"AI: {reply}\n")
            conversation_history.append({"role": "assistant", "content": reply})

    def append_message(self, text):
        self.history.text += text
        self.scroll.scroll_y = 0


class ChatBotApp(App):
    def build(self):
        return ChatBot()


if __name__ == '__main__':
    ChatBotApp().run()
