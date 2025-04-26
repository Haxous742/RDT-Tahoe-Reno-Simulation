# import queue
# import random
# import zlib
# import json
# import copy

# class Packet:
#     def __init__(self, type, seq_num, payload="", checksum=None):
#         self.type = type
#         self.seq_num = seq_num
#         self.payload = payload
#         if checksum is None:
#             self.checksum = self.compute_checksum()
#         else:
#             self.checksum = checksum

#     def compute_checksum(self):
#         data = json.dumps({"type": self.type, "seq_num": self.seq_num, "payload": self.payload})
#         return zlib.crc32(data.encode())

#     def is_corrupt(self):
#         return self.checksum != self.compute_checksum()

# class UnreliableChannel:
#     def __init__(self, corruption_prob=0.1):
#         self.to_server_queue = queue.Queue()
#         self.to_client_queue = queue.Queue()
#         self.corruption_prob = corruption_prob

#     def send_to_server(self, packet):
#         corrupted_packet = copy.deepcopy(packet)
#         if random.random() < self.corruption_prob:
#             if corrupted_packet.type == "DATA":
#                 if random.random() < 0.5:
#                     old_seq = corrupted_packet.seq_num
#                     corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
#                     print(f"Channel corrupted DATA packet: seq_num {old_seq} -> {corrupted_packet.seq_num}")
#                 else:
#                     if corrupted_packet.payload:
#                         idx = random.randint(0, len(corrupted_packet.payload) - 1)
#                         old_payload = corrupted_packet.payload
#                         corrupted_packet.payload = (corrupted_packet.payload[:idx] +
#                                                    chr(ord(corrupted_packet.payload[idx]) ^ 1) +
#                                                    corrupted_packet.payload[idx+1:])
#                         print(f"Channel corrupted DATA packet payload: '{old_payload}' -> '{corrupted_packet.payload}'")
#             elif corrupted_packet.type == "ACK":
#                 old_seq = corrupted_packet.seq_num
#                 corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
#                 print(f"Channel corrupted ACK packet: seq_num {old_seq} -> {corrupted_packet.seq_num}")
#         self.to_server_queue.put(corrupted_packet)

#     def receive_from_client(self):
#         if not self.to_server_queue.empty():
#             return self.to_server_queue.get()
#         return None

#     def send_to_client(self, packet):
#         corrupted_packet = copy.deepcopy(packet)
#         if random.random() < self.corruption_prob:
#             if corrupted_packet.type == "ACK":
#                 old_seq = corrupted_packet.seq_num
#                 corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
#                 print(f"Channel corrupted ACK packet: seq_num {old_seq} -> {corrupted_packet.seq_num}")
#         self.to_client_queue.put(corrupted_packet)

#     def receive_from_server(self):
#         if not self.to_client_queue.empty():
#             return self.to_client_queue.get()
#         return None


import queue
import random
import zlib
import json
import copy
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
        data = json.dumps({"type": self.type, "seq_num": self.seq_num, "payload": self.payload})
        return zlib.crc32(data.encode())

    def is_corrupt(self):
        return self.checksum != self.compute_checksum()

class UnreliableChannel:
    def __init__(self, corruption_prob=0.1):
        self.to_server_queue = queue.Queue()
        self.to_client_queue = queue.Queue()
        self.corruption_prob = corruption_prob

    def send_to_server(self, packet):
        corrupted_packet = copy.deepcopy(packet)
        if random.random() < self.corruption_prob:
            if corrupted_packet.type == "DATA":
                if random.random() < 0.5:
                    old_seq = corrupted_packet.seq_num
                    corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
                    print(f"{Fore.YELLOW}Channel corrupted DATA packet: seq_num {old_seq} -> {corrupted_packet.seq_num}{Style.RESET_ALL}")
                else:
                    if corrupted_packet.payload:
                        idx = random.randint(0, len(corrupted_packet.payload) - 1)
                        old_payload = corrupted_packet.payload
                        corrupted_packet.payload = (corrupted_packet.payload[:idx] +
                                                   chr(ord(corrupted_packet.payload[idx]) ^ 1) +
                                                   corrupted_packet.payload[idx+1:])
                        print(f"{Fore.YELLOW}Channel corrupted DATA packet payload: '{old_payload}' -> '{corrupted_packet.payload}'{Style.RESET_ALL}")
            elif corrupted_packet.type == "ACK":
                old_seq = corrupted_packet.seq_num
                corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
                print(f"{Fore.YELLOW}Channel corrupted ACK packet: seq_num {old_seq} -> {corrupted_packet.seq_num}{Style.RESET_ALL}")
        self.to_server_queue.put(corrupted_packet)

    def receive_from_client(self):
        if not self.to_server_queue.empty():
            return self.to_server_queue.get()
        return None

    def send_to_client(self, packet):
        corrupted_packet = copy.deepcopy(packet)
        if random.random() < self.corruption_prob:
            if corrupted_packet.type == "ACK":
                old_seq = corrupted_packet.seq_num
                corrupted_packet.seq_num = 1 - corrupted_packet.seq_num
                print(f"{Fore.YELLOW}Channel corrupted ACK packet: seq_num {old_seq} -> {corrupted_packet.seq_num}{Style.RESET_ALL}")
        self.to_client_queue.put(corrupted_packet)

    def receive_from_server(self):
        if not self.to_client_queue.empty():
            return self.to_client_queue.get()
        return None