import os
import requests
import hashlib
import time
import random
import telebot

# ==============================
# CONFIGURACIÓN
# ==============================
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
CHAT_ID = -1002728128355  # ⚡ tu canal Chollazos Globales
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
        "keywords": "smartphone",  # palabra clave de prueba
        "fields":
        "productId,productTitle,appSalePrice,productUrl,promotionLink",
        "page_size": 5
    }
    params["sign"] = sign(params, APP_SECRET)

    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

        productos = (data.get("aliexpress_affiliate_product_query_response",
                              {}).get("resp_result",
                                      {}).get("result",
                                              {}).get("products",
                                                      {}).get("product", []))
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
        enlace = item.get("promotion_link", "")

        # Mensaje con HTML limpio
        mensaje = (f"🔥 <b>{titulo}</b>\n"
                   f"💰 Precio: {precio} USD\n"
                   f"🔗 <a href='{enlace}'>Ver en AliExpress</a>")

        bot.send_message(
            CHAT_ID,
            text=mensaje,
            parse_mode="HTML",
            disable_web_page_preview=
            False  # True = sin miniatura, False = con miniatura
        )
    else:
        bot.send_message(CHAT_ID,
                         text="⚠️ No se encontraron productos esta vez.")


print("🤖 Bot automático en marcha (modo prueba cada 30s)...")

# ==============================
# Bucle automático (cada 30s PRUEBA)
# ==============================
while True:
    publicar_oferta()
    time.sleep(3600)  # cada 30 segundos (para pruebas)