from prometheus_client import CollectorRegistry, push_to_gateway, Gauge
import requests
import time
import threading

class AdvancedMetrics:
    def __init__(self, prometheus_url: str):
        self.registry = CollectorRegistry()
        self.prometheus_url = prometheus_url
        
        # Custom business metrics
        self.positive_ratio = Gauge('sentiment_positive_ratio', 
                                   'Ratio of positive predictions', 
                                   registry=self.registry)
        self.negative_ratio = Gauge('sentiment_negative_ratio', 
                                   'Ratio of negative predictions', 
                                   registry=self.registry)
        self.avg_confidence = Gauge('sentiment_avg_confidence', 
                                   'Average prediction confidence', 
                                   registry=self.registry)
        self.prediction_throughput = Gauge('prediction_throughput', 
                                          'Predictions per minute', 
                                          registry=self.registry)
    
    def calculate_advanced_metrics(self, predictions_data):
        """Calculate advanced business metrics"""
        if not predictions_data:
            return
        
        total = len(predictions_data)
        positive_count = sum(1 for p in predictions_data if p['prediction'] == 'Positive')
        negative_count = sum(1 for p in predictions_data if p['prediction'] == 'Negative')
        avg_conf = sum(p['confidence'] for p in predictions_data) / total
        
        self.positive_ratio.set(positive_count / total if total > 0 else 0)
        self.negative_ratio.set(negative_count / total if total > 0 else 0)
        self.avg_confidence.set(avg_conf)
    
    def push_metrics(self):
        """Push custom metrics to Prometheus"""
        push_to_gateway(self.prometheus_url, job='sentiment_metrics', registry=self.registry)