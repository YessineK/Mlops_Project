import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

# Add backend/src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'src'))

# Mock mlflow before importing api
sys.modules['mlflow'] = MagicMock()
sys.modules['mlflow.pyfunc'] = MagicMock()

from api import app, InferencePreprocessor

client = TestClient(app)

# Mock data for testing
sample_data = {
    "trans_date_trans_time": "2025-01-01 12:00:00",
    "amt": 100.0,
    "lat": 40.0,
    "long": -74.0,
    "merch_lat": 40.1,
    "merch_long": -74.1,
    "category": "grocery_pos",
    "gender": "M",
    "state": "NY",
    "job": "Developer",
    "dob": "1990-01-01"
}

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.predict.return_value = np.array([0])
    return model

@pytest.fixture
def mock_preprocessor():
    prep = MagicMock()
    prep.preprocess_inference.return_value = pd.DataFrame([[0.5, 0.2]], columns=['f1', 'f2'])
    prep.feature_names = {
        'numerical_features': ['amt', 'distance_km'],
        'categorical_features': ['category'],
        'all_features': ['amt', 'distance_km', 'category_encoded']
    }
    return prep

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_health_check_degraded():
    # Initially model might be None if mock didn't set global
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

@patch('api.model')
@patch('api.preprocessor')
def test_predict_endpoint(mock_prep, mock_mod):
    # Setup mocks
    mock_mod.predict.return_value = np.array([0])
    mock_prep.preprocess_inference.return_value = pd.DataFrame([1])
    
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    assert "predictions" in response.json()
    assert response.json()["predictions"] == [0]

@patch('api.model')
@patch('api.preprocessor')
def test_predict_csv_endpoint(mock_prep, mock_mod):
    # Setup mocks
    mock_mod.predict.return_value = np.array([0])
    mock_prep.preprocess_inference.return_value = pd.DataFrame([1])
    
    # Create dummy CSV
    csv_content = "amt,lat,long\n100,40,-74"
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    
    response = client.post("/predictCSV", files=files)
    assert response.status_code == 200
    # Verify it returns a CSV file
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    
    # Check content
    content = response.content.decode('utf-8')
    assert "predict" in content
    assert "0" in content

def test_inference_preprocessor_structure():
    # Test that the class exists and has the method
    prep = InferencePreprocessor()
    assert hasattr(prep, 'preprocess_inference')
    # We can't easily test logic without actual pickle files, 
    # but we verified the code structure.
