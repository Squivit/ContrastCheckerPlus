try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
except ImportError:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

 
class CaptureOptions(QWidget):
    
    def __init__(self, MainWindow):
        super().__init__(MainWindow)
        
        self.root = MainWindow
        ## Capture options
        
        capture_options_layout = QVBoxLayout()
        
        overview_change_btn = QPushButton('Change overview area')
        overview_change_btn.clicked.connect(self.root.on_overview_area_change)
        overview_change_btn.setEnabled(True)
        
        capture_options_layout.addWidget(overview_change_btn)
        
        self.overview_data_label = QLabel(f'Overview area \n from (x, y) = {self.root.region[:2]} \n with size = {self.root.region[2:]}')
        self.overview_data_label.setWordWrap(True)
        capture_options_layout.addWidget(self.overview_data_label, alignment=Qt.AlignmentFlag.AlignTop)

        
        capture_options_layout.setContentsMargins(10, 25, 10, 25)
        capture_options_layout.setSpacing(10)

        self.setLayout(capture_options_layout)
