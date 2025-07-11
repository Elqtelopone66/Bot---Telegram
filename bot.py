from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import random
import os
import json
import requests

# Reemplaza esto con tu token
TOKEN = "7538579833:AAFdFvPAioEZh6eXnoEskB9ntRLTSHVWMww"
# Key del clima
WEATHER_API_KEY = "1a1e41a7ef0787e2f4e46f443be470c6"

chistes = [
    "¿Por qué el programador confundió Halloween con Navidad? Porque OCT 31 == DEC 25.",
    "¿Qué le dice un bit al otro? Nos vemos en el bus.",
    "¡Error 404: chiste no encontrado!"
]

# Archivo donde se guardan las tareas
TAREAS_FILE = 'tareas.json'

# ------------------------
# Funciones de almacenamiento
# ------------------------

def cargar_tareas():
    if os.path.exists(TAREAS_FILE):
        if os.path.getsize(TAREAS_FILE) == 0:
            return []  # Archivo vacío = lista vacía
        with open(TAREAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def guardar_tareas(tareas):
    with open(TAREAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tareas, f, indent=2, ensure_ascii=False)

# ------------------------
# Handlers de comandos
# ------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy Noise, Un Bot de Telegram.\nUsa /help para ver los comandos disponibles."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Comandos - Basicos\n'
        ' \n'
        '/start - Iniciar el bot\n'
        '/help - Ver esta ayuda\n'
        '/chiste - Recibir un chiste\n'
        '/info - Informacion sobre el bot\n'
        '/clima - Informacion del clima (Ej: /clima Santiago)\n'
        '/traducir - Traducir texto a otro idioma (ej: /traducir en Hola)\n'
        ' \n'
        'Comandos - Tareas\n'
        '/add - Agregar tarea (ej: /add Comprar pan)\n'
        '/list - Listar tareas\n'
        '/delete - Eliminar tarea (ej: /delete 1)\n'
        '/edit - Editar tarea (ej: /edit 1 Ir al supermercado)\n'
        '/done - Marcar tarea completada (ej: /done 1)\n'
        '/undone - Marcar tarea pendiente (ej: /undone 1)\n'
        '/clear - Eliminar todas las tareas'
    )

async def chiste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(chistes))

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Bot creado por Eduardo Barrera, Proyecto dedicado para mejorar capacidades y practicar programacion.'
    )

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Debes escribir la tarea. Ejemplo: /add Lavar ropa")
        return

    tareas = cargar_tareas()
    tarea_texto = " ".join(context.args)
    tareas.append({'texto': tarea_texto, 'completada': False})
    guardar_tareas(tareas)
    await update.message.reply_text(f"Tarea agregada: {tarea_texto}")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tareas = cargar_tareas()
    if not tareas:
        await update.message.reply_text('No tienes tareas.')
        return
    
    mensaje = 'Tus tareas:\n'
    for i, tarea in enumerate(tareas, start=1):
        estado = "✅" if tarea.get("completada", False) else "❌"
        mensaje += f"{i}. {estado} {tarea['texto']}\n"
    await update.message.reply_text(mensaje)

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text('Debes indicar el numero de tarea. Ejemplo: /delete 1')
        return
    
    index = int(context.args[0]) - 1
    tareas = cargar_tareas()
    if 0 <= index < len(tareas):
        tarea = tareas.pop(index)
        guardar_tareas(tareas)
        await update.message.reply_text(f'Tarea eliminada: {tarea["texto"]}')
    else:
        await update.message.reply_text('Numero de tarea invalido.')

async def edit_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text('Uso correcto: /edit <numero_tarea> <nueva_descripcion>')
        return
    index = int(context.args[0]) - 1
    nuevas_palabras = context.args[1:]
    tareas = cargar_tareas()

    if 0 <= index < len(tareas):
        tarea_antigua = tareas[index]['texto']
        tareas[index]['texto'] = ' '.join(nuevas_palabras)
        guardar_tareas(tareas)
        await update.message.reply_text(f'Tarea editada:\nAntes: {tarea_antigua}\nAhora: {tareas[index]["texto"]}')
    else:
        await update.message.reply_text('Numero de tarea invalido')

