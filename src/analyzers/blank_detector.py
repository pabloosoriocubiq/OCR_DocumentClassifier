from PIL import Image
import numpy as np
from src.utils.logger import Logger


class BlankPageDetector:
 
    def __init__(self, threshold: float = 0.975):
        
        self.threshold = threshold
        self.logger = Logger.get_logger(__name__)
    
    def is_blank_page(self, image: Image.Image) -> bool:
       
        grayscale = image.convert('L')
        
        pixels = np.array(grayscale)
        
        very_white_pixels = np.sum(pixels > 240)
        total_pixels = pixels.size
        white_percentage = very_white_pixels / total_pixels
        #std_dev = np.std(pixels)
        #pixel_range = np.max(pixels) - np.min(pixels)
        
        is_blank = (
            white_percentage >= self.threshold #and
            #std_dev < 10 and
            #pixel_range < 30
        )
        
        if is_blank:
            self.logger.debug(
                f"      Página vacía detectada: {white_percentage:.1%} blancos, "
                #f"std: {std_dev:.1f}, rango: {pixel_range}"
            )
        else:
            self.logger.debug(
                f"      Página CON contenido: {white_percentage:.1%} blancos, "
                #f"std: {std_dev:.1f}, rango: {pixel_range}"
            )
        
        return is_blank
    
    def get_blank_percentage(self, image: Image.Image) -> float:
       
        grayscale = image.convert('L')
        pixels = np.array(grayscale)
        white_pixels = np.sum(pixels > 240)
        total_pixels = pixels.size
        
        return white_pixels / total_pixels