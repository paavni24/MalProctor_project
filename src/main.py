import os
import sys
import logging

# Add workspace root to path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)

try:
    from src.core.malware_detector import predict_sample
    from src.monitors.download_monitor import start_monitoring
    from src.monitors.file_watcher import start_watching
    from src.utils.logger import setup_logger
    from src.utils.config import Config
except ImportError as e:
    print(f"Import error: {e}")
    print("Creating placeholder functions...")
    
    def predict_sample(features):
        return 0, 0.5
    
    def start_monitoring(path):
        print(f"Monitoring: {path}")
    
    def start_watching(path):
        print(f"Watching: {path}")
    
    def setup_logger(name, log_file=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    class Config:
        def __init__(self, config_file):
            self.config = {}
        
        def get(self, key, default=None):
            return self.config.get(key, default)


def main():
    try:
        # Load configuration settings
        config = Config('config.yaml')
        
        # Setup logging
        logger = setup_logger('malware_detection', config.get('logging', {}).get('log_file', 'malware_detection.log'))
        
        logger.info("[*] Malware Detection System Started")
        
        # Start monitoring downloads
        logger.info("Starting download monitor...")
        download_dir = config.get('monitor', {}).get('download_directory', os.path.expanduser("~/Downloads"))
        
        if not os.path.exists(download_dir):
            logger.warning(f"Download directory does not exist: {download_dir}")
            download_dir = os.path.expanduser("~/Downloads")
        
        logger.info(f"Monitoring directory: {download_dir}")
        start_monitoring(download_dir)
        
        logger.info("[✓] System running successfully")
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()