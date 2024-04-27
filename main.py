import telebot
from PIL import Image
from io import BytesIO
from fpdf import FPDF

TOKEN ='6830212442:AAHHR3kzTumQMCljabNo1iXLqNJ8QgmOwD4'
bot = telebot.TeleBot(TOKEN)

image_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the Image to PDF Converter Bot! Send me some images and I'll combine them into a PDF file.")

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    try:
        chat_id = message.chat.id
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        image = Image.open(BytesIO(downloaded_file))

        if chat_id not in image_data:
            image_data[chat_id] = []

        image_data[chat_id].append(image)

        bot.reply_to(message, "Image added successfully!")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

@bot.message_handler(commands=['convert'])
def convert_to_pdf(message):
    try:
        chat_id = message.chat.id

        if chat_id not in image_data or len(image_data[chat_id]) == 0:
            bot.reply_to(message, "No images found. Send some images first.")
            return

        pdf = FPDF()

        for image in image_data[chat_id]:
            pdf.add_page()
            img_temp = BytesIO()
            image.save(img_temp, format='PNG')
            pdf.image(img_temp, x=0, y=0, w=pdf.w, h=pdf.h)

        pdf_file = f"{chat_id}.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            bot.send_document(chat_id, f)

        # Clear the image data for this chat
        del image_data[chat_id]

        bot.reply_to(message, "PDF file created and sent!")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

bot.polling()