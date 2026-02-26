# Fake News Detector - AI-Powered Verification System

A hybrid fake news detection system that combines AI (BERT), heuristic rules, and blockchain for transparent news verification.

## 🌟 Features

1. **BERT AI Model** - Deep learning model that analyzes text patterns
2. **Heuristic Rule Checker** - Rule-based system checking for warning signs
3. **Blockchain Storage** - Immutable record of all verifications
4. **Beautiful Web Interface** - Easy-to-use interface for checking news

## 📋 Prerequisites

- Python 3.9 or higher
- 4GB+ RAM (for BERT model)
- Internet connection (first run downloads BERT model)

## 🚀 Installation & Setup

### Step 1: Extract the ZIP file

Extract `fake-news-detector.zip` to your desired location.

### Step 2: Open Terminal/Command Prompt

**Windows:**
- Press `Win + R`
- Type `cmd` and press Enter
- Navigate to extracted folder: `cd path\to\fake-news-detector`

**Mac/Linux:**
- Open Terminal
- Navigate to extracted folder: `cd path/to/fake-news-detector`

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** First installation may take 5-10 minutes as it downloads:
- PyTorch (large AI framework)
- BERT model (~400MB)
- Other libraries

### Step 5: Run the Application

```bash
python app.py
```

You should see:
```
Loading AI model... This may take a minute...
Using device: cpu
✓ BERT model loaded successfully
✓ Heuristic detector initialized
✓ Blockchain manager initialized
* Running on http://0.0.0.0:5001
```

### Step 6: Open in Browser

Open your web browser and go to:
```
http://localhost:5001
```

## 📖 How to Use

1. **Enter News Article**: Paste or type a news article in the text box
2. **Click "Check News"**: Wait for analysis (takes 2-5 seconds)
3. **View Results**: See predictions from both AI and rule checker
4. **Check History**: View all past verifications in blockchain

## 🎯 Example Articles to Test

### Real News Example:
```
The World Health Organization announced today that global vaccination rates 
have increased by 15% over the past year. Dr. Maria Santos, WHO Director, 
stated in a press conference that this progress is encouraging but more work 
remains to reach vulnerable populations. The data was published in the 
organization's annual health report.
```

### Fake News Example:
```
SHOCKING!!! Scientists REVEAL the TRUTH they DON'T want you to know!!! 
This INCREDIBLE discovery will CHANGE EVERYTHING!!! You won't BELIEVE 
what happened next!!! Share this IMMEDIATELY before it gets DELETED!!!
```

## 🎯 Improving BERT Accuracy (Fine-Tuning)

By default, BERT uses random weights for classification. For much better results, **fine-tune it on the LIAR fake news dataset**:

```bash
# Activate venv first, then:
pip install -r requirements.txt   # ensures 'datasets' is installed
python train_bert.py
```

- **Time:** ~20-60 min on CPU, ~5-10 min on GPU
- **Dataset:** LIAR (12.8K labeled statements from PolitiFact)
- **Output:** Model saved to `models/fake-news-bert/`

The app will automatically use the fine-tuned model on next startup. This significantly improves detection of short sensational claims (e.g. "X is dead" hoaxes).

## 🔧 Troubleshooting

### Problem: "Module not found" error
**Solution:** Make sure you installed requirements:
```bash
pip install -r requirements.txt
```

### Problem: Port 5001 already in use
**Solution:** Edit `app.py` and change `port=5001` to another port (e.g. `5002`) in the last line.

### Problem: BERT model takes too long to load
**Solution:** This is normal on first run. The model (~400MB) is being downloaded.
Subsequent runs will be faster.

### Problem: Out of memory error
**Solution:** Close other applications. BERT needs ~2GB RAM minimum.

## 📊 System Architecture

```
User Input (News Article)
    ↓
┌─────────────────────────────────────┐
│   Text Preprocessing                │
│   - Tokenization                    │
│   - Cleaning                        │
└─────────────────────────────────────┘
    ↓
┌──────────────────┐    ┌──────────────────┐
│  BERT AI Model   │    │ Heuristic Rules  │
│  - Deep Learning │    │ - Pattern Check  │
│  - Confidence    │    │ - Source Check   │
└──────────────────┘    └──────────────────┘
    ↓                           ↓
    └───────────┬───────────────┘
                ↓
    ┌───────────────────────┐
    │   Result Combination  │
    │   - Agreement Check   │
    │   - Confidence Score  │
    └───────────────────────┘
                ↓
    ┌───────────────────────┐
    │  Blockchain Storage   │
    │  - Immutable Record   │
    │  - Hash Verification  │
    └───────────────────────┘
                ↓
         Display Results
```

## 🔒 Blockchain Features

The system uses a simplified blockchain that:
- ✅ Stores each verification permanently
- ✅ Links records with cryptographic hashes
- ✅ Prevents tampering (any change breaks the chain)
- ✅ Provides audit trail

Records are stored in `blockchain_records.json`

## 📁 Project Structure

```
fake-news-detector/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── train_bert.py               # Fine-tune BERT on LIAR dataset (optional)
├── detector/                   # Detection modules
│   ├── __init__.py
│   ├── bert_detector.py        # BERT AI model
│   ├── heuristic_detector.py   # Rule-based checker
│   └── blockchain.py           # Blockchain storage
│
├── templates/                  # HTML templates
│   └── index.html             # Main web interface
│
└── blockchain_records.json     # Verification records (auto-created)
```

## 🎓 How It Works

### BERT AI Model
- Pre-trained on millions of text documents
- Optionally fine-tuned on LIAR dataset (run `train_bert.py`)
- Analyzes semantic meaning and context
- Returns confidence score (0-1)

### Heuristic Rules
Checks for:
- Excessive capitalization (SHOUTING)
- Sensational words (SHOCKING, UNBELIEVABLE)
- Emotional language
- Excessive punctuation (!!!, ???)
- Trusted source mentions
- Grammar quality

### Scoring System
- Each rule adds/subtracts points
- Positive score → Real News
- Negative score → Fake News

### Blockchain
- Each verification gets unique hash
- Links to previous record
- Chain breaks if any record is altered
- Provides tamper-proof audit trail

## 🚀 Advanced Options

### Change Port
Edit `app.py`, line at bottom:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5001 to your port
```

### Customize Heuristic Rules
Edit `detector/heuristic_detector.py`:
- Add your own trusted sources
- Modify sensational word list
- Adjust scoring weights

### View Blockchain Data
```bash
python
>>> from detector.blockchain import BlockchainManager
>>> bm = BlockchainManager()
>>> bm.verify_chain_integrity()
(True, 'Blockchain integrity verified')
```

## 📈 Performance Notes

- **BERT Loading**: 30-60 seconds first time, 3-5 seconds after
- **Analysis Time**: 2-5 seconds per article
- **Memory Usage**: 2-4GB RAM
- **Storage**: ~500MB for model + 1MB per 1000 verifications

## 🤝 Support

For issues or questions:
1. Check troubleshooting section above
2. Verify all dependencies installed correctly
3. Ensure Python 3.9+ is installed

## 📝 License

This is an educational project. Feel free to modify and use for learning purposes.

## 🎉 You're Ready!

Start detecting fake news:
1. Run `python app.py`
2. Open http://localhost:5001
3. Paste a news article
4. Click "Check News"
5. Review the AI and rule-based analysis!

---

**Built with:**
- 🤖 BERT (Transformers)
- 🐍 Python & Flask
- 🔒 Blockchain Technology
- 💻 HTML/CSS/JavaScript
