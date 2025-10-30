from flask import Flask, render_template, request, jsonify, Response
from sqlalchemy import func
from app.prediction import predictor
from app.database import db_manager
from app.models import SentimentPrediction
from app.monitoring import get_metrics, PREDICTION_COUNTER, PREDICTION_DURATION
from config.settings import Config
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db_manager.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        
        if not text:
            return render_template('predict.html', error="Please enter some text")
        
        # Make prediction
        result = predictor.predict(text)
        
        if result['success']:
            # Store in database
            session = db_manager.get_session()
            try:
                prediction_record = SentimentPrediction(
                    text=result['text'],
                    prediction=result['prediction'],
                    confidence=result['confidence'],
                    sentiment_score=result['sentiment_score'],
                    request_id=result['request_id'],
                    processing_time=result['processing_time']
                )
                session.add(prediction_record)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Database error: {e}")
            finally:
                session.close()
            
            return render_template('predict.html', 
                                 result=result,
                                 text=text)
        else:
            return render_template('predict.html', 
                                 error=f"Prediction failed: {result.get('error', 'Unknown error')}",
                                 text=text)
    
    return render_template('predict.html')

@app.route('/history')
def history():
    session = db_manager.get_session()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Get paginated predictions
        predictions = session.query(SentimentPrediction)\
            .order_by(SentimentPrediction.timestamp.desc())\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        total = session.query(SentimentPrediction).count()
        
        return render_template('history.html', 
                             predictions=predictions,
                             page=page,
                             per_page=per_page,
                             total=total)
    finally:
        session.close()

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    result = predictor.predict(text)
    
    if result['success']:
        # Store in database
        session = db_manager.get_session()
        try:
            prediction_record = SentimentPrediction(
                text=result['text'],
                prediction=result['prediction'],
                confidence=result['confidence'],
                sentiment_score=result['sentiment_score'],
                request_id=result['request_id'],
                processing_time=result['processing_time']
            )
            session.add(prediction_record)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()
    
    return jsonify(result)

@app.route('/metrics')
def metrics():
    return Response(get_metrics(), mimetype='text/plain')

@app.route('/dashboard')
def dashboard():
    session = db_manager.get_session()
    try:
        # Get stats for last 24 hours
        yesterday = datetime.utcnow() - timedelta(hours=24)
        
        total_predictions = session.query(SentimentPrediction).count()
        recent_predictions = session.query(SentimentPrediction)\
            .filter(SentimentPrediction.timestamp >= yesterday).count()
        
        sentiment_distribution = session.query(
            SentimentPrediction.prediction,
            func.count(SentimentPrediction.id)
        ).group_by(SentimentPrediction.prediction).all()
        
        avg_confidence = session.query(
            func.avg(SentimentPrediction.confidence)
        ).scalar() or 0
        
        avg_processing_time = session.query(
            func.avg(SentimentPrediction.processing_time)
        ).scalar() or 0
        
        stats = {
            'total_predictions': total_predictions,
            'recent_predictions': recent_predictions,
            'sentiment_distribution': dict(sentiment_distribution),
            'avg_confidence': round(avg_confidence, 3),
            'avg_processing_time': round(avg_processing_time, 4)
        }
        
        return render_template('metrics.html', stats=stats)
        
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.WEBAPP_PORT, debug=Config.DEBUG)