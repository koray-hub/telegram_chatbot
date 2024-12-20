#!/usr/bin/env python
# pylint: disable=unused-argument
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from llm_calls import voicechat_memory, classify_text, extract_text, pdfwithmemory, fewshottext
import os
from subprocess import call
import torch

#Bu kullanılan nesneleri yeniden hatırlatmak için kullanılır
class Storedobject:
    def __init__(self):
        self.obj = None
        self.type= None
    def restartollama(self):
        pwd='ROOT PASSWORD'
        cmd_stop='systemctl stop ollama'
        cmd_start='systemctl start ollama'
        #llm nesnelerini ekran kartından silmek için kullanılır
        call('echo {} | sudo -S {}'.format(pwd, cmd_stop), shell=True)
        call('echo {} | sudo -S {}'.format(pwd, cmd_start), shell=True)


storedobject = Storedobject()
CHOOSING, VOICE, PDFQA, CLASSIFY, EXTRACTION, CANCEL = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    reply_keyboard = [
    ["Voice Chat"],
    ["Pdf Question Answer"],
    ["Extraction"],
    ["Classify","/cancel"],
    ]

    await update.message.reply_text(
        "Merhaba ben Zeki,"
        "Lütfen geliştirilen bir proje türünü seçip işlemlere devam ediniz.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Proje türünü seçiniz?"
        ),
    )

    return CHOOSING


async def router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    text = update.message.text

    if text=="Voice Chat":
        await update.message.reply_text(
        "Lütfen yazılı veya sesli mesajlaşınız.",
        reply_markup=ReplyKeyboardRemove(),
        )
        return VOICE
    elif text=="Pdf Question Answer":
        await update.message.reply_text(
        "Lütfen dosyayı yükledikten sonra metin sorular sorunuz.",
        reply_markup=ReplyKeyboardRemove(),
        )
        return PDFQA
    elif text=="Classify":
        await update.message.reply_text(
        "Sınıflandırmak istediğiniz metni yazıyla giriniz",
        reply_markup=ReplyKeyboardRemove(),
        )
        return CLASSIFY
    elif text=="Extraction":
        await update.message.reply_text(
        "Metinden kelime çıkarımı için yazılı bir metin giriniz.",
        reply_markup=ReplyKeyboardRemove(),
        )
        return EXTRACTION
    return CANCEL


async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    userid = update.message.from_user.id
    if update.message.voice:
        os.chdir("/home/bot/Projects/telegram_chatbot/sound_files")
        dosya = await update.message.voice.get_file()
        await dosya.download_to_drive(dosya.file_unique_id+".ogg")
        os.chdir("/home/bot/Projects")
        if storedobject.obj is not None: #ses tanıma yapılır
            result,story=storedobject.obj.answerquery(message=".",chatid=str(userid),soundfileinput=dosya.file_unique_id+".ogg",soundfileoutput=dosya.file_unique_id+".wav")
            await update.message.reply_text(result)
        else:
            storedobject.obj = voicechat_memory.Voicechat(model="gemma2")
            result,story=storedobject.obj.answerquery(message=".",chatid=str(userid),soundfileinput=dosya.file_unique_id+".ogg",soundfileoutput=dosya.file_unique_id+".wav")
            await update.message.reply_text(result)
    elif storedobject.obj is not None: #sadece mesajla cevap verilir
        question=update.message.text
        result,story=storedobject.obj.answerquery(message=question,chatid=str(userid))
        await update.message.reply_text(result)
    else:
        storedobject.obj = voicechat_memory.Voicechat(model="gemma2")
        question=update.message.text
        result,story=storedobject.obj.answerquery(message=question,chatid=str(userid))
        await update.message.reply_text(result)
    return VOICE


