import os
import tempfile
import PyPDF2
from googletrans import Translator
from fpdf import FPDF
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ضع توكن بوت تليجرام الخاص بك هنا
TOKEN = "6334414905:AAHd90fVpkItvitF7ARK71s-0lAv1cAkUsg"

translator = Translator()

def translate_pdf_to_pdf(input_file, target_lang='ar'):
    # استخراج النص من ملف PDF باستخدام PyPDF2
    with open(input_file, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    # ترجمة النص إلى اللغة المطلوبة (العربية)
    translation = translator.translate(full_text, dest=target_lang)
    translated_text = translation.text
    
    # إنشاء ملف PDF جديد باستخدام FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # تقسيم النص إلى أسطر وإضافتها إلى ملف PDF
    for line in translated_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)
    
    # حفظ ملف PDF الجديد في مسار مؤقت
    output_pdf_path = input_file + "_translated.pdf"
    pdf.output(output_pdf_path)
    return output_pdf_path

def handle_pdf(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type != 'application/pdf':
        update.message.reply_text("يرجى إرسال ملف PDF صالح.")
        return

    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    
    # استخدام ملف مؤقت للتخزين
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        new_file.download(custom_path=tmp.name)
        try:
            # ترجمة الملف وإنشاء PDF جديد بالنص المترجم
            translated_pdf = translate_pdf_to_pdf(tmp.name, target_lang='ar')
            # إرسال ملف PDF الجديد إلى المستخدم
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(translated_pdf, 'rb'))
            os.remove(translated_pdf)
        except Exception as e:
            update.message.reply_text("حدث خطأ أثناء ترجمة الملف.")
            print(e)
        finally:
            os.remove(tmp.name)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً! أرسل لي ملف PDF وسأقوم بترجمته إلى العربية وتحويله إلى ملف PDF.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.pdf, handle_pdf))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
