import logging
import os
import sys
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.feature_extractor import extract_features
from core.malware_detector import predict_sample

class FileWatcher(FileSystemEventHandler):
    """Watch files for changes"""
    
    def __init__(self, directory):
        self.directory = directory
        self.logger = logging.getLogger('malware_detection')
    
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.apk'):
            print(f"[*] New APK detected: {event.src_path}")
            self.process_apk(event.src_path)

    def process_apk(self, apk_path):
        print(f"[*] Extracting features from {apk_path}...")
        features = extract_features(apk_path)
        print(f"[*] Running malware detection...")
        label, probability = predict_sample(features)
        result = "Malware" if label == 1 else "Benign"
        print(f"[*] Detection result for {apk_path}: {result} (Probability: {probability:.4f})")

    def watch(self):
        """Start watching"""
        self.logger.info(f"Watching files in: {self.directory}")

def start_watching(directory):
    """Start file watching"""
    logger = logging.getLogger('malware_detection')
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return
    
    watcher = FileWatcher(directory)
    logger.info(f"File watcher started for: {directory}")
    event_handler = FileWatcher(directory)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    print(f"[*] Watching for new APK files in: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()