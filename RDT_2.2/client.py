# from unreliable_channel import Packet, UnreliableChannel

# class Client:
#     def __init__(self, channel):
#         self.channel = channel
#         self.seq_num = 0
#         self.current_packet = None
#         print(f"Client initialized with seq_num {self.seq_num}")

#     def send_packet(self, data):
#         self.current_packet = Packet("DATA", self.seq_num, data)
#         self.channel.send_to_server(self.current_packet)
#         print(f"Client sent packet with seq_num {self.seq_num}, payload: '{data}'")

#     def receive_ack(self):
#         ack = self.channel.receive_from_server()
#         if ack is None:
#             print("Client: No ACK received yet")
#             return False
#         print(f"Client received ACK with seq_num {ack.seq_num}, corrupt: {ack.is_corrupt()}")
#         if not ack.is_corrupt() and ack.type == "ACK" and ack.seq_num == self.seq_num:
#             print(f"Client: Correct ACK for seq_num {self.seq_num} received")
#             self.seq_num = 1 - self.seq_num
#             print(f"Client: seq_num updated to {self.seq_num}")
#             return True
#         else:
#             print(f"Client: Incorrect or corrupted ACK, retransmitting seq_num {self.seq_num}")
#             self.channel.send_to_server(self.current_packet)
#             return False

from unreliable_channel import Packet, UnreliableChannel
from colorama import Fore, Style, init

init(autoreset=True)

class Client:
    def __init__(self, channel):
        self.channel = channel
        self.seq_num = 0
        self.current_packet = None
        print(f"{Fore.BLUE}Client initialized with seq_num {self.seq_num}{Style.RESET_ALL}")

    def send_packet(self, data):
        self.current_packet = Packet("DATA", self.seq_num, data)
        self.channel.send_to_server(self.current_packet)
        print(f"{Fore.BLUE}Client sent packet with seq_num {self.seq_num}, payload: '{data}', checksum: {self.current_packet.checksum}{Style.RESET_ALL}")

    def receive_ack(self):
        ack = self.channel.receive_from_server()
        if ack is None:
            print(f"{Fore.BLUE}Client: No ACK received yet{Style.RESET_ALL}")
            return False
        corrupt = ack.is_corrupt()
        color = Fore.RED if corrupt else Fore.BLUE
        print(f"{color}Client received ACK with seq_num {ack.seq_num}, checksum: {ack.checksum}, corrupt: {corrupt}{Style.RESET_ALL}")
        if not corrupt and ack.type == "ACK" and ack.seq_num == self.seq_num:
            print(f"{Fore.BLUE}Client: Correct ACK for seq_num {self.seq_num} received{Style.RESET_ALL}")
            self.seq_num = 1 - self.seq_num
            print(f"{Fore.BLUE}Client: seq_num updated to {self.seq_num}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.BLUE}Client: Incorrect or corrupted ACK, retransmitting seq_num {self.seq_num}{Style.RESET_ALL}")
            self.channel.send_to_server(self.current_packet)
            return False