from pathlib import Path
from typing import List, Dict, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager
import traceback

from src.utils.logger import Logger
from src.config import MAX_PARALLEL_WORKERS


class ParallelProcessor:

    
    def __init__(self, max_workers: int = MAX_PARALLEL_WORKERS):

        self.max_workers = max_workers
        self.logger = Logger.get_logger(__name__)
    
    def process_pdfs_parallel(self, 
                             pdf_files: List[Path],
                             process_func: Callable,
                             *args,
                             **kwargs) -> List[Dict]:
       
        if len(pdf_files) == 1:

            self.logger.info("📄 Solo 1 PDF, procesamiento secuencial")
            return [process_func(pdf_files[0], *args, **kwargs)]
        
        self.logger.info(
            f"⚡ Procesamiento paralelo activado: {len(pdf_files)} PDFs, "
            f"{self.max_workers} workers"
        )
        
        results = []
        completed_count = 0
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar todos los trabajos
            future_to_pdf = {
                executor.submit(process_func, pdf_file, *args, **kwargs): pdf_file
                for pdf_file in pdf_files
            }
            
            for future in as_completed(future_to_pdf):
                pdf_file = future_to_pdf[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    self.logger.info(
                        f"✓ Completado [{completed_count}/{len(pdf_files)}]: {pdf_file.name}"
                    )
                    
                except Exception as e:
                    self.logger.error(
                        f"❌ Error procesando {pdf_file.name}: {str(e)}"
                    )
                    self.logger.debug(traceback.format_exc())
                    
                    # Agregar resultado de error
                    results.append({
                        'pdf_name': pdf_file.name,
                        'success': False,
                        'error': str(e)
                    })
        
        self.logger.info(f"✓ Procesamiento paralelo completado: {len(results)} resultados")
        
        return results
    
    def estimate_optimal_workers(self, num_pdfs: int, num_cores: int = None) -> int:
       
        if num_cores is None:
            num_cores = self.max_workers
        
        # No usar más workers que PDFs
        optimal = min(num_pdfs, num_cores)
        
        # Mínimo 1, máximo el configurado
        optimal = max(1, min(optimal, self.max_workers))
        
        return optimal