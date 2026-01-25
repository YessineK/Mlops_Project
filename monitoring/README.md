# Monitoring Module - Evidently AI

This module provides data drift monitoring for the fraud detection MLOps pipeline using Evidently AI.

## Structure

```
monitoring/
├── data/                      # Generated data splits
│   ├── reference_data.csv    # Baseline/training data (80%)
│   └── current_data.csv      # Production/inference data (20%)
├── prepare_data.py           # Data preparation script
├── generate_report.py        # Report generation script
├── run_monitoring.sh         # Automated runner script
├── requirements.txt          # Dependencies
├── monitoring_report.html    # Generated HTML report
└── monitoring_tests.json     # Generated test results (when complete)
```

## Usage

### Quick Start

Run the complete monitoring pipeline:

```bash
cd /Users/bassembenhamed/Desktop/Projects/MLOps
./monitoring/run_monitoring.sh
```

### Step by Step

1. **Prepare Data**:
```bash
python monitoring/prepare_data.py
```
This splits `data/fraud.csv` into reference (80%) and current (20%) datasets.

2. **Generate Reports**:
```bash
python monitoring/generate_report.py
```
This creates:
- `monitoring_report.html` - Interactive HTML dashboard
- `monitoring_tests.json` - Automated test results

3. **View Results**:
```bash
open monitoring/monitoring_report.html
```

## Features

- **Data Drift Detection**: Monitors feature distributions between reference and current data
- **Data Summary**: Provides statistical summaries of datasets
- **Automated Tests**: Runs drift tests and flags issues
- **Visual Reports**: Interactive HTML dashboards

## Dependencies

- evidently
- pandas
- scikit-learn

Install with:
```bash
pip install -r monitoring/requirements.txt
```

## Notes

- The monitoring uses Evidently AI v0.7.17 with legacy API for TestSuite
- Large datasets may take several minutes to process
- Reports are regenerated each time the script runs
