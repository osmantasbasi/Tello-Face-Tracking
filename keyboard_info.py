from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

class KeyboardInfo(QWidget):
        def __init__(self):
                super().__init__()
                loadUi("keyboard_information.ui", self)
                self.setWindowFlags(Qt.WindowStaysOnTopHint)
              
              
              

                
                
