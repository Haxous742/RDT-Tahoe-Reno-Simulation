import argparse
import time
from unreliable_channel import UnreliableChannel
from client import Client
from server import Server
from colorama import Fore, Style

def main():
    sentence = input("Enter a sentence to send: ")
    data_to_send = sentence.split()
    print(f"\nData to send: {data_to_send}\n")
    channel = UnreliableChannel(corruption_prob=0.5, loss_prob=1/3)
    client = Client(channel)
    server = Server(channel)
    print("\nStarting RDT 3.0 simulation...\n")

    for data in data_to_send:
        print(f"\n{Fore.MAGENTA}------- SENDING NEW DATA: '{data}' -------{Style.RESET_ALL}")
        client.send_packet(data)
        while True:
            server.receive_packet()
            if client.receive_ack():
                break
            client.check_timeout()
            time.sleep(0.1)  # Simulate processing delay

    print("\nSIMULATION COMPLETE!!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RDT 3.0 Simulation")
    parser.add_argument("--run", action="store_true", help="Run the RDT 3.0 simulation")
    args = parser.parse_args()
    if args.run:
        main()