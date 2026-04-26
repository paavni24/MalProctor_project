from flask import Blueprint, request, jsonify
from src.core.feature_extractor import extract_features
from src.core.malware_detector import predict_sample

api_bp = Blueprint('api', __name__)

@api_bp.route('/scan', methods=['POST'])
def scan_apk():
    data = request.json
    if not data or 'features' not in data:
        return jsonify({'error': 'No features provided'}), 400

    features = data['features']
    label, probability = predict_sample(features)

    result = {
        'label': 'Malware' if label == 1 else 'Benign',
        'probability': probability
    }
    return jsonify(result), 200

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200