# 📊 Monitoring Module – Evidently AI (CI/CD Integrated)

This module provides **automated data drift monitoring** for the MLOps pipeline using **Evidently AI**, fully integrated into the **Jenkins CI/CD workflow** and published via a **dedicated web server (Nginx)**.

---

## 🎯 Purpose

The goal of this module is to continuously monitor **data distribution changes** between reference data (training) and incoming production data, in order to:

* Detect data drift early
* Maintain model reliability over time
* Support informed retraining decisions

---

## 📁 Module Structure

```
monitoring/
├── data/
│   ├── churn2.csv                    # Reference dataset
│   ├── prod_batch_01_no_drift.csv    # Production batch (no drift)
│   ├── prod_batch_02_light_drift.csv # Production batch (light drift)
│   └── prod_batch_03_strong_drift.csv# Production batch (strong drift)
├── prepare_data.py                   # Data preprocessing & splitting
├── generate_report.py                # Evidently report generation
├── requirements.txt                  # Monitoring dependencies
├── index.html                        # Web entry point for reports
├── monitoring_report.html            # Generated Evidently HTML report
└── monitoring_tests.json             # Drift test results (JSON)
```

---

## 🔄 CI/CD Integration (Jenkins)

The monitoring module is **executed automatically** as part of the Jenkins pipeline.

### Pipeline behavior

At each Jenkins build:

1. Reference and production datasets are compared
2. Evidently runs statistical drift tests
3. An interactive HTML report is generated
4. Results are archived as build artifacts
5. Reports are deployed via an Nginx container

📌 **No manual execution is required**.

---

## 🌐 Report Visualization

The monitoring reports are published through a **dedicated Nginx web server**, independent from Jenkins UI.

🔗 Access URL:

```
http://localhost:9000
```

Available content:

* 📈 **Interactive Evidently HTML report**
* 📋 **JSON file containing test results**

✅ Fully interactive
✅ No Jenkins file rendering issues
✅ Automatically updated at every build

---

## 📊 Generated Outputs

| File                     | Description                                        |
| ------------------------ | -------------------------------------------------- |
| `monitoring_report.html` | Interactive dashboard with drift metrics and plots |
| `monitoring_tests.json`  | Structured results of statistical drift tests      |

---

## 🧠 Drift Interpretation

The Evidently report provides:

* Number of analyzed features
* Features affected by data drift
* Statistical test results (p-values, thresholds)
* Global drift summary

**Guidelines**:

* Minor or no drift → model remains valid
* Significant drift across multiple features → retraining recommended

---

## 🛠️ Local Execution (Optional)

Although monitoring is automated via Jenkins, the module can still be executed locally for testing purposes:

```bash
pip install -r monitoring/requirements.txt
python monitoring/prepare_data.py
python monitoring/generate_report.py
```

Then open:

```bash
open monitoring/monitoring_report.html
```

---

## 📦 Dependencies

* evidently
* pandas
* scikit-learn

Install with:

```bash
pip install -r monitoring/requirements.txt
```

---

## ✅ Key Advantages

* 🔁 Continuous monitoring
* 📊 Clear and interpretable reports
* ⚙️ Fully automated via CI/CD
* 🌐 Independent visualization layer
* 🧪 Reproducible and production-ready

 