import os
import time
import shutil
import cv2
from PIL import Image, ImageTk
import qrcode
from tkinter import Toplevel, Label
from app.utils.storage import PHOTO_DIR, QR_DIR

def _timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

def capture_photo_from_webcam(user_id):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Webcam not available.")
    cv2.namedWindow("Press SPACE to capture, ESC to cancel")
    img_path = None
    while True:
        ret, frame = cam.read()
        if not ret:
            continue
        cv2.imshow("Press SPACE to capture, ESC to cancel", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:  # ESC
            break
        if k == 32:  # SPACE
            filename = f"{user_id}_{_timestamp()}.jpg"
            img_path = os.path.join(PHOTO_DIR, filename)
            cv2.imwrite(img_path, frame)
            break
    cam.release()
    cv2.destroyAllWindows()
    if not img_path:
        raise RuntimeError("Capture cancelled.")
    return img_path

def save_uploaded_photo(user_id, src_path):
    filename = f"{user_id}_{_timestamp()}_{os.path.basename(src_path)}"
    dst = os.path.join(PHOTO_DIR, filename)
    shutil.copy2(src_path, dst)
    return dst

def scan_qr_with_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Webcam not available.")
    detector = cv2.QRCodeDetector()
    cv2.namedWindow("Scan QR (Press ESC to cancel)")
    payload = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        data, points, _ = detector.detectAndDecode(frame)
        if points is not None and data:
            payload = data
            cv2.polylines(frame, [points.astype(int)], True, (0, 255, 0), 2)
            cv2.putText(frame, "QR detected!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Scan QR (Press ESC to cancel)", frame)
            cv2.waitKey(800)
            break
        cv2.imshow("Scan QR (Press ESC to cancel)", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    return payload

def ensure_sample_qr_images():
    """
    Create sample QR images for start/end if they don't exist.
    """
    os.makedirs(QR_DIR, exist_ok=True)
    start_png = os.path.join(QR_DIR, "sample_qr_start.png")
    end_png = os.path.join(QR_DIR, "sample_qr_end.png")
    if not os.path.exists(start_png):
        img = qrcode.make("QR_START")
        img.save(start_png)
    if not os.path.exists(end_png):
        img = qrcode.make("QR_END")
        img.save(end_png)

def show_sample_qr_window(root):
    """
    Popup to display both sample QR codes.
    """
    ensure_sample_qr_images()
    win = Toplevel(root)
    win.title("Sample QR Codes")
    win.geometry("720x400")

    start_img = Image.open(os.path.join(QR_DIR, "sample_qr_start.png")).resize((320, 320))
    end_img = Image.open(os.path.join(QR_DIR, "sample_qr_end.png")).resize((320, 320))
    start_tk = ImageTk.PhotoImage(start_img)
    end_tk = ImageTk.PhotoImage(end_img)

    Label(win, text="Start Shift (scan this):", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, pady=(10, 4))
    Label(win, text="End Shift (scan this):", font=("Segoe UI", 12, "bold")).grid(row=0, column=1, pady=(10, 4))
    Label(win, image=start_tk).grid(row=1, column=0, padx=10, pady=10)
    Label(win, image=end_tk).grid(row=1, column=1, padx=10, pady=10)

    # keep references
    win.start_tk = start_tk
    win.end_tk = end_tk
