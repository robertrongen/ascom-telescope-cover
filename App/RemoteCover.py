import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QGridLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import serial

class SerialThread(QThread):
    signal_data_received = pyqtSignal(str)

    def __init__(self, port_name):
        super().__init__()
        self.port_name = port_name
        self.running = True
        self.ser = None


    def run(self):
        try:
            self.ser = serial.Serial(self.port_name, 57600)
            while self.running:
                if self.ser.in_waiting:
                    raw_data = self.ser.readline()
                    data = raw_data.decode('utf-8').strip()
                    self.signal_data_received.emit(data)
        except Exception as e:
            print(f"Error in SerialThread: {e}")

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        if os.name == 'nt':
            port_name = 'COM3'
        else:
            port_name = '/dev/ttyUSB1'

        self.serialThread = SerialThread(port_name)
        self.serialThread.signal_data_received.connect(self.updateText)
        self.serialThread.start()

    def initUI(self):

        # Define main and highlight styles
        main_stylesheet = """
        QPushButton {
            background-color: #2C3E50;
            color: #BDC3C7;
            border: 1px solid #34495E;
            padding: 5px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #34495E;
        }
        QPushButton:pressed {
            background-color: #2C3E50;
            border: 1px solid #BDC3C7;
        }
        """

        highlight_stylesheet = """
        QPushButton {
            background-color: #E74C3C;
            color: #FFFFFF;
            border: 1px solid #C0392B;
            padding: 5px;
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #EA6153;
        }
        QPushButton:pressed {
            background-color: #E74C3C;
            border: 1px solid #FFFFFF;
        }
        """
        # Background and text color for QTextEdit and main window
        app_stylesheet = """
        QWidget {
            background-color: #1C2833;  
            color: #BDC3C7;  
        }
        QTextEdit {
            border: 1px solid #34495E;
            background-color: #1A242F;
        }
        """

        layout = QVBoxLayout()
        top_button_layout = QHBoxLayout()  # This is for the Open and Close buttons
        bottom_button_layout = QGridLayout()  # This is for the rest of the buttons

        # Create and set up the label for the top buttons
        main_label = QLabel("Remote controller for telescope cover using DarkSkyGeek Switch.", self)
        main_label.setStyleSheet("color: white; font-size: 12px;")
        main_label_layout = QVBoxLayout()  # New layout for main label with margins
        main_label_layout.addWidget(main_label)
        main_label_layout.setContentsMargins(0, 10, 0, 10)  # Add top and bottom margins for the main label
        layout.addLayout(main_label_layout)

        btnOpen = QPushButton('Open Cover', self)
        btnOpen.setStyleSheet(highlight_stylesheet)
        btnOpen.clicked.connect(self.sendOpen)

        btnClose = QPushButton('Close Cover', self)
        btnClose.setStyleSheet(highlight_stylesheet)
        btnClose.clicked.connect(self.sendClose)

        # Add Open and Close buttons to the top button layout
        top_button_layout.addWidget(btnOpen)
        top_button_layout.addWidget(btnClose)

        btnClear = QPushButton('Clear Messages', self)
        btnClear.setStyleSheet(main_stylesheet)
        btnClear.clicked.connect(self.clearMessages)

        btnPing = QPushButton('Test Ping', self)
        btnPing.setStyleSheet(main_stylesheet)
        btnPing.clicked.connect(self.sendPing)

        btnState = QPushButton('Get State', self)
        btnState.setStyleSheet(main_stylesheet)
        btnState.clicked.connect(self.sendGetState)

        # Place the rest of the buttons in the grid layout
        # bottom_button_layout.addWidget(btnClear, 0, 0, 1, 2)  # Top, spans both columns
        bottom_button_layout.addWidget(btnClear, 0, 0) 
        bottom_button_layout.addWidget(btnPing, 0, 1) 
        bottom_button_layout.addWidget(btnState, 0, 2) 

        # Add the top button layout to the main layout
        layout.addLayout(top_button_layout)

        # Create and set up the label for the textEdit and add it after the top buttons
        textEdit_label = QLabel("Serial port messages", self)
        textEdit_label.setStyleSheet("color: lightgray; font-size: 12px;")
        textEdit_label_layout = QVBoxLayout()  # New layout for textEdit label with margins
        textEdit_label_layout.addWidget(textEdit_label)
        textEdit_label_layout.setContentsMargins(0, 10, 0, 10)  # Add top and bottom margins for the textEdit label
        layout.addLayout(textEdit_label_layout)

        # Add the textEdit and the bottom buttons layout to the main layout
        self.textEdit = QTextEdit(self)
        layout.addWidget(self.textEdit)
        layout.addLayout(bottom_button_layout)

        self.setLayout(layout)
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('Remote Cover Controller')
        self.show()

        # Apply the dark theme to the entire app
        app.setStyleSheet(app_stylesheet)

    def sendOpen(self):
        if self.serialThread.ser:
            self.serialThread.ser.write(b'COMMAND:OPEN')
        self.textEdit.append("App sent open command.")

    def sendClose(self):
        if self.serialThread.ser:
            self.serialThread.ser.write(b'COMMAND:CLOSE')
        self.textEdit.append("App sent close command.")

    def sendPing(self):
        if self.serialThread.ser:
            self.serialThread.ser.write(b'COMMAND:PING')
        self.textEdit.append("App sent ping test command.")

    def clearMessages(self):
        self.textEdit.clear()

    def sendGetState(self):
        if self.serialThread.ser:
            self.serialThread.ser.write(b'COMMAND:GETSTATE')
        self.textEdit.append("App sent get state command.")

    def closeEvent(self, event):
        self.serialThread.stop()
        self.serialThread.wait()  # Wait for the thread to finish
        event.accept()

    def updateText(self, data):
        self.textEdit.append(data)
        # self.textEdit.setText(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
