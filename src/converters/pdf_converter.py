from pathlib import Path
from typing import List, Dict, Generator
import fitz  # PyMuPDF
from PIL import Image
import io
import gc

from src.utils.logger import Logger
from src.config import PDF_DPI, CLEAR_MEMORY_AFTER_PAGE


class PDFConverter:
    
    def __init__(self, dpi: int = PDF_DPI):
        
        self.dpi = dpi
        self.zoom = dpi / 72
        self.matrix = fitz.Matrix(self.zoom, self.zoom)
        self.logger = Logger.get_logger(__name__)
    
    def convert_pdf_pages(self, pdf_path: Path) -> Generator[Dict, None, None]:
                                            #Yields: Dict con información de la página procesada
       
        try:
            self.logger.info(f"** Abriendo PDF: {pdf_path.name}")
            pdf_document = fitz.open(pdf_path)
            total_pages = pdf_document.page_count
            
            self.logger.info(f"   Total de páginas: {total_pages}")
            
            for page_num in range(total_pages):
                # Renderizar página
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=self.matrix, alpha=False)
                
                # Convertir a PIL Image en memoria
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Información de la página
                page_info = {
                    'page_number': page_num + 1,
                    'image': image,  # Imagen en memoria
                    'size': image.size,
                    'success': True
                }
                
                pix = None
                
                self.logger.debug(f"   ✔ Página {page_num + 1} convertida en memoria")
                
                yield page_info
                
                
                if CLEAR_MEMORY_AFTER_PAGE:
                    del image
                    gc.collect()
            
            pdf_document.close()
            self.logger.info(f"✔ PDF procesado: {total_pages} páginas")
            
        except Exception as e:
            self.logger.error(f"✗ Error convirtiendo PDF {pdf_path.name}: {str(e)}")
            yield {
                'page_number': 0,
                'image': None,
                'success': False,
                'error': str(e)
            }
    
    def get_pdf_info(self, pdf_path: Path) -> Dict:
        
        try:
            pdf_document = fitz.open(pdf_path)
            info = {
                'filename': pdf_path.name,
                'path': str(pdf_path),
                'total_pages': pdf_document.page_count,
                'success': True
            }
            pdf_document.close()
            return info
        except Exception as e:
            self.logger.error(f"✗ Error obteniendo info de {pdf_path.name}: {str(e)}")
            return {
                'filename': pdf_path.name,
                'success': False,
                'error': str(e)
            }