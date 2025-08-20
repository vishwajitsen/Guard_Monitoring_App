import hashlib
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from app.ui.theme import setup_style
from app.utils.storage import (
    init_storage, add_user, get_user, add_attendance, query_attendance
)
from app.utils.camera import (
    capture_photo_from_webcam, save_uploaded_photo, scan_qr_with_webcam,
    ensure_sample_qr_images, show_sample_qr_window
)
from app.utils.geo import get_current_location, reverse_geocode, to_plus_code


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class GuardApp(tb.Window):
    def __init__(self):
        # Apply base theme; style details added in setup_style()
        super().__init__(themename="flatly")
        setup_style(self)
        self.title("Guard Monitoring App")
        self.geometry("1100x800")
        self.resizable(True, True)

        init_storage()
        ensure_sample_qr_images()

        self.show_start()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ---------------- Start Screen ----------------
    def show_start(self):
        self.clear()

        # Hero header (deep maroon)
        hero = tb.Frame(self, padding=28, style="Hero.TFrame")
        hero.pack(fill=X)
        tb.Label(
            hero,
            text="Guard Monitoring App",
            style="HeroTitle.TLabel",
        ).pack(anchor="center")
        tb.Label(
            hero,
            text="Bold, simple tracking of guard registration, attendance, photos, locations & QR scans (to Excel).",
            style="HeroSub.TLabel",
        ).pack(anchor="center", pady=(6, 0))

        # Button panel
        panel = tb.Frame(self, padding=30)
        panel.pack(expand=True)

        tb.Button(
            panel, text="Login", bootstyle=PRIMARY, width=26,
            style="Big.TButton", command=self.show_login
        ).grid(row=0, column=0, padx=14, pady=14)

        tb.Button(
            panel, text="Register", bootstyle=SUCCESS, width=26,
            style="Big.TButton", command=self.show_register
        ).grid(row=0, column=1, padx=14, pady=14)

        tb.Button(
            panel, text="Admin Dashboard", bootstyle=INFO, width=26,
            style="Big.TButton", command=self.show_admin
        ).grid(row=1, column=0, columnspan=2, padx=14, pady=14)

        tb.Button(
            panel, text="View Sample QR Codes", bootstyle=SECONDARY, width=26,
            style="Big.TButton", command=self.open_sample_qr
        ).grid(row=2, column=0, columnspan=2, padx=14, pady=(6, 10))

        tb.Label(
            self,
            text="Tip: set GOOGLE_MAPS_API_KEY for precise addresses (falls back to OpenStreetMap automatically).",
            style="Footer.TLabel",
        ).pack(pady=(0, 12))

    # ---------------- Register ----------------
    def show_register(self):
        self.clear()
        frame = tb.Frame(self, padding=30)
        frame.pack(expand=True, fill=BOTH)

        tb.Label(frame, text="Register Guard", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 22)
        )

        tb.Label(frame, text="User ID (phone or email):", style="FieldLabel.TLabel").grid(row=1, column=0, sticky=E, pady=6, padx=6)
        self.reg_user = tb.Entry(frame, width=46)
        self.reg_user.grid(row=1, column=1, sticky=W, pady=6, padx=6)

        tb.Label(frame, text="Full Name:", style="FieldLabel.TLabel").grid(row=2, column=0, sticky=E, pady=6, padx=6)
        self.reg_name = tb.Entry(frame, width=46)
        self.reg_name.grid(row=2, column=1, sticky=W, pady=6, padx=6)

        tb.Label(frame, text="Phone:", style="FieldLabel.TLabel").grid(row=3, column=0, sticky=E, pady=6, padx=6)
        self.reg_phone = tb.Entry(frame, width=46)
        self.reg_phone.grid(row=3, column=1, sticky=W, pady=6, padx=6)

        tb.Label(frame, text="Email:", style="FieldLabel.TLabel").grid(row=4, column=0, sticky=E, pady=6, padx=6)
        self.reg_email = tb.Entry(frame, width=46)
        self.reg_email.grid(row=4, column=1, sticky=W, pady=6, padx=6)

        tb.Label(frame, text="Password:", style="FieldLabel.TLabel").grid(row=5, column=0, sticky=E, pady=6, padx=6)
        self.reg_pass = tb.Entry(frame, width=46, show="*")
        self.reg_pass.grid(row=5, column=1, sticky=W, pady=6, padx=6)

        self.photo_path = tb.StringVar(value="")

        def upload_photo():
            path = filedialog.askopenfilename(
                title="Choose Photo", filetypes=[("Image", "*.jpg *.jpeg *.png")]
            )
            if path:
                self.photo_path.set(path)

        tb.Button(frame, text="Upload Photo", bootstyle=SECONDARY, command=upload_photo).grid(
            row=6, column=0, sticky=E, pady=6, padx=6
        )
        tb.Label(frame, textvariable=self.photo_path, style="Hint.TLabel").grid(
            row=6, column=1, sticky=W, pady=6, padx=6
        )

        def do_register():
            user_id = self.reg_user.get().strip()
            name = self.reg_name.get().strip()
            phone = self.reg_phone.get().strip()
            email = self.reg_email.get().strip()
            password = self.reg_pass.get().strip()

            if not (user_id and password):
                messagebox.showerror("Error", "User ID and Password are required")
                return

            try:
                saved_photo = ""
                if self.photo_path.get():
                    saved_photo = save_uploaded_photo(user_id, self.photo_path.get())

                # Always store strings; hash the password
                add_user(
                    str(user_id), str(name), str(phone), str(email),
                    sha256(password), str(saved_photo)
                )
                messagebox.showinfo("Success", "Registered successfully!")
                self.show_start()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tb.Button(
            frame, text="Register", bootstyle=SUCCESS, width=20,
            style="Big.TButton", command=do_register
        ).grid(row=7, column=0, pady=22)
        tb.Button(
            frame, text="Back", bootstyle=SECONDARY, width=20,
            command=self.show_start
        ).grid(row=7, column=1, pady=22, sticky=W)

    # ---------------- Login ----------------
    def show_login(self):
        self.clear()
        frame = tb.Frame(self, padding=30)
        frame.pack(expand=True, fill=BOTH)

        tb.Label(frame, text="Guard Login", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 22)
        )

        tb.Label(frame, text="User ID (phone or email):", style="FieldLabel.TLabel").grid(row=1, column=0, sticky=E, pady=6, padx=6)
        self.log_user = tb.Entry(frame, width=46)
        self.log_user.grid(row=1, column=1, sticky=W, pady=6, padx=6)

        tb.Label(frame, text="Password:", style="FieldLabel.TLabel").grid(row=2, column=0, sticky=E, pady=6, padx=6)
        self.log_pass = tb.Entry(frame, width=46, show="*")
        self.log_pass.grid(row=2, column=1, sticky=W, pady=6, padx=6)

        def do_login():
            user_id = self.log_user.get().strip()
            password = self.log_pass.get().strip()
            user = get_user(user_id)  # now robust to Excel numeric formatting
            if not user or str(user.get("password_hash")) != sha256(password):
                messagebox.showerror("Error", "Invalid credentials")
                return
            self.current_user = user
            self.show_guard_dashboard()

        tb.Button(
            frame, text="Login", bootstyle=PRIMARY, width=20,
            style="Big.TButton", command=do_login
        ).grid(row=3, column=0, pady=22)
        tb.Button(
            frame, text="Back", bootstyle=SECONDARY, width=20,
            command=self.show_start
        ).grid(row=3, column=1, pady=22, sticky=W)

    # ---------------- Guard Dashboard ----------------
    def show_guard_dashboard(self):
        self.clear()
        user_id = self.current_user["user_id"]

        banner = tb.Frame(self, padding=20, style="Hero.TFrame")
        banner.pack(fill=X)
        tb.Label(
            banner,
            text=f"Welcome, {self.current_user.get('name') or user_id}",
            style="HeroTitle.TLabel",
        ).pack(anchor="w")

        frame = tb.Frame(self, padding=18)
        frame.pack(expand=True, fill=BOTH)

        btns = tb.Frame(frame)
        btns.pack(pady=8)

        tb.Button(
            btns, text="Selfie + Location (Login Photo)", bootstyle=SUCCESS,
            width=30, style="Big.TButton", command=self.capture_login_photo
        ).grid(row=0, column=0, padx=12, pady=12)

        tb.Button(
            btns, text="Scan QR (Start Shift)", bootstyle=PRIMARY,
            width=30, style="Big.TButton", command=lambda: self.scan_qr("QR_START")
        ).grid(row=0, column=1, padx=12, pady=12)

        tb.Button(
            btns, text="Scan QR (End Shift)", bootstyle=DANGER,
            width=30, style="Big.TButton", command=lambda: self.scan_qr("QR_END")
        ).grid(row=0, column=2, padx=12, pady=12)

        tb.Button(self, text="View Sample QR Codes", bootstyle=SECONDARY,
                  style="Big.TButton", command=self.open_sample_qr).pack(pady=8)
        tb.Button(self, text="Logout", bootstyle=SECONDARY,
                  command=self.show_start).pack(pady=4)

    def open_sample_qr(self):
        show_sample_qr_window(self)

    def capture_login_photo(self):
        user_id = self.current_user["user_id"]
        choice = messagebox.askyesno("Photo", "Use webcam? (Yes = Webcam, No = Upload file)")
        saved_photo = None
        try:
            if choice:
                saved_photo = capture_photo_from_webcam(user_id)
            else:
                path = filedialog.askopenfilename(
                    title="Choose Photo", filetypes=[("Image", "*.jpg *.jpeg *.png")]
                )
                if not path:
                    return
                saved_photo = save_uploaded_photo(user_id, path)
        except Exception as e:
            messagebox.showerror("Error", f"Photo capture failed: {e}")
            return

        lat, lon, source = get_current_location()
        if source == "manual":
            from tkinter import simpledialog
            lat = simpledialog.askstring("Location", "Enter Latitude:") or ""
            lon = simpledialog.askstring("Location", "Enter Longitude:") or ""

        address, pincode = reverse_geocode(lat, lon)
        plus_code = to_plus_code(lat, lon)

        add_attendance(
            user_id=str(user_id),
            latitude=str(lat), longitude=str(lon),
            address=str(address), pincode=str(pincode), plus_code=str(plus_code),
            photo_path=str(saved_photo),
            action="LOGIN_PHOTO",
            location_source=str(source)
        )
        messagebox.showinfo("Saved", "Login photo + location saved to Excel.")

    def scan_qr(self, action):
        user_id = self.current_user["user_id"]
        try:
            payload = scan_qr_with_webcam()
        except Exception as e:
            messagebox.showerror("Error", f"QR scan failed: {e}")
            return
        if not payload:
            messagebox.showwarning("Cancelled", "QR scan cancelled or not detected.")
            return

        lat, lon, source = get_current_location()
        if source == "manual":
            from tkinter import simpledialog
            lat = simpledialog.askstring("Location", "Enter Latitude:") or ""
            lon = simpledialog.askstring("Location", "Enter Longitude:") or ""

        address, pincode = reverse_geocode(lat, lon)
        plus_code = to_plus_code(lat, lon)

        add_attendance(
            user_id=str(user_id),
            latitude=str(lat), longitude=str(lon),
            address=str(address), pincode=str(pincode), plus_code=str(plus_code),
            photo_path="",
            action=str(action),
            location_source=str(source),
            qr_payload=str(payload)
        )
        messagebox.showinfo("Recorded", f"{action.replace('_',' ')} recorded.\nQR: {payload}\n{address or ''}")

    # ---------------- Admin Dashboard ----------------
    def show_admin(self):
        self.clear()
        frame = tb.Frame(self, padding=15)
        frame.pack(expand=True, fill=BOTH)

        tb.Label(frame, text="Admin Dashboard", style="SectionTitle.TLabel").pack(pady=4)

        # Filters
        filters = tb.Labelframe(frame, text="Filters", padding=10)
        filters.pack(fill=X, padx=5, pady=5)

        self.f_user = tb.Entry(filters, width=25)
        self.f_user.insert(0, "")
        self.f_from = tb.Entry(filters, width=22)
        self.f_to = tb.Entry(filters, width=22)

        tb.Label(filters, text="User ID contains:", style="FieldLabel.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.f_user.grid(row=0, column=1, padx=5, pady=5)
        tb.Label(filters, text="Date from (YYYY-MM-DD HH:MM:SS):", style="FieldLabel.TLabel").grid(row=0, column=2, padx=5, pady=5, sticky=E)
        self.f_from.grid(row=0, column=3, padx=5, pady=5)
        tb.Label(filters, text="Date to (YYYY-MM-DD HH:MM:SS):", style="FieldLabel.TLabel").grid(row=0, column=4, padx=5, pady=5, sticky=E)
        self.f_to.grid(row=0, column=5, padx=5, pady=5)

        self.action_var = tb.StringVar(value="")
        tb.Label(filters, text="Action:", style="FieldLabel.TLabel").grid(row=0, column=6, padx=5, pady=5, sticky=E)
        tb.Combobox(filters, textvariable=self.action_var, values=["", "LOGIN_PHOTO", "QR_START", "QR_END"], width=16).grid(row=0, column=7, padx=5, pady=5)

        btn_row = tb.Frame(filters)
        btn_row.grid(row=0, column=8, padx=5, pady=5)
        tb.Button(btn_row, text="Apply", bootstyle=PRIMARY, command=self.refresh_table).pack(side=LEFT, padx=3)
        tb.Button(btn_row, text="Reset", bootstyle=SECONDARY, command=self.reset_filters).pack(side=LEFT, padx=3)
        tb.Button(btn_row, text="Export Filtered", bootstyle=SUCCESS, command=self.export_filtered).pack(side=LEFT, padx=3)

        # Table
        table_frame = tb.Frame(frame)
        table_frame.pack(expand=True, fill=BOTH, padx=5, pady=5)

        cols = [
            "record_id","user_id","timestamp",
            "latitude","longitude","address","pincode","plus_code",
            "photo_path","action","location_source","qr_payload"
        ]
        self.tree = tb.Treeview(table_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140 if c in ("address",) else 120, anchor="w")
        self.tree.pack(expand=True, fill=BOTH)

        self.refresh_table()
        tb.Button(frame, text="Back", bootstyle=SECONDARY, command=self.show_start).pack(pady=8)

    def reset_filters(self):
        self.f_user.delete(0, "end")
        self.f_from.delete(0, "end")
        self.f_to.delete(0, "end")
        self.action_var.set("")
        self.refresh_table()

    def refresh_table(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        user = self.f_user.get().strip() if hasattr(self, 'f_user') else ""
        date_from = self.f_from.get().strip() if hasattr(self, 'f_from') and self.f_from.get().strip() else None
        date_to = self.f_to.get().strip() if hasattr(self, 'f_to') and self.f_to.get().strip() else None
        action = self.action_var.get() if hasattr(self, 'action_var') else None
        df = query_attendance(user_id=user or None, date_from=date_from, date_to=date_to, action=action or None)
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=[row[c] for c in self.tree.cget("columns")])

    def export_filtered(self):
        from tkinter import filedialog
        user = self.f_user.get().strip() or None
        date_from = self.f_from.get().strip() or None
        date_to = self.f_to.get().strip() or None
        action = self.action_var.get() or None
        df = query_attendance(user_id=user, date_from=date_from, date_to=date_to, action=action)
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], title="Export to Excel")
        if not path:
            return
        try:
            df.to_excel(path, index=False)
            messagebox.showinfo("Exported", f"Saved {len(df)} rows to\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = GuardApp()
    app.mainloop()
