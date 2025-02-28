import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PyPDF2 import PdfReader
from googletrans import Translator
from reportlab.pdfgen import canvas
from io import BytesIO

# تهيئة المترجم
translator = Translator()

# تمكين اللوغاريثمات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('مرحبا! أرسل لي ملف PDF باللغة الإنجليزية وسأقوم بترجمته إلى العربية.')

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def translate_text(text, src='en', dest='ar'):
    translated = translator.translate(text, src=src, dest=dest)
    return translated.text

def create_translated_pdf(translated_text, output_filename):
    packet = BytesIO()
    can = canvas.Canvas(packet)
    
    # إعداد النص العربي (تتطلب تثبيت خطوط عربية)
    can.setFont('Helvetica', 12)
    
    # تقسيم النص إلى أسطر
    lines = translated_text.split('\n')
    
    y = 800  # بداية الكتابة من أعلى الصفحة
    for line in lines:
        can.drawString(72, y, line)
        y -= 15  # التباعد بين الأسطر
        if y < 50:  # إنشاء صفحة جديدة عند الوصول لأسفل الصفحة
            can.showPage()
            y = 800
    
    can.save()
    packet.seek(0)
    return packet

def handle_document(update: Update, context: CallbackContext):
    try:
        # تحميل الملف
        file = update.message.document.get_file()
        pdf_file = BytesIO(file.download_as_bytearray())
        
        # استخراج النص
        original_text = extract_text_from_pdf(pdf_file)
        
        # الترجمة
        translated_text = translate_text(original_text)
        
        # إنشاء PDF مترجم
        output_pdf = create_translated_pdf(translated_text, "translated.pdf")
        
        # إرسال الملف المترجم
        update.message.reply_document(
            document=output_pdf,
            filename="translated_ar.pdf",
            caption="ها هو ملفك المترجم إلى العربية"
        )
        
    except Exception as e:
        logger.error(e)
        update.message.reply_text('حدث خطأ أثناء معالجة الملف. يرجى التأكد من أن الملف صحيح.')

def main():
    # استبدل 'YOUR_TELEGRAM_BOT_TOKEN' بالتوكن الخاص بك
    updater = Updater(token='YOUR_TELEGRAM_BOT_TOKEN', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(MessageHandler(Filters.document, handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
