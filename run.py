"""
Launcher script for the AI Chatbot application.
Starts the server and automatically opens the browser.
"""

import sys
import time
import webbrowser
from app import run_server

def main():
    print("==================================================")
    print("  🚀 Antigravity AI Chatbot Application Starter  ")
    print("==================================================")
    print("  • Web Server: http://localhost:5000")
    print("  • Database: SQLite (chatbot.db)")
    print("  • Press Ctrl+C in terminal to stop the server.")
    print("==================================================")

    # Open browser after 1 second delay
    def open_browser():
        time.sleep(1.2)
        webbrowser.open("http://localhost:5000")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Start server
    run_server()

if __name__ == "__main__":
    main()
