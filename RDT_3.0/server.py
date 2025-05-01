from unreliable_channel import Packet
from colorama import Fore, Style, init

init(autoreset=True)

class Server:
    def __init__(self, channel):
        self.channel = channel
        self.expected_seq_num = 0
        print(f"{Fore.YELLOW}[Server]:{Fore.GREEN} Initialized with expected_seq_num {self.expected_seq_num}{Style.RESET_ALL}")

    def receive_packet(self):
        packet = self.channel.receive_from_client()
        if packet is None:
            print(f"{Fore.YELLOW}[Server]:{Fore.GREEN} No packet received yet{Style.RESET_ALL}")
            return
        corrupt = packet.is_corrupt()
        color = Fore.RED if corrupt else Fore.GREEN
        print(f"{Fore.YELLOW}[Server]:{color} Received packet with seq_num {packet.seq_num}, payload: '{packet.payload}', checksum: {packet.checksum}, corrupt: {corrupt}{Style.RESET_ALL}")
        if not corrupt and packet.type == "DATA" and packet.seq_num == self.expected_seq_num:
            print(f"{Fore.YELLOW}[Server]:{Fore.GREEN} Packet seq_num {packet.seq_num} is correct and in order{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[Server]:{Fore.GREEN} Delivered to upper layer: '{packet.payload}'{Style.RESET_ALL}")
            ack = Packet("ACK", self.expected_seq_num)
            self.channel.send_to_client(ack)
            print(f"{Fore.YELLOW}[Server]:{Fore.GREEN} Sent ACK with seq_num {self.expected_seq_num}, checksum: {ack.checksum}{Style.RESET_ALL}")
            self.expected_seq_num = 1 - self.expected_seq_num
            print(f"{Fore.YELLOW}[Server]:{Fore.GREEN} Expected_seq_num updated to {self.expected_seq_num}{Style.RESET_ALL}")
        else:
            ack_seq_num = 1 - self.expected_seq_num
            if corrupt:
                print(f"{Fore.YELLOW}[Server]:{Fore.RED} Packet is corrupted{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[Server]:{Fore.RED} Packet is out-of-order{Style.RESET_ALL}")
            ack = Packet("ACK", ack_seq_num)
            self.channel.send_to_client(ack)
            print(f"{Fore.YELLOW}[Server]:{Fore.GREEN} Sent ACK with seq_num {ack_seq_num}, checksum: {ack.checksum}{Style.RESET_ALL}")