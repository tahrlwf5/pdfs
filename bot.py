import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import PyPDF2
from googletrans import Translator
from dotenv import load_dotenv
import os

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# استبدل 'YOUR_TELEGRAM_BOT_TOKEN' برمز البوت الخاص بك
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# إنشاء كائن البوت
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# دالة لاستخراج النص من ملف PDF
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# دالة لترجمة النص
def translate_text(text):
    translator = Translator()
    translation = translator.translate(text, src='en', dest='ar')
    return translation.text

# معالج لأمر /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="أرسل لي ملف PDF لترجمته.")

# معالج لرسائل الملفات
def handle_document(update, context):
    file = context.bot.get_file(update.message.document.file_id)
    file_path = f'{update.message.document.file_name}'
    file.download(file_path)

    try:
        text = extract_text_from_pdf(file_path)
        translated_text = translate_text(text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"حدث خطأ: {e}")
    finally:
         os.remove(file_path)

# إنشاء الكائن Updater
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# إضافة المعالجات
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

# بدء تشغيل البوت
updater.start_polling()
updater.idle()