async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text('Debes indicar el número de tarea. Ejemplo: /done 1')
        return

    index = int(context.args[0]) - 1
    tareas = cargar_tareas()
    if 0 <= index < len(tareas):
        tareas[index]["completada"] = True
        guardar_tareas(tareas)
        await update.message.reply_text(f'Tarea marcada como completada: {tareas[index]["texto"]}')
    else:
        await update.message.reply_text('Número de tarea inválido.')

async def undone_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text('Debes indicar el número de tarea. Ejemplo: /undone 1')
        return

    index = int(context.args[0]) - 1
    tareas = cargar_tareas()
    if 0 <= index < len(tareas):
        tareas[index]["completada"] = False
        guardar_tareas(tareas)
        await update.message.reply_text(f'Tarea marcada como pendiente: {tareas[index]["texto"]}')
    else:
        await update.message.reply_text('Número de tarea inválido.')

async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guardar_tareas([])
    await update.message.reply_text("Todas las tareas han sido eliminadas.")

async def responder_mensajes_generales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()

    if any(palabra in mensaje for palabra in ["hola", "buenas", "buenos días", "hi", "hello"]):
        await update.message.reply_text("¡Hola! 😊 ¿Cómo estás?")

    elif any(palabra in mensaje for palabra in ["gracias", "muchas gracias"]):
        await update.message.reply_text("🙌 ¡De nada!")

    elif any(palabra in mensaje for palabra in ["triste", "mal", "deprimido", "depre"]):
        await update.message.reply_text("😢 Ánimo, aquí estoy para ayudarte.")

    elif any(palabra in mensaje for palabra in ["feliz", "contento", "alegre"]):
        await update.message.reply_text("😄 ¡Qué bueno! Me alegra saberlo.")

    elif "me aburro" in mensaje:
        await update.message.reply_text("🥱 ¿Quieres que te cuente un chiste? Usa /chiste 😁")

async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Debes indicar una ciudad. Ejemplo: /clima Santiago")
        return
    
    ciudad = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"

    try:
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            await update.message.reply_text(f"No pude encontrar la ciudad '{ciudad}'. Verifica el nombre.")
            return
        
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        hum = data["main"]["humidity"]
        
        mensaje = (
            f"🌍 *Clima en {ciudad.title()}*\n"
            f"🌡️ Temperatura: {temp} °C\n"
            f"🌤️ Descripción: {desc}\n"
            f"💧 Humedad: {hum}%"
        )
        await update.message.reply_text(mensaje, parse_mode="Markdown")

    except Exception as e:
        print("Error consultando el clima:", e)
        await update.message.reply_text("Ocurrió un error al consultar el clima.")

async def traducir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /traducir <idioma_destino> <texto>")
        return

    idioma_destino = context.args[0]
    texto_a_traducir = " ".join(context.args[1:])

    try:
        response = requests.post(
            "https://libretranslate.de/translate",
            headers={"Content-Type": "application/json"},
            json={
                "q": texto_a_traducir,
                "source": "auto",
                "target": idioma_destino,
                "format": "text"
            }
        )
        result = response.json()
        traduccion = result.get("translatedText")

        if traduccion:
            await update.message.reply_text(f"Traducción ({idioma_destino}):\n{traduccion}")
        else:
            await update.message.reply_text("No se pudo obtener la traducción.")
    except Exception as e:
        await update.message.reply_text(f"Ocurrió un error: {e}")

# ------------------------
# Arranque de la aplicacion
# ------------------------

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chiste", chiste))
    app.add_handler(CommandHandler('info', info))
    app.add_handler(CommandHandler('add', add_task))
    app.add_handler(CommandHandler('list', list_tasks))
    app.add_handler(CommandHandler('delete', delete_task))
    app.add_handler(CommandHandler('edit', edit_task))
    app.add_handler(CommandHandler('done', done_task))
    app.add_handler(CommandHandler('undone', undone_task))
    app.add_handler(CommandHandler('clear', clear_tasks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensajes_generales))
    app.add_handler(CommandHandler("clima", clima))
    app.add_handler(CommandHandler('traducir', traducir))


    print("Bot iniciado. Presiona Ctrl+C para detenerlo.")
    app.run_polling()

