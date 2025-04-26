import random
import time
import copy

class UnreliableChannel:
    def __init__(self, error_rate=0.2, loss_rate=0.1, delay_range=(0.1, 0.3)):
        """
        Initialize the unreliable channel with configurable error parameters
        
        Args:
            error_rate: Probability of introducing bit errors
            loss_rate: Probability of losing a packet
            delay_range: Tuple (min_delay, max_delay) in seconds
        """
        self.error_rate = error_rate
        self.loss_rate = loss_rate
        self.delay_range = delay_range
        
        # Buffers for messages in transit
        self.client_to_server_buffer = []
        self.server_to_client_buffer = []
    
    def corrupt_packet(self, packet):
        """Introduce bit errors into a packet"""
        if isinstance(packet, Packet):
            # Create a copy to avoid modifying the original packet
            corrupted = copy.deepcopy(packet)
            
            # Corrupt the data
            data_list = list(corrupted.data)
            if data_list:  # Check if the data is not empty
                pos = random.randint(0, len(data_list) - 1)
                # Change one character
                char_code = ord(data_list[pos])
                data_list[pos] = chr((char_code + random.randint(1, 25)) % 256)
                corrupted.data = ''.join(data_list)
            
            # Don't recalculate checksum, so the error will be detected
            return corrupted
        
        elif isinstance(packet, ACK):
            # Create a copy to avoid modifying the original ACK
            corrupted = copy.deepcopy(packet)
            # Corrupt the checksum, not the sequence number to preserve protocol behavior
            corrupted.checksum = (corrupted.checksum + random.randint(1, 100)) % 256
            return corrupted
        
        return packet  # Return original if packet type not recognized
    
    def send_to_server(self, packet):
        """Client sends a packet to the server through the unreliable channel"""
        # Check if packet should be lost
        if random.random() < self.loss_rate:
            print(f"CHANNEL: Packet lost in transmission: {packet}")
            return
        
        # Check if packet should be corrupted
        if random.random() < self.error_rate:
            packet = self.corrupt_packet(packet)
            print(f"CHANNEL: Packet corrupted in transmission: {packet}")
        
        # Add transmission delay
        delay = random.uniform(self.delay_range[0], self.delay_range[1])
        delivery_time = time.time() + delay
        
        # Add packet to buffer with delivery time
        self.client_to_server_buffer.append((packet, delivery_time))
        print(f"CHANNEL: Packet in transit to server: {packet}, delivering in {delay:.2f}s")
    
    def send_to_client(self, ack):
        """Server sends an ACK to the client through the unreliable channel"""
        # Check if ACK should be lost
        if random.random() < self.loss_rate:
            print(f"CHANNEL: ACK lost in transmission: {ack}")
            return
        
        # Check if ACK should be corrupted
        if random.random() < self.error_rate:
            ack = self.corrupt_packet(ack)
            print(f"CHANNEL: ACK corrupted in transmission: {ack}")
        
        # Add transmission delay
        delay = random.uniform(self.delay_range[0], self.delay_range[1])
        delivery_time = time.time() + delay
        
        # Add ACK to buffer with delivery time
        self.server_to_client_buffer.append((ack, delivery_time))
        print(f"CHANNEL: ACK in transit to client: {ack}, delivering in {delay:.2f}s")
    
    def receive_from_client(self):
        """Server tries to receive a packet from the client"""
        now = time.time()
        
        # Check for deliverable packets
        deliverable = [item for item in self.client_to_server_buffer if item[1] <= now]
        
        if deliverable:
            # Get and remove the first deliverable packet
            packet, _ = deliverable[0]
            self.client_to_server_buffer.remove((packet, _))
            return packet
        
        return None
    
    def receive_from_server(self):
        """Client tries to receive an ACK from the server"""
        now = time.time()
        
        # Check for deliverable ACKs
        deliverable = [item for item in self.server_to_client_buffer if item[1] <= now]
        
        if deliverable:
            # Get and remove the first deliverable ACK
            ack, _ = deliverable[0]
            self.server_to_client_buffer.remove((ack, _))
            return ack
        
        return None

# Import Packet and ACK classes from client file
from client import Packet, ACK