import pandas as pd
import os
import json
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset

# Legacy imports for TestSuite
from evidently.legacy.test_suite import TestSuite
from evidently.legacy.test_preset import DataDriftTestPreset

def generate_report():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    ref_path = os.path.join(data_dir, 'reference_data.csv')
    curr_path = os.path.join(data_dir, 'current_data.csv')
    
    # Check if data exists
    if not os.path.exists(ref_path) or not os.path.exists(curr_path):
        print("Error: Data files not found. Run prepare_data.py first.")
        return

    print("Loading data...")
    reference_data = pd.read_csv(ref_path)
    current_data = pd.read_csv(curr_path)
    
    # Sample data for faster processing (optional)
    # reference_data = reference_data.sample(n=min(10000, len(reference_data)), random_state=42)
    # current_data = current_data.sample(n=min(5000, len(current_data)), random_state=42)
    
    print(f"Reference data shape: {reference_data.shape}")
    print(f"Current data shape: {current_data.shape}")
    
    print("Generating Data Drift Report...")
    
    # 1. Report (Visual) - New API doesn't use column_mapping in run()
    metrics = [
        DataDriftPreset(),
        DataSummaryPreset()
    ]
    
    report = Report(metrics=metrics)
    snapshot = report.run(current_data=current_data, reference_data=reference_data)
    
    report_path = os.path.join(base_dir, 'monitoring_report.html')
    snapshot.save_html(report_path)
    print(f"✅ Report saved to {report_path}")
    
    # 2. Test Suite (Automated Checks) - Legacy API
    print("Running Test Suite...")
    
    # For legacy TestSuite, we can use column_mapping
    column_mapping = None
    if 'is_fraud' in reference_data.columns:
        from evidently.legacy.pipeline.column_mapping import ColumnMapping
        column_mapping = ColumnMapping()
        column_mapping.target = 'is_fraud'
    
    tests = TestSuite(tests=[
        DataDriftTestPreset(),
    ])
    
    tests.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
    
    # Save test results as JSON
    json_path = os.path.join(base_dir, 'monitoring_tests.json')
    tests.save_json(json_path)
    print(f"✅ Test results saved to {json_path}")
    
    # Check if tests passed
    test_results = tests.as_dict()
    if test_results['summary']['failed_tests'] > 0:
        print(f"⚠️  WARNING: {test_results['summary']['failed_tests']} tests failed!")
    else:
        print("✅ All tests passed.")

if __name__ == "__main__":
    generate_report()
