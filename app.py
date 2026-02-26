from flask import Flask, render_template, request, jsonify
import os
from detector.bert_detector import BERTDetector
from detector.heuristic_detector import HeuristicDetector
from detector.blockchain import BlockchainManager, compute_article_hash
from datetime import datetime

app = Flask(__name__)

# Initialize detectors
print("Loading AI model... This may take a minute...")
bert_detector = BERTDetector()
heuristic_detector = HeuristicDetector()
blockchain_manager = BlockchainManager()

# Agreement required: only classify when BERT and heuristic both agree
MAX_RETRAIN_ITERATIONS = 5

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify')
def verify_page():
    return render_template('verify.html')

@app.route('/check', methods=['POST'])
def check_news():
    try:
        data = request.get_json()
        article_text = data.get('text', '').strip()
        source_url = (data.get('source_url') or '').strip()

        if not article_text or len(article_text) < 10:
            return jsonify({
                'error': 'Please enter a longer article (at least 10 characters)'
            }), 400

        # Get initial predictions (pass source_url for trusted source check)
        bert_result = bert_detector.predict(article_text)
        heuristic_result = heuristic_detector.predict(article_text, source_url=source_url)

        # Retrain loop: when they disagree, use heuristic to train BERT until they agree
        iteration = 0
        while bert_result['label'] != heuristic_result['label'] and iteration < MAX_RETRAIN_ITERATIONS:
            bert_detector.incremental_train(
                article_text,
                heuristic_result['label'],
                num_steps=5,
                lr=2e-5
            )
            bert_result = bert_detector.predict(article_text)
            iteration += 1

        agreement = (bert_result['label'] == heuristic_result['label'])

        if agreement:
            # Both agree - classify and save to blockchain
            final_label = bert_result['label']
            confidence = 'HIGH'
            article_id = f"NEWS_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            article_hash = compute_article_hash(article_text)
            article_preview = article_text[:200]

            tx_hash = blockchain_manager.save_verification(
                article_id=article_id,
                result=final_label,
                bert_score=bert_result['confidence'],
                heuristic_score=heuristic_result['confidence'],
                article_hash=article_hash,
                article_preview=article_preview
            )

            # Persist updated BERT model after successful agreement (from retraining)
            if iteration > 0:
                bert_detector.save_to_disk()

            return jsonify({
                'result': final_label,
                'confidence': confidence,
                'agreement': True,
                'conclusive': True,
                'bert': bert_result,
                'heuristic': heuristic_result,
                'blockchain': {
                    'saved': True,
                    'transaction_hash': tx_hash,
                    'article_id': article_id,
                    'article_hash': article_hash,
                    'verify_url': f'/verify?hash={tx_hash}'
                }
            })
        else:
            # Still disagree after retraining - inconclusive, do NOT save to blockchain
            BERTDetector.add_feedback(article_text, heuristic_result['label'])
            return jsonify({
                'result': None,
                'conclusive': False,
                'agreement': False,
                'bert': bert_result,
                'heuristic': heuristic_result,
                'blockchain': {'saved': False},
                'message': 'Systems could not reach agreement. Feedback recorded for future training.'
            })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    try:
        records = blockchain_manager.get_all_records()
        return jsonify({'records': records})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stats')
def stats():
    """Get real/fake counts and growth over time for graphs"""
    try:
        records = blockchain_manager.get_all_records()
        real_count = sum(1 for r in records if r.get('result') == 'REAL')
        fake_count = sum(1 for r in records if r.get('result') == 'FAKE')
        # Growth over time (cumulative by block order)
        growth = []
        cum_real, cum_fake = 0, 0
        for i, r in enumerate(records):
            if r.get('result') == 'REAL':
                cum_real += 1
            else:
                cum_fake += 1
            growth.append({
                'block': i + 1,
                'iteration': i + 1,
                'total': cum_real + cum_fake,
                'real': cum_real,
                'fake': cum_fake
            })
        return jsonify({
            'real': real_count,
            'fake': fake_count,
            'total': len(records),
            'growth': growth
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify/<transaction_hash>')
def verify_hash(transaction_hash):
    try:
        # Find record by hash
        record = None
        for r in blockchain_manager.records:
            if r['hash'] == transaction_hash:
                record = r
                break
        
        if not record:
            return jsonify({'error': 'Transaction hash not found'}), 404
        
        # Verify integrity
        from detector.blockchain import BlockchainManager
        temp_manager = BlockchainManager()
        
        record_data = {k: v for k, v in record.items() if k not in ('hash', 'previous_hash')}
        calculated_hash = temp_manager.calculate_hash(record_data)
        is_valid = (calculated_hash == record['hash'])
        
        return jsonify({
            'verified': is_valid,
            'record': record,
            'message': 'Record is authentic and unmodified' if is_valid else 'Record has been tampered with!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)

