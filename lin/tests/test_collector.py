"""
Tests for LinMessageCollector
"""
import time
import pytest
from unittest.mock import Mock, MagicMock
from lin.collector import LinMessageCollector
from lin.message import LinMessage


class TestLinMessageCollector:
    """Test LinMessageCollector functionality"""
    
    def test_collector_init(self):
        """Test collector initialization"""
        collector = LinMessageCollector(print_messages=False)
        
        assert collector.bus is None
        assert collector.total_messages == 0
        assert not collector.print_messages
        assert collector.message_queue.empty()
    
    def test_context_manager(self):
        """Test collector as context manager"""
        with LinMessageCollector(print_messages=False) as collector:
            assert collector is not None
            assert not collector._closed
        
        # After exiting context, should be closed
        assert collector._closed
    
    def test_set_bus(self):
        """Test setting a bus object"""
        collector = LinMessageCollector(print_messages=False)
        mock_bus = Mock()
        
        collector.set_bus(mock_bus)
        assert collector.bus is mock_bus
    
    def test_start_collecting_without_bus(self):
        """Test that starting collection without bus raises error"""
        collector = LinMessageCollector(print_messages=False)
        
        with pytest.raises(RuntimeError, match="Bus not registered"):
            collector.start_collecting()
    
    def test_message_formatting(self):
        """Test default message formatter"""
        collector = LinMessageCollector()
        msg = LinMessage(
            timestamp=1234.567890,
            frame_id=0x10,
            data=[0xAA, 0xBB],
            channel="0"
        )
        
        formatted = collector._default_message_formatter(msg)
        
        assert "Timestamp: 1234.567890" in formatted
        assert "Frame ID: 10" in formatted
        assert "Data: AA BB" in formatted
        assert "Length: 2" in formatted
    
    def test_custom_formatter(self):
        """Test custom message formatter"""
        def custom_formatter(msg):
            return f"ID={msg.frame_id}"
        
        collector = LinMessageCollector(
            print_messages=False,
            message_formatter=custom_formatter
        )
        
        msg = LinMessage(frame_id=0x20)
        assert collector.message_formatter(msg) == "ID=32"
    
    def test_get_statistics(self):
        """Test statistics collection"""
        collector = LinMessageCollector(print_messages=False)
        collector.start_time = time.time() - 5  # 5 seconds ago
        collector.total_messages = 100
        
        stats = collector.get_statistics()
        
        assert stats['total_messages'] == 100
        assert 4.9 < stats['elapsed_time'] < 5.1  # Allow small timing variance
        assert 19 < stats['message_rate'] < 21  # ~20 msg/s
        assert stats['queue_size'] == 0
    
    @pytest.mark.timeout(2)
    def test_collect_for_duration(self):
        """Test collecting for specific duration"""
        collector = LinMessageCollector(print_messages=False)
        
        # Mock bus that returns one message then None
        mock_bus = Mock()
        test_msg = LinMessage(frame_id=0x10)
        mock_bus.recv.side_effect = [test_msg, None, None, None]
        
        collector.set_bus(mock_bus)
        
        # Collect for 0.5 seconds
        start = time.time()
        messages = collector.collect_for_duration(0.5)
        duration = time.time() - start
        
        assert 0.4 < duration < 0.6  # Allow timing variance
        assert len(messages) == 1
        assert messages[0].frame_id == 0x10