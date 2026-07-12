"""
Email Phishing Detection Training Script
Uses Hugging Face BERT for binary classification (phishing vs legitimate)
Trains on publicly available phishing datasets
"""

import os
import json
import torch
import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from email import message_from_string
from email.header import decode_header


class EmailPhishingTrainer:
    """Trainer class for Email Phishing Detection using BERT"""
    
    def __init__(self, model_name="bert-base-uncased", max_length=512):
        self.model_name = model_name
        self.max_length = max_length
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
    def parse_email(self, email_content):
        """Parse email and extract relevant features"""
        try:
            msg = message_from_string(email_content)
            
            # Extract subject
            subject = ""
            if msg["Subject"]:
                decoded = decode_header(msg["Subject"])
                subject = "".join([str(t[0], t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded])
            
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except:
                            pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                except:
                    body = msg.get_payload()
            
            # Extract sender
            sender = msg.get("From", "")
            
            # Combine features
            combined = f"Subject: {subject} Sender: {sender} Body: {body}"
            return combined[:self.max_length]
            
        except Exception as e:
            return str(email_content)[:self.max_length]
    
    def extract_features(self, text):
        """Extract additional features from text"""
        features = {
            "has_urgency": bool(re.search(r"\b(urgent|immediate|action required|verify now|expire|deadline)\b", text.lower())),
            "has_suspicious_link": bool(re.search(r"http[s]?://[^\s]+\.xyz|http[s]?://[^\s]+\.(tk|ml|ga|cf)", text.lower())),
            "has_money": bool(re.search(r"\$\d+|\d+\s*(dollars|usd|rupees|inr)", text.lower())),
            "has_account": bool(re.search(r"\b(account|password|login|sign in|verify)\b", text.lower())),
            "all_caps_subject": bool(re.search(r"^[A-Z\s!?]+$", text[:100])),
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "length": len(text)
        }
        return features
    
    def load_sample_dataset(self):
        """Create a sample dataset for training"""
        print("Creating sample dataset...")
        
        # Phishing emails (synthetic examples based on common patterns)
        phishing_emails = [
            "Subject: URGENT Your account will be suspended Body: Dear customer your account will be suspended within 24 hours unless you verify your identity immediately Click here http://verify-account-xyz.com",
            "Subject: Verify your SEBI account now Body: We detected suspicious activity on your SEBI account Please verify immediately http://sebi-verify-official.com",
            "Subject: You won 50000 dollars Body: Congratulations you have won 50000 dollars Click to claim http://lottery-winner.xyz",
            "Subject: Immediate action required Body: Your bank account has been compromised Click to secure http://secure-bank-login.com",
            "Subject: Password reset required Body: Your password has expired Reset now http://password-reset-urgent.com",
            "Subject: Verify your identity Body: We need to verify your identity for security purposes Click here http://identity-verify-xyz.com",
            "Subject: Your payment failed Body: Your payment of 1000 dollars failed Click to retry http://payment-retry.com",
            "Subject: Account suspension warning Body: Your account will be suspended unless you act now http://account-restore.com",
            "Subject: Security alert Body: Unusual activity detected on your account Verify immediately http://security-alert-xyz.com",
            "Subject: Confirm your email Body: Please confirm your email address to continue http://email-confirm-urgent.com",
            "Subject: You have been selected Body: You have been selected for exclusive investment opportunity 1000 returns guaranteed http://exclusive-invest.com",
            "Subject: Update your information Body: Please update your account information immediately http://update-info-urgent.com",
            "Subject: Your subscription expires Body: Your subscription expires today Renew now http://renew-subscription-urgent.com",
            "Subject: Verify your payment method Body: We need to verify your payment method http://payment-verify-xyz.com",
            "Subject: Limited time offer Body: Limited time offer 50 discount on all investments http://limited-offer-invest.com",
        ]
        
        # Legitimate emails
        legitimate_emails = [
            "Subject: Quarterly portfolio statement Body: Your quarterly portfolio statement for Q4 2023 is now available Please log in to your account to view",
            "Subject: Investment update Body: Here is your monthly investment update from our team Market performance has been steady",
            "Subject: Account summary Body: Your account summary for this month is now available in your dashboard",
            "Subject: New fund offering Body: We are pleased to announce a new mutual fund offering Please review the prospectus",
            "Subject: Regulatory update Body: SEBI has announced new regulations affecting mutual fund investments Please review",
            "Subject: Dividend announcement Body: We are pleased to announce a dividend of 5 per unit for our equity fund",
            "Subject: KYC reminder Body: Please complete your KYC verification to continue uninterrupted services",
            "Subject: Tax statement Body: Your tax statement for the financial year is now available for download",
            "Subject: Market outlook Body: Our market outlook for the coming quarter suggests cautious optimism",
            "Subject: Portfolio rebalancing Body: We recommend rebalancing your portfolio based on recent market movements",
            "Subject: New feature announcement Body: We have added new features to our trading platform Please explore",
            "Subject: Fee structure update Body: We are updating our fee structure effective next month Details attached",
            "Subject: Educational webinar Body: Join our educational webinar on investment strategies this Friday",
            "Subject: System maintenance notice Body: Our system will undergo maintenance this weekend Services may be temporarily unavailable",
            "Subject: Annual report Body: Our annual report for the financial year is now available for download",
        ]
        
        # Create dataset
        data = []
        for email in phishing_emails:
            data.append({"text": email, "label": 1})  # 1 = phishing
        for email in legitimate_emails:
            data.append({"text": email, "label": 0})  # 0 = legitimate
        
        # Augment with variations
        augmented_data = []
        for item in data:
            # Create 3 variations per email
            for i in range(3):
                text = item["text"]
                # Add slight variations
                if i == 1:
                    text = text.replace("Body", "Message")
                elif i == 2:
                    text = text.replace("Body", "Content")
                augmented_data.append({"text": text, "label": item["label"]})
        
        data.extend(augmented_data)
        
        df = pd.DataFrame(data)
        print(f"Created dataset with {len(df)} samples")
        print(f"Phishing: {sum(df['label'] == 1)}, Legitimate: {sum(df['label'] == 0)}")
        
        return df
    
    def load_from_csv(self, csv_path, text_column="text", label_column="label"):
        """Load dataset from CSV file"""
        print(f"Loading dataset from {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} samples")
        return df
    
    def prepare_dataset(self, df):
        """Prepare dataset for training"""
        # Split into train and validation
        train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
        
        # Convert to Hugging Face datasets
        train_dataset = Dataset.from_pandas(train_df)
        val_dataset = Dataset.from_pandas(val_df)
        
        return train_dataset, val_dataset
    
    def tokenize_dataset(self, dataset):
        """Tokenize dataset"""
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=self.max_length
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        tokenized_dataset = tokenized_dataset.remove_columns(["text"])
        tokenized_dataset = tokenized_dataset.rename_column("label", "labels")
        tokenized_dataset.set_format("torch")
        
        return tokenized_dataset
    
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary")
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    
    def train(self, train_dataset, val_dataset, output_dir="./email_phishing_model", epochs=3, batch_size=8):
        """Train the model"""
        print("Initializing tokenizer and model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, 
            num_labels=2
        )
        
        print("Tokenizing datasets...")
        train_tokenized = self.tokenize_dataset(train_dataset)
        val_tokenized = self.tokenize_dataset(val_dataset)
        
        print("Setting up training arguments...")
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            learning_rate=2e-5,
        )
        
        print("Initializing trainer...")
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=val_tokenized,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
        )
        
        print("Starting training...")
        trainer.train()
        
        print("Saving model...")
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save training metrics
        metrics = trainer.evaluate()
        with open(f"{output_dir}/training_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        print(f"Training complete! Model saved to {output_dir}")
        print(f"Final metrics: {metrics}")
        
        return trainer, metrics
    
    def plot_confusion_matrix(self, trainer, val_dataset, output_dir):
        """Plot and save confusion matrix"""
        predictions = trainer.predict(val_dataset)
        y_pred = np.argmax(predictions.predictions, axis=1)
        y_true = val_dataset["labels"]
        
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", 
                    xticklabels=["Legitimate", "Phishing"],
                    yticklabels=["Legitimate", "Phishing"])
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title("Confusion Matrix")
        plt.savefig(f"{output_dir}/confusion_matrix.png")
        plt.close()
        
        print(f"Confusion matrix saved to {output_dir}/confusion_matrix.png")
        
        # Print classification report
        print("\nClassification Report:")
        print(classification_report(y_true, y_pred, target_names=["Legitimate", "Phishing"]))
        
        return cm
    
    def generate_sample_predictions(self, output_dir):
        """Generate sample predictions for demonstration"""
        sample_emails = [
            "Subject: URGENT Your account will be suspended Body: Click here to verify http://fake-site.com",
            "Subject: Quarterly statement Body: Your quarterly statement is now available",
            "Subject: You won 10000 dollars Body: Click to claim your prize http://prize-winner.xyz",
            "Subject: Investment update Body: Here is your monthly investment update",
        ]
        
        predictions = []
        for email in sample_emails:
            result = self.predict(email)
            predictions.append({
                "email": email,
                "is_phishing": result["is_phishing"],
                "confidence": result["confidence"],
                "risk_level": result["risk_level"]
            })
        
        with open(f"{output_dir}/sample_predictions.json", "w") as f:
            json.dump(predictions, f, indent=2)
        
        print(f"Sample predictions saved to {output_dir}/sample_predictions.json")
        
        return predictions


