#!/usr/bin/env python3
"""
Fine-tune BERT for fake news detection using the LIAR dataset.
Run this script once to train the model, then the app will automatically use it.
"""

import os
import torch
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset

# LIAR label names (dataset order): false, half-true, mostly-true, true, barely-true, pants-fire
# Binary: FAKE = pants-fire(5), false(0), barely-true(4) | REAL = half-true(1), mostly-true(2), true(3)
FAKE_INDICES = {0, 4, 5}  # false, barely-true, pants-fire

# Output directory for the fine-tuned model
MODEL_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "models", "fake-news-bert")


def main():
    print("=" * 50)
    print("BERT Fine-Tuning for Fake News Detection")
    print("=" * 50)

    # 1. Load LIAR dataset from Hugging Face
    print("\n1. Loading LIAR dataset from Hugging Face...")
    dataset = load_dataset("ucsbnlp/liar")

    # Handle split name (could be 'validation' or 'valid')
    eval_split = "validation" if "validation" in dataset else "valid"

    # 2. Map to binary labels (LIAR uses int labels 0-5)
    print("\n2. Mapping to binary (FAKE/REAL) labels...")

    def map_labels(example):
        label_val = example["label"]
        if isinstance(label_val, int):
            example["labels"] = 0 if label_val in FAKE_INDICES else 1
        else:
            # Fallback if string
            fake_names = {"pants-fire", "false", "barely-true"}
            example["labels"] = 0 if str(label_val).lower() in fake_names else 1
        return example

    dataset = dataset.map(map_labels, batched=False, desc="Mapping labels")

    fake_count = sum(1 for l in dataset["train"]["labels"] if l == 0)
    real_count = sum(1 for l in dataset["train"]["labels"] if l == 1)
    print(f"   Train: {fake_count} FAKE, {real_count} REAL")

    # 3. Load tokenizer and model
    print("\n3. Loading BERT tokenizer and model...")
    model_name = "bert-base-uncased"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # 4. Tokenize dataset
    print("\n4. Tokenizing dataset...")

    def tokenize(examples):
        return tokenizer(
            examples["statement"],
            padding="max_length",
            truncation=True,
            max_length=256,
            return_tensors=None,
        )

    def prepare_split(split):
        tokenized = dataset[split].map(
            tokenize,
            batched=True,
            remove_columns=[c for c in dataset[split].column_names if c != "labels"],
            desc=f"Tokenizing {split}",
        )
        return tokenized

    train_dataset = prepare_split("train")
    eval_dataset = prepare_split(eval_split)

    # 5. Training arguments
    print("\n5. Setting up training...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size = 16 if device == "cuda" else 8
    print(f"   Using device: {device} (batch size: {batch_size})")

    training_args = TrainingArguments(
        output_dir=os.path.join(MODEL_OUTPUT_DIR, "checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size * 2,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_dir=os.path.join(MODEL_OUTPUT_DIR, "logs"),
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        fp16=device == "cuda",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    # 6. Train
    print("\n6. Training (this may take 20-60 minutes on CPU, ~5-10 min on GPU)...")
    trainer.train()

    # 7. Save final model
    print(f"\n7. Saving model to {MODEL_OUTPUT_DIR}...")
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    trainer.save_model(MODEL_OUTPUT_DIR)
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)

    print("\n" + "=" * 50)
    print("✓ Fine-tuning complete!")
    print(f"  Model saved to: {MODEL_OUTPUT_DIR}")
    print("  The app will automatically use this model on next startup.")
    print("=" * 50)


if __name__ == "__main__":
    main()