async def pdfqa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.from_user
    user_chat_id = str(user.id)
    if storedobject.obj is not None:
        if storedobject.type in "pdf":
            text = update.message.text
            # ... (your logic for handling text messages)
            result=storedobject.obj.answerqueryfromdocument(language="Turkish",message=update.message.text,chatid=user_chat_id)
            await update.message.reply_text(result['answer'])
        elif storedobject.type in "txt":
            result=storedobject.obj.answerquery(language="Türkçe",message=update.message.text)
            await update.message.reply_text(result)
    elif update.message.document:
        file_name = update.message.document.file_name
        file_extension = file_name.split('.')[-1].lower()

        if file_extension == 'pdf':
            # Handle PDF file
            dosya = await update.message.document.get_file()
            await dosya.download_to_drive(custom_path='/home/bot/Projects/telegram_chatbot/document_files/'+dosya.file_unique_id+".pdf")
            storedobject.obj= pdfwithmemory.Pdfchat(model="gemma2",documentfileinput=dosya.file_unique_id+".pdf")
            storedobject.type ="pdf"
            await update.message.reply_text("PDF dosyası yüklendi!")
            
        elif file_extension == 'txt':
            dosya = await update.message.document.get_file()
            await dosya.download_to_drive(custom_path='/home/bot/Projects/telegram_chatbot/document_files/'+dosya.file_unique_id+".txt")
            storedobject.obj = fewshottext.Fewshottext(model="llama3.1",textfile=dosya.file_unique_id)
            storedobject.type ="txt"
            await update.message.reply_text("TXT dosyası yüklendi!")
            #bu kısım sonradan düzenlenecektir
        else:
            # Handle other file types
            await update.message.reply_text("Desteklenmeyen dosya tipi!")
    else:
        # Handle text message
        await update.message.reply_text("Lütfen önce pdf dosyasını yükleyiniz.")

    return PDFQA


async def classify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if storedobject.obj is not None:
        question=update.message.text
        result=storedobject.obj.answerquery(message=question)
        result_message="sentiment:"+result.sentiment+"\n"+"aggressiveness:"+str(result.aggressiveness)+"\n"+"language:"+result.language
        await update.message.reply_text(result_message)
    else:
        storedobject.obj = classify_text.Classify_text(model="llama3.1")
        question=update.message.text
        result=storedobject.obj.answerquery(message=question)
        result_message="sentiment:"+result.sentiment+"\n"+"aggressiveness:"+str(result.aggressiveness)+"\n"+"language:"+result.language
        await update.message.reply_text(result_message)

    return CLASSIFY


async def extraction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if storedobject.obj is not None:
        question=update.message.text
        result=storedobject.obj.answerquery(message=question)
        result_message="name:"+str(result.name)+"\n"+"hair_color:"+str(result.hair_color)+"\n"+"height_in_meters:"+str(result.height_in_meters)
        await update.message.reply_text(result_message)
    else:
        question=update.message.text
        storedobject.obj = extract_text.Extract_text(model="llama3.1")
        result=storedobject.obj.answerquery(message=question)
        result_message="name:"+str(result.name)+"\n"+"hair_color:"+str(result.hair_color)+"\n"+"height_in_meters:"+str(result.height_in_meters)
        await update.message.reply_text(result_message)
    return EXTRACTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    del storedobject.obj
    torch.cuda.empty_cache()
    storedobject.obj = None
    storedobject.type = None
    storedobject.restartollama()

    await update.message.reply_text(
        "Bye.", reply_markup=ReplyKeyboardRemove()
    )


    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.Telegram token is free.
    application = Application.builder().token("ENTER YOUR TELEGRAM MESSAGING TOKEN TO HERE").build()
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex(r"^(Voice Chat|Message|Pdf Question Answer|Classify|Extraction)$"), router),
                CommandHandler("cancel", cancel),
                #MessageHandler(filters.Regex("^cancel$"), cancel),
            ],
            VOICE: [
                MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, voice)
            ],
            PDFQA: [
                MessageHandler((filters.TEXT | filters.Document.MimeType('application/pdf') | filters.Document.MimeType('text/plain')) & ~filters.COMMAND, pdfqa)
            ],
            CLASSIFY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, classify)
            ],
            EXTRACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, extraction)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
