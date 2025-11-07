import time
import json
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.generativeai as genai
from config import *


# ============================
#  Initialization Functions
# ============================
def init_google_sheets():
    """Initialize Google Sheets API using service account."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


def init_gemini():
    """Initialize Gemini client."""
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)


# ============================
#  Google Sheets Utilities
# ============================
def read_sheet(service, sheet_name):
    """Read a sheet into a pandas DataFrame, padding short rows automatically."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A:Z"
    ).execute()
    values = result.get("values", [])
    if not values:
        raise ValueError(f"No data found in sheet '{sheet_name}'.")

    headers = values[0]
    rows = values[1:]

    # Pad or trim each row to match header length
    clean_rows = [
        r + [""] * (len(headers) - len(r)) if len(r) < len(headers) else r[:len(headers)]
        for r in rows
    ]

    return pd.DataFrame(clean_rows, columns=headers)



def update_sheet(service, sheet_name, df):
    """Write a pandas DataFrame back to a Google Sheet."""
    values = [df.columns.tolist()] + df.fillna("").values.tolist()
    body = {"values": values}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        body=body
    ).execute()


# ============================
#  LLM Utilities
# ============================
def call_gemini_with_retry(model, prompt):
    """Call Gemini API with retry handling."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini call failed (attempt {attempt}): {e}")
            if "429" in str(e):  # rate-limit specific
                print("⏳ Waiting 60 seconds due to rate limit...")
                time.sleep(60)
            elif attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return None


# ============================
#  Sheet 1 – Client Profiling
# ============================
def extract_client_profile(model, chat_text):
    """LLM 1: Extract client attributes from chat text."""
    prompt = f"""
You are a hospitality industry data analyst.
A hotel guest chat transcript is shown below:

{chat_text}

Determine:
1. Client Type (e.g. New Guest, Returning Guest, Business Traveler, Family Vacationer).
2. Client Interests (e.g. Sea View Rooms, Spa, Dining, Conference Halls).
3. Client Traits (e.g. budget-conscious, luxury-seeking, spontaneous, loyal).

Respond ONLY with strict JSON (no markdown, no explanations):
{{"client_type": "...", "client_interests": ["..."], "client_traits": ["..."]}}
"""
    response = call_gemini_with_retry(model, prompt)
    if not response:
        return None

    # --- CLEAN THE RESPONSE ---
    # remove Markdown ```json ``` wrappers if present
    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.strip("`")
        # remove optional 'json' after opening fence
        clean = clean.replace("json", "", 1).strip()
    # extract first {...} block if multiple
    import re
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        clean = match.group(0)

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        print(f"❌ JSON parse failed for client chat:\n{response}")
        return None



# ============================
#  Sheet 2 – Campaign Strategy
# ============================
def extract_campaign_details(model, client_type, interests, traits):
    """LLM 2: Generate marketing campaign touch points and message format."""
    prompt = f"""
You are a hospitality marketing strategist.
Based on the client information below, design marketing touch points and suggest a concise message format.

Client Type: {client_type}
Client Interests: {interests}
Client Traits: {traits}

Respond ONLY with raw JSON (no markdown, no explanations). 
Ensure that "message_format" is a single text string summarizing all messages briefly.

