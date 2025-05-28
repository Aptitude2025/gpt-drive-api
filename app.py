from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
import json
import os
from google.oauth2 import service_account

creds_info = json.loads(os.environ['GOOGLE_CREDS'])
creds = service_account.Credentials.from_service_account_info(creds_info)


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

if __name__ == '__main__':
    app.run(port=5000)
