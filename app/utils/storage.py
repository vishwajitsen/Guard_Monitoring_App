import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
PHOTO_DIR = os.path.join(DATA_DIR, "photos")
QR_DIR = os.path.join(DATA_DIR, "qrcodes")
USERS_XLSX = os.path.join(DATA_DIR, "users.xlsx")
ATTEND_XLSX = os.path.join(DATA_DIR, "attendance.xlsx")

USER_COLS = ["user_id", "name", "phone", "email", "password_hash", "photo_path"]
ATTEND_COLS = [
    "record_id","user_id","timestamp",
    "latitude","longitude","address","pincode","plus_code",
    "photo_path","action","location_source","qr_payload"
]

def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PHOTO_DIR, exist_ok=True)
    os.makedirs(QR_DIR, exist_ok=True)
    if not os.path.exists(USERS_XLSX):
        pd.DataFrame(columns=USER_COLS).to_excel(USERS_XLSX, index=False)
    if not os.path.exists(ATTEND_XLSX):
        pd.DataFrame(columns=ATTEND_COLS).to_excel(ATTEND_XLSX, index=False)

def _as_str(x):
    return "" if x is None else str(x)

def add_user(user_id, name, phone, email, password_hash, photo_path):
    # Ensure strings to avoid Excel numeric coercion issues
    user_id = _as_str(user_id).strip()
    name = _as_str(name).strip()
    phone = _as_str(phone).strip()
    email = _as_str(email).strip()
    password_hash = _as_str(password_hash).strip()
    photo_path = _as_str(photo_path).strip()

    df = pd.read_excel(USERS_XLSX, dtype=str)
    if not df.empty:
        df["user_id"] = df["user_id"].astype(str).str.strip()
        # Case-insensitive match to avoid duplicates like "USER" vs "user"
        if (df["user_id"].str.casefold() == user_id.casefold()).any():
            raise ValueError("User already exists.")

    new_row = {
        "user_id": user_id, "name": name, "phone": phone, "email": email,
        "password_hash": password_hash, "photo_path": photo_path
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(USERS_XLSX, index=False)

def get_user(user_id):
    """Robust lookup: force both Excel and input to strings, trim, and casefold."""
    key = _as_str(user_id).strip().casefold()
    df = pd.read_excel(USERS_XLSX, dtype=str)
    if df.empty:
        return None
    df["user_id"] = df["user_id"].astype(str).str.strip()
    row = df[df["user_id"].str.casefold() == key]
    return None if row.empty else row.iloc[0].to_dict()

def add_attendance(user_id, latitude, longitude, address, pincode, plus_code,
                   photo_path, action, location_source, qr_payload=""):
    df = pd.read_excel(ATTEND_XLSX, dtype=str)

    # Generate record id (numeric increasing, but store as str for safety)
    try:
        if df.empty:
            next_id = 1
        else:
            # previous values may be strings; coerce safely
            nums = pd.to_numeric(df["record_id"], errors="coerce")
            next_id = (nums.max() or 0) + 1
    except Exception:
        next_id = 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {
        "record_id": str(int(next_id)),
        "user_id": _as_str(user_id).strip(),
        "timestamp": now,
        "latitude": _as_str(latitude),
        "longitude": _as_str(longitude),
        "address": _as_str(address),
        "pincode": _as_str(pincode),
        "plus_code": _as_str(plus_code),
        "photo_path": _as_str(photo_path),
        "action": _as_str(action),
        "location_source": _as_str(location_source),
        "qr_payload": _as_str(qr_payload),
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(ATTEND_XLSX, index=False)

def load_attendance():
    return pd.read_excel(ATTEND_XLSX, dtype=str)

def query_attendance(user_id=None, date_from=None, date_to=None, action=None):
    df = load_attendance()

    if user_id:
        df["user_id"] = df["user_id"].astype(str)
        df = df[df["user_id"].str.contains(str(user_id), na=False, case=False)]

    if date_from:
        df = df[pd.to_datetime(df["timestamp"]) >= pd.to_datetime(date_from)]
    if date_to:
        df = df[pd.to_datetime(df["timestamp"]) <= pd.to_datetime(date_to)]

    if action:
        df = df[df["action"] == action]

    return df
