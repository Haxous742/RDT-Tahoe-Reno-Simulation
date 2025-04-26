# import argparse
# import time
# from unreliable_channel import UnreliableChannel
# from client import Client
# from server import Server

# def main():
#     channel = UnreliableChannel(corruption_prob=0.2)
#     client = Client(channel)
#     server = Server(channel)
#     data_to_send = ["Hello", "World", "This", "Is", "A", "Test"]
#     print("\nStarting RDT 2.2 simulation...\n")

#     for data in data_to_send:
#         print(f"\n--- Sending new data: '{data}' ---")
#         client.send_packet(data)
#         while True:
#             server.receive_packet()
#             if client.receive_ack():
#                 break
#             time.sleep(0.1)  # Simulate processing delay

#     print("\nSimulation completed.")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="RDT 2.2 Simulation")
#     parser.add_argument("--run", action="store_true", help="Run the RDT 2.2 simulation")
#     args = parser.parse_args()
#     if args.run:
#         main()

import argparse
import time
from unreliable_channel import UnreliableChannel
from client import Client
from server import Server

def main():
    sentence = input("Enter a sentence to send: ")
    data_to_send = sentence.split()
    print(f"\nData to send: {data_to_send}\n")
    channel = UnreliableChannel(corruption_prob=0.2)
    client = Client(channel)
    server = Server(channel)
    print("\nStarting RDT 2.2 simulation...\n")

    for data in data_to_send:
        print(f"\n\033[35m--- Sending new data: '{data}' ---\033[0m")
        client.send_packet(data)
        while True:
            server.receive_packet()
            if client.receive_ack():
                break
            time.sleep(0.1)  # Simulate processing delay

    print("\nSimulation completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RDT 2.2 Simulation")
    parser.add_argument("--run", action="store_true", help="Run the RDT 2.2 simulation")
    args = parser.parse_args()
    if args.run:
        main()