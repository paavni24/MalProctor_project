# # import unittest

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.monitors.download_monitor import start_monitoring, DownloadMonitor
from src.monitors.file_watcher import start_watching, FileWatcher


class TestDownloadMonitor:
    """Test DownloadMonitor class"""
    
    @pytest.fixture
    def monitor(self):
        """Create a DownloadMonitor instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DownloadMonitor(tmpdir)
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initializes correctly"""
        assert monitor is not None
        assert os.path.exists(monitor.download_dir)
    
    @patch('src.monitors.download_monitor.subprocess.run')
    @patch('src.monitors.download_monitor.os.path.exists')
    def test_trigger_detection_file_exists(self, mock_exists, mock_subprocess):
        """Test trigger detection when file exists"""
        # Mock os.path.exists to return True
        mock_exists.return_value = True
        # Mock subprocess.run to return success
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        monitor = DownloadMonitor('/fake/downloads')
        result = monitor.trigger_detection('test.apk')
        
        # Verify it was called and returned True
        assert mock_subprocess.called
        assert result is True
    
    @patch('src.monitors.download_monitor.os.path.exists')
    def test_trigger_detection_file_not_found(self, mock_exists):
        """Test trigger detection when file not found"""
        mock_exists.return_value = False
        monitor = DownloadMonitor('/fake/downloads')
        
        result = monitor.trigger_detection('nonexistent.apk')
        assert result is None
    
    @patch('src.monitors.download_monitor.subprocess.run')
    @patch('src.monitors.download_monitor.os.path.exists')
    def test_trigger_detection_on_download(self, mock_exists, mock_subprocess):
        """Test subprocess is called when file exists"""
        mock_exists.return_value = True
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        monitor = DownloadMonitor('/fake/downloads')
        result = monitor.trigger_detection('test.apk')
        
        # Verify subprocess.run was called
        assert mock_subprocess.called
        assert result is True
    
    @patch('src.monitors.download_monitor.DownloadMonitor.monitor')
    def test_start_monitoring(self, mock_monitor_method):
        """Test start_monitoring function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            start_monitoring(tmpdir)
            assert tmpdir is not None


class TestFileWatcher:
    """Test FileWatcher class"""
    
    @pytest.fixture
    def watcher(self):
        """Create a FileWatcher instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield FileWatcher(tmpdir)
    
    def test_watcher_initialization(self, watcher):
        """Test watcher initializes correctly"""
        assert watcher is not None
        assert os.path.exists(watcher.directory)
    
    @patch('src.monitors.file_watcher.time.sleep', side_effect=KeyboardInterrupt)
    @patch('src.monitors.file_watcher.Observer')
    def test_start_watching(self, mock_observer, mock_sleep):
        """Test start_watching function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            start_watching(tmpdir)
            assert tmpdir is not None
            assert mock_observer.called
            assert mock_sleep.called
    
    def test_watching_nonexistent_dir(self):
        """Test watching with invalid directory"""
        nonexistent = "/nonexistent/path/that/does/not/exist"
        watcher = FileWatcher(nonexistent)
        assert watcher.directory == nonexistent


class TestMonitorsIntegration:
    """Integration tests for monitoring systems"""
    
    @patch('src.monitors.file_watcher.time.sleep', side_effect=KeyboardInterrupt)
    @patch('src.monitors.file_watcher.Observer')
    @patch('src.monitors.download_monitor.DownloadMonitor.monitor')
    def test_both_monitors_start(self, mock_dl_monitor, mock_observer, mock_sleep):
        """Test both monitors can start without errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                start_monitoring(tmpdir)
                start_watching(tmpdir)
            except Exception as e:
                pytest.fail(f"Monitors failed to start: {e}")
                
# #if __name__ == '__main__':
# #    unittest.main()

