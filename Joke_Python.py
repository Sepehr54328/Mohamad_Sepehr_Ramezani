import customtkinter as ctk
from PIL import Image
import pyjokes
from translate import Translator
from tkinter.messagebox import showerror
import requests
import gtts
import os
import playsound
from io import BytesIO
import pyttsx3

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

LANGUAGES = {
    'فارسی': ('fa', 'جوک بگو', 'فارسی', 'persian'),
    'English': ('en', 'Tell Joke', 'English', 'english'),
    'Español': ('es', 'Contar Chiste', 'Spanish', 'spanish'),
    'Français': ('fr', 'Dire Blague', 'French', 'french'),
    'Deutsch': ('de', 'Witz erzählen', 'German', 'german'),
    '日本語': ('ja', 'ジョークを言う', 'Japanese', 'japanese'),
    '中文': ('zh', '讲笑话', 'Chinese', 'chinese'),
    'Русский': ('ru', 'Рассказать анекдот', 'Russian', 'russian'),
    'العربية': ('ar', 'قل نكتة', 'Arabic', 'arabic')
}

def check_internet():
    try:
        requests.get('https://www.google.com', timeout=3)
        return True
    except:
        return False

def speak_joke(text, lang, voice_type):
    try:
        if lang == 'fa':
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'persian' in voice.id.lower() or 'iran' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
        else:
            tts = gtts.gTTS(text=text, lang=lang)
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            temp_file = "temp_joke.mp3"
            with open(temp_file, "wb") as f:
                f.write(audio_file.read())
            playsound.playsound(temp_file)
            os.remove(temp_file)
    except Exception as e:
        print(f"Error in speech synthesis: {e}")

def update_ui_texts():
    selected_lang = language_var.get()
    joke_button.configure(text=LANGUAGES[selected_lang][1])
    play_button.configure(text=f"🔊 {LANGUAGES[selected_lang][3]}")

def get_joke(event=None):
    if not check_internet():
        showerror('خطا', 'اتصال اینترنت برقرار نیست!')
        return
    try:
        selected_lang = language_var.get()
        lang_data = LANGUAGES[selected_lang]
        lang_code = lang_data[0]
        joke = pyjokes.get_joke()
        if lang_code != 'en':
            translator = Translator(from_lang='en', to_lang=lang_code)
            translated_joke = translator.translate(joke)
            display_text = translated_joke
        else:
            display_text = joke
        text_box.delete('0.0', 'end')
        text_box.insert('0.0', display_text)
        global last_joke, last_lang, last_voice_type
        last_joke = display_text
        last_lang = lang_code
        last_voice_type = lang_data[3]
    except Exception as e:
        showerror('خطا', f'مشکل در دریافت جوک:\n{str(e)}')

def play_joke():
    if 'last_joke' in globals() and 'last_lang' in globals() and 'last_voice_type' in globals():
        speak_joke(last_joke, last_lang, last_voice_type)
    else:
        showerror('خطا', 'ابتدا یک جوک دریافت کنید!')

root = ctk.CTk()
root.title('جوک های خنده دار')
root.geometry('800x500')
root.resizable(False, False)

try:
    bg_image = ctk.CTkImage(light_image=Image.open("joke2.jpg"), size=(800, 500))
    bg_label = ctk.CTkLabel(root, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    bg_label = ctk.CTkLabel(root, text="", fg_color="#2e2e2e")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

text_box = ctk.CTkTextbox(
    root,
    width=400,
    height=150,
    font=("B Kamran", 16),
    fg_color="#4a5847",
    text_color="white",
    wrap="word",
    border_width=2,
    border_color="#6A7F49",
    corner_radius=10
)
text_box.place(x=20, y=20)

play_button = ctk.CTkButton(
    root,
    text="🔊 فارسی",
    command=play_joke,
    font=("B Kamran", 14),
    width=120,
    height=30,
    fg_color="#3a4739",
    hover_color="#2e3a2e",
    corner_radius=10
)
play_button.place(x=20, y=180)

control_frame = ctk.CTkFrame(root, fg_color="transparent")
control_frame.place(relx=0.5, rely=0.9, anchor="center")

language_var = ctk.StringVar(value='فارسی')
language_menu = ctk.CTkOptionMenu(
    control_frame,
    variable=language_var,
    values=list(LANGUAGES.keys()),
    font=("B Kamran", 16),
    dropdown_font=("B Kamran", 14),
    fg_color="#6A7F49",
    button_color="#4b594a",
    button_hover_color="#3a4739",
    width=200,
    height=35,
    command=lambda _: update_ui_texts()
)
language_menu.pack(side="left", padx=20)

joke_button = ctk.CTkButton(
    control_frame,
    text=LANGUAGES['فارسی'][1],
    command=get_joke,
    font=("B Kamran", 18, "bold"),
    width=200,
    height=40,
    fg_color="#6A7F49",
    hover_color="#4b594a",
    border_width=2,
    border_color="#3a4739",
    corner_radius=20
)
joke_button.pack(side="left", padx=20)

text_box.bind("<Button-1>", get_joke)

root.mainloop()
