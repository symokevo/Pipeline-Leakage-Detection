import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from database import init_db, authenticate

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pipeline Monitoring - Login")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password)
        
        btn_login = QPushButton("Login")
        btn_login.clicked.connect(self.authenticate)
        layout.addWidget(btn_login)
        
        self.setLayout(layout)
    
    def authenticate(self):
        role = authenticate(self.username.text(), self.password.text())
        if role:
            self.main_window = MainWindow(role)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

class MainWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.sensor_data = [
            {"id": 1, "ir": 0, "water": 0, "status": "Normal"},
            {"id": 2, "ir": 0, "water": 0, "status": "Normal"},
            {"id": 3, "ir": 0, "water": 0, "status": "Normal"}
        ]
        
        self.setWindowTitle(f"Pipeline Monitoring - {role.capitalize()} View")
        self.setMinimumSize(800, 600)
        
        self.create_ui()
        self.update_display()
        
        # Auto-refresh every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
    
    def create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Status display
        status_group = QGroupBox("Sensor Status")
        status_layout = QVBoxLayout()
        
        self.sensor_labels = []
        for i in range(3):
            sensor_frame = QWidget()
            sensor_layout = QHBoxLayout()
            
            sensor_layout.addWidget(QLabel(f"Sensor {i+1}:"))
            sensor_layout.addWidget(QLabel("IR: Unknown", objectName=f"ir_{i}"))
            sensor_layout.addWidget(QLabel("Water: Unknown", objectName=f"water_{i}"))
            sensor_layout.addWidget(QLabel("Status: Normal", objectName=f"status_{i}"))
            
            sensor_frame.setLayout(sensor_layout)
            status_layout.addWidget(sensor_frame)
            self.sensor_labels.append({
                "ir": self.findChild(QLabel, f"ir_{i}"),
                "water": self.findChild(QLabel, f"water_{i}"),
                "status": self.findChild(QLabel, f"status_{i}")
            })
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Controls (for engineers/admins)
        if self.role in ("admin", "engineer"):
            control_group = QGroupBox("Sensor Control")
            control_layout = QVBoxLayout()
            
            self.sensor_combo = QComboBox()
            self.sensor_combo.addItems(["1", "2", "3"])
            
            btn_ir = QPushButton("Simulate IR Sensor")
            btn_ir.clicked.connect(self.simulate_ir)
            
            btn_water = QPushButton("Simulate Water Sensor")
            btn_water.clicked.connect(self.simulate_water)
            
            control_layout.addWidget(QLabel("Select Sensor:"))
            control_layout.addWidget(self.sensor_combo)
            control_layout.addWidget(btn_ir)
            control_layout.addWidget(btn_water)
            control_layout.addWidget(QLabel("IR: 0=No Obstacle, 1=Obstacle"))
            control_layout.addWidget(QLabel("Water: 0=Dry, <500=Partial, >=500=Submerged"))
            
            control_group.setLayout(control_layout)
            layout.addWidget(control_group)
        
        central_widget.setLayout(layout)
    
    def update_display(self):
        for i, sensor in enumerate(self.sensor_data):
            self.sensor_labels[i]["ir"].setText(f"IR: {sensor['ir']}")
            self.sensor_labels[i]["water"].setText(f"Water: {sensor['water']}")
            self.sensor_labels[i]["status"].setText(f"Status: {sensor['status']}")
    
    def simulate_ir(self):
        sensor_id = self.sensor_combo.currentIndex()
        value, ok = QInputDialog.getInt(
            self, "IR Simulation", 
            "Enter IR value (0 or 1):", 
            self.sensor_data[sensor_id]["ir"], 0, 1
        )
        if ok:
            self.sensor_data[sensor_id]["ir"] = value
            self.sensor_data[sensor_id]["status"] = "Obstacle" if value else "Normal"
    
    def simulate_water(self):
        sensor_id = self.sensor_combo.currentIndex()
        value, ok = QInputDialog.getInt(
            self, "Water Simulation", 
            "Enter water level (0-1024):", 
            self.sensor_data[sensor_id]["water"], 0, 1024
        )
        if ok and 0 <= value <= 1024:
            self.sensor_data[sensor_id]["water"] = value
            if value == 0:
                self.sensor_data[sensor_id]["status"] = "Dry"
            elif value < 500:
                self.sensor_data[sensor_id]["status"] = "Partial Leak"
            else:
                self.sensor_data[sensor_id]["status"] = "Fully Submerged"

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec())