from numpy import array

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QWidget,QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSlider
except ImportError:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget,QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSlider

from widget_src.flags import DisplayModes


class IA_tab(QWidget):
    
    def __init__(self, MainWidnow):
        super().__init__(MainWidnow)
        
        self.root = MainWidnow
        
        ## Image analysis
        
        image_analysis_layout = QVBoxLayout()

        # normal label
        
        display_mode_lbl = QLabel(f'Image color display mode')
        image_analysis_layout.addWidget(display_mode_lbl)

        # reference grab button
        
        self.IA_TAB_ref_grab_btn = QPushButton('Grab reference')
        self.IA_TAB_ref_grab_btn.clicked.connect(self.grab_IA_ref)
        image_analysis_layout.addWidget(self.IA_TAB_ref_grab_btn, alignment=Qt.AlignmentFlag.AlignTop)

        self.reference_rgb = array([0, 0, 0])

        # reference info label
        
        self.IA_TAB_ref_lbl = QLabel('Reference for contrast not defined')
        image_analysis_layout.addWidget(self.IA_TAB_ref_lbl, alignment=Qt.AlignmentFlag.AlignTop)
        self.IA_TAB_ref_lbl.setWordWrap(True)

        # display modes combo box

        self.display_modes = [ DisplayModes.Default , DisplayModes.GrayscaleContrast , DisplayModes.ColorContrast ]

        self.IA_TAB_display_modes_combo = QComboBox()
        self.IA_TAB_display_modes_combo.addItems(self.display_modes)
        self.IA_TAB_display_modes_combo.currentTextChanged.connect(self.root.change_display_mode)
        
        self.root.display_mode = self.display_modes[0]
        
        image_analysis_layout.addWidget(self.IA_TAB_display_modes_combo, alignment=Qt.AlignmentFlag.AlignTop)
        
        # contrast enhancement factor label and slider
        
        image_analysis_layout.addWidget(QLabel('Contrast enhancement factor'), alignment=Qt.AlignmentFlag.AlignTop)
        
        CEF_contrainer = QHBoxLayout()
        
        CEF_max = 20
        CEF_min = 0
        
        self.CEF_slider = QSlider(Qt.Orientation.Horizontal)
        self.CEF_slider.setFixedHeight(20)
        self.CEF_slider.setMinimum(CEF_min)
        self.CEF_slider.setMaximum(4 * CEF_max)
        self.CEF_slider.setSingleStep(1)
        self.CEF_slider.setValue(4 * 1)

        self.CEF_slider.valueChanged.connect(self.root.update_CEF)
        
        CEF_contrainer.addWidget(self.CEF_slider)
        
        self.CEF_lbl = QLabel('1')
        
        CEF_contrainer.addWidget(self.CEF_lbl)
        
        image_analysis_layout.addLayout(CEF_contrainer)
        
        
        # two general contrast modes
        
        CEF_buttons_container = QHBoxLayout()
        
        CEF_mode_1_btn = QPushButton('High contrast (5)')
        CEF_mode_1_btn.clicked.connect(self.CEF_mode_1)
        CEF_mode_1_btn.setEnabled(True)
        
        CEF_buttons_container.addWidget(CEF_mode_1_btn)
        
        CEF_mode_2_btn = QPushButton('Max contrast')
        CEF_mode_2_btn.clicked.connect(self.CEF_mode_2)
        CEF_mode_2_btn.setEnabled(True)
        
        CEF_buttons_container.addWidget(CEF_mode_2_btn)
        
        image_analysis_layout.addLayout(CEF_buttons_container)
        
        # finish layout and set as widget
        
        image_analysis_layout.setSpacing(10)
        image_analysis_layout.setContentsMargins(10, 25, 10, 25)

        self.setLayout(image_analysis_layout)


    def CEF_mode_1(self):
        # contrast factor 55 is 5*4 value on slider
        val = int(5 * 4)
        self.CEF_slider.setValue(val)
        self.root.update_CEF(val)


    def CEF_mode_2(self):
        # contrast factor MAX is 10*4 value on slider
        val = self.CEF_slider.maximum()
        self.CEF_slider.setValue(val)
        self.root.update_CEF(val)




    # begins reference color grabbing in main window
    def grab_IA_ref(self):
        self.IA_TAB_ref_grab_btn.setText('Grabbing...')
        self.IA_TAB_ref_grab_btn.setEnabled(False)
        self.root.IA_ref_grabbing = True


    def reference_grabbed(self, c):
        self.IA_TAB_ref_grab_btn.setEnabled(True)
        self.IA_TAB_ref_grab_btn.setText('Grab reference')
        self.set_IA_ref_lbl(c)
        
        
    def set_IA_ref_lbl(self, rgb):
        self.IA_TAB_ref_lbl.setText(f'Reference for contrast = {rgb}')
