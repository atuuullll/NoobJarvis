# window_control.py - Control Windows applications
import subprocess
import os
import webbrowser
import psutil
import time

# List of safe applications that JARVIS can control without asking
SAFE_APPS = {
    'notepad': 'notepad.exe',
    'calculator': 'calc.exe',
    'chrome': 'chrome.exe',
    'firefox': 'firefox.exe',
    'edge': 'msedge.exe',
    'word': 'winword.exe',
    'excel': 'excel.exe',
    'powerpoint': 'powerpnt.exe',
    'paint': 'mspaint.exe',
    'vlc': 'vlc.exe',
    'spotify': 'spotify.exe',
    'discord': 'discord.exe',
    'youtube': 'https://www.youtube.com',
    'gmail': 'https://mail.google.com',
    'whatsapp': 'https://web.whatsapp.com',
}

def open_application(app_name):
    """Open an application by name"""
    app_name = app_name.lower().strip()
    
    # Check if it's a URL
    if app_name.startswith('http://') or app_name.startswith('https://'):
        try:
            webbrowser.open(app_name)
            return True, f"Opening {app_name}"
        except Exception as e:
            return False, f"Failed to open URL: {e}"
    
    # Check if it's a safe app
    if app_name in SAFE_APPS:
        app_path = SAFE_APPS[app_name]
        
        # If it's a URL, open in browser
        if app_path.startswith('http'):
            try:
                webbrowser.open(app_path)
                return True, f"Opening {app_name} in browser"
            except Exception as e:
                return False, f"Failed to open {app_name}: {e}"
        
        # If it's an executable, try to run it
        try:
            subprocess.Popen(app_path, shell=True)
            return True, f"Opening {app_name}"
        except Exception as e:
            return False, f"Failed to open {app_name}: {e}"
    
    # Try to open it as a general command
    try:
        subprocess.Popen(app_name, shell=True)
        return True, f"Opening {app_name}"
    except Exception as e:
        return False, f"Application '{app_name}' not found. Try: {', '.join(list(SAFE_APPS.keys())[:5])}"

def close_application(app_name):
    """Close an application by name"""
    app_name = app_name.lower().strip()
    
    # Map common names to process names
    process_names = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'edge': 'msedge.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'powerpoint': 'powerpnt.exe',
        'paint': 'mspaint.exe',
        'vlc': 'vlc.exe',
        'spotify': 'spotify.exe',
        'discord': 'discord.exe',
    }
    
    process_name = process_names.get(app_name, f'{app_name}.exe')
    
    try:
        # Use taskkill to close the application
        os.system(f'taskkill /im {process_name} /f')
        return True, f"Closed {app_name}"
    except Exception as e:
        return False, f"Failed to close {app_name}: {e}"

def list_running_apps():
    """Get list of currently running applications"""
    running_apps = []
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get executable name only
                name = proc.info['name'].lower()
                if name.endswith('.exe'):
                    running_apps.append(name.replace('.exe', ''))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"Error listing apps: {e}")
    
    return running_apps

def get_open_windows():
    """Get list of open window titles"""
    try:
        import pygetwindow as gw
        windows = gw.getAllTitles()
        return [w for w in windows if w.strip()]
    except:
        return []
