from enum import Enum

class DisplayModes(str, Enum):
    
    Default = 'Default Image'
    ColorContrast = 'Contrast Color (CC)'
    GrayscaleContrast = 'Contrast Grayscale (CG)'