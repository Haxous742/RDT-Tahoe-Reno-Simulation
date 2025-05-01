import queue
import random
from colorama import Fore, Style, init

init(autoreset=True)

class Packet:
    def __init__(self, type, seq_num, payload="", checksum=None):
        self.type = type
        self.seq_num = seq_num
        self.payload = payload
        if checksum is None:
            self.checksum = self.compute_checksum()
        else:
            self.checksum = checksum

    def compute_checksum(self):
        data = f"{self.type}{self.seq_num}{self.payload}".encode()
        checksum = 0
        for byte in data:
            checksum += byte
        return checksum % 256

    def is_corrupt(self):
        return self.checksum != self.compute_checksum()

class UnreliableChannel:
    def __init__(self, corruption_prob=0.7):
        self.to_server_queue = queue.Queue()
        self.to_client_queue = queue.Queue()
        self.corruption_prob = corruption_prob

    def send_to_server(self, packet):
        corrupted_packet = Packet(packet.type, packet.seq_num, packet.payload, packet.checksum)
        rand = random.random()
        if rand < self.corruption_prob:
            if corrupted_packet.type == "DATA":
                if random.choice([True, False]):
                    corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
                    print(f"{Fore.YELLOW}          Channel corrupted DATA packet: seq_num flipped{Style.RESET_ALL}")
                else:
                    if corrupted_packet.payload:
                        idx = random.randint(0, len(corrupted_packet.payload) - 1)
                        corrupted_packet.payload = (corrupted_packet.payload[:idx] +
                                                chr(ord(corrupted_packet.payload[idx]) + 1) +
                                                corrupted_packet.payload[idx+1:])
                        print(f"{Fore.YELLOW}          Channel corrupted DATA packet: payload altered{Style.RESET_ALL}")
            elif corrupted_packet.type == "ACK":
                corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
                print(f"{Fore.YELLOW}         Channel corrupted ACK packet{Style.RESET_ALL}")
        
        self.to_server_queue.put(corrupted_packet)

    def receive_from_client(self):
        if not self.to_server_queue.empty():
            return self.to_server_queue.get()
        return None

    def send_to_client(self, packet):
        corrupted_packet = Packet(packet.type, packet.seq_num, packet.payload, packet.checksum)
        if random.random() < self.corruption_prob:
            if corrupted_packet.type == "ACK":
                old_seq = corrupted_packet.seq_num
                corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
                print(f"{Fore.YELLOW}          Channel corrupted ACK packet {Style.RESET_ALL}")
        self.to_client_queue.put(corrupted_packet)

    def receive_from_server(self):
        if not self.to_client_queue.empty():
            return self.to_client_queue.get()
        return None