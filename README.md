Guard Monitoring App

A desktop application built with Python for guard attendance monitoring using photo, location, and QR code scanning.

🚀 How to Run on Windows

1. Clone or Download the Project


git clone https://github.com/vishwajitsen/Guard_Monitoring_App.git


cd Guard_Monitoring_App

2. Create and Activate Virtual Environment

python -m venv .venv


.venv\Scripts\activate


3. Install Required Dependencies

pip install -r requirements.txt

4. (Optional) Set Google Maps API Key

Create a .env file in the project root:

GOOGLE_MAPS_API_KEY=your_api_key_here

5. Run the Application


python -m app.main

📂 Project Structure
Guard_Monitoring_App/
│── app/
│   ├── main.py         # Main entry point
│   ├── ui/             # UI (theme, components)
│   ├── utils/          # Utility functions (camera, QR, etc.)
│── data/               # Auto-created: users, attendance, photos
│── requirements.txt    # Dependencies
│── README.md

🛠 Features

✅ User Registration with photo
✅ Secure Login
✅ Attendance upload with photo + location
✅ QR Code scan for shift management
✅ Admin dashboard for monitoring

👉 To stop the app, just close the window or press CTRL+C in CMD.