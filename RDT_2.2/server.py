# from unreliable_channel import Packet, UnreliableChannel

# class Server:
#     def __init__(self, channel):
#         self.channel = channel
#         self.expected_seq_num = 0
#         print(f"Server initialized with expected_seq_num {self.expected_seq_num}")

#     def receive_packet(self):
#         packet = self.channel.receive_from_client()
#         if packet is None:
#             print("Server: No packet received yet")
#             return
#         print(f"Server received packet with seq_num {packet.seq_num}, payload: '{packet.payload}', corrupt: {packet.is_corrupt()}")
#         if not packet.is_corrupt() and packet.type == "DATA" and packet.seq_num == self.expected_seq_num:
#             print(f"Server: Packet seq_num {packet.seq_num} is correct and in order")
#             print(f"Delivered to upper layer: '{packet.payload}'")
#             ack = Packet("ACK", self.expected_seq_num)
#             self.channel.send_to_client(ack)
#             print(f"Server sent ACK with seq_num {self.expected_seq_num}")
#             self.expected_seq_num = 1 - self.expected_seq_num
#             print(f"Server: expected_seq_num updated to {self.expected_seq_num}")
#         else:
#             ack_seq_num = 1 - self.expected_seq_num
#             print(f"Server: Packet is corrupted or out-of-order, sending ACK for seq_num {ack_seq_num}")
#             ack = Packet("ACK", ack_seq_num)
#             self.channel.send_to_client(ack)


from unreliable_channel import Packet, UnreliableChannel
from colorama import Fore, Style, init

init(autoreset=True)

class Server:
    def __init__(self, channel):
        self.channel = channel
        self.expected_seq_num = 0
        print(f"{Fore.GREEN}Server initialized with expected_seq_num {self.expected_seq_num}{Style.RESET_ALL}")

    def receive_packet(self):
        packet = self.channel.receive_from_client()
        if packet is None:
            print(f"{Fore.GREEN}Server: No packet received yet{Style.RESET_ALL}")
            return
        corrupt = packet.is_corrupt()
        color = Fore.RED if corrupt else Fore.GREEN
        print(f"{color}Server received packet with seq_num {packet.seq_num}, payload: '{packet.payload}', checksum: {packet.checksum}, corrupt: {corrupt}{Style.RESET_ALL}")
        if not corrupt and packet.type == "DATA" and packet.seq_num == self.expected_seq_num:
            print(f"{Fore.GREEN}Server: Packet seq_num {packet.seq_num} is correct and in order{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Delivered to upper layer: '{packet.payload}'{Style.RESET_ALL}")
            ack = Packet("ACK", self.expected_seq_num)
            self.channel.send_to_client(ack)
            print(f"{Fore.GREEN}Server sent ACK with seq_num {self.expected_seq_num}, checksum: {ack.checksum}{Style.RESET_ALL}")
            self.expected_seq_num = 1 - self.expected_seq_num
            print(f"{Fore.GREEN}Server: expected_seq_num updated to {self.expected_seq_num}{Style.RESET_ALL}")
        else:
            ack_seq_num = 1 - self.expected_seq_num
            print(f"{Fore.GREEN}Server: Packet is corrupted or out-of-order, sending ACK for seq_num {ack_seq_num}{Style.RESET_ALL}")
            ack = Packet("ACK", ack_seq_num)
            self.channel.send_to_client(ack)
            print(f"{Fore.GREEN}Server sent ACK with seq_num {ack_seq_num}, checksum: {ack.checksum}{Style.RESET_ALL}")