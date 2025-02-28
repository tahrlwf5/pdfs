import os
import tempfile
import pdfplumber
from deep_translator import GoogleTranslator
from fpdf import FPDF
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "6334414905:AAHd90fVpkItvitF7ARK71s-0lAv1cAkUsg"

def extract_text_from_pdf(input_file):
    """ استخراج النص من ملف PDF """
    text = ""
    try:
        with pdfplumber.open(input_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
    return text if text.strip() else None

def translate_text(text, target_lang="ar"):
    """ ترجمة النص إلى العربية """
    chunk_size = 5000  # تقسيم النصوص الطويلة
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    translated_chunks = []
    try:
        for chunk in chunks:
            translated_text = GoogleTranslator(source="auto", target=target_lang).translate(chunk)
            translated_chunks.append(translated_text)
    except Exception as e:
        print(f"Error while translating: {e}")
        return None
    
    return "\n".join(translated_chunks)

def create_pdf(text, output_path):
    """ إنشاء ملف PDF جديد باستخدام خط يدعم العربية """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # تحميل الخط العربي
    font_path = "arial.ttf"  # تأكد من وجود الخط في نفس مجلد المشروع
    pdf.add_font("Arabic", "", font_path, uni=True)
    pdf.set_font("Arabic", size=12)

    # إضافة النص مع محاذاته لليمين
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, txt=line, align="R")

    pdf.output(output_path)

def handle_pdf(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type != 'application/pdf':
        update.message.reply_text("❌ يرجى إرسال ملف PDF صالح.")
        return

    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        new_file.download(custom_path=tmp.name)
        extracted_text = extract_text_from_pdf(tmp.name)
        
        if not extracted_text:
            update.message.reply_text("⚠️ لم أتمكن من استخراج النص من هذا الملف.")
            os.remove(tmp.name)
            return
        
        translated_text = translate_text(extracted_text, target_lang='ar')
        
        if not translated_text:
            update.message.reply_text("⚠️ حدث خطأ أثناء الترجمة.")
            os.remove(tmp.name)
            return
        
        translated_pdf_path = tmp.name + "_translated.pdf"
        create_pdf(translated_text, translated_pdf_path)

        context.bot.send_document(chat_id=update.effective_chat.id, document=open(translated_pdf_path, 'rb'))
        
        os.remove(tmp.name)
        os.remove(translated_pdf_path)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 مرحباً! أرسل لي ملف PDF وسأقوم بترجمته إلى العربية وتحويله إلى PDF جديد.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.pdf, handle_pdf))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
