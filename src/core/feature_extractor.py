import logging
import os
import sys

logger = logging.getLogger('malware_detection')

# Try to import magic, but don't fail if it's not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available, skipping MIME type detection")


def extract_features(file_path):
    """Extract features from a file"""
    features = {
        'file_size': 0,
        'entropy': 0.0,
        'num_sections': 0,
        'num_imports': 0,
        'has_debug': 0,
        'has_reloc': 0,
        'string_count': 0,
        'suspicious_apis': 0,
        'packed': 0
    }
    
    try:
        # Get file size
        if os.path.exists(file_path):
            features['file_size'] = os.path.getsize(file_path)
            
            # Calculate entropy
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    features['entropy'] = calculate_entropy(data)
            except Exception as e:
                logger.warning(f"Could not calculate entropy: {e}")
            
            logger.info(f"Extracted features from: {file_path}")
        else:
            logger.warning(f"File not found: {file_path}")
    
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
    
    return features


def calculate_entropy(data):
    """Calculate Shannon entropy of data"""
    import math
    from collections import Counter
    
    if not data:
        return 0.0
    
    entropy = 0.0
    for count in Counter(data).values():
        p = count / len(data)
        entropy -= p * math.log2(p)
    
    return entropy