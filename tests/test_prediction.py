import pytest
import torch
from app.prediction import SentimentPredictor
from config.settings import Config

class TestPrediction:
    @pytest.fixture
    def predictor(self):
        return SentimentPredictor(Config.MODEL_PATH, Config.VOCAB_PATH)
    
    def test_predictor_initialization(self, predictor):
        assert predictor is not None
        assert predictor.model is not None
        assert predictor.preprocessor is not None
    
    def test_prediction_positive(self, predictor):
        result = predictor.predict("I love this product! It's amazing!")
        assert result['success'] == True
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'sentiment_score' in result
    
    def test_prediction_negative(self, predictor):
        result = predictor.predict("This is terrible and awful!")
        assert result['success'] == True
        assert 'prediction' in result
    
    def test_prediction_empty_text(self, predictor):
        result = predictor.predict("")
        assert result['success'] == False