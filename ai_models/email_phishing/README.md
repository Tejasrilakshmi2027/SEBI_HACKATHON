# Email Phishing Detection AI

Complete implementation of email phishing detection using Hugging Face BERT model with Explainable AI.

## Features

- **BERT-based Classification**: Uses pre-trained BERT model for binary classification (phishing vs legitimate)
- **Real Training**: Trains on sample dataset with data augmentation
- **Explainable AI**: Provides detailed explanations with highlighted regions
- **Feature Extraction**: Extracts linguistic features for analysis
- **API Integration**: FastAPI endpoints for detection
- **React Integration**: Frontend component for UI
- **Accuracy Metrics**: Tracks accuracy, precision, recall, F1 score
- **Confusion Matrix**: Visual representation of model performance

## Installation

```bash
cd ai_models/email_phishing
pip install -r requirements.txt
```

## Training

### Train the Model

```bash
python training.py
```

This will:
1. Create a sample dataset with phishing and legitimate emails
2. Augment the data with variations
3. Train a BERT model for 5 epochs
4. Save the model to `./saved_model/`
5. Generate confusion matrix
6. Save training metrics and sample predictions

### Training Output

- **Model saved to**: `./saved_model/`
- **Training metrics**: `./saved_model/training_metrics.json`
- **Confusion matrix**: `./saved_model/confusion_matrix.png`
- **Sample predictions**: `./saved_model/sample_predictions.json`

### Expected Metrics

On the sample dataset:
- Accuracy: ~85-95%
- Precision: ~85-95%
- Recall: ~85-95%
- F1 Score: ~85-95%

## Inference

### Run Inference

```bash
python inference.py
```

This will test the model on sample emails and display:
- Phishing prediction
- Confidence score
- Risk level
- Trust score
- Explanations with highlighted regions
- Recommendations

### Inference Output

```json
{
  "is_phishing": true,
  "confidence": 0.92,
  "risk_level": "critical",
  "trust_score": 8,
  "probabilities": {
    "legitimate": 0.08,
    "phishing": 0.92
  },
  "explanations": [
    {
      "type": "urgency",
      "message": "Detected 2 urgency keyword(s) which are common in phishing emails",
      "severity": "high"
    },
    {
      "type": "suspicious_url",
      "message": "Found 1 suspicious URL(s) with known malicious TLDs",
      "severity": "critical"
    }
  ],
  "highlighted_regions": [
    {
      "text": "URGENT",
      "start": 8,
      "end": 14,
      "reason": "Urgency keyword",
      "severity": "high"
    },
    {
      "text": "http://verify-account-xyz.com",
      "start": 120,
      "end": 147,
      "reason": "Suspicious URL",
      "severity": "critical"
    }
  ],
  "recommendations": [
    "Delete this email immediately",
    "Do not click on any links or attachments",
    "Report to your IT security team",
    "Block the sender"
  ]
}
```

## API Integration

### Backend Service

The backend service is located at:
`backend/app/services/email_phishing_service.py`

### API Endpoints

#### Detect Phishing
```
POST /api/v1/email-phishing/detect
```

Request:
```json
{
  "email_content": "Subject: URGENT Your account will be suspended Body: Click here to verify http://fake-site.com"
}
```

Response:
```json
{
  "is_phishing": true,
  "confidence": 0.92,
  "risk_level": "critical",
  "trust_score": 8,
  "probabilities": {
    "legitimate": 0.08,
    "phishing": 0.92
  },
  "explanations": [...],
  "highlighted_regions": [...],
  "recommendations": [...]
}
```

#### Batch Detect
```
POST /api/v1/email-phishing/batch-detect
```

Request:
```json
{
  "emails": ["email1 content", "email2 content"]
}
```

Response:
```json
{
  "results": [...],
  "total": 2,
  "phishing_count": 1
}
```

#### Feature Importance
```
POST /api/v1/email-phishing/feature-importance
```

