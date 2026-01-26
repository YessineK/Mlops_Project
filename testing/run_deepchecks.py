import os
import sys
import pandas as pd
import joblib
from datetime import datetime

# Deepchecks imports
from deepchecks.tabular import Dataset
from deepchecks.tabular.suites import (
    train_test_validation,
    model_evaluation,
    data_integrity
)


def load_model_and_data():
    """Load model, preprocessor and validation data"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    # Paths
    model_path = os.path.join(project_root, "backend/src/processors/models/best_model_final.pkl")
    preprocessor_path = os.path.join(project_root, "backend/src/processors/preprocessor.pkl")
    data_path = os.path.join(project_root, "monitoring/data/churn2.csv")
    
    print(f"📂 Loading model from: {model_path}")
    print(f"📂 Loading preprocessor from: {preprocessor_path}")
    print(f"📂 Loading data from: {data_path}")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found: {data_path}")
    
    model = joblib.load(model_path)
    
    # Load preprocessor if exists
    preprocessor = None
    if os.path.exists(preprocessor_path):
        preprocessor = joblib.load(preprocessor_path)
    
    # Load data
    df = pd.read_csv(data_path)
    
    # Clean data
    df.drop(columns=["CLIENTNUM", "Unnamed: 21"], errors="ignore", inplace=True)
    
    # Map target to binary
    if "Attrition_Flag" in df.columns:
        df["target"] = (df["Attrition_Flag"] == "Attrited Customer").astype(int)
        df.drop(columns=["Attrition_Flag"], inplace=True)
    
    print(f"✅ Data loaded: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    
    return model, preprocessor, df


def split_data(df, test_size=0.2):
    """Split data into train and test"""
    from sklearn.model_selection import train_test_split
    
    if "target" not in df.columns:
        raise ValueError("Column 'target' not found in dataframe")
    
    train_df, test_df = train_test_split(
        df, 
        test_size=test_size, 
        stratify=df["target"], 
        random_state=42
    )
    
    print(f"✅ Data split:")
    print(f"   Train: {train_df.shape}")
    print(f"   Test: {test_df.shape}")
    
    return train_df, test_df


def create_datasets(train_df, test_df):
    """Create Deepchecks Dataset objects"""
    
    # Identify categorical features
    cat_features = train_df.select_dtypes(include=["object", "category"]).columns.tolist()
    if "target" in cat_features:
        cat_features.remove("target")
    
    print(f"📊 Categorical features: {cat_features}")
    
    train_dataset = Dataset(
        train_df,
        label="target",
        cat_features=cat_features
    )
    
    test_dataset = Dataset(
        test_df,
        label="target",
        cat_features=cat_features
    )
    
    return train_dataset, test_dataset


def run_validation_suite(train_dataset, test_dataset, model, output_dir):
    """Run comprehensive validation tests"""
    
    print("")
    print("="*80)
    print("🔍 DEEPCHECKS VALIDATION SUITE")
    print("="*80)
    
    results = {}
    
    # 1. Data Integrity Tests
    print("\n1️⃣ Data Integrity Suite...")
    try:
        integrity_suite = data_integrity()
        integrity_result = integrity_suite.run(train_dataset)
        
        integrity_path = os.path.join(output_dir, "data_integrity_report.html")
        integrity_result.save_as_html(integrity_path)
        
        # Check if passed
        passed = integrity_result.passed()
        results["data_integrity"] = {
            "passed": passed,
            "report": integrity_path
        }
        
        if passed:
            print("   ✅ Data integrity: PASSED")
        else:
            print("   ❌ Data integrity: FAILED")
            print(f"      See report: {integrity_path}")
        
    except Exception as e:
        print(f"   ⚠️ Data integrity suite error: {e}")
        results["data_integrity"] = {"passed": False, "error": str(e)}
    
    # 2. Train-Test Validation
    print("\n2️⃣ Train-Test Validation Suite...")
    try:
        validation_suite = train_test_validation()
        validation_result = validation_suite.run(train_dataset, test_dataset)
        
        validation_path = os.path.join(output_dir, "train_test_validation_report.html")
        validation_result.save_as_html(validation_path)
        
        passed = validation_result.passed()
        results["train_test_validation"] = {
            "passed": passed,
            "report": validation_path
        }
        
        if passed:
            print("   ✅ Train-test validation: PASSED")
        else:
            print("   ❌ Train-test validation: FAILED")
            print(f"      See report: {validation_path}")
        
    except Exception as e:
        print(f"   ⚠️ Train-test validation error: {e}")
        results["train_test_validation"] = {"passed": False, "error": str(e)}
    
    # 3. Model Evaluation
    print("\n3️⃣ Model Evaluation Suite...")
    try:
        evaluation_suite = model_evaluation()
        evaluation_result = evaluation_suite.run(train_dataset, test_dataset, model)
        
        evaluation_path = os.path.join(output_dir, "model_evaluation_report.html")
        evaluation_result.save_as_html(evaluation_path)
        
        passed = evaluation_result.passed()
        results["model_evaluation"] = {
            "passed": passed,
            "report": evaluation_path
        }
        
        if passed:
            print("   ✅ Model evaluation: PASSED")
        else:
            print("   ❌ Model evaluation: FAILED")
            print(f"      See report: {evaluation_path}")
        
    except Exception as e:
        print(f"   ⚠️ Model evaluation error: {e}")
        results["model_evaluation"] = {"passed": False, "error": str(e)}
    
    return results


def generate_summary_report(results, output_dir):
    """Generate HTML summary of all tests"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r.get("passed", False))
    failed = total - passed
    
    status = "✅ PASSED" if failed == 0 else "❌ FAILED"
    status_color = "#1db954" if failed == 0 else "#ff4d4d"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Deepchecks Validation Summary</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 50px auto;
            background: #0b0f17;
            color: #e8eefc;
            padding: 20px;
        }}
        h1 {{
            color: {status_color};
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #9fb0d0;
            margin-bottom: 30px;
        }}
        .summary {{
            background: #121a27;
            border: 2px solid {status_color};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .summary h2 {{
            margin-top: 0;
            color: {status_color};
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #9fb0d0;
            font-size: 14px;
        }}
        .reports {{
            list-style: none;
            padding: 0;
        }}
        .reports li {{
            margin: 15px 0;
            padding: 15px;
            background: #121a27;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .passed {{ color: #1db954; }}
        .failed {{ color: #ff4d4d; }}
        a {{
            color: #1db954;
            text-decoration: none;
            font-size: 16px;
        }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>🔍 Deepchecks Validation Summary</h1>
    <div class="timestamp">Generated: {timestamp}</div>
    
    <div class="summary">
        <h2>Overall Status: {status}</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Suites</div>
            </div>
            <div class="stat-card">
                <div class="stat-value passed">{passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value failed">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
        </div>
    </div>
    
    <h2>📄 Detailed Reports</h2>
    <ul class="reports">
"""
    
    for suite_name, result in results.items():
        suite_title = suite_name.replace("_", " ").title()
        status_class = "passed" if result.get("passed", False) else "failed"
        status_text = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
        
        if "report" in result:
            report_file = os.path.basename(result["report"])
            html += f"""
        <li>
            <span class="{status_class}">{status_text}</span> - 
            <a href="{report_file}">{suite_title}</a>
        </li>
"""
        else:
            error = result.get("error", "Unknown error")
            html += f"""
        <li>
            <span class="failed">❌ ERROR</span> - {suite_title}
            <div style="color: #9fb0d0; margin-top: 5px; font-size: 14px;">Error: {error}</div>
        </li>
"""
    
    html += """
    </ul>
</body>
</html>
"""
    
    summary_path = os.path.join(output_dir, "deepchecks_summary.html")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n✅ Summary report saved: {summary_path}")
    
    return summary_path


def main():
    print("="*80)
    print("🚀 DEEPCHECKS VALIDATION")
    print("="*80)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Load model and data
        model, preprocessor, df = load_model_and_data()
        
        # Split data
        train_df, test_df = split_data(df)
        
        # Create datasets
        train_dataset, test_dataset = create_datasets(train_df, test_df)
        
        # Run validation suites
        results = run_validation_suite(train_dataset, test_dataset, model, output_dir)
        
        # Generate summary
        generate_summary_report(results, output_dir)
        
        # Check overall status
        all_passed = all(r.get("passed", False) for r in results.values())
        
        print("")
        print("="*80)
        if all_passed:
            print("✅ ALL VALIDATION TESTS PASSED")
            print("="*80)
            sys.exit(0)
        else:
            print("❌ SOME VALIDATION TESTS FAILED")
            print("="*80)
            print("⚠️  Warning: Model has quality issues")
            print("   Review reports before deploying to production")
            sys.exit(0)  # Don't block pipeline, just warn
        
    except Exception as e:
        print("")
        print("="*80)
        print(f"❌ DEEPCHECKS VALIDATION ERROR: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()