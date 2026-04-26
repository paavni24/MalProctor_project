# Real-Time Malware Detection System

This project implements a real-time malware detection system that monitors APK file downloads and checks them for potential malware using machine learning techniques.

## Project Structure

```
malware-detection-system
├── src
│   ├── core
│   │   ├── malware_detector.py       # Main logic for malware detection
│   │   ├── feature_extractor.py       # Extracts features from APK files
│   │   └── __init__.py                # Marks core as a Python package
│   ├── monitors
│   │   ├── download_monitor.py         # Monitors APK downloads
│   │   ├── file_watcher.py             # Watches directory for new APK files
│   │   └── __init__.py                 # Marks monitors as a Python package
│   ├── api
│   │   ├── routes.py                   # Defines API routes for the system
│   │   ├── handlers.py                 # Handles API requests and responses
│   │   └── __init__.py                 # Marks api as a Python package
│   ├── utils
│   │   ├── logger.py                   # Provides logging functionality
│   │   ├── config.py                   # Handles configuration settings
│   │   └── __init__.py                 # Marks utils as a Python package
│   ├── models
│   │   ├── results.py                  # Defines data structures for results
│   │   └── __init__.py                 # Marks models as a Python package
│   └── main.py                         # Entry point for the application
├── data
│   ├── dataset.json                    # Dataset for training the model
│   ├── best_model.pkl                  # Trained machine learning model
│   └── scaler.pkl                      # Scaler for standardizing features
├── tests
│   ├── test_detector.py                # Unit tests for malware detection
│   ├── test_monitor.py                 # Unit tests for monitoring components
│   └── __init__.py                     # Marks tests as a Python package
├── requirements.txt                    # Lists project dependencies
├── config.yaml                         # Configuration settings in YAML format
└── README.md                           # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd malware-detection-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure that you have the necessary dataset (`dataset.json`) in the `data` directory.
2. Run the main application:
   ```
   python src/main.py
   ```

3. The system will start monitoring for APK downloads and will automatically check them for malware.

## Features

- **Real-time Monitoring**: Monitors APK downloads and initiates scans immediately.
- **Machine Learning Detection**: Utilizes a trained model to detect malware based on extracted features.
- **API Integration**: Provides API endpoints for initiating scans and retrieving results.
- **Logging**: Tracks events and errors for easier debugging and monitoring.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.



## Setup Summary

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create dataset
python tests/create_dataset.py

# 3. Train model
python src/core/malware_detector.py

# 4. Run tests
python -m pytest tests/ -v

# 5. Run main application
python src/main.py

## python -m pytest tests/test_monitor.py -v -s

# # Inference helper — run on a new feature-extracted JSON row

