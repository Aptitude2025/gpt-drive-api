from google_auth_oauthlib.flow import InstalledAppFlow

# Define the required Drive scope
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Create the flow from your credentials.json file
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

# Run a local server to complete authentication in browser
creds = flow.run_local_server(port=8080)

# Save the credentials to token.json
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("✅ token.json has been created successfully.")
