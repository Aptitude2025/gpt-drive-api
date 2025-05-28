from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os, json

app = Flask(__name__)

# Required scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Load credentials from env var
creds_info = json.loads(os.environ['GOOGLE_CREDS'])
creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)

@app.route('/read-file', methods=['GET'])
def read_file():
    file_name = request.args.get('name')
    if not file_name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q=f"name='{file_name}' and trashed=false",
        pageSize=1,
        fields="files(id, name)"
    ).execute()

    items = results.get('files', [])
    if not items:
        return jsonify({"error": "File not found"}), 404

    file_id = items[0]['id']
    try:
        file = service.files().get_media(fileId=file_id).execute()
        return jsonify({"content": file.decode('utf-8')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ THIS PART IS CRITICAL FOR RENDER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
