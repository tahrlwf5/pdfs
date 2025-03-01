import os
import requests
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# تكوين المفاتيح
ASPOSE_CLIENT_ID = "e01bc130-02d3-4cf4-9f0e-39e9190c17ad"  # App SID
ASPOSE_CLIENT_SECRET = "e952086756d6bd8d5f8a525464ae676e"  # App Key
TELEGRAM_BOT_TOKEN = "6016945663:AAFYr1oaLltIgeMtw5Lb5uSabyVWL4R7UcU"  # توكن البوت

# دالة للحصول على Token من Aspose
def get_aspose_token():
    auth_url = "https://api.aspose.cloud/connect/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": ASPOSE_CLIENT_ID,
        "client_secret": ASPOSE_CLIENT_SECRET
    }
    response = requests.post(auth_url, data=auth_data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to get Aspose token: " + response.text)

# دالة لترجمة ملف PDF باستخدام Aspose API
def translate_pdf(file_path, target_language="ar"):
    token = get_aspose_token()
    translate_url = "https://api.aspose.ai/v1.0/pdf/translate"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open(file_path, "rb")}
    data = {"targetLanguage": target_language}

    response = requests.post(translate_url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception("Failed to translate PDF: " + response.text)

# دالة لمعالجة أمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! أرسل لي ملف PDF لأقوم بترجمته إلى اللغة العربية.")

# دالة لمعالجة ملف PDF المرسل
def handle_pdf(update: Update, context: CallbackContext):
    try:
        # تنزيل الملف من التليجرام
        file = update.message.document.get_file()
        downloaded_file = file.download()

        # ترجمة الملف
        translated_pdf = translate_pdf(downloaded_file)

        # إرسال الملف المترجم إلى المستخدم
        update.message.reply_document(document=InputFile(translated_pdf, filename="translated.pdf"))
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {str(e)}")
    finally:
        # حذف الملفات المؤقتة
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

# دالة رئيسية لتشغيل البوت
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    # إضافة handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_pdf))

    # بدء البوت
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
