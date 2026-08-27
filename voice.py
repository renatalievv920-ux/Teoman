import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import time

# =========================
# ТЕОМАН
# =========================

VOICE = "ru-RU"

engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

recognizer = sr.Recognizer()


def speak(text):
    print("Теоман:", text)
    engine.say(text)
    engine.runAndWait()


def listen():
    with sr.Microphone() as source:
        print("\nСлушаю...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=7
            )

            command = recognizer.recognize_google(
                audio,
                language=VOICE
            ).lower()

            print("Ты:", command)
            return command

        except sr.WaitTimeoutError:
            return ""

        except sr.UnknownValueError:
            print("Не понял, повтори.")
            return ""

        except sr.RequestError:
            speak("Нет подключения к интернету.")
            return ""


# =========================
# КОМАНДЫ
# =========================

def execute_command(command):

    # Приветствие
    if "привет" in command or "здравствуй" in command:
        speak("Привет! Я Теоман. Я готов работать.")
        return True

    # Время
    if "который час" in command or "сколько времени" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak("Сейчас " + now)
        return True

    # Открыть YouTube
    if "открой youtube" in command or "включи youtube" in command:
        speak("Открываю YouTube.")
        webbrowser.open("https://www.youtube.com")
        return True

    # Открыть WhatsApp
    if "открой whatsapp" in command or "открой ватсап" in command:
        speak("Открываю WhatsApp.")
        webbrowser.open("https://web.whatsapp.com")
        return True

    # Позвонить через WhatsApp
    if "позвони" in command or "позвонить" in command:

        if "аниме" in command or "аниме кизы" in command:
            number = "905518266380"

            speak("Открываю WhatsApp для звонка.")

            url = "https://wa.me/" + number
            webbrowser.open(url)

            time.sleep(3)

            speak("WhatsApp открыт. Нажми кнопку звонка.")

            return True

        speak("Скажи имя контакта, которому нужно позвонить.")
        return True

    # Открыть Google
    if "открой google" in command or "открой гугл" in command:
        speak("Открываю Google.")
        webbrowser.open("https://www.google.com")
        return True

    # Скриншот
    if "скриншот" in command:
        speak("Для скриншота нужно установить дополнительный модуль.")
        return True

    # Стоп
    if (
        "стоп" in command
        or "остановись" in command
        or "выключись" in command
        or "пока" in command
    ):
        speak("Теоман остановлен.")
        return False

    # Помощь
    if "помощь" in command or "что ты умеешь" in command:
        speak(
            "Я умею открывать YouTube, WhatsApp и Google, "
            "показывать время и открывать WhatsApp для звонка."
        )
        return True

    speak("Я пока не умею выполнять эту команду.")
    return True


# =========================
# ЗАПУСК
# =========================

speak("Привет! Я Теоман. Я готов работать.")

running = True

while running:
    command = listen()

    if command:
        running = execute_command(command)
