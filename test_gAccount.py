from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID = "1Wztt1f0IqAUjIMj5Angz8sl9UBlLulfeEjd70tSxaZs"  # from sheet URL

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



