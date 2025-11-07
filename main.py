import re
import time
import json
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import (
    SPREADSHEET_ID,
    CLIENTS_SHEET,
    CAMPAIGNS_SHEET,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    REQUEST_DELAY,
    BATCH_SIZE,
)
import google.generativeai as genai

# -------------------------------------------------------------------
# 🔧 SETUP
# -------------------------------------------------------------------
def init_google_sheets():
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()


def init_gemini():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)


# -------------------------------------------------------------------
# 🧹 SHEET HELPERS
# -------------------------------------------------------------------
def read_sheet(service, sheet_name):
    """Read a Google Sheet into a pandas DataFrame (auto-pads rows)."""
    result = service.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A:Z"
    ).execute()
    values = result.get("values", [])
    if not values:
        raise ValueError(f"No data found in sheet '{sheet_name}'.")
    headers, rows = values[0], values[1:]
    clean_rows = [
        r + [""] * (len(headers) - len(r)) if len(r) < len(headers) else r[:len(headers)]
        for r in rows
    ]
    return pd.DataFrame(clean_rows, columns=headers)


def update_sheet(service, sheet_name, df):
    """Write a DataFrame back to Google Sheets."""
    values = [df.columns.tolist()] + df.values.tolist()
    service.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A:Z"
    ).execute()
    service.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()


# -------------------------------------------------------------------
# 🧠 LLM CALLS
# -------------------------------------------------------------------
def call_gemini_with_retry(model, prompt, max_retries=3):
    """Call Gemini with basic retry/backoff handling."""
    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"⚠️ Gemini call failed (attempt {attempt}): {e}")
            if "429" in str(e):  # rate limit
                print("⏳ Waiting 60 seconds due to rate limit...")
                time.sleep(60)
            else:
                time.sleep(5)
    return None


# -------------------------------------------------------------------
# 🧩 CLIENT ENRICHMENT
# -------------------------------------------------------------------
def extract_client_profile(model, chat_text):
    """Use Gemini to extract client attributes."""
    prompt = f"""
You are a hospitality data analyst. Based on this hotel guest chat:

{chat_text}

Identify:
1. client_type
2. client_interests (list)
3. client_traits (list)

Respond with **only** JSON (no markdown), e.g.:
{{
  "client_type": "Business Traveler",
  "client_interests": ["Spa", "Dining"],
  "client_traits": ["Luxury-seeking", "Efficient"]
}}
"""
    response = call_gemini_with_retry(model, prompt)
    if not response:
        return None

    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.strip("`").replace("json", "", 1).strip()
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        clean = match.group(0)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        print(f"❌ JSON parse failed for client chat:\n{response}")
        return None


def infer_client_category(model, client_type, interests, traits):
    """Use a second Gemini instance to infer Client Category."""
    prompt = f"""
You are a hotel marketing analyst.
Based on the following client profile, determine a short descriptive Client Category label or a few keywords.

Client Type: {client_type}
Client Interests: {interests}
Client Traits: {traits}

Respond ONLY with plain text listing 1–3 descriptive categories or keywords (comma-separated), e.g.:
Leisure, Family, Spa
"""
    response = call_gemini_with_retry(model, prompt)
    if not response:
        return ""
    # Clean and simplify
    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.strip("`").replace("json", "", 1).strip()
    return clean


# -------------------------------------------------------------------
# 🎯 CAMPAIGN LOGIC
# -------------------------------------------------------------------
def generate_campaign_id(existing_ids):
    pattern = re.compile(r"CMP-(\d+)")
    nums = [int(pattern.search(cid).group(1)) for cid in existing_ids if pattern.search(cid)]
    next_id = max(nums) + 1 if nums else 1
    return f"CMP-{next_id:04d}"


def find_matching_clients(df_clients, target_category):
    """Find clients where Client Category overlaps with campaign Target Category."""
    if not target_category:
        return pd.DataFrame()

    target_words = set([w.strip().lower() for w in re.split(r"[ ,;/]+", target_category) if w.strip()])
    matches = []

    for _, row in df_clients.iterrows():
        client_cats = str(row.get("Client Category", "")).lower()
        if any(word in client_cats for word in target_words):
            matches.append(row)

    return pd.DataFrame(matches)


