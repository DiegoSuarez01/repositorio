import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import fitz  # PyMuPDF

print("🔍 Cloudinary cargado desde:", cloudinary.__file__)

# 🔧 Configura Cloudinary con tus credenciales reales
cloudinary.config(
    cloud_name='dacj8yaea',
    api_key='912348664722477',
    api_secret='Kf_f5lBlZoLvu6aZBqGN3tPWFH8',
    secure=True
)

# 📁 Carpeta local donde están tus PDFs
carpeta_pdfs = 'C:\\Users\\User\\Desktop\\media'  # Ajusta esta ruta

# 🔧 Límite de tamaño (10MB)
MAX_TAMANO = 10 * 1024 * 1024  # 10 MB en bytes

def comprimir_pdf(ruta_original, ruta_comprimida):
    try:
        doc = fitz.open(ruta_original)
        doc.save(ruta_comprimida, garbage=4, deflate=True)
        doc.close()
        print(f"✅ Comprimido: {os.path.basename(ruta_comprimida)}")
    except Exception as e:
        print(f"❌ Error al comprimir {ruta_original}: {e}")

def subir_pdf(ruta_pdf):
    try:
        res = cloudinary.uploader.upload(ruta_pdf, resource_type="raw")
        print(f"✅ Subido correctamente: {os.path.basename(ruta_pdf)}")
        print(f"🌐 URL: {res['secure_url']}")
    except Exception as e:
        print(f"❌ Error al subir {ruta_pdf}: {e}")

# 🔄 Subir todos los PDF
for archivo in os.listdir(carpeta_pdfs):
    if archivo.lower().endswith('.pdf'):
        ruta = os.path.join(carpeta_pdfs, archivo)
        tamano = os.path.getsize(ruta)

        print(f"📄 Procesando: {archivo} ({round(tamano / (1024 * 1024), 2)} MB)")

        if tamano > MAX_TAMANO:
            ruta_comprimida = ruta.replace('.pdf', '_comprimido.pdf')
            comprimir_pdf(ruta, ruta_comprimida)

            if os.path.exists(ruta_comprimida):
                subir_pdf(ruta_comprimida)
            else:
                print(f"⚠️ No se generó el archivo comprimido para: {archivo}")
        else:
            subir_pdf(ruta)

        print("-" * 50)
