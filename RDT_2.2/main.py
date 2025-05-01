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
    channel = UnreliableChannel(corruption_prob=0.2)
    client = Client(channel)
    server = Server(channel)
    print("\nStarting RDT 2.2 simulation...\n")

    for data in data_to_send:
        print(f"\n{Fore.MAGENTA}------- SENDING NEW DATA: '{data}' -------{Style.RESET_ALL}")
        client.send_packet(data)
        while True:
            server.receive_packet()
            if client.receive_ack():
                break
            time.sleep(0.1)  

    print("\nSIMULATION COMPLETE!!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RDT 2.2 Simulation")
    parser.add_argument("--run", action="store_true", help="Run the RDT 2.2 simulation")
    args = parser.parse_args()
    if args.run:
        main()