def main():
    """Main training function"""
    print("=" * 60)
    print("Email Phishing Detection Training")
    print("=" * 60)
    
    # Initialize trainer
    trainer = EmailPhishingTrainer(model_name="bert-base-uncased", max_length=512)
    
    # Load or create dataset
    print("\nLoading dataset...")
    df = trainer.load_sample_dataset()
    
    # Prepare dataset
    print("\nPreparing dataset...")
    train_dataset, val_dataset = trainer.prepare_dataset(df)
    
    # Train model
    print("\nTraining model...")
    output_dir = "./ai_models/email_phishing/saved_model"
    os.makedirs(output_dir, exist_ok=True)
    
    trained_model, metrics = trainer.train(
        train_dataset, 
        val_dataset, 
        output_dir=output_dir,
        epochs=5,
        batch_size=4
    )
    
    # Plot confusion matrix
    print("\nGenerating confusion matrix...")
    trainer.plot_confusion_matrix(trained_model, val_dataset, output_dir)
    
    # Generate sample predictions
    print("\nGenerating sample predictions...")
    trainer.generate_sample_predictions(output_dir)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"Model saved to: {output_dir}")
    print(f"Accuracy: {metrics['eval_accuracy']:.4f}")
    print(f"Precision: {metrics['eval_precision']:.4f}")
    print(f"Recall: {metrics['eval_recall']:.4f}")
    print(f"F1 Score: {metrics['eval_f1']:.4f}")


if __name__ == "__main__":
    main()
