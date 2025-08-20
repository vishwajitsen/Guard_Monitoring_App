# Guard_Monitoring_App

A beautiful maroon-themed desktop app to register guards, log in, capture their selfie + current location, and take QR-based attendance (start/end). Everything is saved to Excel files.

## Features
- Maroon-themed, modern **Tkinter + ttkbootstrap** GUI.
- **Register/Login** using phone or email (user id) + password.
- **All data saved to Excel** (in `data/`):
  - `users.xlsx` → guard master file (user id + photo + details).
  - `attendance.xlsx` → each activity row: selfie capture, QR start, QR end.
- **Capture photo** (from camera or file) and **current location**.
- **Scan QR** using your webcam (OpenCV QRCodeDetector, no external zbar needed).
- **Admin dashboard** with filters and export.

## Folder Structure
```
Guard_Monitoring_App/
├─ app/
│  ├─ main.py
│  ├─ ui/
│  │  └─ theme.py
│  └─ utils/
│     ├─ storage.py
│     ├─ camera.py
│     └─ geo.py
├─ data/
│  ├─ users.xlsx
│  └─ attendance.xlsx
├─ photos/              # saved selfies/uploads
├─ qr/                  # optional: saved/loaded QR images
├─ requirements.txt
└─ README.md
```

## Quick Start
1. Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate   # macOS/Linux

   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app/main.py
   ```

> If geolocation fails due to network restrictions, the app will kindly ask the guard to enter the location manually.

## Excel Schemas
### `data/users.xlsx`
| user_id | name | phone | email | password_hash | photo_path | created_at |
|--------:|------|-------|-------|---------------|------------|------------|

### `data/attendance.xlsx`
| record_id | user_id | timestamp | latitude | longitude | photo_path | action | location_source | qr_payload |
|----------:|--------:|-----------|----------|-----------|------------|--------|-----------------|------------|

Actions: `LOGIN_PHOTO`, `QR_START`, `QR_END`.

## Notes
- Passwords are stored as SHA-256 hashes.
- Webcam optional: you can also upload a selfie from file.
- Admin dashboard: open from the main screen to review/filter/export attendance.
