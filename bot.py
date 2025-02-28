import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import tempfile
import PyPDF2
from googletrans import Translator

# إعداد سجل الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# ضع توكن بوت تليجرام الخاص بك هنا
TOKEN = "6334414905:AAHd90fVpkItvitF7ARK71s-0lAv1cAkUsg"

# تهيئة المترجم
translator = Translator()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً! أرسل لي ملف PDF وسأقوم بترجمته.")

def translate_pdf(file_path, target_lang='en'):
    """
    دالة تقوم باستخراج النص من ملف PDF وترجمته للغة الهدف.
    """
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    # ترجمة النص
    translated = translator.translate(text, dest=target_lang)
    return translated.text

def handle_pdf(update: Update, context: CallbackContext):
    file = update.message.document
    # التأكد من أن الملف هو PDF
    if file.mime_type != 'application/pdf':
        update.message.reply_text("يرجى إرسال ملف PDF صالح.")
        return

    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    
    # استخدام ملف مؤقت للتخزين
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        new_file.download(custom_path=tmp.name)
        try:
            # تغيير target_lang إلى اللغة المطلوبة (مثلاً "ar" للعربية أو "en" للإنجليزية)
            translated_text = translate_pdf(tmp.name, target_lang='en')
            # إذا كان النص طويل جداً نقوم بتقسيمه على رسائل متعددة
            if len(translated_text) > 4096:
                for i in range(0, len(translated_text), 4096):
                    update.message.reply_text(translated_text[i:i+4096])
            else:
                update.message.reply_text(translated_text)
        except Exception as e:
            update.message.reply_text("حدث خطأ أثناء ترجمة الملف.")
            logging.error(e)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.pdf, handle_pdf))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
