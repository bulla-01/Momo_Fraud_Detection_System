import streamlit as st
import requests
from datetime import date

st.title("📊 Transaction Volume Checker")

# Input for date
selected_date = st.date_input("Select a date", date.today(), key="date_picker")

# Fetch transaction volume when the page loads or the date is changed
@st.cache_data(show_spinner=False)
def fetch_transaction_volume(date_val):
    try:
        response = requests.get(
            "http://localhost:8000/transaction_volume/",
            params={"date": date_val.isoformat()}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "API request failed"}
    except Exception as e:
        return {"error": str(e)}

# Load volume when date changes
data = fetch_transaction_volume(selected_date)

# Display result
if "volume" in data:
    st.success(f"Total transaction volume on {data['trxdate']}:")
    st.text_area("Amount", f"{data['volume']} GHS", height=50)
elif "error" in data:
    st.error(data["error"])
else:
    st.warning("No volume data found.")
