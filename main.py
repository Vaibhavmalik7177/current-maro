import os
import sys
import time
import threading
import psutil
import requests
import tkinter as tk
from tkinter import messagebox, ttk

# System Configurations
ESP32_IP = "192.168.1.50"  # Update with your ESP32 local IP address
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts" if sys.platform == "win32" else "/etc/hosts"
REDIRECT_IP = "127.0.0.1"

# App State Data
app_data = {
    "blocked_websites": ["instagram.com", "facebook.com"],
    "apps": [
        {"name": "Instagram", "process": "instagram.exe", "limit_mins": 15, "used_secs": 450, "category": "Social"},
        {"name": "YouTube", "process": "chrome.exe", "limit_mins": 30, "used_secs": 2100, "category": "Video"},
        {"name": "Gaming", "process": "gta5.exe", "limit_mins": 60, "used_secs": 2100, "category": "Entertainment"},
        {"name": "Other apps", "process": "vlc.exe", "limit_mins": 120, "used_secs": 3840, "category": "Everything else"}
    ]
}

def trigger_esp32(state):
    try:
        requests.get(f"http://{ESP32_IP}/{state}", timeout=1)
    except Exception:
        pass  # Failsafe if ESP32 is offline

def block_websites_system():
    """Modifies local hosts file to block unwanted domain resolution."""
    try:
        with open(HOSTS_PATH, "r+") as file:
            content = file.read()
            for site in app_data["blocked_websites"]:
                entry = f"{REDIRECT_IP} {site}\n"
                if site not in content:
                    file.write(entry)
    except PermissionError:
        pass  # Requires Admin/Sudo privileges to write to hosts file

class FocusBandDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FocusBand — Your digital discipline companion")
        self.root.geometry("900x660")
        self.root.config(bg="#0b0d14")
        
        self.is_monitoring = True
        
        # Build UI layout
        self.create_sidebar()
        self.create_main_content()
        
        # Start background monitor thread
        self.thread = threading.Thread(target=self.background_monitor_loop, daemon=True)
        self.thread.start()

    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#0f111a", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        logo = tk.Label(sidebar, text="☷  focusband", font=("Arial", 12, "bold"), fg="#ffffff", bg="#0f111a")
        logo.pack(anchor="w", padx=20, pady=25)
        
        tk.Label(sidebar, text="Overview", font=("Arial", 11), fg="#ffffff", bg="#1c1f33", padx=12, pady=8).pack(fill=tk.X, padx=10, pady=2)
        tk.Label(sidebar, text="My app limits", font=("Arial", 11), fg="#7d84a6", bg="#0f111a", padx=12, pady=8).pack(fill=tk.X, padx=10, pady=2)
        tk.Label(sidebar, text="Insights", font=("Arial", 11), fg="#7d84a6", bg="#0f111a", padx=12, pady=8).pack(fill=tk.X, padx=10, pady=2)
        
        # Wristband status card at bottom
        wrist_card = tk.Frame(sidebar, bg="#141724", padx=12, pady=12)
        wrist_card.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=20)
        
        status_row = tk.Frame(wrist_card, bg="#141724")
        status_row.pack(anchor="w")
        
        canvas = tk.Canvas(status_row, width=10, height=10, bg="#141724", highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=(0, 6))
        canvas.create_oval(2, 2, 8, 8, fill="#10b981", outline="")
        
        tk.Label(status_row, text="Connected", font=("Arial", 10, "bold"), fg="#ffffff", bg="#141724").pack(side=tk.LEFT)
        tk.Label(wrist_card, text="FocusBand One — Hardware active", font=("Arial", 9), fg="#646b8f", bg="#141724").pack(anchor="w", pady=(4, 0))

    def create_main_content(self):
        content = tk.Frame(self.root, bg="#0b0d14")
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        tk.Label(content, text="Good afternoon, User ✨", font=("Arial", 18, "bold"), fg="#ffffff", bg="#0b0d14").pack(anchor="w")
        tk.Label(content, text="Every intentional minute is a win.", font=("Arial", 10), fg="#646b8f", bg="#0b0d14").pack(anchor="w", pady=(2, 15))
        
        # Metric Cards
        metrics_frame = tk.Frame(content, bg="#0b0d14")
        metrics_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_card(metrics_frame, "SCREEN TIME TODAY", "3h 39m", "#ffffff", 0)
        self.create_card(metrics_frame, "FOCUS SCORE", "75 /100", "#34d399", 1)
        self.create_card(metrics_frame, "YOUR FOCUSBAND", "Ready when you are", "#34d399", 2)
        
        # App Limits Section
        tk.Label(content, text="Your app limits", font=("Arial", 12, "bold"), fg="#ffffff", bg="#0b0d14").pack(anchor="w", pady=(10, 10))
        
        self.apps_container = tk.Frame(content, bg="#0b0d14")
        self.apps_container.pack(fill=tk.X)
        self.refresh_app_ui()

        # Website Blocker Input Section (User interactive block input)
        block_frame = tk.Frame(content, bg="#121522", padx=15, pady=15)
        block_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(block_frame, text="Block Unwanted Websites", font=("Arial", 11, "bold"), fg="#ffffff", bg="#121522").pack(anchor="w")
        tk.Label(block_frame, text="Type a website domain below to block it instantly system-wide", font=("Arial", 9), fg="#646b8f", bg="#121522").pack(anchor="w", pady=(2, 8))
        
        input_row = tk.Frame(block_frame, bg="#121522")
        input_row.pack(fill=tk.X)
        
        self.site_entry = tk.Entry(input_row, font=("Arial", 10), bg="#0b0d14", fg="#ffffff", insertbackground="white", relief="flat")
        self.site_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        
        add_btn = tk.Button(input_row, text="Add Domain Block", font=("Arial", 10, "bold"), bg="#6366f1", fg="#ffffff", relief="flat", padx=12, command=self.add_website)
        add_btn.pack(side=tk.RIGHT)
        
        # Dynamic Tags Frame for Blocked Websites
        self.tags_frame = tk.Frame(block_frame, bg="#121522")
        self.tags_frame.pack(anchor="w", pady=(10, 0))
        self.refresh_website_tags()

    def create_card(self, parent, title, value, val_color, col_idx):
        card = tk.Frame(parent, bg="#121522", padx=15, pady=15, width=220)
        card.grid(row=0, column=col_idx, padx=(0, 15), sticky="nsew")
        parent.grid_columnconfigure(col_idx, weight=1)
        
        tk.Label(card, text=title, font=("Arial", 9, "bold"), fg="#646b8f", bg="#121522").pack(anchor="w")
        tk.Label(card, text=value, font=("Arial", 16, "bold"), fg=val_color, bg="#121522").pack(anchor="w", pady=(8, 0))

    def refresh_app_ui(self):
        for widget in self.apps_container.winfo_children():
            widget.destroy()
            
        for idx, item in enumerate(app_data["apps"]):
            row = tk.Frame(self.apps_container, bg="#121522", padx=12, pady=10)
            row.pack(fill=tk.X, pady=4)
            
            info_frame = tk.Frame(row, bg="#121522", width=130)
            info_frame.pack(side=tk.LEFT, anchor="w")
            tk.Label(info_frame, text=item["name"], font=("Arial", 10, "bold"), fg="#ffffff", bg="#121522").pack(anchor="w")
            tk.Label(info_frame, text=item["category"], font=("Arial", 8), fg="#646b8f", bg="#121522").pack(anchor="w")
            
            used_mins = int(item["used_secs"] // 60)
            tk.Label(row, text=f"{used_mins}m used", font=("Arial", 9), fg="#a3a8c3", bg="#121522", width=10).pack(side=tk.LEFT, padx=10)
            
            canvas_bar = tk.Canvas(row, height=6, bg="#1c2035", highlightthickness=0)
            canvas_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15)
            
            limit_secs = item["limit_mins"] * 60
            pct = min(1.0, item["used_secs"] / limit_secs) if limit_secs > 0 else 0
            bar_colors = ["#ec4899", "#f43f5e", "#6366f1", "#06b6d4"]
            chosen_color = bar_colors[idx % len(bar_colors)]
            
            canvas_bar.update()
            width = canvas_bar.winfo_width() or 180
            canvas_bar.create_rectangle(0, 0, width * pct, 6, fill=chosen_color, outline="")
            
            limit_box = tk.Frame(row, bg="#121522")
            limit_box.pack(side=tk.RIGHT)
            
            # Spinbox to allow users to change app time limits interactively
            spin = tk.Spinbox(limit_box, from_=1, to=300, width=4, font=("Arial", 10), justify="center", bg="#0b0d14", fg="#ffffff", relief="flat", command=lambda i=item, s=spin: self.update_limit(i, s))
            spin.delete(0, "end")
            spin.insert(0, str(item["limit_mins"]))
            spin.pack(side=tk.LEFT, padx=(0, 4))
            
            tk.Label(limit_box, text="min", font=("Arial", 9), fg="#a3a8c3", bg="#121522").pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(limit_box, text="On track", font=("Arial", 8, "bold"), fg="#34d399", bg="#064e3b", padx=6, pady=2).pack(side=tk.LEFT)

    def update_limit(self, item, spinbox):
        try:
            item["limit_mins"] = int(spinbox.get())
        except ValueError:
            pass

    def refresh_website_tags(self):
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
            
        for site in app_data["blocked_websites"]:
            tag = tk.Label(self.tags_frame, text=f"🔒 {site}", font=("Arial", 9), fg="#a3a8c3", bg="#1c2035", padx=8, pady=3)
            tag.pack(side=tk.LEFT, padx=(0, 6))

    def add_website(self):
        site = self.site_entry.get().strip().lower()
        if site and site not in app_data["blocked_websites"]:
            app_data["blocked_websites"].append(site)
            block_websites_system()
            self.refresh_website_tags()
            self.site_entry.delete(0, tk.END)

    def background_monitor_loop(self):
        block_websites_system()
        while self.is_monitoring:
            over_limit = False
            try:
                running_procs = [p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info['name']]
                
                for item in app_data["apps"]:
                    if item["process"].lower() in running_procs:
                        item["used_secs"] += 2
                        if (item["used_secs"] / 60) >= item["limit_mins"]:
                            over_limit = True
            except Exception:
                pass

            trigger_esp32("on" if over_limit else "off")
            time.sleep(2)

if __name__ == "__main__":
    root = tk.Tk()
    app = FocusBandDesktopApp(root)
    root.mainloop()