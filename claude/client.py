import random
import time

class Packet:
    def __init__(self, seq_num, data, checksum=None):
        self.seq_num = seq_num  # 1-bit sequence number (0 or 1)
        self.data = data
        self.checksum = self.calculate_checksum() if checksum is None else checksum
    
    def calculate_checksum(self):
        # Simple checksum: sum of ASCII values of data modulo 256
        return sum(ord(c) for c in self.data) % 256
    
    def is_valid(self):
        return self.checksum == self.calculate_checksum()
    
    def __str__(self):
        return f"Packet(seq={self.seq_num}, data='{self.data}', checksum={self.checksum})"

class ACK:
    def __init__(self, seq_num, checksum=None):
        self.seq_num = seq_num
        self.checksum = self.calculate_checksum() if checksum is None else checksum
    
    def calculate_checksum(self):
        # Simple checksum for ACK
        return (self.seq_num * 42) % 256
    
    def is_valid(self):
        return self.checksum == self.calculate_checksum()
    
    def __str__(self):
        return f"ACK(seq={self.seq_num}, checksum={self.checksum})"

class RDTClient:
    def __init__(self, channel):
        self.seq_num = 0  # Start with sequence number 0
        self.channel = channel
        self.current_packet = None
        self.timeout = 1.0  # Timeout in seconds
    
    def send_data(self, data):
        print(f"CLIENT: Sending data: '{data}'")
        
        # Create packet with current sequence number
        self.current_packet = Packet(self.seq_num, data)
        print(f"CLIENT: Created {self.current_packet}")
        
        # Send the packet and wait for ACK
        self.send_and_wait()
        
        # Toggle sequence number for next packet
        self.seq_num = 1 - self.seq_num
    
    def send_and_wait(self):
        ack_received = False
        attempts = 0
        
        while not ack_received:
            attempts += 1
            print(f"CLIENT: Sending packet attempt {attempts}: {self.current_packet}")
            
            # Send packet through unreliable channel
            self.channel.send_to_server(self.current_packet)
            
            # Set timeout
            start_time = time.time()
            
            # Wait for ACK or timeout
            while time.time() - start_time < self.timeout:
                response = self.channel.receive_from_server()
                if response:
                    if not isinstance(response, ACK):
                        print("CLIENT: Received invalid response type")
                        continue
                    
                    if not response.is_valid():
                        print(f"CLIENT: Received corrupted ACK: {response}")
                        continue
                    
                    if response.seq_num == self.seq_num:
                        print(f"CLIENT: Received correct ACK: {response}")
                        ack_received = True
                        break
                    else:
                        print(f"CLIENT: Received ACK with wrong sequence number: {response}")
                
                time.sleep(0.1)  # Small sleep to prevent CPU hogging
            
            if not ack_received:
                print(f"CLIENT: Timeout occurred, retransmitting packet")

def test_client(channel, data_to_send):
    client = RDTClient(channel)
    for data in data_to_send:
        client.send_data(data)
        time.sleep(0.5)  # Small delay between sends for readability