import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7398444341:AAFKRYxXFDgE60ZTor95dr1OvMRJq4dB50o'
API_URL = "http://pass-gpt.nowtechai.com/api/v1/pass"

TOPIC_STATE = 1
NUMBER_STATE = 2

async def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.message.from_user.first_name
    context.user_data['state'] = TOPIC_STATE 
    await update.message.reply_text(
        f"Hello {user_first_name}! Please provide the topic you want to ask questions about(@FF_OO_X).\n"
        f"مرحبا {user_first_name}! من فضلك قدم لي الموضوع الذي تريد أن تطرح عليه الأسئلة(@FF_OO_X)."
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    state = context.user_data.get('state')
    
    if state == TOPIC_STATE:
        user_message = update.message.text
        context.user_data['topic'] = user_message
        context.user_data['language'] = 'ar' if any(char in user_message for char in 'اىبپتثجحخدذرزسشصضطظعغفقكلمنهوي') else 'en'
        context.user_data['state'] = NUMBER_STATE

        if context.user_data['language'] == 'en':
            await update.message.reply_text("How many questions would you like to ask about this topic? Please enter a number.")
        else:
            await update.message.reply_text("كم عدد الأسئلة التي تود طرحها عن هذا الموضوع؟ يرجى إدخال رقم.")
    elif state == NUMBER_STATE:
        try:
            num_questions = int(update.message.text)
            context.user_data['num_questions'] = num_questions
            topic = context.user_data.get('topic', '')
            language = context.user_data.get('language', 'en')
            
            if language == 'en':
                content = f"Please provide {num_questions} questions about {topic} with answers in both Arabic and English."
                system_content = "You are a smart bot trained to provide information and answers in both Arabic and English."
            else:
                content = f"من فضلك، قدم لي {num_questions} أسئلة حول {topic} مع الإجابات، باللغة العربية فقط."
                system_content = "أنت بوت ذكي مدرب على تقديم المعلومات والإجابات باللغة العربية."

            payload = json.dumps({
                "contents": [
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            })

            headers = {
                'User-Agent': "Ktor client",
                'Connection': "Keep-Alive",
                'Accept': "application/json",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/json",
                'Key': "2igU1CCr5VhyaQJsl/OyVbQmu28gutzEYzsQ3u4svKlI4C51cb8wXA60L6EyKiEcLLgWqo6FYxYDn0F35yuCBg==",
                'TimeStamps': "1725220917109",
                'Accept-Charset': "UTF-8"
            }

            response = requests.post(API_URL, data=payload, headers=headers)
            
            if response.status_code == 200:
                lines = response.text.splitlines()
                message = ''.join([json.loads(line[5:])['content'] for line in lines if line.startswith('data:')])
                await update.message.reply_text(message)
            else:
                await update.message.reply_text(f"Error: Received status code {response.status_code}")
        
        except ValueError:
            if context.user_data.get('language') == 'en':
                await update.message.reply_text("Please enter a valid number.")
            else:
                await update.message.reply_text("يرجى إدخال رقم صحيح.")
    else:
        await update.message.reply_text("It looks like something went wrong. Please start over by typing /start.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()