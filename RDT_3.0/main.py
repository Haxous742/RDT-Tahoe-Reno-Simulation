import argparse
import time
from unreliable_channel import UnreliableChannel
from client import Client
from server import Server

def main():
    sentence = input("Enter a sentence to send: ")
    data_to_send = sentence.split()
    print(f"\nData to send: {data_to_send}\n")
    channel = UnreliableChannel(corruption_prob=0.2, loss_prob=0.2)
    client = Client(channel)
    server = Server(channel)
    print("\nStarting RDT 3.0 simulation...\n")
    for data in data_to_send:
        print(f"\n--- Sending new data: '{data}' ---")
        client.send_packet(data)
        while True:
            server.receive_packet()
            if client.receive_ack():
                break
            client.check_timeout()
            time.sleep(0.1)  # Simulate processing delay
    print("\nSimulation completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RDT 3.0 Simulation")
    parser.add_argument("--run", action="store_true", help="Run the RDT 3.0 simulation")
    args = parser.parse_args()
    if args.run:
        main()