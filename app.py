# backend/app.py
from flask import Flask, request, jsonify
from PIL import Image
import io
import numpy as np
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import os
import requests

app = Flask(__name__)

def pil_to_cv2(img_pil):
    img = np.array(img_pil)
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def decode_barcodes(pil_image):
    cv_img = pil_to_cv2(pil_image)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    pil_gray = Image.fromarray(gray)

    results = decode(
        pil_gray,
        symbols=[
            ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.QRCODE,
            ZBarSymbol.CODE39, ZBarSymbol.CODE128,
            ZBarSymbol.UPCA, ZBarSymbol.UPCE
        ]
    )

    output = []
    for r in results:
        try:
            data = r.data.decode('utf-8')
        except:
            data = r.data.decode('latin-1', errors='ignore')

        output.append({
            'type': r.type,
            'data': data,
            'rect': {
                'left': r.rect.left,
                'top': r.rect.top,
                'width': r.rect.width,
                'height': r.rect.height
            }
        })
    return output

def fetch_product_details(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        if data.get("status") == 0:
            return None  # product not found

        product = data["product"]

        return {
            "name": product.get("product_name", "Unknown"),
            "brand": product.get("brands", "Unknown"),
            "ingredients": product.get("ingredients_text", "Not available"),
            "nutriments": product.get("nutriments", {}),
            "nutriscore": product.get("nutriscore_grade", "Not available"),
            "image": product.get("image_url", None),
            "categories": product.get("categories", "")
        }
    except Exception as e:
        print("Error fetching product:", e)
        return None

def normalize_barcode(code, barcode_type):
    """
    UPC-A is 12 digits. Convert to EAN-13 by adding leading 0.
    """
    if barcode_type == "UPCA" and len(code) == 12:
        return "0" + code  # Convert UPC-A -> EAN-13
    return code


@app.route('/scan', methods=['POST'])
def scan():

    if 'file' not in request.files:
        return jsonify({'error': "No image uploaded. Use form field name 'file'."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': "Empty file name."}), 400

    try:
        img_bytes = file.read()
        pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    except Exception as e:
        return jsonify({'error': "Invalid image: " + str(e)}), 400

    # Step 1: Decode barcode
    barcodes = decode_barcodes(pil_img)

    # Step 2: Fetch product details
    food_details = None
    if barcodes:
        code = barcodes[0]["data"]
        barcode_type = barcodes[0]["type"]

        # Convert UPC-A → EAN-13
        code = normalize_barcode(code, barcode_type)

        # Query OpenFoodFacts API
        food_details = fetch_product_details(code)

    # IMPORTANT — ALWAYS RETURN THIS
    return jsonify({
        'barcodes': barcodes,
        'food_details': food_details
    })


@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'Barcode scanner backend is running.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
