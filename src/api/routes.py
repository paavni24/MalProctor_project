from flask import Blueprint, request, jsonify
from src.core.malware_detector import predict_sample
import os

api = Blueprint('api', __name__)

@api.route('/scan', methods=['POST'])
def scan_file():
    if not request.json or 'features' not in request.json:
        return jsonify({'error': 'No features provided'}), 400

    features = request.json['features']
    label, probability = predict_sample(features)

    return jsonify({
        'label': 'Malware' if label else 'Benign',
        'probability': probability
    })

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200