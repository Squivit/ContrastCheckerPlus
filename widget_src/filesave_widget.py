try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPalette, QColor
    from PyQt6.QtWidgets import (QWidget,
                                QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QLineEdit, QFileDialog, QCheckBox, QSpinBox, QButtonGroup)
except ImportError:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPalette, QColor
    from PyQt5.QtWidgets import (QWidget,
                                QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QLineEdit, QFileDialog, QCheckBox, QSpinBox, QButtonGroup)

import time
from widget_src.flags import DisplayModes

class FileSaver(QWidget):
    
    def __init__(self, MainWindow, bg_color = '#31363b'):
        super().__init__(MainWindow)
        
        self.root = MainWindow
        
        zooms = ['x5', 'x10', 'x20', 'x50']
        self.zoom = zooms[0]

        self.default_filesave_loc = r'C:'

        # set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
        self.setPalette(palette)

        # create layout
        
        file_saver = QVBoxLayout()

        file_saver.addWidget(QLabel('File saving settings'), alignment=Qt.AlignmentFlag.AlignTop)        
                
        # name edit
        
        folder_lookout_layout = QHBoxLayout()

        file_saver.addWidget(QLabel('Folder location'), alignment=Qt.AlignmentFlag.AlignTop)
            
        self.folder_loc = QLineEdit(f'{self.default_filesave_loc}')
        
        # update the folder location

        folder_lookout_layout.addWidget(self.folder_loc, alignment=Qt.AlignmentFlag.AlignTop)

        self.file_save_btn = QPushButton('Browse')
        self.file_save_btn.clicked.connect(self.browse_btn_clicked)
        
        folder_lookout_layout.addWidget(self.file_save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        file_saver.addLayout(folder_lookout_layout)
        
        ## options checkboxes
        
        checkbox_holder = QVBoxLayout()
        
        self.fixed_check = QCheckBox('Fixed name')
        self.fixed_check.setChecked(False)
        self.fixed_check.clicked.connect(self.checkboxes_state_changed)

        self.flake_number_spin = QSpinBox()
        self.flake_number_spin.setMinimum(0)
        self.flake_number_spin.setMinimumWidth(75)
        self.flake_number_spin.valueChanged.connect(self.checkboxes_state_changed)

        self.flake_check = QCheckBox('Flake number')
        self.flake_check.setChecked(False)
        self.flake_check.setCheckable(False)
        self.flake_check.clicked.connect(self.checkboxes_state_changed)

        self.mode_check = QCheckBox('Display mode')
        self.mode_check.setChecked(False)
        self.mode_check.setCheckable(False)
        self.mode_check.clicked.connect(self.checkboxes_state_changed)

        self.time_check = QCheckBox('Date && time')
        self.time_check.setChecked(False)
        self.time_check.setCheckable(False)
        self.time_check.clicked.connect(self.checkboxes_state_changed)

        self.zoom_btns = QButtonGroup(self)
        z_btns = []

        for zoom in zooms:
            temp_btn = QPushButton(zoom)
            temp_btn.setCheckable(True)
            if zoom == zooms[0]:
                temp_btn.setChecked(True)
            else:
                temp_btn.setChecked(False)
            z_btns.append(temp_btn)
            self.zoom_btns.addButton(temp_btn)
            
        self.zoom_btns.buttonPressed.connect(lambda btn: self.zoom_changed(btn.text()))

        checkbox_holder.addWidget(self.fixed_check, Qt.AlignmentFlag.AlignLeft)
    
        box1 = QHBoxLayout()
        box1.addWidget(self.flake_check, Qt.AlignmentFlag.AlignLeft)
        box1.addWidget(self.flake_number_spin, Qt.AlignmentFlag.AlignLeft)
        checkbox_holder.addLayout(box1)
        
        box2 = QHBoxLayout()
        box2.addWidget(self.mode_check, Qt.AlignmentFlag.AlignLeft)
        box2.addWidget(self.time_check, Qt.AlignmentFlag.AlignLeft)
        checkbox_holder.addLayout(box2)

        checkbox_holder.addWidget(QLabel('Microscope zoom'), alignment=Qt.AlignmentFlag.AlignTop)

        box3 = QHBoxLayout()
        for zoom_btn in self.zoom_btns.buttons():
            box3.addWidget(zoom_btn, Qt.AlignmentFlag.AlignCenter)
        checkbox_holder.addLayout(box3)
        
        file_saver.addLayout(checkbox_holder)
        
        ## File namer
        
        file_saver.addWidget(QLabel('File name'), alignment=Qt.AlignmentFlag.AlignTop)
            
        self.filename = QLineEdit(f'image.png')
        
        # update file name
        self.filename.textChanged.connect(self.update_filename)
        self.update_filename('image.png')

        file_saver.addWidget(self.filename, alignment=Qt.AlignmentFlag.AlignTop)
        

        self.file_save_btn = QPushButton('Save')
        self.file_save_btn.setEnabled(False)
        self.file_save_btn.clicked.connect(self.save_image)
        
        file_saver.addWidget(self.file_save_btn, alignment=Qt.AlignmentFlag.AlignRight)
                
                
        self.setLayout(file_saver)
        self.setFixedWidth(400)
                

    def browse_btn_clicked(self):
        response = QFileDialog.getExistingDirectory(
            parent = self,
            caption = 'Select directory',
            directory = self.default_filesave_loc,
        )
        
        self.default_filesave_loc = response
        self.folder_loc.setText(response)        
  
  
    def zoom_changed(self, zoom):
        self.zoom = zoom
        self.checkboxes_state_changed()
  
  
    def checkboxes_state_changed(self):
        
        if self.fixed_check.isChecked():
            
            # enable checkable for checkboxes
            if not self.flake_check.isCheckable():
                self.flake_check.setCheckable(True)
                self.mode_check.setCheckable(True)
                self.time_check.setCheckable(True)
            
            self.filename.setEnabled(False)
            
            file_name = 'flake'
            
            if self.flake_check.isChecked():
                file_name += f'_{self.flake_number_spin.value()}'

            file_name += f'_{self.zoom}'

            if self.mode_check.isChecked():
                
                if self.root.display_mode == DisplayModes.Default:
                    file_name += f'_raw'
                elif self.root.display_mode == DisplayModes.GrayscaleContrast:
                    file_name += f'_grayscale'
                elif self.root.display_mode == DisplayModes.ColorContrast:
                    file_name += f'_contrast'

            if self.time_check.isChecked():
                file_name += f'_{time.strftime("%H:%M:%S", time.localtime())}'
                
            self.update_filename(file_name)
            self.filename.setText(file_name)

        else:

            self.filename.setEnabled(True)
            self.flake_check.setCheckable(False)
            self.mode_check.setCheckable(False)
            self.time_check.setCheckable(False)
    

    def update_filename(self, t):
        self.save_file_name = t


    def save_image(self):

        self.checkboxes_state_changed()

        if self.root.original_pixelmap is None:
            return
        
        file_destination = f'{self.default_filesave_loc}/{self.save_file_name.replace(":", "_")}'
        file_destination = file_destination.split('.png')[0]
                            
        image = self.root.original_pixelmap

        if self.root.display_mode == DisplayModes.GrayscaleContrast:
            image = self.root.contrast_grayscale
        elif self.root.display_mode == DisplayModes.ColorContrast:
            image = self.root.contrast_color


        image.toImage().save(f'{file_destination}.png', 'png', -1)