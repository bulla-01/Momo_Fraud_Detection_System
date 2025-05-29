#transacton_vollume.py
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from collections import defaultdict


user_tx_times = defaultdict(list)

def check_user_frequency(txn):
    user = txn["nameOrig"]
    now = datetime.fromisoformat(txn["trxdate"].replace("Z", "+00:00"))

    # Keep only transactions from the past hour
    recent_times = [t for t in user_tx_times[user] if now - t < timedelta(hours=1)]
    recent_times.append(now)
    user_tx_times[user] = recent_times

    return len(recent_times)




        
        
