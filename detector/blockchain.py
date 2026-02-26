import json
import hashlib
from datetime import datetime
import os


def compute_article_hash(text):
    """SHA256 hash of article text for verification"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class BlockchainManager:
    """
    Simplified blockchain for storing verification records
    (Uses local file storage instead of real blockchain for ease of setup)
    """
    
    def __init__(self, storage_file='blockchain_records.json'):
        self.storage_file = storage_file
        self.records = []
        self.load_records()
        print("✓ Blockchain manager initialized")
    
    def load_records(self):
        """Load existing records from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.records = json.load(f)
            except:
                self.records = []
        else:
            self.records = []
    
    def save_records(self):
        """Save records to file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.records, f, indent=2)
    
    def calculate_hash(self, data):
        """Calculate hash for data integrity"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def save_verification(self, article_id, result, bert_score, heuristic_score,
                         article_hash=None, article_preview=None):
        """
        Save verification result to blockchain.
        Only call when BERT and heuristic agree.

        Args:
            article_id: Unique identifier for article
            result: REAL or FAKE
            bert_score: Confidence from BERT model
            heuristic_score: Confidence from heuristic model
            article_hash: SHA256 of article text (for user verification)
            article_preview: First 200 chars of article (for readability)

        Returns:
            Transaction hash (simulated)
        """
        try:
            # Create record
            record = {
                'article_id': article_id,
                'result': result,
                'bert_score': bert_score,
                'heuristic_score': heuristic_score,
                'article_hash': article_hash or '',
                'article_preview': (article_preview or '')[:200],
                'timestamp': datetime.now().isoformat(),
                'block_number': len(self.records) + 1
            }
            
            # Calculate hash
            record['hash'] = self.calculate_hash(record)
            
            # Add previous hash for chain linking
            if self.records:
                record['previous_hash'] = self.records[-1]['hash']
            else:
                record['previous_hash'] = '0' * 64
            
            # Add to chain
            self.records.append(record)
            self.save_records()
            
            return record['hash']
            
        except Exception as e:
            print(f"Error saving to blockchain: {e}")
            return None
    
    def get_record(self, article_id):
        """Get a specific record by article ID"""
        for record in self.records:
            if record['article_id'] == article_id:
                return record
        return None
    
    def get_all_records(self):
        """Get all verification records"""
        return self.records
    
    def verify_chain_integrity(self):
        """Verify the integrity of the blockchain"""
        for i in range(len(self.records)):
            record = self.records[i]
            record_data = {
                k: v for k, v in record.items()
                if k not in ['hash', 'previous_hash']
            }
            calculated_hash = self.calculate_hash(record_data)
            
            if calculated_hash != record['hash']:
                return False, f"Block {i+1} has been tampered with"
            
            # Verify chain link
            if i > 0:
                if record['previous_hash'] != self.records[i-1]['hash']:
                    return False, f"Block {i+1} chain link broken"
        
        return True, "Blockchain integrity verified"
