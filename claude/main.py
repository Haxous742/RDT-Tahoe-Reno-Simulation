import time
import threading
from client import RDTClient, Packet, ACK
from server import RDTServer
from unreliable_channel import UnreliableChannel

def main():
    print("Starting RDT 2.2 Protocol Simulation")
    
    # Create unreliable channel with specified error rates
    channel = UnreliableChannel(error_rate=0.2, loss_rate=0.1)
    
    # Create server and client
    server = RDTServer(channel)
    client = RDTClient(channel)
    
    # Data to send
    data_to_send = [
        "Hello, world!",
        "Testing RDT 2.2",
        "This is a longer message to test the protocol with more data.",
        "Final test message"
    ]
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.start_listening, args=(len(data_to_send)*3,))
    server_thread.daemon = True
    server_thread.start()
    
    # Allow server to start up
    time.sleep(0.5)
    
    # Send data from client
    for data in data_to_send:
        client.send_data(data)
        time.sleep(1)  # Wait a bit between sends for readability
    
    # Wait for all transmissions to complete
    time.sleep(2)
    
    # Print received data for verification
    print("\nSummary of transmission:")
    print(f"Data sent by client: {data_to_send}")
    print(f"Data received by server: {server.received_data}")
    
    # Verify all data was received correctly
    if data_to_send == server.received_data:
        print("SUCCESS: All data was correctly received!")
    else:
        print("ERROR: Some data was not correctly received.")

if __name__ == "__main__":
    main()