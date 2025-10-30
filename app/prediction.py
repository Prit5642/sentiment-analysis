import torch
import time
import uuid
from typing import Dict, Any
from app.monitoring import monitor_prediction
from config.settings import Config
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import Vocab
import pickle

# INPUT_SIZE = 51719  # Vocabulary size
# EMBED_SIZE = 128
# HIDDEN_SIZE = 256
# MAX_SEQ_LEN = 256

# model = torch.load('C:/Prit/MLOps/assignment/ml_model/model.pth', map_location="cpu")

# with open('C:/Prit/MLOps/assignment/ml_model/vocab.pkl', 'rb') as f:
#     vocab: Vocab = pickle.load(f)

# tokenizer = get_tokenizer("basic_english", language="en")


class SentimentPredictor:
    def __init__(self, model_path: str, vocab_path: str):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Load model with fallback for pickled class lookup issues
        # Sometimes a model saved from a script references the model class
        # under the '__main__' module (e.g. '__main__.SentiNN'). When the
        # code that unpickles runs under a different module (like
        # 'run_webapp.py'), pickle can't find the class and raises
        # "Can't get attribute 'SentiNN'". To robustly handle that case,
        # import the real class and inject it into the '__main__' module
        # namespace before retrying the load.
        try:
            self.model = torch.load(model_path, map_location="cpu")
        except AttributeError as e:
            # Detect the specific missing-class during unpickling
            msg = str(e)
            if "Can't get attribute 'SentiNN'" in msg or 'SentiNN' in msg:
                import sys
                # Import the architecture where SentiNN is defined
                import ml_model.model_architecture as arch
                # Inject into __main__ so pickle can resolve it
                try:
                    sys.modules['__main__'].SentiNN = arch.SentiNN
                except Exception:
                    # As a fallback, set attribute on the module object returned
                    import types
                    main_mod = sys.modules.get('__main__')
                    if main_mod is None:
                        main_mod = types.ModuleType('__main__')
                        sys.modules['__main__'] = main_mod
                    setattr(main_mod, 'SentiNN', arch.SentiNN)

                # Retry loading now that SentiNN is available
                self.model = torch.load(model_path, map_location="cpu")
            else:
                # re-raise if it's a different AttributeError
                raise
        # Move model to device and set evaluation mode
        try:
            self.model.to(self.device)
            self.model.eval()
        except Exception:
            # If model is a state_dict or other object, ignore here; caller
            # can handle or further errors will be raised at inference
            pass
        with open(vocab_path, 'rb') as f:
            self.vocab: Vocab = pickle.load(f)
        # self.model.to(self.device)
        # self.model.eval()
    def preprocess_text(self, text):
        tokenizer = get_tokenizer("basic_english", language="en")
        """Convert raw text to tensor suitable for model input"""
        # Tokenize and convert to numerical IDs
        MAX_SEQ_LEN = 256
        tokens = tokenizer(text)
        token_ids = self.vocab(tokens)
        
        # Truncate to MAX_SEQ_LEN and append <eos> (id=1 as per your train.py)
        token_ids = token_ids[:MAX_SEQ_LEN]
        token_ids.append(1)  # <eos>
        
        # Pad sequence with <pad> (id=2)
        padded = [2] * (MAX_SEQ_LEN + 1)
        padded[:len(token_ids)] = token_ids
        
        # Convert to tensor
        tensor = torch.tensor([padded], dtype=torch.long).to("cpu")
        return tensor
    
    @monitor_prediction
    def predict(self, text: str) -> Dict[str, Any]:
        """Make sentiment prediction with monitoring"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)

            with torch.no_grad():
                output = self.model(processed_text)
                prediction = torch.argmax(output, dim=1).item()
                
            sentiment = "Positive" if prediction == 1 else "Negative"
            prediction_prob = torch.softmax(output, dim=1)[0][prediction].item()
            sentiment_score = output[0][1].item() - output[0][0].item()
            # Determine sentiment label
            
            processing_time = time.time() - start_time
            
            result = {
                'request_id': request_id,
                'text': text,
                'prediction': sentiment,
                'confidence': prediction_prob,
                'sentiment_score': sentiment_score,
                'processing_time': processing_time,
                'success': True
            }
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'request_id': request_id,
                'text': text,
                'prediction': 'Error',
                'confidence': 0.0,
                'sentiment_score': 0.0,
                'processing_time': processing_time,
                'success': False,
                'error': str(e)
            }

# Global predictor instance
predictor = SentimentPredictor(Config.MODEL_PATH, Config.VOCAB_PATH)