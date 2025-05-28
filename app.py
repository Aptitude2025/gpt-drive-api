from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import mimetypes
import io
import fitz  # PyMuPDF
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Load credentials from environment
creds_info = json.loads(os.environ['GOOGLE_CREDS'])
creds = service_account.Credentials.from_service_account_info(creds_info)
drive_service = build('drive', 'v3', credentials=creds)

def extract_pdf_text(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

@app.route('/read-file', methods=['GET'])
def read_file():
    file_name = request.args.get('name')
    if not file_name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    results = drive_service.files().list(
        q=f"name='{file_name}' and trashed=false",
        pageSize=1,
        fields="files(id, name, mimeType)"
    ).execute()

    items = results.get('files', [])
    if not items:
        return jsonify({"error": "File not found"}), 404

    file = items[0]
    file_id = file['id']
    mime_type = file['mimeType']

    try:
        # Google Docs
        if mime_type == 'application/vnd.google-apps.document':
            exported = drive_service.files().export(fileId=file_id, mimeType='text/plain').execute()
            return jsonify({"content": exported})

        # PDFs
        elif mime_type == 'application/pdf':
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, drive_service.files().get_media(fileId=file_id))
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            text = extract_pdf_text(fh.read())
            return jsonify({"content": text})

        # Plain text
        elif mime_type in ['text/plain', 'text/csv']:
            content = drive_service.files().get_media(fileId=file_id).execute()
            return jsonify({"content": content.decode('utf-8')})

        else:
            return jsonify({"error": f"Unsupported MIME type: {mime_type}"}), 415

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
