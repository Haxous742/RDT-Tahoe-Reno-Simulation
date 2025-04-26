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
            if corrupt:
                print(f"{Fore.GREEN}Server: Received corrupted packet, sending ACK for seq_num {ack_seq_num}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Server: Received duplicate packet with seq_num {packet.seq_num}, sending ACK for seq_num {ack_seq_num}{Style.RESET_ALL}")
            ack = Packet("ACK", ack_seq_num)
            self.channel.send_to_client(ack)
            print(f"{Fore.GREEN}Server sent ACK with seq_num {ack_seq_num}, checksum: {ack.checksum}{Style.RESET_ALL}")