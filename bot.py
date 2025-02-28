import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import PyPDF2
from googletrans import Translator
from dotenv import load_dotenv
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import traceback

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TELEGRAM_BOT_TOKEN is None:
    print("Error: TELEGRAM_BOT_TOKEN is not set. Please check your .env file or Docker environment variables.")
    exit(1)

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
translator = Translator()

# تسجيل الخط العربي
pdfmetrics.registerFont(TTFont('ArabicFont', 'Arial.ttf'))  # استبدل 'arial-unicode-ms.ttf' بمسار ملف الخط

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text: {e}")
        traceback.print_exc()
    return text

def translate_text(text):
    try:
        translation = translator.translate(text, src='en', dest='ar')
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        traceback.print_exc()
        return "حدث خطأ في الترجمة."

def create_translated_pdf(original_file_name, translated_text):
    translated_file_name = f"translated_{original_file_name}.pdf"
    c = canvas.Canvas(translated_file_name)
    c.setFont('ArabicFont', 12)
    lines = translated_text.split('\n')
    y = 750
    for line in lines:
        try:
            c.drawString(100, y, line)
            y -= 20
        except Exception as e:
            print(f"Error drawing line: {e}")
            traceback.print_exc()
            y -= 20
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
        if not text.strip():
            context.bot.send_message(chat_id=update.effective_chat.id, text="لم يتم العثور على نص في ملف PDF.")
            return

        translated_text = translate_text(text)
        translated_file_name = create_translated_pdf(update.message.document.file_name, translated_text)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(translated_file_name, 'rb'))
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"حدث خطأ: {e}")
        traceback.print_exc()
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
