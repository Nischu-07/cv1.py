# 📦 Advanced Food Barcode Scanner (Streamlit App)

A powerful barcode-scanning application built using **Streamlit**, **OpenCV**, and **Pyzbar**, enhanced with a multi-API food product lookup system to achieve maximum coverage and accuracy.

The app allows users to scan **food product barcodes** using a camera and automatically retrieves:

- 🛒 Product Name  
- 🏷 Brand  
- 🍽 Category  
- 🌍 Country of Origin  
- 🍎 Nutrition per 100g  
- 🧪 Ingredients  
- 🖼 Product Image  

---

## 🚀 Features

### 🔍 1. Smart Barcode Detection
The scanner uses advanced image preprocessing to accurately detect barcodes, even in difficult conditions:

- Grayscale conversion  
- Gaussian blur  
- Adaptive thresholding  
- Otsu thresholding  
- CLAHE enhancement  
- Sharpening filters  

### 🌐 2. Multi-API Food Product Search
To maximize the chances of finding product data, the app queries multiple OpenFoodFacts endpoints:

1. **OpenFoodFacts API v2**  
2. **OpenFoodFacts API v0**  
3. **OpenFoodFacts Search API**  
4. **OpenFoodFacts India Database**  

If any API returns
