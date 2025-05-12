
import streamlit as st
import requests
import pandas as pd
import os
import random
from dotenv import load_dotenv

# Load env vars
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TOKEN_URL = os.getenv("TOKEN_URL")
LEAD_API_PATH = "/services/apexrest/lead/createlead"

# Global error log
error_log = []

# Token and send helpers
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

# Logo + Title
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://i.imgur.com/CsnXPLZ.jpeg", width=100)
with col2:
    st.title("Boopin → Salesforce Lead Integration")

st.markdown("---")
st.markdown("## 🧾 Manual Lead Submission")

token = None
campaign_list = ["PET-Q2-2025", "PET-Summer-2025", "PET-Offers-2025"]
rand_id = random.randint(1000, 9999)

with st.expander("📥 Submit a Test Lead"):
    with st.form("manual_form"):
        firstname = st.text_input("First Name", f"Test {rand_id}")
        lastname = st.text_input("Last Name", "Dummy")
        mobile = st.text_input("Mobile", f"05123{rand_id}")
        email = st.text_input("Email", f"test{rand_id}@example.com")
        selected_campaign = st.selectbox("Select Campaign", campaign_list)
        submit_manual = st.form_submit_button("Send Lead to Salesforce")

    if submit_manual:
        try:
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
                "Campaign_Name": selected_campaign,
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
            status, resp = send_lead(token, lead_data)
            if status == 200:
                st.success("✅ Lead sent successfully!")
            else:
                err_msg = f"❌ Failed. Status {status}, Response: {resp}"
                st.error(err_msg)
                from datetime import datetime
            error_log.append({"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Section": "Manual", "Error": err_msg})
        except Exception as e:
            err_msg = f"Manual Submission Error: {str(e)}"
            st.error(err_msg)
            from datetime import datetime
            error_log.append({"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Section": "Manual", "Error": err_msg})

# Uploads
st.markdown("---")
st.markdown("## 📤 Bulk Upload: TikTok & Snapchat Leads")

for platform in ["TikTok", "Snapchat"]:
    with st.expander(f"📂 Upload {platform} Leads"):
        uploaded_file = st.file_uploader(f"Upload {platform} CSV", type="csv", key=f"{platform}_file")

        if uploaded_file:
            df = pd.read_csv(uploaded_file)

            required_cols = {"Firstname", "Lastname", "Mobile", "Email"}
            if not required_cols.issubset(df.columns):
                err_msg = f"CSV must include: {', '.join(required_cols)}"
                st.error(err_msg)
                from datetime import datetime
                error_log.append({"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Section": platform, "Error": err_msg})
                continue

            selected_campaign = st.selectbox(f"Select Campaign for {platform}", campaign_list, key=f"{platform}_campaign")

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
                        "Firstname": f"Test {row['Firstname']}",
                        "Lastname": f"Dummy {row['Lastname']}",
                        "Mobile": row["Mobile"],
                        "Email": row["Email"],
                        "DealerCode": "PTC",
                        "Shrm_SvCtr": "PETROMIN Jubail",
                        "Make": "Jeep",
                        "Line": "Wrangler",
                        "Entry_Form": "EN",
                        "Market": "Saudi Arabia",
                        "Campaign_Source": platform,
                        "Campaign_Name": selected_campaign,
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
                            fail_msg = f"{resp}"
                            results.append({**row, "Status": "Failed", "Message": fail_msg})
                            from datetime import datetime
                            error_log.append({"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Section": platform, "Error": f"Row {i}: {fail_msg}"})
                    except Exception as e:
                        err_msg = f"{platform} Lead Error (row {i}): {str(e)}"
                        results.append({**row, "Status": "Failed", "Message": str(e)})
                        from datetime import datetime
                error_log.append({"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Section": platform, "Error": err_msg})

                result_df = pd.DataFrame(results)
                st.success(f"✅ {platform}: {sum(result_df['Status'] == 'Success')} leads sent.")
                st.warning(f"⚠️ {platform}: {sum(result_df['Status'] == 'Failed')} failed.")
                st.dataframe(result_df)

                full_log_csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(f"⬇️ Download {platform} Log", full_log_csv, f"{platform.lower()}_submission_log.csv", "text/csv", key=f"{platform}_log")

                failed_df = result_df[result_df["Status"] == "Failed"]
                if not failed_df.empty:
                    failed_csv = failed_df.to_csv(index=False).encode('utf-8')
                    st.download_button(f"⬇️ Download Failed {platform} Leads", failed_csv, f"{platform.lower()}_failed.csv", "text/csv", key=f"{platform}_failed")

# Show error log if any
if error_log:
    st.markdown("---")
    st.markdown("## 🛑 Error Log (Live)")
    error_df = pd.DataFrame(error_log)
    st.dataframe(error_df)
error_csv = error_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Error Log", error_csv, "error_log.csv", "text/csv", key="error_log_download")

# Theme selector (sidebar only)
st.sidebar.title("🎨 Appearance")
st.sidebar.selectbox("🌗 Theme Mode", ["Light", "Dark", "Follow System"])
st.sidebar.caption("Use ⚙️ menu at top-right to apply theme.")
