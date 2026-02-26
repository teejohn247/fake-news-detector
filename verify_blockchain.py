"""
Blockchain Verification Tool
Use this to verify blockchain records and check integrity
"""

import json
import hashlib
from datetime import datetime

class BlockchainVerifier:
    def __init__(self, storage_file='blockchain_records.json'):
        self.storage_file = storage_file
        self.records = []
        self.load_records()
    
    def load_records(self):
        """Load blockchain records from file"""
        try:
            with open(self.storage_file, 'r') as f:
                self.records = json.load(f)
            print(f"✓ Loaded {len(self.records)} records from blockchain")
        except FileNotFoundError:
            print("❌ No blockchain records found. Run the app first to create some.")
            self.records = []
        except json.JSONDecodeError:
            print("❌ Blockchain file is corrupted")
            self.records = []
    
    def calculate_hash(self, data):
        """Calculate hash for verification"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def find_by_hash(self, transaction_hash):
        """Find a record by its transaction hash"""
        for record in self.records:
            if record['hash'] == transaction_hash:
                return record
        return None
    
    def find_by_article_id(self, article_id):
        """Find a record by article ID"""
        for record in self.records:
            if record['article_id'] == article_id:
                return record
        return None
    
    def display_record(self, record):
        """Display a single record in a nice format"""
        if not record:
            print("❌ Record not found")
            return
        
        print("\n" + "="*70)
        print("📄 BLOCKCHAIN RECORD")
        print("="*70)
        print(f"Block Number:      #{record['block_number']}")
        print(f"Article ID:        {record['article_id']}")
        print(f"Result:            {record['result']}")
        print(f"BERT Score:        {record['bert_score']:.4f}")
        print(f"Heuristic Score:   {record['heuristic_score']:.4f}")
        print(f"Timestamp:         {record['timestamp']}")
        print(f"\n🔒 Transaction Hash:")
        print(f"   {record['hash']}")
        print(f"\n🔗 Previous Hash:")
        print(f"   {record['previous_hash']}")
        print("="*70 + "\n")
    
    def verify_record(self, transaction_hash):
        """Verify a record's integrity using its hash"""
        record = self.find_by_hash(transaction_hash)
        
        if not record:
            print(f"❌ No record found with hash: {transaction_hash}")
            return False
        
        # Recalculate hash (use same keys as when saved)
        record_data = {k: v for k, v in record.items() if k not in ('hash', 'previous_hash')}
        calculated_hash = self.calculate_hash(record_data)
        
        if calculated_hash == record['hash']:
            print("✅ VERIFICATION SUCCESSFUL")
            print("   Record is authentic and has not been tampered with")
            self.display_record(record)
            return True
        else:
            print("❌ VERIFICATION FAILED")
            print("   Record has been tampered with!")
            print(f"   Expected hash: {record['hash']}")
            print(f"   Calculated hash: {calculated_hash}")
            return False
    
    def verify_chain_integrity(self):
        """Verify the entire blockchain's integrity"""
        print("\n🔍 VERIFYING BLOCKCHAIN INTEGRITY...")
        print("="*70)
        
        if not self.records:
            print("❌ No records to verify")
            return False
        
        for i, record in enumerate(self.records):
            record_data = {k: v for k, v in record.items() if k not in ('hash', 'previous_hash')}
            calculated_hash = self.calculate_hash(record_data)
            
            if calculated_hash != record['hash']:
                print(f"❌ Block #{i+1} has been tampered with!")
                print(f"   Expected: {record['hash']}")
                print(f"   Got: {calculated_hash}")
                return False
            
            # Verify chain link
            if i > 0:
                if record['previous_hash'] != self.records[i-1]['hash']:
                    print(f"❌ Chain broken at block #{i+1}!")
                    print(f"   Previous hash doesn't match")
                    return False
            
            print(f"✓ Block #{i+1} verified")
        
        print("="*70)
        print("✅ BLOCKCHAIN INTEGRITY VERIFIED")
        print(f"   All {len(self.records)} blocks are authentic and properly linked")
        return True
    
    def list_all_records(self):
        """List all records in the blockchain"""
        if not self.records:
            print("❌ No records in blockchain")
            return
        
        print("\n📊 ALL BLOCKCHAIN RECORDS")
        print("="*70)
        
        for record in self.records:
            result_symbol = "✅" if record['result'] == "REAL" else "❌"
            print(f"{result_symbol} Block #{record['block_number']} | {record['article_id']}")
            print(f"   Result: {record['result']} | Time: {record['timestamp']}")
            print(f"   Hash: {record['hash'][:32]}...")
            print()
        
        print("="*70)
        print(f"Total Records: {len(self.records)}")
    
    def search_by_result(self, result_type):
        """Search for all REAL or FAKE news records"""
        result_type = result_type.upper()
        
        matching_records = [r for r in self.records if r['result'] == result_type]
        
        if not matching_records:
            print(f"❌ No {result_type} news records found")
            return
        
        print(f"\n📊 ALL {result_type} NEWS RECORDS")
        print("="*70)
        
        for record in matching_records:
            print(f"Block #{record['block_number']} | {record['article_id']}")
            print(f"   Timestamp: {record['timestamp']}")
            print(f"   Hash: {record['hash'][:32]}...")
            print()
        
        print("="*70)
        print(f"Total {result_type} Records: {len(matching_records)}")

def main():
    """Main menu for blockchain verification"""
    verifier = BlockchainVerifier()
    
    if not verifier.records:
        print("\n⚠️  No blockchain records found!")
        print("   Run the main application first to create some records.")
        return
    
    while True:
        print("\n" + "="*70)
        print("🔍 BLOCKCHAIN VERIFICATION TOOL")
        print("="*70)
        print("1. Verify record by transaction hash")
        print("2. Search by article ID")
        print("3. Verify entire blockchain integrity")
        print("4. List all records")
        print("5. Search REAL news")
        print("6. Search FAKE news")
        print("7. Exit")
        print("="*70)
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            hash_input = input("\nEnter transaction hash: ").strip()
            verifier.verify_record(hash_input)
            
        elif choice == '2':
            article_id = input("\nEnter article ID: ").strip()
            record = verifier.find_by_article_id(article_id)
            verifier.display_record(record)
            
        elif choice == '3':
            verifier.verify_chain_integrity()
            
        elif choice == '4':
            verifier.list_all_records()
            
        elif choice == '5':
            verifier.search_by_result('REAL')
            
        elif choice == '6':
            verifier.search_by_result('FAKE')
            
        elif choice == '7':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-7")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()