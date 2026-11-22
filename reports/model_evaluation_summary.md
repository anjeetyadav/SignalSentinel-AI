# SignalSentinel AI — ML Model Evaluation

## 1. Model Overview

SignalSentinel AI uses an unsupervised Isolation Forest model to identify unusual sales behaviour across 10 retail stores.

The model is designed to support business investigation by highlighting potentially abnormal sales patterns.

## 2. Model Configuration

- Algorithm: Isolation Forest
- Estimators: 200
- Random State: 42
- Training strategy: Chronological 80/20 split
- Features:
  - Daily sales deviation from previous 7 days
  - Daily sales deviation from historical same-weekday average
  - Sales trend compared with previous 28 days

## 3. Training and Testing

| Parameter | Result |
|---|---|
| Training records | 14,800 |
| Testing records | 3,710 |
| Training period | 1 Apr 2011 – 19 Apr 2015 |
| Testing period | 20 Apr 2015 – 24 Apr 2016 |

## 4. Final Model Results

| Metric | Result |
|---|---:|
| Test records | 3,710 |
| ML anomalies detected | 374 |
| Anomaly rate | 10.08% |
| Rule-based alerts | 98 |
| Both methods flagged | 73 |
| ML-only detections | 301 |
| Rule-only detections | 25 |
| Rule-alert coverage | 74.49% |

## 5. Model Comparison

Both models were compared using the same 3,710 test records.

| Metric | Original Model | Weekday-Adjusted Model |
|---|---:|---:|
| Anomalies detected | 473 | 374 |
| Both models flagged | 284 | 284 |
| Model-only detections | 189 | 90 |
| Rule-alert coverage | 93.88% | 74.49% |

The weekday-adjusted model reduced weekend anomaly concentration, particularly on Saturdays and Sundays.

## 6. Important Limitations

- The dataset does not contain independently verified anomaly labels.
- Rule-based alerts are comparison references, not ground truth.
- Anomaly detection does not establish the cause of unusual sales behaviour.
- The model is a historical anomaly detection prototype, not a validated future-sales forecasting or early-warning prediction system.
- Further validation is required before operational deployment.

## 7. Conclusion

The weekday-adjusted Isolation Forest model was selected as the primary experimental model for SignalSentinel AI.

It identifies unusual historical sales patterns and provides store-level and date-level outputs for further business investigation.