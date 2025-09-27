import os
import requests
import hashlib
import time
import random
import telebot
from telebot import types

# ==============================
# CONFIGURACIÓN
# ==============================
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
CHAT_ID = int(os.getenv("CHAT_ID", "-1002728128355"))  # tu canal
bot = telebot.TeleBot(TOKEN)

API_URL = "https://api-sg.aliexpress.com/sync"

# ==============================
# FUNCIÓN: generar firma
# ==============================
def sign(params, secret):
    sorted_params = sorted(params.items())
    query = "".join([f"{k}{v}" for k, v in sorted_params])
    sign_str = f"{secret}{query}{secret}"
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

# ==============================
# FUNCIÓN: obtener productos
# ==============================
def obtener_productos():
    params = {
        "app_key": APP_KEY,
        "method": "aliexpress.affiliate.product.query",
        "timestamp": str(int(time.time() * 1000)),
        "sign_method": "md5",
        "keywords": "smartphone",   # palabra clave (puedes cambiarla)
        "fields": "productId,productTitle,appSalePrice,productUrl,promotionLink,discount,shopName",
        "page_size": 5
    }
    params["sign"] = sign(params, APP_SECRET)

    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

        productos = (
            data.get("aliexpress_affiliate_product_query_response", {})
                .get("resp_result", {})
                .get("result", {})
                .get("products", {})
                .get("product", [])
        )
        return productos
    except Exception as e:
        print("❌ Error en la API:", e)
        return []

# ==============================
# FUNCIÓN: publicar en canal
# ==============================
def publicar_oferta():
    productos = obtener_productos()
    if productos:
        item = random.choice(productos)
        titulo = item.get("product_title", "Producto sin título")
        precio = item.get("app_sale_price", "??")
        descuento = item.get("discount", "N/A")
        tienda = item.get("shop_name", "AliExpress")
        enlace = item.get("promotion_link", "")

        # Mensaje con formato atractivo
        mensaje = (
            f"🔥 <b>{titulo}</b>\n"
            f"💰 Precio: <b>{precio} USD</b>\n"
            f"🏷️ Descuento: {descuento}\n"
            f"📦 Tienda: {tienda}"
        )

        # Crear botón "Comprar ahora"
        markup = types.InlineKeyboardMarkup()
        boton = types.InlineKeyboardButton("🛒 Comprar ahora", url=enlace)
        markup.add(boton)

        bot.send_message(
            CHAT_ID,
            text=mensaje,
            parse_mode="HTML",
            reply_markup=markup,
            disable_web_page_preview=False
        )
    else:
        bot.send_message(CHAT_ID, text="⚠️ No se encontraron productos esta vez.")

print("🤖 Bot automático en marcha (modo cada hora)...")

# ==============================
# Bucle automático (cada hora)
# ==============================
while True:
    publicar_oferta()
    time.sleep(3600)  # cada hora