# -------------------------------------------------------------------
# 🚀 MAIN PROCESS
# -------------------------------------------------------------------
def process_clients_and_campaigns():
    sheets = init_google_sheets()

    # LLM instances
    gemini_client_analyzer = init_gemini()      # extracts type, interests, traits
    gemini_client_categorizer = init_gemini()   # infers category
    print("✅ Initialized Gemini instances.")

    # === STEP 1: Read Clients sheet ===
    df_clients = read_sheet(sheets, CLIENTS_SHEET)
    for col in ["Client Type", "Client Interests", "Client Traits", "Client Category"]:
        if col not in df_clients.columns:
            df_clients[col] = ""

    total_clients = len(df_clients)
    print(f"🧾 Found {total_clients} clients in '{CLIENTS_SHEET}'.")

    # === STEP 2: Fill missing client profiles ===
    for start in range(0, total_clients, BATCH_SIZE):
        batch = df_clients.iloc[start:start + BATCH_SIZE]
        print(f"\n🔹 Processing batch {start // BATCH_SIZE + 1} ({len(batch)} clients)...")

        for idx, row in batch.iterrows():
            client_id = row.get("Client ID", f"C{idx+1}")
            chat = str(row.get("Chat Text", "")).strip()

            if not chat:
                continue

            # Step 2A: Extract Type, Interests, Traits (LLM #1)
            if not row.get("Client Type", "").strip():
                print(f"🔍 Analyzing client {client_id} ...")
                profile = extract_client_profile(gemini_client_analyzer, chat)
                if profile:
                    df_clients.at[idx, "Client Type"] = profile.get("client_type", "")
                    df_clients.at[idx, "Client Interests"] = ", ".join(profile.get("client_interests", []))
                    df_clients.at[idx, "Client Traits"] = ", ".join(profile.get("client_traits", []))
                    print(f"✅ {client_id} profile updated.")
                else:
                    print(f"⚠️ {client_id} profile could not be parsed.")
                time.sleep(REQUEST_DELAY)

            # Step 2B: Infer Category (LLM #2)
            if not row.get("Client Category", "").strip():
                client_type = df_clients.at[idx, "Client Type"]
                interests = df_clients.at[idx, "Client Interests"]
                traits = df_clients.at[idx, "Client Traits"]
                print(f"🧩 Inferring category for {client_id} ...")
                category = infer_client_category(gemini_client_categorizer, client_type, interests, traits)
                df_clients.at[idx, "Client Category"] = category
                print(f"🏷️ {client_id} category: {category}")
                time.sleep(REQUEST_DELAY)

        update_sheet(sheets, CLIENTS_SHEET, df_clients)
        print("💾 Batch saved to Clients sheet.")

    # === STEP 3: Process Campaigns sheet ===
    df_campaigns = read_sheet(sheets, CAMPAIGNS_SHEET)
    if "Campaign ID" not in df_campaigns.columns:
        df_campaigns["Campaign ID"] = ""
    if "Campaign Message Count" not in df_campaigns.columns:
        df_campaigns["Campaign Message Count"] = ""

    print(f"\n📢 Processing {len(df_campaigns)} campaigns...")

    existing_ids = df_campaigns["Campaign ID"].dropna().tolist()

    for idx, row in df_campaigns.iterrows():
        target_category = str(row.get("Target Client Category", "")).strip()
        campaign_id = str(row.get("Campaign ID", "")).strip()

        if not target_category:
            print(f"⚠️ Skipping row {idx+1} — no Target Client Category.")
            continue

        if not campaign_id:
            campaign_id = generate_campaign_id(existing_ids)
            df_campaigns.at[idx, "Campaign ID"] = campaign_id
            existing_ids.append(campaign_id)
            print(f"🆔 Assigned Campaign ID: {campaign_id}")

        matched_clients = find_matching_clients(df_clients, target_category)
        match_count = len(matched_clients)
        df_campaigns.at[idx, "Campaign Message Count"] = match_count

        print(f"🎯 {campaign_id} — Target '{target_category}' matched {match_count} clients.")

        if match_count > 0:
            print("👥 Matching Clients:")
            for _, client in matched_clients.iterrows():
                print(f"   - {client.get('Client Name')} | {client.get('Client Email')} | {client.get('Client Phone')}")

        time.sleep(REQUEST_DELAY)

    update_sheet(sheets, CAMPAIGNS_SHEET, df_campaigns)
    print("\n✅ All campaign details updated successfully.")


# -------------------------------------------------------------------
# ▶️ RUN
# -------------------------------------------------------------------
if __name__ == "__main__":
    process_clients_and_campaigns()
