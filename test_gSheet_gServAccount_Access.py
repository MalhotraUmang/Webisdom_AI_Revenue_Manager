from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID = "1Wztt1f0IqAUjIMj5Angz8sl9UBlLulfeEjd70tSxaZs"

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="Clients!A1:D6"  # adjust sheet name if needed
).execute()

print(result.get("values", []))