from pathlib import Path
from typing import Dict
import gc
from datetime import datetime
import cv2
from PIL import Image
from src.config import (
    PDF_INPUT_FOLDER,
    LOG_FILE,
    LOG_LEVEL,
    ENABLE_ROI_OCR, ANGLE_CONFIDENCE_THRESHOLD
)
from src.utils.logger import setup_logging
from src.converters.pdf_converter import PDFConverter
from src.processors.ocr_processor import OCRProcessor
from src.processors.classifier import DocumentClassifier
from src.generators.pdf_generator import PDFGenerator

class DocumentProcessor:
    
    def __init__(self):
        
        self.logger = setup_logging(LOG_FILE, LOG_LEVEL)
        self.logger.info("  Inicializando sistema...")     
        self.converter = PDFConverter()
        self.ocr = OCRProcessor()
        self.classifier = DocumentClassifier()
        self.generator = PDFGenerator()
        self.logger.info("✔ Sistema listo\n")
    
    def process_pdf(self, pdf_path: Path) -> Dict:
        
        self.logger.info("="*70)
        self.logger.info(f"PROCESANDO: {pdf_path.name}")
        self.logger.info("="*70)
        
        start_time = datetime.now()
        
        pdf_info = self.converter.get_pdf_info(pdf_path)
        if not pdf_info['success']:
            return {'success': False, 'error': 'No se pudo leer el PDF ✗'}
        
        total_pages = pdf_info['total_pages']
        classifications = []
        roi_count = 0
        
        for page_data in self.converter.convert_pdf_pages(pdf_path):
            if not page_data['success']:
                continue
            
            page_num = page_data['page_number']
            image = page_data['image']
            
            self.logger.info(f"📄 Procesando página {page_num}/{total_pages}")
            
            if ENABLE_ROI_OCR:
                
                angle, ocr_angle_confidence = self.ocr.document_orientation_angle(image)
                
                if angle > 0 and ocr_angle_confidence > ANGLE_CONFIDENCE_THRESHOLD:
                    image = self.ocr.rotate_image_by_angle(image, angle, ocr_angle_confidence)
                    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)               
                    image = Image.fromarray(img)
                    text, ocr_confidence, used_roi_only = self.ocr.extract_text_roi_strategy(image)
                else:
                    text, ocr_confidence, used_roi_only = self.ocr.extract_text_roi_strategy(image)  
                             
                doc_type_tmp, primary_found_tmp, secondary_found_tmp, total_keywords_tmp, num_candidates_tmp = self.classifier.classify_page(text)
                keywords = primary_found_tmp + secondary_found_tmp
                roi_usage = False
                    
                if num_candidates_tmp >=2:
                    roi_usage = False
                elif doc_type_tmp == "UNKNOWN" and len(keywords) == 0:
                    roi_usage = False
                else:
                    doc_config = self.classifier.document_types.get(doc_type_tmp, {})
                    is_functional = doc_config.get('functional', False)
                    min_secondary = doc_config.get('min_secondary_matches', 0)
                        
                    if is_functional:
                            
                        if len(secondary_found_tmp) > min_secondary:
                            roi_usage = True                       
                        else:
                            roi_usage = False
                    else:
                        roi_usage = True
                    
                if roi_usage:

                    doc_type = doc_type_tmp
                    primary_found = primary_found_tmp
                    secondary_found = secondary_found_tmp
                    total_keywords = total_keywords_tmp
                    num_candidates = num_candidates_tmp
                    keywords = primary_found + secondary_found
                    roi_count += 1
                else:
                    text, ocr_confidence = self.ocr.extract_text_from_image(image)
                    image.save("demo2.png")                                   
                    doc_type, primary_found, secondary_found, total_keywords, num_candidates = self.classifier.classify_page(text)
                    keywords = primary_found + secondary_found
                    used_roi_only = False 
            else:
                angle, ocr_angle_confidence = self.ocr.document_orientation_angle(image)
                image = self.ocr.rotate_image_by_angle(image, angle, ocr_angle_confidence)
                text, ocr_confidence = self.ocr.extract_text_from_image(image)
                doc_type, primary_found, secondary_found, total_keywords, num_candidates = self.classifier.classify_page(text)
                keywords = primary_found + secondary_found
                used_roi_only = False 
            

            is_functional = self.classifier.is_functional(doc_type)

            classification = {
                'page_number': page_num,
                'document_type': doc_type,
                'functional': is_functional,
                'ocr_confidence': round(ocr_confidence, 4),
                'keywords_found': keywords,
                'used_roi': used_roi_only,
                'is_blank': False
            }
            classifications.append(classification)
            
            status = "✓" if is_functional else "✗"
            roi_indicator = " [ROI]" if used_roi_only else ""
            self.logger.info(
                f"   {doc_type} {status}{roi_indicator} "
                f"(keywords: {total_keywords})"
            )
            
            del image
            gc.collect()
        
        document_groups = self.classifier.group_consecutive_pages(classifications)

        self.classifier.save_classification_report(
            pdf_path.name,
            classifications,
            document_groups
        )
        
        generated_pdfs = self.generator.generate_separated_pdfs(
            pdf_path,
            document_groups
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        functional_pages = sum(1 for c in classifications if c['functional'])
        
        result = {
            'pdf_name': pdf_path.name,
            'total_pages': total_pages,
            'functional_pages': functional_pages,
            'non_functional_pages': total_pages - functional_pages,
            'pdfs_generated': len(generated_pdfs),
            'generated_files': generated_pdfs,
            'processing_time': processing_time,
            'roi_optimizations': roi_count,
            'success': True
        }
        
        self.logger.info(f"\n✓ Completado en {processing_time:.2f}s")
        self.logger.info(
            f"   Páginas: {functional_pages} funcionales, "
            f"{total_pages - functional_pages} eliminadas"
        )
        if ENABLE_ROI_OCR and roi_count > 0:
            self.logger.info(f"   Optimización ROI: {roi_count}/{total_pages} páginas")
        self.logger.info(f"   PDFs generados: {len(generated_pdfs)}\n")
        
        return result
    
    def process_all_pdfs(self) -> Dict:
        pdf_files = list(PDF_INPUT_FOLDER.glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning("X  No se encontraron archivos PDF en la carpeta")
            return {
                'success': False,
                'message': 'No se encontraron PDFs para procesar'
            }
        
        self.logger.info(f"Se encontraron {len(pdf_files)} PDFs para procesar\n")
        
        overall_start = datetime.now()
        

        self.logger.info(f" Procesamiento secuencial\n")
        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            self.logger.info(f" **Progreso: {i}/{len(pdf_files)}")
            result = self.process_pdf(pdf_file)
            results.append(result)
            gc.collect()
        
        successful = [r for r in results if r.get('success', False)]
        total_time = (datetime.now() - overall_start).total_seconds()
        total_pages = sum(r.get('total_pages', 0) for r in successful)
        total_functional = sum(r.get('functional_pages', 0) for r in successful)
        total_generated = sum(r.get('pdfs_generated', 0) for r in successful)
        total_roi_optimizations = sum(r.get('roi_optimizations', 0) for r in successful)
        
        self.logger.info("\n" + "="*70)
        self.logger.info("  * RESUMEN FINAL *")
        self.logger.info("="*70)
        self.logger.info(f"PDFs procesados: {len(successful)}/{len(pdf_files)}")
        self.logger.info(f"Tiempo total: {total_time:.2f}s")
        
        avg_time = total_time / len(successful) if successful else 0
        self.logger.info(f"Tiempo promedio por PDF: {avg_time:.2f}s")
        
        self.logger.info(f"Páginas analizadas: {total_pages}")
        self.logger.info(f"Páginas funcionales: {total_functional}")
        self.logger.info(f"Páginas eliminadas: {total_pages - total_functional}")
        self.logger.info(f"PDFs generados: {total_generated}")
        
        if ENABLE_ROI_OCR and total_roi_optimizations > 0:
            roi_percentage = (total_roi_optimizations / total_pages) * 100 if total_pages > 0 else 0
            self.logger.info(f"Optimizaciones ROI: {total_roi_optimizations}/{total_pages} ({roi_percentage:.1f}%)")
        
        self.logger.info("="*70 + "\n")
        
        return {
            'total_pdfs': len(pdf_files),
            'successful': len(successful),
            'failed': len(pdf_files) - len(successful),
            'total_pages': total_pages,
            'functional_pages': total_functional,
            'pdfs_generated': total_generated,
            'roi_optimizations': total_roi_optimizations,
            'total_time': total_time,
            'avg_time_per_pdf': avg_time,
            'results': results,
            'success': True
        }



def main():
    PDF_INPUT_FOLDER.mkdir(exist_ok=True)
    
    processor = DocumentProcessor()
    results = processor.process_all_pdfs()
    
    if results['success']:
        processor.logger.debug("\n✔ PROCESAMIENTO COMPLETADO")
        processor.logger.debug(f"PDFs procesados: {results['successful']}/{results['total_pdfs']}")
        processor.logger.debug(f"Tiempo total: {results['total_time']:.2f}s")


if __name__ == "__main__":
    main()