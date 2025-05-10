import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TOKEN_URL = os.getenv("TOKEN_URL")
LEAD_API_PATH = "/services/apexrest/lead/createlead"

def get_salesforce_token():
    payload = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json()

def send_lead(token_data, lead_payload):
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Content-Type": "application/json"
    }
    instance_url = token_data["instance_url"]
    response = requests.post(instance_url + LEAD_API_PATH, headers=headers, json=lead_payload)
    return response.status_code, response.text

# App logo + title + theme toggle
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://i.imgur.com/CsnXPLZ.jpeg", width=100)
with col2:
    st.title("Boopin → Salesforce Lead Integration")

theme_choice = st.selectbox("🌗 Theme Preference (select in ⚙️ Settings → Theme):", ["Light", "Dark", "Follow System"])
st.caption("Use Streamlit’s top-right ⚙️ menu → **Settings → Theme** to apply your preferred mode.")

token = None

# Manual form section
with st.expander("📤 Submit Single Lead Manually"):
    with st.form("manual_form"):
        firstname = st.text_input("First Name", "John")
        lastname = st.text_input("Last Name", "Doe")
        mobile = st.text_input("Mobile", "0512345678")
        email = st.text_input("Email", "john.doe@example.com")
        submit_manual = st.form_submit_button("Send Lead to Salesforce")

    if submit_manual:
        token = get_salesforce_token()
        lead_data = {
            "Enquiry_Type": "Book_a_Test_Drive",
            "Firstname": firstname,
            "Lastname": lastname,
            "Mobile": mobile,
            "Email": email,
            "DealerCode": "PTC",
            "Shrm_SvCtr": "PETROMIN Jubail",
            "Make": "Jeep",
            "Line": "Wrangler",
            "Entry_Form": "EN",
            "Market": "Saudi Arabia",
            "Campaign_Source": "Manual",
            "Campaign_Name": "PET-Q2-2025",
            "Campaign_Medium": "Boopin",
            "TestDriveType": "In Showroom",
            "Extended_Privacy": "true",
            "Purchase_TimeFrame": "More than 3 months",
            "Source_Site": "manual entry",
            "Marketing_Communication_Consent": "1",
            "Fund": "DD",
            "FormCode": "PET_Q2_25",
            "Request_Origin": "https://www.jeep-saudi.com",
            "MasterKey": "Jeep_EN_GENERIC_RI:RP:TD_0_8_1_6_50_42"
        }

        try:
            status, resp = send_lead(token, lead_data)
            if status == 200:
                st.success("✅ Lead sent successfully!")
            else:
                st.error(f"❌ Failed. Status {status}, Response: {resp}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Multiple platform uploads
st.markdown("### 📁 Upload Leads from TikTok and Snapchat")

for platform in ["TikTok", "Snapchat"]:
    st.subheader(f"{platform} Leads")

    uploaded_file = st.file_uploader(f"Upload {platform} CSV", type="csv", key=f"{platform}_file")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        required_cols = {"Firstname", "Lastname", "Mobile", "Email"}
        if not required_cols.issubset(df.columns):
            st.error(f"CSV must include these columns: {', '.join(required_cols)}")
            continue

        # Preview toggle
        if st.checkbox(f"🔍 Preview full {platform} CSV", key=f"{platform}_preview"):
            st.dataframe(df)
        else:
            st.dataframe(df.head())

        if st.button(f"📤 Send {platform} Leads to Salesforce", key=f"{platform}_submit"):
            token = token or get_salesforce_token()
            results = []

            for i, row in df.iterrows():
                lead_data = {
                    "Enquiry_Type": "Book_a_Test_Drive",
                    "Firstname": row["Firstname"],
                    "Lastname": row["Lastname"],
                    "Mobile": row["Mobile"],
                    "Email": row["Email"],
                    "DealerCode": "PTC",
                    "Shrm_SvCtr": "PETROMIN Jubail",
                    "Make": "Jeep",
                    "Line": "Wrangler",
                    "Entry_Form": "EN",
                    "Market": "Saudi Arabia",
                    "Campaign_Source": platform,
                    "Campaign_Name": "PET-Q2-2025",
                    "Campaign_Medium": "Boopin",
                    "TestDriveType": "In Showroom",
                    "Extended_Privacy": "true",
                    "Purchase_TimeFrame": "More than 3 months",
                    "Source_Site": f"{platform.lower()} Ads",
                    "Marketing_Communication_Consent": "1",
                    "Fund": "DD",
                    "FormCode": "PET_Q2_25",
                    "Request_Origin": "https://www.jeep-saudi.com",
                    "MasterKey": "Jeep_EN_GENERIC_RI:RP:TD_0_8_1_6_50_42"
                }

                try:
                    status, resp = send_lead(token, lead_data)
                    if status == 200:
                        results.append({**row, "Status": "Success", "Message": "Lead sent"})
                    else:
                        results.append({**row, "Status": "Failed", "Message": f"{resp}"})
                except Exception as e:
                    results.append({**row, "Status": "Failed", "Message": str(e)})

            result_df = pd.DataFrame(results)
            st.success(f"✅ {platform}: {sum(result_df['Status'] == 'Success')} leads sent.")
            st.warning(f"⚠️ {platform}: {sum(result_df['Status'] == 'Failed')} failed.")
            st.dataframe(result_df)

            # Download full log
            full_log_csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"⬇️ Download {platform} Log", full_log_csv, f"{platform.lower()}_submission_log.csv", "text/csv", key=f"{platform}_log")

            # Download only failed rows
            failed_df = result_df[result_df["Status"] == "Failed"]
            if not failed_df.empty:
                failed_csv = failed_df.to_csv(index=False).encode('utf-8')
                st.download_button(f"⬇️ Download Failed {platform} Leads", failed_csv, f"{platform.lower()}_failed.csv", "text/csv", key=f"{platform}_failed")
