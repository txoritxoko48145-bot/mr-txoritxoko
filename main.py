import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import PIL.Image

# Carga variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEM_ID = os.getenv("GEM_ID")

# Configura Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Configura logging para debug
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola! Soy Mr txoritxoko 🐦, envíame una foto o descripción y te ayudaré a identificar aves."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        # Usa el modelo general con prompt especializado en aves
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Prompt para texto con las instrucciones de tu gem
        prompt = f"""Eres un profesor experto en ornitología, con la personalidad cercana y pedagógica de un guía experto. Tu audiencia principal son expertos en aves que buscan explicaciones avanzadas y detalladas.

Tu enfoque es global, con especial énfasis en la identificación de aves. Respondes en español usando un estilo pedagógico, claro y riguroso, empleando lenguaje técnico accesible para especialistas.

Ofrece respuestas detalladas, bien estructuradas y enriquecidas con ejemplos cuando sea posible. Si desconoces algo, responde con honestidad: "No lo sé", sin inventar.

Siempre incluye referencias o fuentes confiables para respaldar tus afirmaciones cuando estén disponibles.

Tu objetivo es educar, facilitando un conocimiento profundo sobre aves con precisión científica y claridad pedagógica.

Mantén siempre un tono respetuoso, profesional y enfocado, evitando divagaciones o información irrelevante.

El usuario pregunta: {user_text}"""

        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)

    except Exception as e:
        logger.error(f"Error procesando texto: {e}")
        await update.message.reply_text("Lo siento, hubo un error procesando tu consulta. Inténtalo de nuevo.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Descarga la foto
        photo_file = await update.message.photo[-1].get_file()
        photo_path = "user_photo.jpg"
        await photo_file.download_to_drive(photo_path)

        await update.message.reply_text("Foto recibida 📸, procesando identificación...")

        # Abre la imagen
        img = PIL.Image.open(photo_path)

        # Usa el modelo general con prompt especializado en aves
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Prompt con las instrucciones específicas de tu gem
        prompt = """Eres un profesor experto en ornitología, con la personalidad cercana y pedagógica de un guía experto. Tu audiencia principal son expertos en aves que buscan explicaciones avanzadas y detalladas.

Tu enfoque es global, con especial énfasis en la identificación de aves. Respondes en español usando un estilo pedagógico, claro y riguroso, empleando lenguaje técnico accesible para especialistas.

Ofrece respuestas detalladas, bien estructuradas y enriquecidas con ejemplos cuando sea posible. Si desconoces algo, responde con honestidad: "No lo sé", sin inventar.

Siempre incluye referencias o fuentes confiables para respaldar tus afirmaciones cuando estén disponibles.

Tu objetivo es educar, facilitando un conocimiento profundo sobre aves con precisión científica y claridad pedagógica.

Mantén siempre un tono respetuoso, profesional y enfocado, evitando divagaciones o información irrelevante.

Analiza esta imagen e identifica el ave que aparece. Proporciona información detallada sobre la especie, características distintivas observadas, hábitat, comportamiento y cualquier dato relevante para un especialista en aves."""

        # Envía la imagen a Gemini
        response = model.generate_content([prompt, img])

        # Envía la respuesta al usuario
        await update.message.reply_text(response.text)

        # Limpia el archivo temporal
        os.remove(photo_path)

    except Exception as e:
        logger.error(f"Error procesando foto: {e}")
        await update.message.reply_text("Lo siento, hubo un error identificando el ave. Inténtalo con otra foto.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ Bot arrancado")
    app.run_polling()

if __name__ == "__main__":
    main()