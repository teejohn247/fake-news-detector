from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn as nn
import os
import json

# Path to fine-tuned model (created by train_bert.py)
FINE_TUNED_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "fake-news-bert",
)
FEEDBACK_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "feedback_disagreements.jsonl",
)


class BERTDetector:
    def __init__(self):
        """Initialize BERT model for fake news detection"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print(f"Using device: {self.device}")

        # Use fine-tuned model if available, otherwise fall back to base BERT
        if os.path.exists(os.path.join(FINE_TUNED_MODEL_PATH, "config.json")):
            model_path = FINE_TUNED_MODEL_PATH
            print("Loading fine-tuned model (trained on LIAR dataset)...")
        else:
            model_path = "bert-base-uncased"
            print("Fine-tuned model not found. Using base BERT (run train_bert.py to improve accuracy)...")

        try:
            self.tokenizer = BertTokenizer.from_pretrained(model_path)
            self.model = BertForSequenceClassification.from_pretrained(
                model_path,
                num_labels=2  # Binary: Real or Fake
            )
            self.model.to(self.device)
            self.model.eval()
            print("✓ BERT model loaded successfully")
        except Exception as e:
            print(f"Error loading BERT model: {e}")
            raise
    
    def preprocess_text(self, text):
        """Clean and prepare text for BERT"""
        # Basic cleaning
        text = text.lower().strip()
        
        # Tokenize with BERT tokenizer
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        )
        
        return inputs
    
    def predict(self, text):
        """
        Predict if news is REAL or FAKE
        
        Args:
            text: News article text
            
        Returns:
            dict: {
                'label': 'REAL' or 'FAKE',
                'confidence': float (0-1),
                'probabilities': {'real': float, 'fake': float}
            }
        """
        try:
            # Preprocess
            inputs = self.preprocess_text(text)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
            
            # Get prediction
            prediction = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][prediction].item()
            
            # Convert to labels
            label = 'REAL' if prediction == 1 else 'FAKE'
            
            return {
                'label': label,
                'confidence': round(confidence, 4),
                'probabilities': {
                    'fake': round(probabilities[0][0].item(), 4),
                    'real': round(probabilities[0][1].item(), 4)
                },
                'method': 'BERT AI Model'
            }
            
        except Exception as e:
            print(f"Error in BERT prediction: {e}")
            return {
                'label': 'ERROR',
                'confidence': 0.0,
                'error': str(e)
            }

    def incremental_train(self, text, label, num_steps=5, lr=2e-5):
        """
        Fine-tune BERT on a single example using heuristic label as ground truth.
        Used when BERT and heuristic disagree - train BERT to align with heuristic.

        Args:
            text: Article text
            label: 'REAL' or 'FAKE' (from heuristic)
            num_steps: Number of gradient steps
            lr: Learning rate
        """
        try:
            self.model.train()
            target = 1 if label == 'REAL' else 0
            inputs = self.preprocess_text(text)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            target_tensor = torch.tensor([target], dtype=torch.long).to(self.device)

            optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
            loss_fn = nn.CrossEntropyLoss()

            for _ in range(num_steps):
                optimizer.zero_grad()
                outputs = self.model(**inputs)
                loss = loss_fn(outputs.logits, target_tensor)
                loss.backward()
                optimizer.step()

            self.model.eval()
        except Exception as e:
            print(f"Error in incremental train: {e}")
            self.model.eval()

    def save_to_disk(self):
        """Save current model to disk (e.g. after incremental training)"""
        os.makedirs(FINE_TUNED_MODEL_PATH, exist_ok=True)
        self.model.save_pretrained(FINE_TUNED_MODEL_PATH)
        self.tokenizer.save_pretrained(FINE_TUNED_MODEL_PATH)

    @staticmethod
    def add_feedback(text, heuristic_label):
        """Add disagreement to feedback file for later batch retraining"""
        try:
            with open(FEEDBACK_FILE, 'a') as f:
                f.write(json.dumps({
                    'text': text[:2000],
                    'label': heuristic_label,
                    'binary': 1 if heuristic_label == 'REAL' else 0
                }) + '\n')
        except Exception as e:
            print(f"Error saving feedback: {e}")
