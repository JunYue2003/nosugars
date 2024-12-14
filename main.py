import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import logging
import time
import sys
import json
from datetime import datetime
import pytz
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageTk

# 日誌設置
logging.basicConfig(
    filename="noip_updater.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 配置檔案名稱
CONFIG_FILE = "noip_config.json"
ICON_FILE = "icon.png"  # 托盤圖標文件
BG_IMAGE_FILE = "background.png"  # 背景圖片文件


class NoIPUpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("No-IP 自動更新工具")
        self.root.geometry("1100x700")  # 預設視窗大小
        self.root.minsize(850, 500)  # 設定視窗最小大小

        # 設置按鈕樣式
        self.set_styles()

        # 設置圖示
        self.set_icon()

        # 初始化變數
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.update_interval = tk.IntVar(value=300)
        self.domains = []
        self.update_event = threading.Event()
        self.threads = []
        self.tray_icon = None

        # 添加背景圖片
        self.set_background()

        # 創建界面
        self.create_widgets()
        # 加載配置
        self.load_config()

        # 綁定事件，處理視窗大小調整
        self.root.bind("<Configure>", self.resize_background)

        # 綁定關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        # 初始調整背景圖片
        self.resize_background()

    def set_styles(self):
        """設置按鈕樣式"""
        style = ttk.Style()
        style.theme_use("clam")  # 確保使用支持樣式配置的主題

        # 按鈕默認樣式
        style.configure(
            "Custom.TButton",
            font=("Arial", 12, "bold"),
            foreground="white",  # 按鈕文字顏色
            background="#ADD8E6",  # 淡藍色按鈕背景色
            padding=(10, 5),  # 按鈕內間距
            borderwidth=1,  # 按鈕邊框寬度
            relief="flat",
        )

        # 鼠標懸停效果
        style.map(
            "Custom.TButton",
            background=[
                ("active", "#5A7BED")  # 懸停背景顏色 (深藍色)
            ],
            foreground=[
                ("active", "white"),  # 懸停文字顏色 (白色)
            ],
        )

    def set_icon(self):
        """設置工作列和左上角圖標"""
        try:
            icon_image = Image.open(ICON_FILE)
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(False, icon_photo)
        except FileNotFoundError:
            messagebox.showerror("錯誤", f"找不到圖標文件：{ICON_FILE}")
            sys.exit()

    def set_background(self):
        """設置背景圖片"""
        try:
            self.bg_image = Image.open(BG_IMAGE_FILE)
            self.canvas = tk.Canvas(self.root, highlightthickness=0, bg="#2B2B2B")
            self.canvas.pack(fill="both", expand=True)
            self.bg_canvas_image = self.canvas.create_image(0, 0, anchor="nw")
        except FileNotFoundError:
            messagebox.showerror("錯誤", f"找不到背景圖片文件：{BG_IMAGE_FILE}")
            sys.exit()

    def resize_background(self, event=None):
        """根據視窗大小調整背景圖片"""
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        resized_image = self.bg_image.resize((new_width, new_height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        self.canvas.itemconfig(self.bg_canvas_image, image=self.bg_photo)
        self.canvas.config(width=new_width, height=new_height)

    def create_widgets(self):
        """創建界面"""
        # 頂部功能按鈕區域
        button_frame = tk.Frame(self.root, bg="#2B2B2B")  # 深灰色背景
        button_frame.place(relx=0.02, rely=0.02, relwidth=0.46, relheight=0.2)

        # 程式說明文字
        tk.Label(
            button_frame,
            text="本程式用於自動更新 No-IP 域名，並顯示運行日誌。",
            font=("Arial", 10),
            fg="white",
            bg="#2B2B2B",
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        # 按鈕區域
        self.start_button = ttk.Button(button_frame, text="啟動", command=self.start_updating, style="Custom.TButton")
        self.start_button.grid(row=1, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_updating, state=tk.DISABLED, style="Custom.TButton")
        self.stop_button.grid(row=1, column=1, padx=10, pady=10)

        self.exit_button = ttk.Button(button_frame, text="退出", command=self.exit_app, style="Custom.TButton")
        self.exit_button.grid(row=1, column=2, padx=10, pady=10)

        # 左側輸入區域
        input_frame = tk.Frame(self.root, bg="#2B2B2B")  # 深灰色背景
        input_frame.place(relx=0.02, rely=0.25, relwidth=0.46, relheight=0.67)

        tk.Label(input_frame, text="使用者名稱：", anchor="w", font=("Arial", 10), fg="white", bg="#2B2B2B").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        self.username_entry = ttk.Entry(input_frame, textvariable=self.username, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="密碼：", anchor="w", font=("Arial", 10), fg="white", bg="#2B2B2B").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.password_entry = ttk.Entry(input_frame, textvariable=self.password, show="*", width=30)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="更新間隔(秒)：", anchor="w", font=("Arial", 10), fg="white", bg="#2B2B2B").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.interval_entry = ttk.Entry(input_frame, textvariable=self.update_interval, width=30)
        self.interval_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="域名：", anchor="w", font=("Arial", 10), fg="white", bg="#2B2B2B").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.domain_entry = ttk.Entry(input_frame, width=30)
        self.domain_entry.grid(row=3, column=1, padx=10, pady=5)
        self.domain_entry.bind("<Return>", lambda event: self.add_domain())

        self.add_domain_button = ttk.Button(input_frame, text="添加域名", command=self.add_domain, style="Custom.TButton")
        self.add_domain_button.grid(row=3, column=2, padx=10, pady=5)

        self.domain_listbox = tk.Listbox(input_frame, height=10, width=40, bg="#2B2B2B", fg="white")
        self.domain_listbox.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.remove_domain_button = ttk.Button(input_frame, text="刪除選中域名", command=self.remove_domain, style="Custom.TButton")
        self.remove_domain_button.grid(row=5, column=0, columnspan=3, pady=10)

        # 日誌顯示區域
        log_frame = tk.Frame(self.root, bg="#2B2B2B")
        log_frame.place(relx=0.5, rely=0.02, relwidth=0.46, relheight=0.9)

        tk.Label(log_frame, text="運行日誌", font=("Arial", 12, "bold"), fg="white", bg="#2B2B2B").pack(pady=10)
        self.log_text = tk.Text(log_frame, state=tk.DISABLED, wrap="word", bg="#2B2B2B", fg="white", font=("Arial", 10))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    def add_domain(self):
        domain = self.domain_entry.get().strip()
        if domain and domain not in self.domains:
            self.domains.append(domain)
            self.domain_listbox.insert(tk.END, domain)
            self.domain_entry.delete(0, tk.END)
            self.save_config()

    def remove_domain(self):
        selected = self.domain_listbox.curselection()
        if selected:
            domain = self.domain_listbox.get(selected[0])
            self.domains.remove(domain)
            self.domain_listbox.delete(selected[0])
            self.save_config()

    def log_message(self, message):
        pst_time = datetime.now(pytz.timezone("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M:%S PST")
        log_entry = f"[{pst_time}] {message}"
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_updating(self):
        if not self.username.get() or not self.password.get():
            messagebox.showerror("錯誤", "請填寫使用者名稱和密碼")
            return
        if not self.domains:
            messagebox.showerror("錯誤", "請添加至少一個域名")
            return

        self.update_event.set()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        for domain in self.domains:
            thread = threading.Thread(target=self.update_noip, args=(domain,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def stop_updating(self):
        self.update_event.clear()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_noip(self, domain):
        while self.update_event.is_set():
            try:
                url = f"https://dynupdate.no-ip.com/nic/update"
                auth = (self.username.get(), self.password.get())
                params = {"hostname": domain}
                response = requests.get(url, params=params, auth=auth, timeout=10)
                if response.status_code == 200:
                    message = f"[{domain}] 更新成功: {response.text}"
                else:
                    message = f"[{domain}] 更新失敗，狀態碼: {response.status_code}, 響應: {response.text}"
                self.log_message(message)
            except requests.RequestException as e:
                self.log_message(f"[{domain}] 更新錯誤: {e}")
            time.sleep(self.update_interval.get())

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.username.set(config.get("username", ""))
                self.password.set(config.get("password", ""))
                self.domains = config.get("domains", [])
                for domain in self.domains:
                    self.domain_listbox.insert(tk.END, domain)
        except FileNotFoundError:
            pass

    def save_config(self):
        config = {
            "username": self.username.get(),
            "password": self.password.get(),
            "domains": self.domains,
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    def hide_to_tray(self):
        self.root.withdraw()
        self.create_tray_icon()

    def create_tray_icon(self):
        try:
            image = Image.open(ICON_FILE)
        except FileNotFoundError:
            messagebox.showerror("錯誤", f"找不到圖標文件：{ICON_FILE}")
            sys.exit()

        self.tray_icon = Icon(
            "NoIPUpdater",
            image,
            menu=Menu(
                MenuItem("顯示窗口", lambda: self.show_window()),
                MenuItem("退出", lambda: self.exit_app()),
            ),
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.root.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def exit_app(self):
        self.stop_updating()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    app = NoIPUpdaterApp(root)
    root.mainloop()
