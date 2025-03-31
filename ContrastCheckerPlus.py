import sys
from numpy import array, round, sum, sign, uint8, float64, frombuffer, stack

try:
    from PyQt6.QtCore import (Qt, QSize, QTimer)
    from PyQt6.QtGui import QGuiApplication, QImage, QPalette, QColor, QPixmap, QFont
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                                QVBoxLayout, QHBoxLayout, QTabWidget,
                                QLabel, QPushButton, QComboBox)
except ImportError:
    from PyQt5.QtCore import (Qt, QSize, QTimer)
    from PyQt5.QtGui import QGuiApplication, QImage, QPalette, QColor, QPixmap, QFont
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                                QVBoxLayout, QHBoxLayout, QTabWidget,
                                QLabel, QPushButton, QComboBox)

from widget_src import filesave_widget, image_analysis_tab, capture_options
from widget_src.flags import DisplayModes


class MainWindow(QMainWindow):
    
    display_mode = None
    video_running = False
    
    contrast_grayscale = None
    contrast_color = None
    IA_ref_grabbing = False
    
    reference_rgb = [0, 0, 0]
    
    def __init__(self, region):
        super().__init__()
                
        self.setWindowTitle('Contrast Checker Plus (CC+) v.1.0 by R Komar')
                
        
        
        # set color grab area
        self.radius = 3
        self.region = [region[key] for key in region.keys()]    
        self.on_radius_change(self.radius)
        
        
        self.original_pixelmap = None
        self.monitor_index = 0
        
        self.snippingWidget = SnippingWidget(parent = self, app=QApplication.instance(), monitor_index=self.monitor_index)
        self.snippingWidget.onSnippingCompleted = self.onSnippingCompleted

        
        left_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        btn = QPushButton('Snapshot')
        btn.pressed.connect(self.shoot_screen)
        button_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.video_btn = QPushButton('Video')
        self.video_btn.setCheckable(True)
        self.video_btn.toggled.connect(self.switch_continuous)
        
        self.video_timer = QTimer()
        self.video_timer.setInterval(50)
        self.video_timer.timeout.connect(self.shoot_screen)
        
        button_layout.addWidget(self.video_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        
        btn = QPushButton('Grab colors')
        btn.pressed.connect(self.start_grabbing_colors)
        button_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.grabbing = False
        
        combo_box = QComboBox()
        combo_box.addItems([f'Screen {ii + 1}' for ii in range(len(QGuiApplication.screens()))])
        combo_box.currentIndexChanged.connect(self.change_screen)

        button_layout.addWidget(combo_box)
        
        left_layout.addLayout(button_layout)
        

        self.img = QImage()
        
        self.image = QLabel()
        self.image.setFixedSize(QSize(region['width'], region['height']))
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.mousePressEvent = self.get_color_on_img

        self.image.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('blue'))
        self.image.setPalette(palette)

        left_layout.addWidget(self.image, alignment=Qt.AlignmentFlag.AlignCenter)
        
        
        self.contrast_label = QLabel()
        self.set_contrast_label()
        left_layout.addWidget(self.contrast_label)
        
        
        right_layout = QVBoxLayout()
        
        tabs = QTabWidget()
        tabs.setFixedWidth(400)

        
        self.capture_options_widget = capture_options.CaptureOptions(self)
        
        tabs.addTab(self.capture_options_widget, 'Capture settings')        
        
        ## image analysis widget
        
        self.image_analysis_widget = image_analysis_tab.IA_tab(self)
        self.update_CEF(4)

        tabs.addTab(self.image_analysis_widget, 'Image analysis')
        
        ## collect widget

        right_layout.addWidget(tabs, alignment=Qt.AlignmentFlag.AlignTop)
        
        ## File saver

        self.file_saver_widget = filesave_widget.FileSaver(self)
        
        right_layout.addWidget(self.file_saver_widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        ## Master layout and widget
        
        master_layout = QHBoxLayout()
        master_layout.addLayout(left_layout)
        master_layout.addLayout(right_layout)
        
        widget = QWidget()
        widget.setLayout(master_layout)
        
        self.setCentralWidget(widget)        
    

    def change_screen(self, i):
        self.monitor_index = i
        self.snippingWidget.update_monitor(i)

        
    def shoot_screen(self):
        self.contrast_grayscale = None
        self.contrast_color = None
        
        screen = QGuiApplication.screens()[self.monitor_index]
        window = self.windowHandle()
        window.setScreen(screen)
        
        if window:
            screen = window.screen()
        if not screen:
            return

        self.original_pixelmap = screen.grabWindow(0, *self.region)
        
        if self.original_pixelmap.devicePixelRatio() > 1:
            print('Non 1 pixel ratio, probably not 1920x1080 px display')
            self.original_pixelmap = self.original_pixelmap.scaledToHeight(int(self.region[3]))
        
        self.display_image()
        
        if not self.video_running:
            self.file_saver_widget.file_save_btn.setEnabled(True)


    def switch_continuous(self):
        
        if self.video_btn.isChecked():
            
            self.video_running = True
            self.video_timer.start()
            self.file_saver_widget.file_save_btn.setEnabled(False)
            
        else:
            
            self.video_running = False
            self.video_timer.stop()
            self.file_saver_widget.file_save_btn.setEnabled(True)


    def update_screenshot_label(self, image):
        self.image.setFixedSize(QSize(image.size()))        
        self.image.setPixmap(image)
        self.img = QImage(self.original_pixelmap)


    def start_grabbing_colors(self):
        
        self.grabbing = True
        self.grabbed = 0
        self.new_colors = [None, None]

        self.set_contrast_label(*self.new_colors)


    def get_color_on_img(self, e):
        
        if self.grabbing:
            
            # get position
            x = e.pos().x()
            y = e.pos().y()
                                                          
            # define area to average over
            area = [ x, y ] + self.area
                         
            # sum over specified area           
            c = sum([ self.img.pixelColor( pos[0] , pos[1] ).getRgb()[:-1] for pos in area ], axis = 0, dtype=float)
            
            # normalization
            c /= len(area)
            c = array(c, dtype=uint8)
                        
            self.new_colors[self.grabbed] = c
            
            # track grabbed color color
            self.grabbed += 1
            
            self.set_contrast_label(*self.new_colors)
            
            if self.grabbed == 2:
                self.grabbing = False
                pass
            
        elif self.IA_ref_grabbing:
            
            # get position
            x = e.pos().x()
            y = e.pos().y()
                                                          
            # define area to average over
            area = [ x, y ] + self.area
                         
            # sum over specified area           
            c = sum([ self.img.pixelColor( pos[0] , pos[1] ).getRgb()[:-1] for pos in area ], axis = 0, dtype=float)
            
            # normalization
            c /= len(area)
            c = array(c, dtype=uint8)
            
            self.IA_ref_grabbing = False
            
            self.reference_rgb = c
            self.image_analysis_widget.reference_grabbed(c)
            
            self.contrast_grayscale = None
            self.contrast_color = None
            
            self.display_image()
            

    def change_display_mode(self, value):
        
        self.display_mode = value
        self.display_image()
        
        
    def display_image(self):
            
        if self.original_pixelmap is None:
            return
            
        if self.display_mode == DisplayModes.Default:
            
            self.update_screenshot_label(self.original_pixelmap)
        
        elif self.display_mode == DisplayModes.GrayscaleContrast:
                        
            if self.contrast_grayscale is None:
                                                        
                width = self.region[2]
                height = self.region[3]
                
                # Reformatting to numpy array

                channels_count = 3
                qimg = self.original_pixelmap.toImage()
                qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
                b = qimg.bits()
                b.setsize(width * height * channels_count)
                arr = frombuffer(b, uint8).reshape((height, width, channels_count))[:, :, :3]
                
                # seems that during calculations below it remembers its uint8 type and loops through the modulo
                arr = array(arr, dtype = float)
                
                # apply color contrast transform and average over rgb (to grayscale)
                # 1 - avg is to reverse the colorscale (the closer to reference the brighter)
                
                arr_transform = array(1 - sum( abs( self.color_contrast(arr) ), axis=2)/3, dtype = float)
                
                arr_transform = (arr_transform - 1) * (1 + self.contrast_enhance_factor) + 1
                
                # from range 0-1 to standard rgb 0-255
                arr_transform *= 255

                # limit max rgb values to 0 and 255
                arr[arr > 255] = 255
                arr[arr < 0] = 0
                                
                arr_transform = array(stack([arr_transform, arr_transform, arr_transform], axis = 2), dtype= uint8)

                self.contrast_grayscale = QPixmap(QImage(arr_transform.data, arr_transform.shape[1], arr_transform.shape[0], QImage.Format.Format_RGB888))
                
            self.update_screenshot_label(self.contrast_grayscale)
            
        
        elif self.display_mode == DisplayModes.ColorContrast:
            
            if self.contrast_color is None:
                            
                width = self.region[2]
                height = self.region[3]
                
                # Reformatting to numpy array

                channels_count = 3
                qimg = self.original_pixelmap.toImage()
                qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
                b = qimg.bits()
                b.setsize(width * height * channels_count)
                arr = frombuffer(b, uint8).reshape((height, width, channels_count))[:, :, :3].copy()
                
                arr = array(arr, dtype = float64)
                
                # apply color contrast transform multiplied by 255 to enhance the contrast
                CC_arr = self.color_contrast(arr) * self.contrast_enhance_factor

                CC_arr[CC_arr < -1] = -1
                CC_arr[CC_arr > 1] = 1
                arr *= (1 + CC_arr)
                #arr += self.reference_rgb * CC_arr
                                                              
                # limit max rgb values to 0 and 255
                arr[arr > 255] = 255
                arr[arr < 0] = 0

                arr = array(arr, dtype=uint8)
                                                                 
                self.contrast_color = QPixmap.fromImage(QImage(arr.data, arr.shape[1], arr.shape[0], QImage.Format.Format_RGB888))
                
            self.update_screenshot_label(self.contrast_color)
        
        else:
            
            print(f'Display mode {self.display_mode} not defined')
        
        
    def update_CEF(self, v):
        self.contrast_enhance_factor = v / 4.
        self.image_analysis_widget.CEF_lbl.setText(f'{self.contrast_enhance_factor}')
        self.contrast_grayscale = None
        self.contrast_color = None
        
        self.display_image()
  

    def set_contrast_label(self, reference_rgb = None, point_rgb = None):
        in_text = 'Reference '
        
        if reference_rgb is None:
            in_text += 'not defined\n'
        else:
            in_text += f'rgb values = {reference_rgb}\n'
            
        in_text += 'Point '
            
        if point_rgb is None:
            in_text += 'not defined\n'
        else:
            in_text += f'rgb values = {point_rgb}\n'
        
        in_text += 'Color contrast[%]: '
        
        if reference_rgb is None or point_rgb is None:
            in_text += 'not available'
        else:
            prgb = array(point_rgb)
            rrgb = array(reference_rgb)
                        
            # 1 - sign(|x|) removes divide by zero exception (makes denominator 1 if 0 and normal otherwise)
            in_text += f'{round(self.color_contrast(prgb, rrgb) * 100, 1)}'
        
        self.contrast_label.setText(in_text)

    
    def on_radius_change(self, v):

        self.radius = v
        rad = v - 1
                
        self.area = []
            
        [ [ self.area.append([x, y]) for y in range(abs(x) - rad, rad - abs(x) + 1, 1) ] for x in range(-rad, rad + 1, 1) ]
        self.area = array(self.area)
   
   
    def onSnippingCompleted(self, frame):        
        self.setWindowState(Qt.WindowState.WindowActive)
        #self.image_analysis_widget.IA_TAB_display_modes_combo.setCurrentIndex(0)
        
        if frame is None:
            return 

        self.region = frame
        
        self.capture_options_widget.overview_data_label.setText(f'Overview area in Screen {self.monitor_index + 1} \n from (x, y) = {self.region[:2]} \n with size = {self.region[2:]}')
        
        self.shoot_screen()


    def on_overview_area_change(self):
        self.setWindowState(Qt.WindowState.WindowMinimized)
        self.snippingWidget.start()


    def color_contrast(self, point_rgb, ref_rgb = None):
        if ref_rgb is None:
            prgb = array(point_rgb, dtype=int)
            rrgb = array(self.reference_rgb, dtype=int)
        else:
            prgb = array(point_rgb, dtype=int)
            rrgb = array(ref_rgb, dtype=int)
        return (prgb - rrgb) / (prgb + rrgb  + (1 - sign(abs(prgb + rrgb))) )
        
        

try:
    from PyQt6.QtGui import QCursor, QPainter, QPen
    from PyQt6.QtCore import QPointF, QRectF
except ImportError:
    from PyQt5.QtGui import QCursor, QPainter, QPen
    from PyQt5.QtCore import QPointF, QRectF

  
class SnippingWidget(QWidget):
    is_snipping = False

    def __init__(self, parent=None, app=None, monitor_index = 0):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.app = app
        self.screen = self.app.screens()[monitor_index]
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        self.begin = QPointF()
        self.end = QPointF()
        self.onSnippingCompleted = None
        
        self.offset = [0, 0]

    def update_monitor(self, index):
        self.screen = self.app.screens()[index]
        self.offset = [self.screen.availableGeometry().x(), self.screen.availableGeometry().y()]
        self.setGeometry(*self.offset, self.screen.size().width(), self.screen.size().height())
        
    def start(self):
        SnippingWidget.is_snipping = True
        self.setWindowOpacity(0.1)
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.show()

    def paintEvent(self, event):
        
        if SnippingWidget.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.15
        else:
            self.begin = QPointF()
            self.end = QPointF()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QPainter(self)
        qp.setPen(QPen(QColor('black'), lw))
        qp.setBrush(QColor(*brush_color))
        rect = QRectF(self.begin, self.end)
        qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = QPointF(event.pos())
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = QPointF(event.pos())
        self.update()

    def mouseReleaseEvent(self, event):
        SnippingWidget.is_snipping = False
        QApplication.restoreOverrideCursor()
        
        # map to global position to omit shift from the header
        self.begin = self.mapToGlobal(self.begin.toPoint())
        self.end = self.mapToGlobal(self.end.toPoint())
        
        x1 = int(min(self.begin.x(), self.end.x()))
        y1 = int(min(self.begin.y(), self.end.y()))
        x2 = int(max(self.begin.x(), self.end.x()))
        y2 = int(max(self.begin.y(), self.end.y()))

        self.repaint()
        QApplication.processEvents()

        self.onSnippingCompleted([x1 - self.offset[0], y1 - self.offset[1], x2 - x1, y2 - y1])

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))

        self.close()

  
    
if __name__ == '__main__':
    
    w = 600
    h = 600
    x = 0
    y = 0

    region = {
        'x0': x,
        'y0': y,
        'width': w,
        'height': h
    }

    app = QApplication(sys.argv)

    app.setStyle('Windows')
    app.setFont( QFont('Segoe UI', 10) )

    with open('styles.qss', 'r') as f:
        style = f.read()
        app.setStyleSheet(style)

    window = MainWindow(region)
    window.show()

    app.exec()