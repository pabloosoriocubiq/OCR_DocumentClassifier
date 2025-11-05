from typing import Tuple
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
from paddleocr import DocImgOrientationClassification
from paddle.vision.transforms import functional as F

from src.utils.logger import Logger
from src.config import (
    OCR_LANGUAGE, 
    OCR_USE_ANGLE_CLS,
    ENABLE_ROI_OCR,
    ROI_HEADER_PERCENTAGE,
    ROI_CONFIDENCE_THRESHOLD,
    ANGLE_TOLERANCE,
    ROI_FOOTER_PERCENTAGE
)

def rotate_image_without_cropping(image, angle):

    import cv2
    height, width = image.shape[:2]
    image_center = (width / 2, height / 2)

    # Get the 2D rotation matrix
    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)

    # Calculate the new bounding box dimensions
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # Adjust the rotation matrix to center the rotated image
    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    # Perform the affine transformation
    rotated_image = cv2.warpAffine(image, rotation_mat, (bound_w, bound_h))
    return rotated_image

class OCRProcessor:
    
    def __init__(self, lang: str = OCR_LANGUAGE):

        self.logger = Logger.get_logger(__name__)
        self.logger.info(f"✓ Inicializando PaddleOCR (idioma: {lang})...")
        
        try:
            self.ocr = PaddleOCR(
                use_textline_orientation= OCR_USE_ANGLE_CLS,
                lang=lang,
                device = "cpu"
            )
            self.document_orientation = DocImgOrientationClassification(model_name="PP-LCNet_x1_0_doc_ori")
            self.logger.info("✓ PaddleOCR inicializado correctamente")
        except Exception as e:
            self.logger.error(f"✗ Error inicializando PaddleOCR: {str(e)}")
            raise
    
    def extract_header_region(self, image: Image.Image) -> Image.Image:

        width, height = image.size
        header_height = int(height * ROI_HEADER_PERCENTAGE)
        
        # Recorte
        header_region = image.crop((0, 0, width, header_height))
        return header_region
    
    def extract_footer_region(self, image: Image.Image) -> Image.Image:

        width, height = image.size
        footer_height = int(height * ROI_FOOTER_PERCENTAGE)
        footer_start = height - footer_height
        footer_region = image.crop((0, footer_start, width, height))
        return footer_region
    
    def extract_text_from_region(self, image: Image.Image) -> Tuple[str, float]:

        try:
            img_array = np.array(image)
            
            result = self.ocr.predict(input=img_array)
            
            if not result or not result[0]:
                return "", 0.0
            
            # Extraer textos y confianzas
            texts = []
            confidences = []
            
            for line in result:
                
                text = line['rec_texts']
                confidence = line['rec_scores']
                texts.append(text)
                confidences.append(confidence)
        
            if len(text) == 0:
                return "", 0.0
            else:   
                full_text = ' '.join(texts[0])
                avg_confidence = sum(confidences[0]) / len(confidences[0])
                return full_text, avg_confidence
            
    
        except Exception as e:
            self.logger.error(f" Error en OCR de región: {str(e)}")

            return "", 0.0
    
    def extract_text_from_image(self, image: Image.Image,) -> Tuple[str, float]:

        return self.extract_text_from_region(image)
    
    def extract_text_roi_strategy(self, image: Image.Image, need_footer: bool) -> Tuple[str, float, bool]:
 
        if not ENABLE_ROI_OCR:

            text, confidence = self.extract_text_from_image(image)
            return text, confidence, False
        
        if not need_footer:
            header_region_image = self.extract_header_region(image)
            header_text, header_confidence = self.extract_text_from_region(header_region_image)
            
            has_useful_content = (
                header_confidence >= ROI_CONFIDENCE_THRESHOLD and 
                len(header_text) > 30 and
                len(header_text.strip()) > 10  # No solo espacios
                
            )
            if has_useful_content:
                return header_text, header_confidence, True
        
        else:
            footer_region_image = self.extract_footer_region(image)
            footer_text, footer_confidence = self.extract_text_from_region(footer_region_image)
                
            has_useful_content = (
                footer_confidence >= ROI_CONFIDENCE_THRESHOLD and 
                len(footer_text) > 5 and
                len(footer_text.strip()) > 5  # No solo espacios
                )
            if has_useful_content:
                return footer_text, footer_confidence, True
        
        full_text, full_confidence = self.extract_text_from_image(image)
        
        return full_text, full_confidence, False
    
    def document_orientation_angle(self, image: Image.Image) -> Tuple[float, float]:
        
            try: 
                img_array = np.array(image)
                result = self.document_orientation.predict(img_array)
                if not result or not result[0]:
                    return "", 0.0
                
                for line in result: 
                    angle = line['label_names'][0]
                    confidence = float(line['scores'][0])
                    final_angle = float(angle)          
                       
                return final_angle, confidence
            
            except Exception as e:
                self.logger.error(f" Error en OCR de región: {str(e)}")
                return 0.0, 0.0
            
        
    def rotate_image_by_angle(self, image, final_angle, confidence):
            import cv2
            
            if abs(final_angle - 90) <= ANGLE_TOLERANCE:
                self.logger.info("   Se detecta imagen rotada a la derecha, se realiza corrección.")
                opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                image = rotate_image_without_cropping(opencvImage, 90)
                return image
            elif abs(final_angle - 180) <= ANGLE_TOLERANCE:
                self.logger.info("   Se detecta imagen al revés, se realiza corrección.")
                opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                image = rotate_image_without_cropping(opencvImage, 180)
                return image
            elif abs(final_angle - 270) <= ANGLE_TOLERANCE:
                self.logger.info("   Se detecta imagen rotada a la izquierda, se realiza corrección.")
                opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                image = rotate_image_without_cropping(opencvImage, -90)
                return image

        