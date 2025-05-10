import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Salesforce credentials from secrets or .env
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TOKEN_URL = os.getenv("TOKEN_URL")
LEAD_API_PATH = "/services/apexrest/lead/createlead"

# Authenticate and get access token
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

# Send lead data to Salesforce
def send_lead(token_data, lead_payload):
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Content-Type": "application/json"
    }
    instance_url = token_data["instance_url"]
    response = requests.post(instance_url + LEAD_API_PATH, headers=headers, json=lead_payload)
    return response.status_code, response.text

# Streamlit UI
st.title("Boopin → Salesforce Lead Integration")

with st.form("lead_form"):
    firstname = st.text_input("First Name", "John")
    lastname = st.text_input("Last Name", "Doe")
    mobile = st.text_input("Mobile", "0512345678")
    email = st.text_input("Email", "john.doe@example.com")
    submitted = st.form_submit_button("Send Lead to Salesforce")

# On submit
if submitted:
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
        "Campaign_Source": "Display",
        "Campaign_Name": "PET-Q2-2025",
        "Campaign_Medium": "Boopin",
        "TestDriveType": "In Showroom",
        "Extended_Privacy": "true",
        "Purchase_TimeFrame": "More than 3 months",
        "Source_Site": "Snapchat Ads",
        "Marketing_Communication_Consent": "1",
        "Fund": "DD",
        "FormCode": "PET_Q2_25",
        "Request_Origin": "https://www.jeep-saudi.com"  # ✅ Mandatory field added
    }

    try:
        token = get_salesforce_token()
        status, response = send_lead(token, lead_data)
        if status == 200:
            st.success(f"Lead sent successfully! Status: {status}")
        else:
            st.error(f"Lead failed! Status: {status}\nResponse: {response}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