Response:
```json
{
  "features": {
    "urgency_keywords": 2,
    "suspicious_urls": 1,
    "money_mentions": 0,
    ...
  },
  "importance": {
    "urgency_score": 0.8,
    "url_risk": 1.0,
    "financial_risk": 0.0,
    ...
  }
}
```

## React Integration

### Frontend Service

The frontend service is located at:
`frontend/src/services/emailPhishingService.ts`

### React Component

The React component is located at:
`frontend/src/components/EmailPhishingDetector.tsx`

### Usage

```tsx
import { EmailPhishingDetector } from '../components/EmailPhishingDetector';

function MyPage() {
  return (
    <EmailPhishingDetector 
      onResult={(result) => console.log(result)} 
    />
  );
}
```

## Explainable AI Features

### Highlighted Regions

The model highlights suspicious regions in the email:
- **Urgency keywords**: urgent, immediate, action required, etc.
- **Suspicious URLs**: URLs with malicious TLDs (.xyz, .tk, .ml, etc.)
- **Money mentions**: Dollar amounts, financial terms
- **Suspicious words**: free, winner, prize, lottery, etc.

### Explanations

The model provides human-readable explanations:
- Type of suspicious pattern detected
- Severity level (critical, high, medium, positive)
- Detailed message explaining the finding

### Feature Importance

The model calculates feature importance scores:
- **urgency_score**: Importance of urgency keywords
- **url_risk**: Importance of suspicious URLs
- **financial_risk**: Importance of money mentions
- **account_risk**: Importance of account-related keywords
- **formatting_risk**: Importance of formatting issues
- **punctuation_risk**: Importance of punctuation patterns

 Risk Levels

- **Critical**: Trust score 0-20, confidence > 0.8
- **High**: Trust score 21-40, confidence > 0.6
- **Medium**: Trust score 41-60, confidence > 0.4
- **Low**: Trust score 61-100, confidence > 0.8

## Sample Dataset

The training script creates a sample dataset with:
- 15 phishing emails with common patterns
- 15 legitimate emails from financial institutions
- 3 variations per email (45 total samples per class)
- 90 total training samples

### Phishing Patterns
- Urgency keywords in subject
- Suspicious URLs with malicious TLDs
- Money/financial promises
- Account verification requests
- Prize/lottery scams

### Legitimate Patterns
- Official communications
- Portfolio statements
- Investment updates
- Regulatory announcements
- Educational content

## Model Architecture

- **Base Model**: BERT (bert-base-uncased)
- **Classification Head**: Binary classification (2 labels)
- **Max Length**: 512 tokens
- **Learning Rate**: 2e-5
- **Batch Size**: 4
- **Epochs**: 5
- **Optimizer**: AdamW
- **Loss Function**: Cross-entropy

## Performance

On the sample dataset:
- Training time: ~5-10 minutes (CPU), ~1-2 minutes (GPU)
- Inference time: ~100-200ms per email (CPU), ~10-50ms (GPU)
- Model size: ~418MB

## Troubleshooting

### Model Not Found

If the model is not found at the expected path, the service will fall back to the base BERT model. To fix:
1. Run `python training.py` to train and save the model
2. Ensure the model is saved to `./saved_model/`

### CUDA Out of Memory

If you get CUDA OOM errors:
1. Reduce batch size in training.py
2. Use CPU instead of GPU
3. Reduce max_length parameter

### Import Errors

If you get import errors:
1. Ensure all requirements are installed: `pip install -r requirements.txt`
2. Check Python version (3.8+ required)
3. Ensure transformers and torch are compatible versions

## Future Improvements

- Train on larger real-world phishing datasets
- Add more linguistic features
- Implement ensemble models
- Add email header analysis
- Integrate with email providers for real-time scanning
- Add multi-language support
- Implement fine-tuning for specific domains (banking, SEBI, etc.)

## References

- Hugging Face Transformers: https://huggingface.co/docs/transformers
- BERT Paper: https://arxiv.org/abs/1810.04805
- Phishing Email Datasets:
  - https://www.kaggle.com/datasets/subhajournal/phishingemails
  - https://github.com/drwadeforge/phishing-dataset
