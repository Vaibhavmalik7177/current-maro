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
        title_label = tk.Label(root, text="Focus Monitor", font=("Arial", 16))

        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=20)

        self.monitoring = False
        self.monitor_thread = None