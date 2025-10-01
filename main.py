import os
import requests
import hashlib
import time
import random
import telebot

# ==============================
# CONFIGURACIÓN
# ==============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Leer CHAT_ID de dos formas posibles (compatibilidad)
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")

API_URL = "https://api-sg.aliexpress.com/sync"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ==============================
# LOG INICIAL
# ==============================
print("🚀 Bot iniciado")
print("📌 TELEGRAM_TOKEN leído:", "OK" if TELEGRAM_TOKEN else "❌ VACÍO")
print("📌 CHAT_ID leído:", CHAT_ID if CHAT_ID else "❌ VACÍO")
print("📌 APP_KEY leído:", "OK" if APP_KEY else "❌ VACÍO")
print("📌 APP_SECRET leído:", "OK" if APP_SECRET else "❌ VACÍO")

# ==============================
# FUNCIÓN: FIRMAR PETICIÓN
# ==============================
def sign(params, secret):
    sorted_params = sorted(params.items())
    query = "".join([f"{k}{v}" for k, v in sorted_params])
    sign_str = f"{secret}{query}{secret}"
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

# ==============================
# FUNCIÓN: OBTENER PRODUCTOS
# ==============================
def get_products():
    params = {
        "app_key": APP_KEY,
        "method": "aliexpress.affiliate.product.query",
        "timestamp": str(int(time.time() * 1000)),
        "sign_method": "md5",
        "keywords": "earbuds,charger,wireless,smart,robot,air fryer,beauty,massage,portable,projector",
        "target_sale_price_from": "3",
        "target_sale_price_to": "40",
        "fields": "productId,productTitle,appSalePrice,originalPrice,discount,shopTitle,storeId,productUrl,productMainImageUrl,promotionLink"
    }

    # Firmar petición
    params["sign"] = sign(params, APP_SECRET)

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        data = response.json()
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
        return products
    except Exception as e:
        print("❌ Error obteniendo productos:", e)
        return []

# ==============================
# FUNCIÓN: PUBLICAR EN TELEGRAM
# ==============================
def publicar_producto(product):
    if not CHAT_ID:
        print("⚠️ CHAT_ID está vacío. No se puede publicar en Telegram.")
        return

    titulo = product.get("product_title", "Producto AliExpress")
    precio = product.get("target_sale_price", "N/A")
    precio_original = product.get("original_price", "N/A")
    enlace = product.get("promotion_link", product.get("product_url"))
    imagen = product.get("product_main_image_url", "")

    # Calcular descuento manual
    descuento_calc = "N/A"
    try:
        if precio and precio_original and precio_original != "N/A":
            precio_f = float(str(precio).replace("$", "").replace("USD", "").strip())
            precio_o = float(str(precio_original).replace("$", "").replace("USD", "").strip())
            if precio_o > 0:
                descuento_calc = round(((precio_o - precio_f) / precio_o) * 100, 1)
    except Exception as e:
        print("⚠️ Error calculando descuento:", e)

    # Obtener tienda
    tienda = product.get("shop_title")
    if not tienda:
        tienda_id = product.get("store_id") or product.get("storeId")
        if tienda_id:
            tienda = f"https://es.aliexpress.com/store/{tienda_id}"
        else:
            tienda = "AliExpress"

    mensaje = f"""
🔥 ¡OFERTA FLASH!

📌 <b>{titulo}</b>
💰 Precio: <b>{precio} USD</b> (Antes: {precio_original} USD)
🔻 Descuento: {descuento_calc}%
🏬 Tienda: {tienda}

👉 <a href="{enlace}">Comprar ahora</a>
"""

    try:
        bot.send_photo(
            CHAT_ID,
            photo=imagen,
            caption=mensaje,
            parse_mode="HTML"
        )
        print("✅ Publicado:", titulo)
    except Exception as e:
        print("❌ Error publicando en Telegram:", e)

# ==============================
# LOOP PRINCIPAL
# ==============================
def main():
    while True:
        productos = get_products()
        if productos:
            producto = random.choice(productos)  # Elegir producto aleatorio
            publicar_producto(producto)
        else:
            print("⚠️ No se obtuvieron productos válidos")

        # Esperar 1 hora (3600 segundos)
        time.sleep(3600)

if __name__ == "__main__":
    main()
