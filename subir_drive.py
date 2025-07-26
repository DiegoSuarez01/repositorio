import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 📁 Ruta de tus PDFs
carpeta_pdfs = "C:/Users/User/Desktop/media"  # Ajusta si es necesario

# 🔒 Permiso básico para subir archivos
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def autenticar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials1.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def subir_a_drive(service, ruta_pdf):
    nombre_archivo = os.path.basename(ruta_pdf)
    metadata = {'name': nombre_archivo}
    media = MediaFileUpload(ruta_pdf, mimetype='application/pdf')
    archivo = service.files().create(body=metadata, media_body=media, fields='id').execute()

    file_id = archivo.get('id')

    # Compartir enlace público
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    enlace = f"https://drive.google.com/file/d/{file_id}/view"
    return nombre_archivo, enlace

def subir_todos():
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)

    for archivo in os.listdir(carpeta_pdfs):
        if archivo.lower().endswith('.pdf'):
            ruta = os.path.join(carpeta_pdfs, archivo)
            print(f"📤 Subiendo: {archivo}")
            nombre, enlace = subir_a_drive(service, ruta)
            print(f"✅ {nombre} → {enlace}")
            print("-" * 60)

if __name__ == "__main__":
    subir_todos()