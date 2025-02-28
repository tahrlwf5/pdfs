import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import PyPDF2
from googletrans import Translator
from dotenv import load_dotenv
import os
from reportlab.pdfgen import canvas

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TELEGRAM_BOT_TOKEN is None:
    print("Error: TELEGRAM_BOT_TOKEN is not set. Please check your .env file or Docker environment variables.")
    exit(1)

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def translate_text(text):
    translator = Translator()
    translation = translator.translate(text, src='en', dest='ar')
    return translation.text

def create_translated_pdf(original_file_name, translated_text):
    translated_file_name = f"translated_{original_file_name}"
    c = canvas.Canvas(translated_file_name)
    c.drawString(100, 750, translated_text)  # يمكنك تعديل الموضع والتنسيق هنا
    c.save()
    return translated_file_name

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="أرسل لي ملف PDF لترجمته.")

def handle_document(update, context):
    file = context.bot.get_file(update.message.document.file_id)
    file_path = f'{update.message.document.file_name}'
    file.download(file_path)

    try:
        text = extract_text_from_pdf(file_path)
        translated_text = translate_text(text)
        translated_file_name = create_translated_pdf(update.message.document.file_name, translated_text)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(translated_file_name, 'rb'))
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"حدث خطأ: {e}")
    finally:
        os.remove(file_path)
        if 'translated_file_name' in locals() and os.path.exists(translated_file_name):
            os.remove(translated_file_name)

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

updater.start_polling()
updater.idle()
