from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
from functools import wraps

# Metrics
PREDICTION_COUNTER = Counter('sentiment_predictions_total', 
                            'Total sentiment predictions', 
                            ['sentiment', 'status'])

PREDICTION_DURATION = Histogram('sentiment_prediction_duration_seconds',
                               'Prediction processing time')

CONFIDENCE_GAUGE = Gauge('sentiment_confidence', 
                        'Prediction confidence', 
                        ['sentiment'])

SENTIMENT_SCORE = Gauge('sentiment_score_current',
                       'Current sentiment score')

ACTIVE_REQUESTS = Gauge('active_requests', 'Active prediction requests')

ERROR_COUNTER = Counter('prediction_errors_total', 'Total prediction errors')

def monitor_prediction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with ACTIVE_REQUESTS.track_inprogress():
            start_time = time.time()
            result = func(*args, **kwargs)
            processing_time = time.time() - start_time
            
            PREDICTION_DURATION.observe(processing_time)
            
            if result.get('success', False):
                PREDICTION_COUNTER.labels(
                    sentiment=result['prediction'],
                    status='success'
                ).inc()
                
                CONFIDENCE_GAUGE.labels(
                    sentiment=result['prediction']
                ).set(result['confidence'])
                
                SENTIMENT_SCORE.set(result['sentiment_score'])
            else:
                PREDICTION_COUNTER.labels(
                    sentiment='error',
                    status='error'
                ).inc()
                ERROR_COUNTER.inc()
            
            return result
    return wrapper

def get_metrics():
    return generate_latest(REGISTRY)