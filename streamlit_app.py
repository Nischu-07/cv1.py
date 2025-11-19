# frontend/streamlit_app.py
import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Barcode Detector (Upload Image)", layout="centered")

st.title("Barcode Detector — Upload an Image")
st.write("Upload an image (photo or scan) and the backend will detect barcodes and show product details.")

# Backend URL
BACKEND_URL = "http://localhost:5000"   # Change to your Render backend URL when deployed
scan_endpoint = BACKEND_URL.rstrip('/') + "/scan"

uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg", "tiff", "bmp"])

data = None  # So food details block won't crash

if uploaded_file is not None:

    # Show preview
    image = Image.open(io.BytesIO(uploaded_file.read())).convert('RGB')
    st.image(image, caption="Uploaded image", use_column_width=True)
    st.write("---")

    st.write("Sending image to backend for scanning...")

    # Prepare file payload
    uploaded_file.seek(0)
    files = {"file": ("uploaded_image.jpg", uploaded_file, "image/jpeg")}

    try:
        resp = requests.post(scan_endpoint, files=files, timeout=20)
        if resp.status_code != 200:
            st.error(f"Backend error: {resp.status_code} — {resp.text}")
        else:
            data = resp.json()
            barcodes = data.get("barcodes", [])

            if not barcodes:
                st.info("No barcodes detected.")

            else:
                st.success(f"Found {len(barcodes)} barcode(s).")

                for i, b in enumerate(barcodes, start=1):
                    st.subheader(f"Barcode {i}")
                    st.write(f"**Type:** {b.get('type')}")
                    st.write(f"**Data:** `{b.get('data')}`")
                    rect = b.get("rect", {})
                    st.write(
                        f"Bounding box: left={rect.get('left')}, top={rect.get('top')}, "
                        f"w={rect.get('width')}, h={rect.get('height')}"
                    )

    except Exception as e:
        st.error(f"Request failed: {e}")


# ----------------------------------------------------
#          FOOD DETAILS SECTION (AFTER SCAN)
# ----------------------------------------------------

if data and "food_details" in data and data["food_details"]:
    fd = data["food_details"]

    st.write("---")
    st.header("🍎 Food Item Detected")

    st.write(f"### **Product:** {fd['name']}")
    st.write(f"**Brand:** {fd['brand']}")
    st.write(f"**Categories:** {fd['categories']}")

    # Nutri-score box
    st.write(f"**Nutri-score:** :green[{fd['nutriscore'].upper()}]")

    # Product image
    if fd["image"]:
        st.image(fd["image"], caption="Product Image", width=300)

    st.subheader("Nutritional Values (per 100g)")
    nutr = fd["nutriments"]

    # Show nutrition in clean bullet format
    for key, val in nutr.items():
        st.write(f"- **{key.replace('_', ' ').title()}:** {val}")

    st.subheader("Ingredients")
    st.write(fd["ingredients"])

elif data:
    st.warning("No food details found for this barcode.")
