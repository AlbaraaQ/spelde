import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# إعداد تسجيل الأخطاء والمعلومات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إعداد عنوان API Together
TOGETHER_API_URL = "https://api.together.xyz/playground/image/black-forest-labs/FLUX.1-schnell-Free"  # استبدل 'endpoint' بالمسار الصحيح الذي تريد استخدامه

# نموذج افتراضي
user_selected_model = {}

# وظيفة لبدء البوت وتعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل رسالة لاستخدام API Together.\n"
                                    "للاختيار بين النماذج، استخدم الأمر /choose_model.")

# وظيفة لاختيار النموذج عبر زر Inline
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Example Model 1", callback_data="example_model_1"),
         InlineKeyboardButton("Example Model 2", callback_data="example_model_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر النموذج الذي ترغب باستخدامه:", reply_markup=reply_markup)

# وظيفة لمعالجة اختيار النموذج
async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    selected_model = query.data
    user_selected_model[user_id] = selected_model
    
    await query.answer()
    await query.edit_message_text(text=f"تم اختيار النموذج: {selected_model}")

# وظيفة للتفاعل مع API Together
def call_together_api(prompt):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_TOKEN'  # إذا كان هناك توكن مطلوب
    }
    data = {
        "input": prompt  # قم بتعديل البيانات حسب احتياجات API Together
    }
    response = requests.post(TOGETHER_API_URL, json=data, headers=headers)
    return response.json()  # إعادة الرد من API، يمكنك تعديله حسب الاستجابة

# وظيفة للرد على الرسائل باستخدام API Together
async def respond_to_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text

    # إذا كنت تريد استخدام نموذج معين، يمكن تخصيصه هنا
    response = call_together_api(prompt=user_message)

    # إرسال الرد للمستخدم
    if 'response_key' in response:  # قم بتعديل المفتاح بناءً على الاستجابة الفعلية
        bot_response = response['response_key']
    else:
        bot_response = "عذرًا، لم أتمكن من الحصول على رد."

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
