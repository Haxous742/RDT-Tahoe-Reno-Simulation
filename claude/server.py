import random
import time
import copy

class RDTServer:
    def __init__(self, channel):
        self.expected_seq_num = 0  # Start expecting sequence number 0
        self.channel = channel
        self.last_ack = None
        self.received_data = []  # Store delivered data for testing purposes
    
    def receive(self):
        while True:
            packet = self.channel.receive_from_client()
            if packet:
                print(f"SERVER: Received {packet}")
                
                if not packet.is_valid():
                    print("SERVER: Packet is corrupted")
                    self.send_ack(1 - self.expected_seq_num)  # Send ACK for last correctly received packet
                    continue
                
                if packet.seq_num != self.expected_seq_num:
                    print(f"SERVER: Packet has wrong sequence number. Expected {self.expected_seq_num}, got {packet.seq_num}")
                    self.send_ack(1 - self.expected_seq_num)  # Send ACK for last correctly received packet
                    continue
                
                # Packet is correct and in order
                print(f"SERVER: Delivering data to upper layer: '{packet.data}'")
                self.received_data.append(packet.data)  # Store for testing
                
                # Send ACK for the received packet
                self.send_ack(self.expected_seq_num)
                
                # Update expected sequence number
                self.expected_seq_num = 1 - self.expected_seq_num
                return packet.data
    
    def send_ack(self, seq_num):
        ack = ACK(seq_num)
        print(f"SERVER: Sending {ack}")
        self.last_ack = ack
        self.channel.send_to_client(ack)
    
    def start_listening(self, max_packets=10):
        """Start listening for incoming packets up to a maximum number"""
        print("SERVER: Started listening for packets")
        for _ in range(max_packets):
            data = self.receive()
            if data:
                print(f"SERVER: Successfully processed packet with data: '{data}'")
            time.sleep(0.1)  # Small delay
        print("SERVER: Finished listening")

# Import Packet and ACK classes from client file
from client import Packet, ACK