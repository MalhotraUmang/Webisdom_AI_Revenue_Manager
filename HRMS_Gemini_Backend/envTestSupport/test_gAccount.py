from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
from config import (
    SERVICE_ACCOUNT_FILE,
    SPREADSHEET_ID,
)

SERVICE_ACCOUNT_FILE = SERVICE_ACCOUNT_FILE
SPREADSHEET_ID = SPREADSHEET_ID

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

# Example: Read first 5 rows from "Clients" sheet
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="Clients!A1:E6"
).execute()

print(result.get("values", []))



