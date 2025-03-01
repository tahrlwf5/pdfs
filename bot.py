import os
import requests
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# تكوين المفاتيح
ASPOSE_CLIENT_ID = "e01bc130-02d3-4cf4-9f0e-39e9190c17ad"  # App SID
ASPOSE_CLIENT_SECRET = "5ddd7b591d433f3c93e70e18db36d358"  # App Key
TELEGRAM_BOT_TOKEN = "6016945663:AAFYr1oaLltIgeMtw5Lb5uSabyVWL4R7UcU"  # توكن البوت

# دالة للحصول على Token من Aspose مع معالجة الأخطاء
def get_aspose_token():
    try:
        auth_url = "https://api.aspose.cloud/connect/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": ASPOSE_CLIENT_ID,
            "client_secret": ASPOSE_CLIENT_SECRET
        }
        response = requests.post(auth_url, data=auth_data)
        response.raise_for_status()  # يرفع استثناء إذا كان هناك خطأ
        return response.json().get("access_token")
    except Exception as e:
        raise Exception(f"فشل الحصول على Token: {str(e)}")

# دالة لترجمة ملف PDF مع تسجيل الأخطاء
def translate_pdf(file_path, target_language="ar"):
    try:
        token = get_aspose_token()
        translate_url = "https://api.aspose.cloud/v4.0/pdf/translate"  # المسار الجديد
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": open(file_path, "rb")}
        data = {"targetLanguage": target_language}

        response = requests.post(translate_url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise Exception(f"خطأ في الترجمة: {str(e)}")

# دالة لمعالجة أمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! أرسل لي ملف PDF لأقوم بترجمته إلى العربية.")

# دالة لمعالجة ملف PDF المرسل
def handle_pdf(update: Update, context: CallbackContext):
    downloaded_file = None
    try:
        # تنزيل الملف
        file = update.message.document.get_file()
        downloaded_file = file.download()

        # ترجمة الملف
        translated_pdf = translate_pdf(downloaded_file)

        # إرسال الملف المترجم
        update.message.reply_document(
            document=InputFile(translated_pdf, filename="translated.pdf"),
            caption="تمت الترجمة بنجاح! 🎉"
        )

    except Exception as e:
        error_msg = f"❌ حدث خطأ أثناء الترجمة:\n{str(e)}"
        update.message.reply_text(error_msg)

    finally:
        # حذف الملفات المؤقتة
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)

# دالة رئيسية لتشغيل البوت
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_pdf))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
