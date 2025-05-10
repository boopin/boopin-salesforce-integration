# Boopin Salesforce Lead Integration

This Streamlit app allows Boopin to securely send leads from Snapchat or TikTok Lead Gen forms directly into Salesforce via API — without giving ad account access to external agencies.

---

## 🚀 Features

- 🔐 Salesforce OAuth2.0 authentication
- 📤 Lead submission via Salesforce Lead Capture API
- 🧾 Dynamic form to enter lead data
- ☁️ Compatible with Streamlit Cloud deployment
- 💼 Secure credentials via `.env` file (excluded from repo)

---

## 🧰 Technologies Used

- Python 3
- Streamlit
- Requests
- dotenv

---

## 📁 Project Structure

boopin-salesforce-integration/
├── main.py # Streamlit frontend + integration logic
├── .env.template # Environment variable template (for Streamlit Secrets)
├── requirements.txt # Python dependencies

yaml
Copy
Edit

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
You can also upload directly via browser if not using Git locally.

### 2. Create `.env` File Locally (do not commit it)

CLIENT_ID=your_salesforce_client_id
CLIENT_SECRET=your_salesforce_client_secret
USERNAME=your_salesforce_username
PASSWORD=your_salesforce_password
TOKEN_URL=https://test.salesforce.com/services/oauth2/token

yaml
Copy
Edit

> 🔒 Never commit your `.env` file. Only share `.env.template` in the repo.

---

### 3. Install Requirements

```bash
pip install -r requirements.txt
4. Run the App
bash
Copy
Edit
streamlit run main.py
