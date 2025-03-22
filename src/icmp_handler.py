# src/icmp_handler.py
import struct
import os
import socket

class ICMPPacket:
    def __init__(self):
        self.type = 8  # Echo request
        self.code = 0
        self.checksum = 0
        self.id = os.getpid() & 0xFFFF
        self.sequence = 0

    def create_packet(self, sequence):
        """Create ICMP packet"""
        self.sequence = sequence
        
        # Create header
        header = struct.pack('bbHHh', 
                           self.type, 
                           self.code, 
                           self.checksum, 
                           self.id, 
                           self.sequence)
        
        # Add some data
        data = b'PING' * 4
        
        # Calculate checksum
        packet = header + data
        self.checksum = self._calculate_checksum(packet)
        
        # Recreate packet with correct checksum
        header = struct.pack('bbHHh',
                           self.type,
                           self.code,
                           self.checksum,
                           self.id,
                           self.sequence)
        
        return header + data

    def _calculate_checksum(self, data):
        """Calculate checksum for ICMP packet"""
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + (data[i + 1] if i + 1 < len(data) else 0)
            checksum += word
        while checksum >> 16:
            checksum = (checksum & 0xffff) + (checksum >> 16)
        return ~checksum & 0xffff