Example:
{{
  "touch_points": ["Email", "SMS", "Social Media"],
  "message_format": "Email greeting, SMS reminder, social media teaser."
}}
"""

    response = call_gemini_with_retry(model, prompt)
    if not response:
        return None

    # --- CLEAN THE RESPONSE ---
    clean = response.strip()

    # Remove markdown-style ```json ... ``` wrappers if present
    if clean.startswith("```"):
        clean = clean.strip("`")
        clean = clean.replace("json", "", 1).strip()

    # Extract the first {...} JSON object block
    import re
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        clean = match.group(0)

    # Attempt to parse cleaned text as JSON
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        print(f"❌ JSON parse failed for campaign generation:\n{response}")
        return None




# ============================
#  Main Workflow
# ============================
def process_clients_and_campaigns():
    """Main workflow — process client profiles and generate campaigns."""
    sheets = init_google_sheets()
    gemini_client_analyzer = init_gemini()     # For 'Clients' sheet
    gemini_client_campaign = init_gemini()     # For 'Campaigns' sheet

    # === Step 1: Load Clients Sheet ===
    df_clients = read_sheet(sheets, CLIENTS_SHEET)
    for col in ["Client Type", "Client Interests", "Client Traits"]:
        if col not in df_clients.columns:
            df_clients[col] = ""

    total_clients = len(df_clients)
    print(f"🧾 Found {total_clients} clients to process in '{CLIENTS_SHEET}'.")

    # === Step 2: Process Clients in Batches ===
    for start in range(0, total_clients, BATCH_SIZE):
        batch = df_clients.iloc[start:start + BATCH_SIZE]
        print(f"\n🔹 Processing batch {start // BATCH_SIZE + 1} ({len(batch)} clients)...")

        for idx, row in batch.iterrows():
            client_id = row.get("Client ID", f"C{idx+1}")
            chat = str(row.get("Chat Text", "")).strip()

            # Skip if no chat text or already processed
            if not chat:
                print(f"⚠️ Skipping {client_id} — no chat text found.")
                continue
            if row.get("Client Type", "").strip():
                print(f"⏩ Skipping {client_id} — already processed.")
                continue

            print(f"🔍 Analyzing client {client_id} ...")

            # --- Extract client profile (Type, Interests, Traits) ---
            profile = extract_client_profile(gemini_client_analyzer, chat)
            if profile:
                df_clients.at[idx, "Client Type"] = profile.get("client_type", "")
                df_clients.at[idx, "Client Interests"] = ", ".join(profile.get("client_interests", []))
                df_clients.at[idx, "Client Traits"] = ", ".join(profile.get("client_traits", []))
                print(f"✅ {client_id} profile updated.")
            else:
                print(f"⚠️ {client_id} profile could not be parsed.")
                continue

            time.sleep(REQUEST_DELAY)

        # Save progress after each batch
        update_sheet(sheets, CLIENTS_SHEET, df_clients)
        print("💾 Batch saved to Clients sheet.")

    # === Step 3: Use Clients Sheet → Generate Campaigns Sheet ===
    df_campaigns = pd.DataFrame(columns=["Client ID", "Touch Points", "Message Format"])

    for idx, row in df_clients.iterrows():
        client_id = row.get("Client ID", f"C{idx+1}")
        client_type = row.get("Client Type", "").strip()
        interests = row.get("Client Interests", "").strip()
        traits = row.get("Client Traits", "").strip()

        if not client_type:
            continue  # skip if profile not extracted

        print(f"🎯 Generating campaign for {client_id} ...")

        campaign = extract_campaign_details(
            gemini_client_campaign,
            client_type,
            interests,
            traits
        )
        if campaign:
            # --- Normalize touch points ---
            touch_points = campaign.get("touch_points", [])
            # Handle if touch_points is a list of dicts or strings
            if isinstance(touch_points, list):
                normalized = []
                for tp in touch_points:
                    if isinstance(tp, dict):
                        # Join dict values into readable format
                        normalized.append(" - ".join(f"{k}: {v}" for k, v in tp.items()))
                    else:
                        normalized.append(str(tp))
                touch_points_str = ", ".join(normalized)
            else:
                touch_points_str = str(touch_points)

            # --- Normalize message format ---
            message_format = campaign.get("message_format", "")
            if isinstance(message_format, dict):
                # Join all key-value pairs into readable text
                formatted = []
                for k, v in message_format.items():
                    formatted.append(f"{k}: {v}")
                message_format_str = "\n\n".join(formatted)
            else:
                message_format_str = str(message_format)

            # --- Add to Campaigns DataFrame ---
            df_campaigns.loc[len(df_campaigns)] = [
                client_id,
                touch_points_str,
                message_format_str
            ]
            print(f"📣 Campaign ready for {client_id}.")
        else:
            df_campaigns.loc[len(df_campaigns)] = [client_id, "", ""]
            print(f"⚠️ Campaign generation failed for {client_id}.")

        time.sleep(REQUEST_DELAY)

    update_sheet(sheets, CAMPAIGNS_SHEET, df_campaigns)
    print("\n✅ All campaign details saved to 'Campaigns' sheet.")



if __name__ == "__main__":
    process_clients_and_campaigns()
