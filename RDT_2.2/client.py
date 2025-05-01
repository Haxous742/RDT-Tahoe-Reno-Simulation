from unreliable_channel import Packet, UnreliableChannel
from colorama import Fore, Style, init

init(autoreset=True)

class Client:
    def __init__(self, channel):
        self.channel = channel
        self.seq_num = 0
        self.current_packet = None
        print(f"{Fore.CYAN}[Client]:{Fore.BLUE} Initialized with seq_num {self.seq_num}{Style.RESET_ALL}")

    def send_packet(self, data):
        self.current_packet = Packet("DATA", self.seq_num, data)
        self.channel.send_to_server(self.current_packet)
        print(f"{Fore.CYAN}[Client]:{Fore.BLUE} Sent packet with seq_num {self.seq_num}, payload: '{data}', checksum: {self.current_packet.checksum}{Style.RESET_ALL}")

    def receive_ack(self):
        ack = self.channel.receive_from_server()
        if ack is None:
            print(f"{Fore.CYAN}[Client]:{Fore.BLUE} No ACK received yet{Style.RESET_ALL}")
            return False
        corrupt = ack.is_corrupt()
        if corrupt:
            print(f"{Fore.CYAN}[Client]:{Fore.RED} Received corrupted ACK{Style.RESET_ALL}")
        elif ack.seq_num != self.seq_num:
            print(f"{Fore.CYAN}[Client]:{Fore.RED} Received out-of-order ACK{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}[Client]:{Fore.GREEN} Received correct ACK for seq_num {self.seq_num}{Style.RESET_ALL}")
            self.seq_num = 1 - self.seq_num
            print(f"{Fore.CYAN}[Client]:{Fore.BLUE} seq_num updated to {self.seq_num}{Style.RESET_ALL}")
            return True
        print(f"{Fore.CYAN}[Client]:{Fore.RED} Retransmitting packet with seq_num {self.seq_num}{Style.RESET_ALL}")
        self.channel.send_to_server(self.current_packet)
        return False