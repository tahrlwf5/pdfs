import io
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import aiohttp

# إعدادات البوت
TOKEN = "6016945663:AAFYr1oaLltIgeMtw5Lb5uSabyVWL4R7UcU"
ALLOWED_EXTENSIONS = {'.pdf'}

# تفعيل التسجيل للأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file_name = document.file_name or ""
    
    if not any(file_name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        await update.message.reply_text("❌ يرجى إرسال ملف بامتداد .pdf")
        return

    await update.message.reply_text("⏳ جاري المعالجة...")
    
    try:
        # تحميل الملف من تليجرام
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()
        
        # إرسال الملف إلى i2pdf.com (أو أي خدمة تدعم التحويل من PDF إلى DOCX/PPTX)
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field('file', file_bytes, filename=file_name)
            
            # هنا نحدد نوع التحويل (مثلاً إلى DOCX)
            async with session.post('https://i2pdf.com/upload', data=form_data) as response:
                if response.status == 200 and response.content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
                    converted_bytes = await response.read()
                    
                    # إرسال الملف المحوّل
                    await update.message.reply_document(
                        document=io.BytesIO(converted_bytes),
                        filename=f"{file_name.split('.')[0]}.docx"  # أو .pptx حسب النوع المطلوب
                    )
                else:
                    await update.message.reply_text("❌ فشل التحويل، يرجى المحاولة لاحقًا")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء المعالجة")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    logging.info("Bot is running...")
    application.run_polling()
