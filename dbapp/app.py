from flask import Flask, jsonify, request, render_template, Response
from app.database import db_manager
from app.models import SentimentPrediction
from app.monitoring import get_metrics
from config.settings import Config
from sqlalchemy import func, desc
import json

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return jsonify({
        'message': 'Sentiment Analysis DB API',
        'endpoints': {
            '/predictions': 'GET all predictions',
            '/predictions/<id>': 'GET specific prediction',
            '/stats': 'GET statistics',
            '/metrics': 'Prometheus metrics'
        }
    })

@app.route('/predictions')
def get_predictions():
    session = db_manager.get_session()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        sentiment_filter = request.args.get('sentiment')
        
        query = session.query(SentimentPrediction)
        
        if sentiment_filter:
            query = query.filter(SentimentPrediction.prediction == sentiment_filter)
        
        predictions = query.order_by(desc(SentimentPrediction.timestamp))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        total = query.count()
        
        return jsonify({
            'predictions': [p.to_dict() for p in predictions],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    finally:
        session.close()

@app.route('/predictions/<int:prediction_id>')
def get_prediction(prediction_id):
    session = db_manager.get_session()
    try:
        prediction = session.query(SentimentPrediction)\
            .filter(SentimentPrediction.id == prediction_id)\
            .first()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        return jsonify(prediction.to_dict())
    finally:
        session.close()

@app.route('/stats')
def get_stats():
    session = db_manager.get_session()
    try:
        # Basic statistics
        total_predictions = session.query(SentimentPrediction).count()
        
        # Sentiment distribution
        sentiment_stats = session.query(
            SentimentPrediction.prediction,
            func.count(SentimentPrediction.id).label('count'),
            func.avg(SentimentPrediction.confidence).label('avg_confidence'),
            func.avg(SentimentPrediction.processing_time).label('avg_processing_time')
        ).group_by(SentimentPrediction.prediction).all()
        
        # Recent activity (last hour)
        from datetime import datetime, timedelta
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_count = session.query(SentimentPrediction)\
            .filter(SentimentPrediction.timestamp >= one_hour_ago)\
            .count()
        
        # Confidence statistics
        confidence_stats = session.query(
            func.min(SentimentPrediction.confidence).label('min_confidence'),
            func.max(SentimentPrediction.confidence).label('max_confidence'),
            func.avg(SentimentPrediction.confidence).label('avg_confidence')
        ).first()
        
        stats = {
            'total_predictions': total_predictions,
            'recent_activity_last_hour': recent_count,
            'sentiment_distribution': [
                {
                    'sentiment': stat.prediction,
                    'count': stat.count,
                    'avg_confidence': float(stat.avg_confidence or 0),
                    'avg_processing_time': float(stat.avg_processing_time or 0)
                }
                for stat in sentiment_stats
            ],
            'confidence_stats': {
                'min': float(confidence_stats.min_confidence or 0),
                'max': float(confidence_stats.max_confidence or 0),
                'average': float(confidence_stats.avg_confidence or 0)
            }
        }
        
        return jsonify(stats)
    finally:
        session.close()

@app.route('/metrics')
def metrics():
    from app.monitoring import get_metrics
    return Response(get_metrics(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.DBAPP_PORT, debug=Config.DEBUG)