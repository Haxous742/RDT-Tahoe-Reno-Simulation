import time
from unreliable_channel import Packet, UnreliableChannel
from colorama import Fore, Style, init

init(autoreset=True)

class Client:
    def __init__(self, channel):
        self.channel = channel
        self.seq_num = 0
        self.current_packet = None
        self.waiting_for_ack = False
        self.send_time = 0
        self.timeout = 1.0  # seconds
        print(f"{Fore.BLUE}Client initialized with seq_num {self.seq_num}{Style.RESET_ALL}")

    def send_packet(self, data):
        self.current_packet = Packet("DATA", self.seq_num, data)
        self.channel.send_to_server(self.current_packet)
        self.waiting_for_ack = True
        self.send_time = time.time()
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
            self.waiting_for_ack = False
            self.seq_num = 1 - self.seq_num
            print(f"{Fore.BLUE}Client: seq_num updated to {self.seq_num}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.BLUE}Client: Received incorrect or corrupted ACK, ignoring{Style.RESET_ALL}")
            return False

    def check_timeout(self):
        if self.waiting_for_ack and time.time() - self.send_time > self.timeout:
            print(f"{Fore.RED}Client: Timeout occurred, retransmitting packet with seq_num {self.seq_num}{Style.RESET_ALL}")
            self.channel.send_to_server(self.current_packet)
            self.send_time = time.time()