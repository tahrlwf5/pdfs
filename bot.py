import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

ILOVEPDF_API_KEY = "project_public_427a705fefe6806d93e71e594366e8f4_BB-az04a88ec77d44e6ba4915582b9b20692a"
BOT_TOKEN = "6016945663:AAFYr1oaLltIgeMtw5Lb5uSabyVWL4R7UcU"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("مرحبًا! أرسل لي ملف PDF لتحويله إلى DOCX أو PPTX")

async def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    
    if document.mime_type != 'application/pdf':
        await update.message.reply_text("الرجاء إرسال ملف PDF فقط")
        return
    
    file = await context.bot.get_file(document.file_id)
    file_path = f"temp_{document.file_id}.pdf"
    await file.download_to_drive(file_path)
    
    context.user_data['file_path'] = file_path
    
    keyboard = [
        [InlineKeyboardButton("PDF إلى DOCX", callback_data='pdf2docx'),
         InlineKeyboardButton("PDF إلى PPTX", callback_data='pdf2pptx')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("اختر نوع التحويل:", reply_markup=reply_markup)

async def handle_conversion(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    conversion_type = query.data
    file_path = context.user_data.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        await query.edit_message_text("حدث خطأ، الرجاء إعادة المحاولة")
        return
    
    try:
        download_url = await convert_file(file_path, conversion_type)
        converted_file = download_file(download_url)
        
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=converted_file,
            filename=f"converted_{conversion_type}.{conversion_type.split('2')[-1]}"
        )
        
    except Exception as e:
        await query.edit_message_text(f"فشل التحويل: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def convert_file(file_path: str, task: str):
    # Create task
    create_task_url = f"https://api.ilovepdf.com/v1/{task}"
    headers = {"Authorization": f"Bearer {ILOVEPDF_API_KEY}"}
    
    response = requests.post(create_task_url, headers=headers)
    response.raise_for_status()
    task_data = response.json()
    
    # Upload file
    upload_url = task_data['server'] + task_data['task']
    files = {'file': open(file_path, 'rb')}
    response = requests.post(upload_url, files=files)
    response.raise_for_status()
    
    # Process file
    process_url = f"https://{task_data['server']}/v1/process"
    response = requests.post(process_url, headers=headers, json={'task': task_data['task']})
    response.raise_for_status()
    
    # Get download link
    download_url = f"https://{task_data['server']}/v1/download/{task_data['task']}"
    return download_url

def download_file(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(handle_conversion))
    
    application.run_polling()

if __name__ == "__main__":
    main()
