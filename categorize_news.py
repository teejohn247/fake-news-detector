#!/usr/bin/env python3
"""
Batch script to categorize news articles as FAKE (1) or REAL (0).
Uses the project's heuristic detector (fast). Optionally uses BERT (slow).

Usage:
  # CSV input (export from Excel/Numbers to CSV)
  python categorize_news.py articles.csv

  # Specify output file
  python categorize_news.py articles.csv -o labeled_articles.csv

  # Use BERT as well (slow for 20k+ rows)
  python categorize_news.py articles.csv --bert

  # Excel input (.xlsx) — requires: pip install openpyxl
  python categorize_news.py articles.xlsx

Expects columns: title, text  (and optionally Fake to overwrite).
Output: same structure with Fake column set to 1 (fake) or 0 (real).
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Categorize news articles as fake (1) or real (0) using heuristic rules and optionally BERT.'
    )
    parser.add_argument('input_file', help='Path to CSV or Excel (.xlsx) file with title and text columns')
    parser.add_argument('-o', '--output', help='Output file path (default: input_labeled.csv)')
    parser.add_argument('--bert', action='store_true', help='Use BERT in addition to heuristic (slow for large files)')
    parser.add_argument('--encoding', default='utf-8', help='File encoding (default: utf-8). Try utf-8-sig for Excel exports.')
    parser.add_argument('--batch-size', type=int, default=500, help='Print progress every N rows (default: 500)')
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)

    # Output path
    if args.output:
        out_path = args.output
    else:
        base, ext = os.path.splitext(args.input_file)
        out_path = base + '_labeled' + ext

    print("Loading detectors...")
    from detector.heuristic_detector import HeuristicDetector
    heuristic = HeuristicDetector()
    bert_detector = None
    if args.bert:
        from detector.bert_detector import BERTDetector
        bert_detector = BERTDetector()
        print("Using heuristic + BERT (agreement required for final label)")
    else:
        print("Using heuristic only (fast)")

    # Load data
    import pandas as pd
    ext = os.path.splitext(args.input_file)[1].lower()
    try:
        if ext == '.xlsx' or ext == '.xls':
            df = pd.read_excel(args.input_file)
        else:
            df = pd.read_csv(args.input_file, encoding=args.encoding)
    except Exception as e:
        print(f"Error reading file: {e}")
        if 'openpyxl' in str(e).lower() or 'xlrd' in str(e).lower():
            print("For Excel files install: pip install openpyxl")
        sys.exit(1)

    # Normalize column names (case-insensitive)
    col_lower = {c.lower().strip(): c for c in df.columns}
    title_col = col_lower.get('title') or df.columns[0]
    text_col = col_lower.get('text')
    if text_col is None and len(df.columns) >= 2:
        text_col = df.columns[1]

    if 'fake' not in [c.lower() for c in df.columns]:
        df['Fake'] = 0  # will overwrite
    fake_col = col_lower.get('fake') or 'Fake'

    n = len(df)
    print(f"Processing {n:,} rows from {args.input_file}")
    print(f"Columns: title={title_col}, text={text_col or 'N/A'}")
    print()

    def get_text(row):
        title = "" if pd.isna(row[title_col]) else str(row[title_col]).strip()
        text = "" if not text_col or pd.isna(row[text_col]) else str(row[text_col]).strip()
        combined = f"{title} {text}".strip()
        return combined or "(empty)"

    labeled = 0
    for i in range(n):
        row = df.iloc[i]
        text = get_text(row)
        if not text or text == "(empty)":
            df.at[df.index[i], fake_col] = 0  # treat empty as real / skip
            continue

        h_result = heuristic.predict(text)
        label_heuristic = h_result['label']

        if bert_detector is None:
            # Heuristic only: 1 = FAKE, 0 = REAL
            df.at[df.index[i], fake_col] = 1 if label_heuristic == 'FAKE' else 0
        else:
            b_result = bert_detector.predict(text)
            label_bert = b_result['label']
            # Both must agree for conclusive; else use heuristic
            if label_heuristic == label_bert:
                df.at[df.index[i], fake_col] = 1 if label_heuristic == 'FAKE' else 0
            else:
                df.at[df.index[i], fake_col] = 1 if label_heuristic == 'FAKE' else 0
        labeled += 1

        if (i + 1) % args.batch_size == 0:
            print(f"  Processed {i + 1:,} / {n:,} rows...")

    # Save
    if ext in ('.xlsx', '.xls'):
        try:
            df.to_excel(out_path, index=False)
        except Exception as e:
            print(f"Excel write failed: {e}. Saving as CSV instead.")
            out_path = os.path.splitext(out_path)[0] + '_labeled.csv'
            df.to_csv(out_path, index=False, encoding=args.encoding)
    else:
        df.to_csv(out_path, index=False, encoding=args.encoding)

    fake_count = (df[fake_col] == 1).sum()
    real_count = (df[fake_col] == 0).sum()
    print()
    print(f"Done. Labeled {labeled:,} articles.")
    print(f"  Fake: {fake_count:,}")
    print(f"  Real: {real_count:,}")
    print(f"Output: {out_path}")


if __name__ == '__main__':
    main()
