import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from together import Together  # تأكد من تثبيت مكتبة together

# إعداد تسجيل الأخطاء والمعلومات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تهيئة عميل Together
client = Together(api_key="5ba5c96173d4c62eab6e81edc5abc3f32c4a8c2aa732ef6edbdb2135d27ffdeb")

# وظيفة لبدء البوت وتعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل نصًا وسأقوم بتوليد صورة لك باستخدام نموذج FLUX.")

# وظيفة لتوليد الصور باستخدام Together API
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    await update.message.reply_text("جاري إنشاء الصورة... قد يستغرق ذلك بعض الوقت.")

    try:
        # توليد الصورة باستخدام Together API
        response = client.images.generate(
            prompt=user_prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",  # استخدام النموذج المحدد
            width=1024,
            height=768,
            steps=1,
            n=1,
            response_format="b64_json"
        )
        
        # استخراج الصورة من الاستجابة (إذا كانت متوفرة)
        if response.data:
            image_base64 = response.data[0].b64_json
            # تحويل الصورة من base64 إلى صورة يمكن إرسالها
            import base64
            from io import BytesIO
            from PIL import Image

            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            image_path = "/tmp/generated_image.png"
            image.save(image_path)

            # إرسال الصورة إلى المستخدم
            await update.message.reply_photo(photo=open(image_path, 'rb'))
        else:
            await update.message.reply_text("عذرًا، لم أتمكن من توليد صورة. يرجى المحاولة مرة أخرى.")

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء توليد الصورة: {e}")

# إعداد البوت ومعالجات الرسائل
def main():
    # استبدل 'YOUR_TELEGRAM_BOT_TOKEN' بالتوكن الخاص بالبوت
    app = ApplicationBuilder().token('7899242313:AAFFGciUkN7td9D4ixS0OQu_biI9CBKR7FQ').build()

    # الأوامر ومعالجات الرسائل
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

    # تشغيل البوت
    app.run_polling()

if __name__ == "__main__":
    main()
