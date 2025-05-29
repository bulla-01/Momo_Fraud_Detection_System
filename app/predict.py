import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
import logging
import smtplib
from email.message import EmailMessage
from collections import defaultdict
from datetime import datetime, timedelta

# In-memory tracker for transaction frequency
user_tx_times = defaultdict(list)

# ========== Model & Asset Loading ==========
try:
    feature_columns = joblib.load("feature_columns.pkl")
except Exception as e:
    logging.error(f"❌ Error loading feature columns: {e}")
    feature_columns = []

try:
    mlp_encoder = tf.keras.models.load_model("mlp_encoder.h5")
    logging.info("✅ MLP encoder loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading MLP encoder: {e}")
    mlp_encoder = None

try:
    ensemble_model = joblib.load("xgb_sklearn_wrapper.pkl")
    logging.info("✅ Ensemble model loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading Ensemble model: {e}")
    ensemble_model = None

try:
    scaler = joblib.load("scaler.pkl")
    logging.info("✅ Scaler loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading scaler: {e}")
    scaler = None

# ========== Preprocessing ==========
def preprocess_input(txn: dict):
    df = pd.DataFrame([txn])

    df["nameOrig_numeric"] = df["nameOrig"].str.extract(r"(\d+)").astype(float)
    df["nameDest_numeric"] = df["nameDest"].str.extract(r"(\d+)").astype(float)

    df["type"] = df["type"].str.upper()
    type_dummies = pd.get_dummies(df["type"], prefix="type", dtype=int)
    df = pd.concat([df, type_dummies], axis=1)

    df["trx_bal_origin"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
    df["trx_bal_dest"] = df["newbalanceDest"] - df["oldbalanceDest"]
    df["origin_amt_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1)
    df["dest_amt_ratio"] = df["amount"] / (df["oldbalanceDest"] + 1)
    df["origin_old_zero"] = (df["oldbalanceOrg"] == 0).astype(int)
    df["origin_new_zero"] = (df["newbalanceOrig"] == 0).astype(int)
    df["dest_old_zero"] = (df["oldbalanceDest"] == 0).astype(int)
    df["dest_new_zero"] = (df["newbalanceDest"] == 0).astype(int)
    df["trx_per_user"] = 1
    df["average_amt_per_user"] = df["amount"]
    df["large_value_flag"] = ((df.get("type_TRANSFER", 0) == 1) & (df["amount"] > 200000)).astype(int)
    df["flag_empty_dest"] = ((df["newbalanceDest"] == 0) & (df["amount"] > 0)).astype(int)

    df.drop(columns=["nameOrig", "nameDest", "type", "trxdate", "mobilenetwork", "beneficiaryname"],
            errors='ignore', inplace=True)

    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_columns]
    scaled = scaler.transform(df)
    return scaled

# ========== Frequency Rule ==========
def check_user_frequency(txn):
    user = txn["nameOrig"]
    now = datetime.fromisoformat(txn["trxdate"].replace("Z", "+00:00"))
    recent_times = [t for t in user_tx_times[user] if now - t < timedelta(hours=1)]
    recent_times.append(now)
    user_tx_times[user] = recent_times
    return len(recent_times)

# ========== Prediction Logic ==========
def predict_fraud(txn: dict) -> tuple[int, float, str, str]:
    if txn["amount"] > 1e8 or txn["newbalanceOrig"] < 0:
        return (
            1,
            1.0,
            "High amount or negative balance",
            "Rule-based: High amount or negative balance"
        )

    if check_user_frequency(txn) > 10:
        logging.info(f"User {txn['nameOrig']} exceeded 10 txns in past hour.")
        return (
            1,
            0.95,
            "Unusual transaction frequency",
            "Rule-based: Unusual transaction frequency"
        )

    preprocessed = preprocess_input(txn)
    encoded = mlp_encoder.predict(preprocessed)
    prob = ensemble_model.predict_proba(encoded)[0][1]
    logging.info(f"Fraud probability: {prob}")

    return (
        int(prob > 0.6),
        round(float(prob), 4),
        "ML model prediction",
        "ML-based: Probability > 0.3"
    )

# ========== Email Alert ==========
def send_fraud_alert_email(txn, is_fraud: int, risk_score: float, reason: str):
    try:
        msg = EmailMessage()
        msg["Subject"] = "🚨 Fraudulent Transaction Detected"
        msg["From"] = "sarfof06@gmail.com"
        msg["To"] = "bentjun25@gmail.com,piesiegloria25@gmail.com,jboateng349@gmail.com,peprahf63@gmail.com"

        message = f"""
🚨 FRAUD ALERT 🚨

A potentially fraudulent transaction was detected.

📅 Date: {txn.get('trxdate')}
📱 Initiator: {txn.get('nameOrig')}
👤 Beneficiary: {txn.get('beneficiaryname')} ({txn.get('nameDest')})
💵 Amount: GHS {txn.get('amount')}
📡 Mobile Network: {txn.get('mobilenetwork')}
📍 Location: Lat {txn.get('latitude')}, Long {txn.get('longitude')}

🔍 Detection Method: {reason}
📊 Risk Score: {risk_score}
⚠️ Flagged as Fraud: {'YES' if is_fraud else 'NO'}

Full Transaction:
{txn}
"""
        msg.set_content(message)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("sarfof06@gmail.com", "mhtehnhylovnlplj")
            server.send_message(msg, to_addrs=[
                "bentjun25@gmail.com",
                "piesiegloria25@gmail.com",
                "peprahf63@gmail.com",
                "jboateng349@gmail.com"
                
            ])

        logging.info("✅ Fraud alert email sent successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to send fraud alert email: {e}")
