import pandas as pd
import os
from sklearn.model_selection import train_test_split

def prepare_data():
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'fraud.csv')
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    print(f"Loading data from {data_path}...")
    
    # Load data
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
        return

    print(f"Data loaded. Shape: {df.shape}")
    
    # Sort by date if possible to simulate drift over time
    if 'trans_date_trans_time' in df.columns:
        print("Sorting by date...")
        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
        df = df.sort_values('trans_date_trans_time')
    
    # Split into reference and current
    # Reference: First 80% (Training/Baseline)
    # Current: Last 20% (Production/Inference)
    split_index = int(len(df) * 0.8)
    
    reference_data = df.iloc[:split_index]
    current_data = df.iloc[split_index:]
    
    print(f"Reference data shape: {reference_data.shape}")
    print(f"Current data shape: {current_data.shape}")
    
    # Save
    os.makedirs(output_dir, exist_ok=True)
    
    ref_path = os.path.join(output_dir, 'reference_data.csv')
    curr_path = os.path.join(output_dir, 'current_data.csv')
    
    reference_data.to_csv(ref_path, index=False)
    current_data.to_csv(curr_path, index=False)
    
    print(f"Saved reference data to {ref_path}")
    print(f"Saved current data to {curr_path}")

if __name__ == "__main__":
    prepare_data()
