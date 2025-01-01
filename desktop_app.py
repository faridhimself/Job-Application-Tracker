import sys
import os
import psutil
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, 
                            QMenu, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
import threading
import time
import signal

class PostgresManager:
    def __init__(self):
        self.pg_bin_path = r"C:\Program Files\PostgreSQL\16\bin"  # Adjust version if needed
        self.postgres_process = None

    def start_postgres(self):
        if not self.is_postgres_running():
            try:
                postgres_cmd = os.path.join(self.pg_bin_path, "pg_ctl.exe")
                data_dir = os.path.join(self.pg_bin_path, "..", "data")
                
                self.postgres_process = subprocess.Popen(
                    [postgres_cmd, "start", "-D", data_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(5)  # Wait for PostgreSQL to start
                return True
            except Exception as e:
                print(f"Error starting PostgreSQL: {e}")
                return False
        return True

    def stop_postgres(self):
        if self.is_postgres_running():
            try:
                postgres_cmd = os.path.join(self.pg_bin_path, "pg_ctl.exe")
                data_dir = os.path.join(self.pg_bin_path, "..", "data")
                
                subprocess.run(
                    [postgres_cmd, "stop", "-D", data_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(2)  # Wait for PostgreSQL to stop
                return True
            except Exception as e:
                print(f"Error stopping PostgreSQL: {e}")
                return False
        return True

    def is_postgres_running(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'postgres.exe':
                return True
        return False

class FlaskThread(QThread):
    def run(self):
        import app
        print("Starting Flask server...")
        app.app.run(port=5000, debug=True)

class JobTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Application Tracker")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize PostgreSQL manager
        self.pg_manager = PostgresManager()
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Create web view
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        
        # Start PostgreSQL and Flask server
        self.start_services()
        
        # Wait a bit for Flask to start
        print("Waiting for Flask server to start...")
        time.sleep(2)
        
        # Load the web application with cache buster
        print("Loading web application...")
        self.web_view.setUrl(Qt.QUrl(f"http://localhost:5000?t={int(time.time())}"))
        
        # Refresh the page every 30 seconds to show updates
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_page)
        self.refresh_timer.start(30000)  # 30 seconds
        
    def refresh_page(self):
        """Refresh the web view to show updated content"""
        print("Refreshing page...")
        self.web_view.setUrl(Qt.QUrl(f"http://localhost:5000?t={int(time.time())}"))

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('Job Application Tracker')
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def start_services(self):
        # Start PostgreSQL
        if not self.pg_manager.start_postgres():
            QMessageBox.critical(self, "Error", "Failed to start PostgreSQL server!")
            sys.exit(1)
        
        # Start Flask server in a separate thread
        self.flask_thread = FlaskThread()
        self.flask_thread.start()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Job Application Tracker",
            "Application is still running in the system tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def quit_application(self):
        # Stop PostgreSQL
        self.pg_manager.stop_postgres()
        
        # Stop Flask thread
        if hasattr(self, 'flask_thread'):
            self.flask_thread.terminate()
        
        QApplication.quit()

if __name__ == '__main__':
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    window = JobTrackerApp()
    window.show()
    sys.exit(app.exec())
