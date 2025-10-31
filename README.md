# PDF OCR Document Classifier

Sistema automatizado de clasificación y separación de documentos PDF usando PaddleOCR.

## 📋 Descripción

Procesa PDFs mixtos, clasifica páginas por tipo (Invoice, Packing List, etc.) y genera PDFs separados eliminando documentos no funcionales.

## 🚀 Características

- Detección automática de orientación y rotación de imágenes
- OCR inteligente con estrategia ROI (35% superior de la página)
- Clasificación basada en keywords primary/secondary
- Generación de reportes JSON/TXT
- Procesamiento paralelo opcional

## 🛠️ Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/pabloosoriocubiq/OCR_DocumentClassifier.git
cd pdf-ocr-classifier
```

2. Crear entorno virtual:
```bash
python -m venv venv_ocr
source venv_ocr/bin/activate  # Mac/Linux
venv_ocr\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 📦 Uso
```bash
python main.py
```

Coloca tus PDFs en la carpeta `pdfs/` y el sistema generará:
- PDFs separados en `pdfs_procesados/`
- Reportes en `clasificacion/`

## 🔧 Configuración

Edita `src/config.py` para ajustar:
- `ENABLE_ROI_OCR`: Activar/desactivar estrategia ROI
- `ROI_HEADER_PERCENTAGE`: Porcentaje de la página a analizar


## 👤 Autor

Pablo Osorio - [@pabloosoriocubiq]