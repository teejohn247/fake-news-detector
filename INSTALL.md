# QUICK START GUIDE - Fake News Detector

## 🎯 For Complete Beginners

Follow these exact steps to get the system running in 10-15 minutes.

---

## ⚙️ STEP 1: Install Python

### Windows:
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or higher
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

### Mac:
1. Open Terminal
2. Install Homebrew (if not installed):
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install Python:
   ```
   brew install python
   ```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Verify Installation:
Open Terminal/Command Prompt and type:
```bash
python --version
```
You should see: `Python 3.11.x` or higher

---

## 📦 STEP 2: Extract the ZIP File

1. Find `fake-news-detector.zip`
2. Right-click → Extract All (Windows) or Double-click (Mac)
3. Remember the location (e.g., `C:\Users\YourName\fake-news-detector`)

---

## 🚀 STEP 3: Run the Application

### Windows (Easy Way):
1. Open the extracted folder
2. **Double-click** `start.bat`
3. Wait for installation (5-10 minutes first time)
4. Browser will show the application

### Mac/Linux (Easy Way):
1. Open Terminal
2. Navigate to folder:
   ```bash
   cd path/to/fake-news-detector
   ```
3. Run:
   ```bash
   bash start.sh
   ```
4. Wait for installation
5. Open browser to `http://localhost:5001`

### Manual Way (All Systems):

**Step 3a: Open Terminal/Command Prompt**

Windows:
- Press `Win + R`
- Type `cmd`
- Press Enter

Mac:
- Press `Cmd + Space`
- Type `Terminal`
- Press Enter

Linux:
- Press `Ctrl + Alt + T`

**Step 3b: Navigate to Folder**

```bash
# Replace with your actual path
cd C:\Users\YourName\fake-news-detector  # Windows
cd /Users/YourName/fake-news-detector    # Mac
cd /home/yourname/fake-news-detector     # Linux
```

**Step 3c: Create Virtual Environment**

```bash
python -m venv venv
```

**Step 3d: Activate Virtual Environment**

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your command line.

**Step 3e: Install Dependencies**

```bash
pip install -r requirements.txt
```

**This will take 5-10 minutes.** It's downloading:
- PyTorch (large AI library)
- BERT model (~400MB)
- Other libraries

**Step 3f: Run the Application**

```bash
python app.py
```

You should see:
```
Loading AI model... This may take a minute...
✓ BERT model loaded successfully
✓ Heuristic detector initialized
✓ Blockchain manager initialized
* Running on http://0.0.0.0:5001
```

**Step 3g: Open in Browser**

Open your web browser and go to:
```
http://localhost:5001
```

---

## ✅ STEP 4: Test the System

### Test with Fake News:
Paste this in the text box:
```
SHOCKING DISCOVERY!!! Scientists DON'T want you to know this TRUTH!!! 
This AMAZING breakthrough will CHANGE EVERYTHING!!! You won't BELIEVE 
what happened next!!! Share IMMEDIATELY before it gets DELETED!!!
```

Click "Check News" → Should detect as **FAKE**

### Test with Real News:
Paste this:
```
The World Health Organization reported today that vaccination rates have 
improved globally. Dr. Maria Santos stated in a press conference that while 
progress has been made, continued efforts are needed to reach all populations. 
The findings were published in the WHO's annual health report.
```

Click "Check News" → Should detect as **REAL**

---

## 🎉 You're Done!

The system is now running. You can:
- ✅ Check any news article
- ✅ View AI and rule-based analysis
- ✅ See blockchain verification records
- ✅ View history of all checks

---

## ❓ Common Problems & Solutions

### Problem: "Python not found"
**Solution:** 
- Install Python from python.org
- Make sure to check "Add to PATH" during installation
- Restart your computer

### Problem: "pip not found"
**Solution:**
```bash
python -m ensurepip --upgrade
```

### Problem: Port 5001 already in use
**Solution:** 
Edit `app.py`, change the last line to use a different port (e.g. 5002):
```python
app.run(debug=True, host='0.0.0.0', port=5002)
```
Then open: http://localhost:5001

### Problem: Installation taking too long
**Solution:** 
This is normal! First installation downloads ~1GB of libraries.
- BERT model: ~400MB
- PyTorch: ~200MB
- Other libraries: ~400MB

Be patient, it's a one-time download.

### Problem: "Out of memory" error
**Solution:**
- Close other applications
- Your computer needs at least 4GB RAM
- If still failing, your computer may not be powerful enough

### Problem: Nothing happens when I run start.bat
**Solution:**
- Right-click `start.bat`
- Select "Run as Administrator"
- Or use manual installation method

---

## 📞 Need More Help?

1. Check README.md for detailed documentation
2. Look at troubleshooting section
3. Make sure you have:
   - Python 3.9 or higher
   - 4GB+ RAM
   - Internet connection (for first run)

---

## 🎓 What Happens Behind the Scenes

When you check news:
1. Text is cleaned and prepared
2. BERT AI analyzes semantic patterns
3. Rule checker looks for warning signs
4. Both results are compared
5. Record is saved to blockchain
6. Results displayed in beautiful interface

---

## 🔄 To Use Again Later

Next time you want to use the system:

**Windows:**
- Double-click `start.bat`

**Mac/Linux:**
```bash
cd path/to/fake-news-detector
bash start.sh
```

**Or manually:**
```bash
cd path/to/fake-news-detector
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

Then open: http://localhost:5001

---

## 💡 Tips

- Keep the terminal window open while using the app
- First run takes longer (downloads model)
- Analysis takes 2-5 seconds per article
- Check "View History" to see all past verifications
- Blockchain records are permanent and tamper-proof

---

## 🎯 Quick Checklist

Before asking for help, verify:
- [ ] Python 3.9+ installed (`python --version`)
- [ ] In correct folder (`cd path/to/fake-news-detector`)
- [ ] Virtual environment activated (see `(venv)` in terminal)
- [ ] Dependencies installed (`pip list` shows flask, transformers, torch)
- [ ] Port 5001 is available
- [ ] Computer has 4GB+ RAM
- [ ] Internet connection working

---

**Enjoy detecting fake news! 🔍**
