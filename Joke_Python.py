import customtkinter as ctk
from PIL import Image
import pyjokes
from translate import Translator
from tkinter.messagebox import showerror
import requests
import os
import tempfile
import asyncio
from gtts import gTTS
import playsound
import edge_tts
import sys

# تنظیم حالت و تم برنامه
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# دیکشنری زبان‌ها
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

# نگاشت زبان‌ها به کدهای edge-tts
EDGE_TTS_VOICES = {
    'fa': 'fa-IR-DilaraNeural',
    'en': 'en-US-JennyNeural',
    'es': 'es-ES-ElviraNeural',
    'fr': 'fr-FR-DeniseNeural',
    'de': 'de-DE-KatjaNeural',
    'ja': 'ja-JP-NanamiNeural',
    'zh': 'zh-CN-XiaoxiaoNeural',
    'ru': 'ru-RU-SvetlanaNeural',
    'ar': 'ar-SA-ZariyahNeural'
}


def check_internet():
    try:
        requests.get('https://www.google.com', timeout=3)
        return True
    except:
        return False


async def edge_tts_speak(text, voice):
    try:
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            temp_file = fp.name
            await communicate.save(temp_file)
            playsound.playsound(temp_file)
            os.unlink(temp_file)
    except Exception as e:
        print(f"Error with edge-tts: {e}")
        raise


def gtts_speak(text, lang):
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            tts = gTTS(text=text, lang=lang)
            tts.save(fp.name)
            fp.close()
            playsound.playsound(fp.name)
            os.unlink(fp.name)
    except Exception as e:
        print(f"Error with gTTS: {e}")
        raise


def speak_joke(text, lang_data):
    lang_code = lang_data[0]

    # ابتدا با edge-tts امتحان می‌کنیم (آفلاین در ویندوز)
    if sys.platform == 'win32' and lang_code in EDGE_TTS_VOICES:
        try:
            voice = EDGE_TTS_VOICES[lang_code]
            asyncio.run(edge_tts_speak(text, voice))
            return
        except:
            print("Falling back to gTTS")

    # اگر edge-tts کار نکرد یا در سیستم غیرویندوزی هستیم، از gTTS استفاده می‌کنیم
    if check_internet():
        try:
            gtts_speak(text, lang_code)
            return
        except:
            pass

    # اگر همه روش‌ها شکست خوردند
    showerror('خطا', 'امکان پخش صدا وجود ندارد. لطفاً اتصال اینترنت را بررسی کنید.')


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

        global last_joke, last_lang_data
        last_joke = display_text
        last_lang_data = lang_data
    except Exception as e:
        showerror('خطا', f'مشکل در دریافت جوک:\n{str(e)}')


def play_joke():
    if 'last_joke' in globals() and 'last_lang_data' in globals():
        speak_joke(last_joke, last_lang_data)
    else:
        showerror('خطا', 'ابتدا یک جوک دریافت کنید!')


# ایجاد پنجره اصلی
root = ctk.CTk()
root.title('جوک های خنده دار')
root.geometry('800x500')
root.resizable(False, False)

# پس‌زمینه
try:
    bg_image = ctk.CTkImage(light_image=Image.open("joke2.jpg"), size=(800, 500))
    bg_label = ctk.CTkLabel(root, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    bg_label = ctk.CTkLabel(root, text="", fg_color="#2e2e2e")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ویجت‌های برنامه
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
