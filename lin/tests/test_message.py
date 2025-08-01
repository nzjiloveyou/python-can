"""
Tests for LinMessage class
"""
import pytest
from lin.message import LinMessage


class TestLinMessage:
    """Test LinMessage functionality"""
    
    def test_create_basic_message(self):
        """Test creating a basic LIN message"""
        msg = LinMessage(frame_id=0x10, data=[0x01, 0x02, 0x03])
        
        assert msg.frame_id == 0x10
        assert msg.data == bytearray([0x01, 0x02, 0x03])
        assert len(msg.data) == 3
        assert msg.direction == "Rx"
        assert not msg.is_error_frame
    
    def test_create_message_with_all_params(self):
        """Test creating a message with all parameters"""
        msg = LinMessage(
            timestamp=1234.5678,
            frame_id=0x3F,
            data=b'\x11\x22\x33\x44',
            checksum=0xAB,
            direction="Tx",
            is_error_frame=False,
            channel="0"
        )
        
        assert msg.timestamp == 1234.5678
        assert msg.frame_id == 0x3F
        assert msg.data == bytearray([0x11, 0x22, 0x33, 0x44])
        assert msg.checksum == 0xAB
        assert msg.direction == "Tx"
        assert msg.channel == "0"
    
    def test_invalid_frame_id(self):
        """Test that invalid frame IDs raise ValueError"""
        with pytest.raises(ValueError, match="Invalid LIN frame ID"):
            LinMessage(frame_id=64)  # Max is 63
        
        with pytest.raises(ValueError, match="Invalid LIN frame ID"):
            LinMessage(frame_id=-1)
    
    def test_data_too_long(self):
        """Test that data longer than 8 bytes raises ValueError"""
        with pytest.raises(ValueError, match="exceeds maximum of 8 bytes"):
            LinMessage(frame_id=0x10, data=[0] * 9)
    
    def test_empty_data(self):
        """Test message with no data"""
        msg = LinMessage(frame_id=0x10)
        assert len(msg.data) == 0
        assert msg.data == bytearray()
    
    def test_string_representation(self):
        """Test string representation of message"""
        msg = LinMessage(frame_id=0x10, data=[0xAA, 0xBB])
        str_repr = str(msg)
        
        assert "ID: 0x10" in str_repr
        assert "Data: [AA BB]" in str_repr
        assert "Direction: Rx" in str_repr
    
    def test_data_types(self):
        """Test different data input types"""
        # List
        msg1 = LinMessage(frame_id=0x10, data=[1, 2, 3])
        assert msg1.data == bytearray([1, 2, 3])
        
        # Bytes
        msg2 = LinMessage(frame_id=0x10, data=b'\x01\x02\x03')
        assert msg2.data == bytearray([1, 2, 3])
        
        # Bytearray
        msg3 = LinMessage(frame_id=0x10, data=bytearray([1, 2, 3]))
        assert msg3.data == bytearray([1, 2, 3])
        
        # Tuple
        msg4 = LinMessage(frame_id=0x10, data=(1, 2, 3))
        assert msg4.data == bytearray([1, 2, 3])