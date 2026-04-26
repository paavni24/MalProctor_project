import pandas as pd
import numpy as np
import os

# Set random seed for reproducibility
np.random.seed(42)

# Number of samples
n_samples = 50000
n_benign = 35000
n_malware = 15000

# CREATE DATASET WITH STRONGER SIGNAL - improved from Option 1
# Features now have clearer separation between benign and malware

np.random.seed(42)

# STRONG SIGNAL FEATURES - Better separation for accuracy
# Feature 1: Entropy (High entropy = packed/encrypted, likely malware)
entropy_benign = np.random.normal(3.5, 1.0, n_benign)  # Lower entropy for normal binaries
entropy_malware = np.random.normal(6.5, 1.0, n_malware)  # High entropy for packed malware

# Feature 2: Suspicious API count (Malware uses more suspicious APIs)
suspicious_apis_benign = np.random.normal(2, 2, n_benign).astype(int).clip(0, 50)  
suspicious_apis_malware = np.random.normal(15, 5, n_malware).astype(int).clip(0, 50)  # 13-unit mean difference

# Feature 3: Number of imports (Malware often has unusual imports)
num_imports_benign = np.random.normal(25, 10, n_benign).astype(int).clip(1, 100)
num_imports_malware = np.random.normal(50, 15, n_malware).astype(int).clip(1, 100)  # Clear separation

# Feature 4: File size (Packed malware often smaller/larger)
file_size_benign = np.random.normal(500000, 200000, n_benign).astype(int).clip(1000, 5000000)
file_size_malware = np.random.normal(150000, 100000, n_malware).astype(int).clip(1000, 5000000)

# REMAINING FEATURES - still have some noise
num_sections_benign = np.random.normal(4, 1.5, n_benign).astype(int).clip(1, 15)
num_sections_malware = np.random.normal(7, 2, n_malware).astype(int).clip(1, 15)

has_debug_benign = np.random.choice([0, 1], n_benign, p=[0.7, 0.3])
has_debug_malware = np.random.choice([0, 1], n_malware, p=[0.95, 0.05])

has_reloc_benign = np.random.choice([0, 1], n_benign, p=[0.6, 0.4])
has_reloc_malware = np.random.choice([0, 1], n_malware, p=[0.8, 0.2])

string_count_benign = np.random.normal(200, 100, n_benign).astype(int).clip(10, 1000)
string_count_malware = np.random.normal(100, 80, n_malware).astype(int).clip(10, 1000)

packed_benign = np.random.choice([0, 1], n_benign, p=[0.9, 0.1])
packed_malware = np.random.choice([0, 1], n_malware, p=[0.3, 0.7])

# Create feature data for benign files
benign_data = {
    'file_size': file_size_benign,
    'entropy': entropy_benign,
    'num_sections': num_sections_benign,
    'num_imports': num_imports_benign,
    'has_debug': has_debug_benign,
    'has_reloc': has_reloc_benign,
    'string_count': string_count_benign,
    'suspicious_apis': suspicious_apis_benign,
    'packed': packed_benign,
    'class': 0
}

# Create feature data for malware files
malware_data = {
    'file_size': file_size_malware,
    'entropy': entropy_malware,
    'num_sections': num_sections_malware,
    'num_imports': num_imports_malware,
    'has_debug': has_debug_malware,
    'has_reloc': has_reloc_malware,
    'string_count': string_count_malware,
    'suspicious_apis': suspicious_apis_malware,
    'packed': packed_malware,
    'class': 1
}

# Create dataframes
df_benign = pd.DataFrame(benign_data)
df_malware = pd.DataFrame(malware_data)

# Combine and shuffle
df = pd.concat([df_benign, df_malware], ignore_index=True)
df = df.sample(frac=1).reset_index(drop=True)

# Get the workspace root and construct proper path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset_path = os.path.join(workspace_root, 'data', 'dataset.json')

# Ensure data directory exists
os.makedirs(os.path.dirname(dataset_path), exist_ok=True)

# Save to JSON
df.to_json(dataset_path, orient='records', indent=4)

print(f"Dataset created with {len(df)} samples")
print(f"Benign samples: {len(df[df['class'] == 0])}")
print(f"Malware samples: {len(df[df['class'] == 1])}")
print(f"Saved to: {dataset_path}")
print("\nFirst few rows:")
print(df.head())