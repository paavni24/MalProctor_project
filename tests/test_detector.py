import pytest
import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.malware_detector import load_data, apply_smote, predict_sample


class TestMalwareDetector:
    """Test malware detection system"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample test data"""
        np.random.seed(42)
        data = {
            'file_size': np.random.randint(1000, 50000000, 100),
            'entropy': np.random.uniform(2, 7, 100),
            'num_sections': np.random.randint(2, 15, 100),
            'num_imports': np.random.randint(5, 100, 100),
            'has_debug': np.random.choice([0, 1], 100),
            'has_reloc': np.random.choice([0, 1], 100),
            'string_count': np.random.randint(10, 500, 100),
            'suspicious_apis': np.random.randint(0, 30, 100),
            'packed': np.random.choice([0, 1], 100),
            'class': np.random.choice([0, 1], 100)
        }
        return pd.DataFrame(data)
    
    def test_load_data(self):
        """Test data loading"""
        try:
            X_train, X_test, y_train, y_test = load_data()
            assert X_train is not None
            assert X_test is not None
            assert y_train is not None
            assert y_test is not None
            assert len(X_train) > 0
            assert len(X_test) > 0
        except FileNotFoundError:
            pytest.skip("Dataset not found - run create_dataset.py first")
    
    def test_smote_application(self, sample_data):
        """Test SMOTE balancing"""
        X = sample_data.drop('class', axis=1)
        y = sample_data['class']
        
        X_bal, y_bal = apply_smote(X, y)
        
        assert X_bal is not None
        assert y_bal is not None
        assert len(X_bal) >= len(X)
        assert len(y_bal) >= len(y)
    
    def test_predict_sample(self):
        """Test sample prediction"""
        try:
            feature_dict = {
                'file_size': 1000000,
                'entropy': 5.5,
                'num_sections': 5,
                'num_imports': 30,
                'has_debug': 0,
                'has_reloc': 1,
                'string_count': 100,
                'suspicious_apis': 10,
                'packed': 1
            }
            label, prob = predict_sample(feature_dict)
            
            assert label in [0, 1], "Label should be 0 or 1"
            assert 0 <= prob <= 1, "Probability should be between 0 and 1"
        except FileNotFoundError:
            pytest.skip("Model not trained - run malware_detector.py first")