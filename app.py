from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

app = Flask(__name__)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = None

def authenticate():
    global creds
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

# authenticate()

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
