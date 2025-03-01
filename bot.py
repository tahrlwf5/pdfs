import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from pdf2pptx import Converter
import requests

# إعدادات التطبيق
ILOVEPDF_API_KEY = "project_public_427a705fefe6806d93e71e594366e8f4_BB-az04a88ec77d44e6ba4915582b9b20692a"
BOT_TOKEN = "6016945663:AAFYr1oaLltIgeMtw5Lb5uSabyVWL4R7UcU"
TEMPORARY_FOLDER = "temp_files"

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: CallbackContext):
    """معالجة أمر /start"""
    await update.message.reply_text("مرحبًا! أرسل لي ملف PDF لتحويله إلى DOCX أو PPTX")

async def handle_document(update: Update, context: CallbackContext):
    """معالجة الملفات المرسلة"""
    document = update.message.document
    
    if document.mime_type != 'application/pdf':
        await update.message.reply_text("❌ الرجاء إرسال ملف PDF فقط")
        return
    
    # إنشاء مجلد مؤقت إذا لم يكن موجودًا
    os.makedirs(TEMPORARY_FOLDER, exist_ok=True)
    
    # تنزيل الملف
    file = await context.bot.get_file(document.file_id)
    input_path = os.path.join(TEMPORARY_FOLDER, f"input_{document.file_id}.pdf")
    await file.download_to_drive(input_path)
    
    context.user_data['input_path'] = input_path
    
    # إنشاء أزرار الاختيار
    keyboard = [
        [InlineKeyboardButton("PDF إلى DOCX 📄", callback_data='docx'),
         InlineKeyboardButton("PDF إلى PPTX 📊", callback_data='pptx')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🔄 اختر نوع التحويل:", reply_markup=reply_markup)

async def handle_conversion(update: Update, context: CallbackContext):
    """معالجة عملية التحويل"""
    query = update.callback_query
    await query.answer()
    
    conversion_type = query.data
    input_path = context.user_data.get('input_path')
    
    if not input_path or not os.path.exists(input_path):
        await query.edit_message_text("❌ الملف غير موجود، الرجاء إعادة المحاولة")
        return
    
    try:
        output_path = os.path.join(TEMPORARY_FOLDER, f"output_{conversion_type}.{conversion_type}")
        
        if conversion_type == 'docx':
            # استخدام ilovepdf API لتحويل DOCX
            download_url = await convert_via_ilovepdf(input_path, 'pdf2docx')
            converted_file = download_file(download_url)
            with open(output_path, 'wb') as f:
                f.write(converted_file)
        elif conversion_type == 'pptx':
            # استخدام مكتبة pdf2pptx للتحويل المحلي
            cv = Converter(input_path)
            cv.convert(output_path)
            cv.close()
        
        # إرسال الملف المحول
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=output_path,
            filename=f"converted.{conversion_type}"
        )
        await query.edit_message_text("✅ تم التحويل بنجاح!")
        
    except Exception as e:
        logging.error(f"Conversion error: {str(e)}")
        await query.edit_message_text(f"❌ فشل التحويل: {str(e)}")
    finally:
        # تنظيف الملفات المؤقتة
        cleanup_files(input_path, output_path)

async def convert_via_ilovepdf(file_path: str, task: str):
    """استخدام ilovepdf API للتحويل"""
    headers = {"Authorization": f"Bearer {ILOVEPDF_API_KEY}"}
    
    # إنشاء المهمة
    create_task_url = f"https://api.ilovepdf.com/v1/{task}"
    response = requests.post(create_task_url, headers=headers)
    response.raise_for_status()
    task_data = response.json()
    
    # رفع الملف
    upload_url = task_data['server'] + task_data['task']
    with open(file_path, 'rb') as f:
        response = requests.post(upload_url, files={'file': f})
    response.raise_for_status()
    
    # معالجة الملف
    process_url = f"https://{task_data['server']}/v1/process"
    response = requests.post(process_url, headers=headers, json={'task': task_data['task']})
    response.raise_for_status()
    
    # رابط التنزيل
    return f"https://{task_data['server']}/v1/download/{task_data['task']}"

def download_file(url: str):
    """تنزيل الملف من الرابط"""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def cleanup_files(*paths):
    """حذف الملفات المؤقتة"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logging.warning(f"Error deleting file {path}: {str(e)}")

def main():
    """الدالة الرئيسية"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(handle_conversion))
    
    # بدء البوت
    application.run_polling()
    logging.info("Bot is running...")

if __name__ == "__main__":
    main()
