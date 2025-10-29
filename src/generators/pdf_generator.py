from pathlib import Path
from typing import List, Dict
import fitz  # PyMuPDF

from src.utils.logger import Logger
from src.config import PDF_OUTPUT_FOLDER


class PDFGenerator:
 
    
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.output_folder = PDF_OUTPUT_FOLDER
        self.output_folder.mkdir(exist_ok=True)
    
    def generate_separated_pdfs(self, 
                                pdf_path: Path,
                                document_groups: List[Dict]) -> List[Dict]:
        
        if not document_groups:
            self.logger.warning(f"* No hay grupos de documentos para {pdf_path.name}")
            return []
        
        pdf_name = pdf_path.stem
        
        output_folder = self.output_folder
        output_folder.mkdir(exist_ok=True)

        try:
            pdf_document = fitz.open(pdf_path)
        except Exception as e:
            self.logger.error(f"X Error abriendo PDF {pdf_path.name}: {str(e)}")
            return []
        
        generated_pdfs = []
        
        type_counter = {}
        
        for group in document_groups:
            doc_type = group['type'].lower()
            pages = group['pages']
            
            if doc_type in type_counter:
                type_counter[doc_type] += 1
                output_filename = f"{pdf_name}_{doc_type}_{type_counter[doc_type]}.pdf"
            else:
                type_counter[doc_type] = 1
                output_filename = f"{pdf_name}_{doc_type}.pdf"
            
            try:
                new_pdf = fitz.open()
                
                for page_num in pages:

                    new_pdf.insert_pdf(pdf_document, from_page=page_num-1, to_page=page_num-1)
                
                output_path = output_folder / output_filename
                new_pdf.save(output_path)
                new_pdf.close()
                
                pdf_info = {
                    'type': group['type'],
                    'pages': pages,
                    'filename': output_filename,
                    'path': str(output_path),
                    'page_count': len(pages)
                }
                generated_pdfs.append(pdf_info)
                
                self.logger.info(
                    f"  ✓ {output_filename} (páginas {pages[0]}-{pages[-1]}, "
                    f"total: {len(pages)})"
                )
                
            except Exception as e:
                self.logger.error(f"X  Error generando PDF {doc_type}: {str(e)}")
                continue
        
        pdf_document.close()
        
        self.logger.info(f"✓ Generados {len(generated_pdfs)} PDF")
        return generated_pdfs