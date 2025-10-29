"""Configuración con secondary keywords para validación de contexto."""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PDF_INPUT_FOLDER = BASE_DIR / "pdfs"
CLASSIFICATION_FOLDER = BASE_DIR / "clasificacion"
PDF_OUTPUT_FOLDER = BASE_DIR / "pdfs_procesados"

PDF_DPI = 300
IMAGE_FORMAT = "PNG"

OCR_LANGUAGE = "en"
OCR_USE_GPU = False
OCR_USE_ANGLE_CLS = True

CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.25
TEXT_PREVIEW_LENGTH = 400
EARLY_STOPPING_CONFIDENCE = 0.55

ENABLE_PARALLEL_PROCESSING = False
MAX_PARALLEL_WORKERS = 2

ENABLE_ROI_OCR = True
ROI_HEADER_PERCENTAGE = 0.4
ROI_FOOTER_PERCENTAGE = 0.3
ROI_CONFIDENCE_THRESHOLD = 0.75
ANGLE_TOLERANCE = 5
ANGLE_CONFIDENCE_THRESHOLD = 0.70

DOCUMENT_TYPES = {
    'INVOICE': {
        'primary_keywords': ['invoice', 'fatura', 'commercial invoice', 'original invoice'],
        'secondary_keywords': [
            'payment terms', 'terms of payment', 'value', 'deduction',
            'invoice #', 'net 30', 'net 30 days', 'tracking',
            'amount due', 'balance due', 'tax', 'tax rate', 'number', 'amount',
            'subtotal', 'tax amount', 'invoice', 'total amount', 'unit', 'unit price',
            'extended price', 'price', '(usd)', 'usd', 'freight', 'products',
            'remit to', 'wire transfer', 'swift code', 'IRN', 'purchase',
            'invoice number', 'commercial', 'description', 'point', 'account',
            'bank account', 'account number', 'customer po', 'po box',
            'salesorder', 'completed salesorder', 'po number', 'swift',
            'tax id', 'tax registration', 'order', 'p.o', 'direct inquiries',
            'customs invoice', 'csi', '$', 'customer', 'sales', 'bank',
            'bill to', 'billed to', 'sold to', 'delivery point', 'buyer',
            'ship from', 'ship to', 'ship via', 'sales representative',
            'your tax number', 'discount', 'payment method'
        ],
        'min_secondary_matches': 3, 
        'functional': True,
        'priority': 100
    },
    
    'PACKING_LIST': {
        'primary_keywords': ['packing list', 'packinglist', 'packing list', 'packlist'],
        'secondary_keywords': [
            'your order no', 'delivery no', 'packing list', 'package', 'part number',
            'delivery per', 'lb', 'swift code', 'total weight', 'carton',
            'shipping method', 'quantity ordered', 'quantity shipped',
            'gross weight', 'net weight', 'oty', 'stock', 'bill to', 'company',
            'ship to', 'shipped to', 'packed by', 'pieces', 'po', 'customer po',
            'lb', 'kg', 'quantity', 'qty', 'net', 'purchase order', 'po#', 'item',
            'terms of delivery', 'delivery terms', 'exw', 'fob', 'gross', 'order',
            'pos', 'material', 'coo', 'dimensions', 'packaging', 'meauserement', 'lot code',
            'quant', 'incoterms', 'shipped', 'total shipped', 'packing list no',
            'purchase order number', 'packing list number', 'pkg', 'shipment', 'addendum',
            'shipper:', 'shipped to', 'wt', 'dim', 'inches', 'packed', 'shipment number',
            'box', 'boxes', 'cartons', 'pos', 'sales', 'sales order', 'ship via',
            'item number', 'rel', 'packed qty', 'u/m', 'ea'],
        'min_secondary_matches': 3,
        'functional': True,
        'priority': 90
    },
    
    'PACKING_SLIP': {
        'primary_keywords': ['packing slip', 'packingslip', 'packing slip', 'pack slip'],
        'secondary_keywords': [

            'shipment reference', 'tracking number',
            'customer', 'partner', 'packing slip', 'bill to', 'ship to',
            'load', 'unit', 'lb', 'kg', 'delivery terms', 'terms of delivery',
            'shipped to', 'load', 'ship via', 'terms', 'kg', 'order', 'order number',
            'package quantity', 'shipped quantity', 'gross', 'pos',
            'back order', 'weight', 'boxes', 'content', 'contents',
            'ship-from warehouse', 'total weight',
            'ordered', 'shipped', 'line item', 'catalog', 'qty', 'oty',
            'um', 'ship from', 'pack', 'pack date', 'uom', 
            'license type', 'license number', 'packing details', 'condition',
            'serial number', 'po no', 'pack slip', 'pack slip No',
            'shipped to', 'exporter', 'ship from', 'waybill'
        ],
        'min_secondary_matches': 3,
        'functional': True,
        'priority': 80
    },
    
    'CERTIFICATE_ORIGIN': {
        'primary_keywords': [
            'certificate of origin', 'certificate', 'certificate of conformance'
        ],
        'secondary_keywords': [
            'conformance', 'manufacturer', 'approving', 'faa', 'faa form',
            'hts number', 'hts code', 'order number', 'organization', 'mouser',
            'harmonized', 'customs', 'material', 'covered', 'tracking', 'hts',
            'eccn', 'country', 'consignee', 'authority', 'approval', 'distributor',
            'coo', 'certify', 'date', 'p.o', 'serial number', 'purchase order',
            'tariff', 'autorized', 'approval', 'authorized', 'manufacturers', "MANUFACTURERS'",
            'listing', 'below'
        ],
        'min_secondary_matches': 2,
        'functional': False,
        'priority': 10
    },
    
    'CARTAGE_ADVICE': {
        'primary_keywords': [
            'cartage advice',
            'booking details'
        ],
        'secondary_keywords': [
            'transport booking',
            'transport company',
            'pick up:', 'delivery:',
            'instructions details',
            'shipment:'
        ],
        'min_secondary_matches': 2,
        'functional': False,
        'priority': 10
    }, 
    
    'KNOWN_SHIPPER': {
        'primary_keywords': [
            'known shipper cargo', 'known shipper', 'id check'
        ],
        'secondary_keywords': [
            'blank', 'reviewed', 'matching', 'photo',
            'ground', 'type', 'first', 'id', 'indicate',
            'global', 'government', 'authority', 'time'  
              ],
        'min_secondary_matches': 4,
        'functional': False,
        'priority': 10
    },

    'DELIVERY_NOTE': {
        'primary_keywords': [
            'delivery note', 'delivery receipt'
        ],
        'secondary_keywords': ['terms of delivery', 'responsible is', 'customer',
                               'responsible', 'number', 'reference', 'reference number',
                               'our order no', 'customer number',
                               'fax', 'responsible is', 'waybill', 'copy', 'prepaid',
                               'collect'],
        'min_secondary_matches': 2,
        'functional': False,
        'priority': 10
    },
    
    'SHIPPER_INSTRUCTIONS': {
        'primary_keywords': [
            "shipper's letter of instructions",
            'sli',
            'shipping instructions',
            'letter of instructions',
            'shipper instructions'
        ],
        'secondary_keywords': [
            'freight', 'model', 'USPPI', 'party', 'parties',
            'related party', 'related parties', 'sli', 'id',
            'controls', 'goods', 'nordson',
            'fed id#', 'notify', 'distribution', 'instructions',
            'model', 'bill', 'fed', 'fordwarder', 'consignee',
            'ein', 'irs', 'password', 'zip code',  'comodity',
            'forwarding', 'indicator', 'type', 'export'],
        'min_secondary_matches': 3,
        'functional': False,
        'priority': 5
    }
}

# LOGGING
LOG_FILE = BASE_DIR / "pdf_processing.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5

# PERFORMANCE
ENABLE_EARLY_STOPPING = True
CLEAR_MEMORY_AFTER_PAGE = True