import psutil
import platform
import os
import subprocess
import ctypes

class SystemTools:
    def get_system_telemetry(self):
        """Returns comprehensive system telemetry for MSI Vector 17."""
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
        memory = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        
        telemetry = {
            "device": "MSI Vector 17",
            "cpu_usage": f"{cpu_usage}%",
            "cpu_freq": f"{cpu_freq}MHz",
            "memory_usage": f"{memory.percent}% ({memory.used // (1024**2)}MB / {memory.total // (1024**2)}MB)",
            "os": platform.system(),
            "os_release": platform.release(),
            "battery": f"{battery.percent}%" if battery else "N/A",
            "power_status": "Plugged In" if battery and battery.power_plugged else "On Battery" if battery else "N/A"
        }
        
        # GPU telemetry (NVIDIA RTX 40-series typically found in Vector 17)
        try:
            gpu_output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total,clocks.current.graphics", "--format=csv,noheader,nounits"], 
                encoding='utf-8'
            )
            gpu_util, gpu_temp, gpu_mem_used, gpu_mem_total, gpu_clock = gpu_output.strip().split(', ')
            telemetry["gpu_usage"] = f"{gpu_util}%"
            telemetry["gpu_temp"] = f"{gpu_temp}C"
            telemetry["gpu_memory"] = f"{gpu_mem_used}MB / {gpu_mem_total}MB"
            telemetry["gpu_clock"] = f"{gpu_clock}MHz"
        except (subprocess.CalledProcessError, FileNotFoundError):
            telemetry["gpu_usage"] = "N/A"
            telemetry["gpu_temp"] = "N/A"
        
        # Disk usage
        disk = psutil.disk_usage('/')
        telemetry["disk_usage"] = f"{disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"

        return telemetry

    def launch_app(self, app_name):
        """Launches common apps or search for executables."""
        app_map = {
            "chrome": "chrome.exe",
            "browser": "chrome.exe",
            "code": "code.cmd",
            "terminal": "powershell.exe",
            "notepad": "notepad.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe"
        }
        
        target = app_map.get(app_name.lower(), app_name)
        try:
            os.startfile(target)
            return f"Initiating launch sequence for {app_name}."
        except Exception:
            # Try searching in common paths if not found
            return f"Unable to locate the execution path for {app_name}. I recommend checking the installation directory."

    def control_media(self, action):
        """Controls media and volume with Jarvis-style confirmation."""
        VK_VOLUME_MUTE = 0xAD
        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF
        VK_MEDIA_NEXT_TRACK = 0xB0
        VK_MEDIA_PREV_TRACK = 0xB1
        VK_MEDIA_PLAY_PAUSE = 0xB3

        key_map = {
            "mute": VK_VOLUME_MUTE,
            "vol_down": VK_VOLUME_DOWN,
            "vol_up": VK_VOLUME_UP,
            "next": VK_MEDIA_NEXT_TRACK,
            "prev": VK_MEDIA_PREV_TRACK,
            "play_pause": VK_MEDIA_PLAY_PAUSE
        }
        
        if action in key_map:
            # Press and release
            ctypes.windll.user32.keybd_event(key_map[action], 0, 0, 0)
            ctypes.windll.user32.keybd_event(key_map[action], 0, 2, 0)
            
            responses = {
                "vol_up": "Increasing volume.",
                "vol_down": "Decreasing volume.",
                "mute": "Audio muted.",
                "play_pause": "Toggling media playback.",
                "next": "Skipping to the next track.",
                "prev": "Returning to the previous track."
            }
            return responses.get(action, f"Action {action} completed.")
        return f"I encountered an error attempting to {action}. The command is not recognized."
