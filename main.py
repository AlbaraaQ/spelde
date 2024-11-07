import logging
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from g4f.client import Client

# إعداد تسجيل الأخطاء والمعلومات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تهيئة عميل g4f
client = Client()

# قائمة النماذج المتاحة
MODELS = {
    "GPT-3.5": "gpt-3.5-turbo",
    "GPT-4": "gpt-4",
    "GPT-Neo": "EleutherAI/gpt-neo-2.7B",
    "BLOOM": "bigscience/bloom",
    "Flan-T5-XL": "google/flan-t5-xl",
    "LLaMA-2": "meta-llama/LLaMA-2-7b",
    "Flux": "flux-model"  # إضافة نموذج Flux
}

# نموذج افتراضي
user_selected_model = {}

# وظيفة لبدء البوت وتعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل رسالتك لبدء المحادثة.\n"
                                    "للاختيار بين النماذج، استخدم الأمر /choose_model.")

# وظيفة لاختيار النموذج عبر زر Inline
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=name) for name in MODELS]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر النموذج الذي ترغب باستخدامه:", reply_markup=reply_markup)

# وظيفة لمعالجة اختيار النموذج
async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    selected_model = query.data
    user_selected_model[user_id] = MODELS[selected_model]
    
    await query.answer()
    await query.edit_message_text(text=f"تم اختيار النموذج: {selected_model}")

# وظيفة للرد على الرسائل من خلال النموذج المحدد
async def respond_to_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text

    # اختيار النموذج الحالي للمستخدم، أو النموذج الافتراضي
    model = user_selected_model.get(user_id, MODELS["GPT-3.5"])

    # إعداد الرسالة لإرسالها إلى g4f
    messages = [{"role": "user", "content": user_message}]
    
    # الحصول على رد النموذج
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=100  # حدد الحد الأقصى لعدد الكلمات في الرد
    )
    bot_response = response.choices[0].message.content

    # إرسال الرد إلى المستخدم
    await update.message.reply_text(bot_response)

# إعداد البوت ومعالجات الرسائل
def main():
    # استبدل 'YOUR_TELEGRAM_BOT_TOKEN' بالتوكن الخاص بالبوت
    app = ApplicationBuilder().token('7899242313:AAFFGciUkN7td9D4ixS0OQu_biI9CBKR7FQ').build()

    # الأوامر ومعالجات الرسائل
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("choose_model", choose_model))
    app.add_handler(CallbackQueryHandler(set_model))  # معالجة اختيار النموذج من الأزرار
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_message))

    # تشغيل البوت
    app.run_polling()

if __name__ == "__main__":
    main()
