import logging
import os
import sys
import subprocess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class DownloadMonitor:
    """Monitor downloads directory for malware"""
    
    def __init__(self, download_directory):
        self.download_dir = download_directory
        self.logger = logging.getLogger('malware_detection')
    
    def trigger_detection(self, filename):
        """Trigger malware detection on a file"""
        file_path = os.path.join(self.download_dir, filename)
        
        if not os.path.exists(file_path):
            self.logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            self.logger.info(f"Triggering detection on: {filename}")
            # Only call subprocess if file actually exists
            result = subprocess.run(
                ['python', 'src/core/malware_detector.py', filename],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error(f"Detection timeout for: {filename}")
            return None
        except Exception as e:
            self.logger.error(f"Error triggering detection: {e}")
            return None
    
    def monitor(self):
        """Start monitoring"""
        self.logger.info(f"Monitoring downloads in: {self.download_dir}")


def start_monitoring(directory):
    """Start download monitoring"""
    logger = logging.getLogger('malware_detection')
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return
    
    monitor = DownloadMonitor(directory)
    logger.info(f"Download monitor started for: {directory}")