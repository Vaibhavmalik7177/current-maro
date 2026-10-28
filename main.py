import threading
import time
import tkinter as tk 
from tkinter import messagebox
import requests
import psutil

# Configuration
ESP32_IP = ""  #IP OF ESP32
UNWANTED_APP = []
MAX_TIME= 60 # Maximum time (in seconds)

class FocusMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard")
        self.root.geometry("450x350")

        self.elapsed_time = 0
        self.is_running = False
        self.light_status = "OFF"

        #UI
        title_label = tk.Label(root, text="Focus Monitor", font=("Arial", 18,"bold"),fg="#ffffff",bg="#1e1e1e")
        title_label.pack(pady=15)

        self.status_label = tk.Label(root, text="Status: Not Monitoring", font=("Arial", 12), fg="#ffffff", bg="#1e1e1e")
        self.status_label.pack(pady=5)

        self.time_label = tk.Label(root, text="Time spent on distractions: 0 seconds", font=("Arial", 12), fg="#ffffff", bg="#1e1e1e")
        self.time_label.pack(pady=5)

        self.light_table = tk.Label(root, text="Light Status: OFF", font=("Arial", 14), fg="#ffffff", bg="#1e1e1e")
        self.light_table.pack(pady=15)

        self.start_btn = tk.Button(root, text="Start Monitoring", command=self.start_monitoring, font=("Arial", 12), bg="#4CAF50", fg="#ffffff")
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, font=("Arial", 12), bg="#f44336", fg="#ffffff")
        self.stop_btn.pack(pady=5)
    def trigger_esp32(self, state):
        try:
            requests.get(f"http://{ESP32_IP}/{state}", timeout=1)
            self.light_status = state.upper()
            self.light_table.config(text=f"Light Status: {self.light_status}",fg=color)
            color = "#2ecc71" if state == "off" else "#e74c3c"
        except requests.exceptions.RequestException:
            pass # Silent Exist 
