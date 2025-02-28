import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from PyPDF2 import PdfReader
from googletrans import Translator

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# تهيئة المترجم
translator = Translator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('مرحبا! أرسل لي ملف PDF باللغة الإنجليزية وسأقوم بترجمته إلى العربية.')

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    file = await update.message.document.get_file()

    # تنزيل الملف
    pdf_path = f'temp_{user.id}.pdf'
    await file.download_to_drive(pdf_path)
    
    try:
        # استخراج النص من PDF
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        
        # الترجمة إلى العربية
        translated = translator.translate(text, src='en', dest='ar').text
        
        # إرسال النص المترجم كملف
        output_path = f'translated_{user.id}.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        
        await update.message.reply_document(
            document=output_path,
            caption='ها هو النص المترجم'
        )
        
    except Exception as e:
        await update.message.reply_text(f'حدث خطأ: {str(e)}')
    finally:
        # تنظيف الملفات المؤقتة
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(output_path):
            os.remove(output_path)

def main():
    # الحصول على توكن البوت من البيئة
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("لم يتم تعيين TELEGRAM_BOT_TOKEN في البيئة")
    
    # إنشاء التطبيق
    application = Application.builder().token(token).build()
    
    # تسجيل ال handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    
    # إعدادات النشر على Railway
    port = int(os.environ.get('PORT', 8443))
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if webhook_url:
        # وضع النشر على Railway
        application.run_webhook(
            listen='0.0.0.0',
            port=port,
            webhook_url=webhook_url
        )
    else:
        # وضع التطوير المحلي
        application.run_polling()

if __name__ == '__main__':
    main()
