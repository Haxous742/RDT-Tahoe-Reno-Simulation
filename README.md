# Reliable Data Transfer (RDT) Simulations: RDT 2.2 and RDT 3.0

This project provides Python implementations of two Reliable Data Transfer (RDT) protocols: **RDT 2.2** and **RDT 3.0**. These protocols are simulated over an unreliable channel that can corrupt or lose packets, demonstrating how reliable communication can be achieved despite these challenges.

- **RDT 2.2** focuses on error detection and retransmission using acknowledgments (ACKs).
- **RDT 3.0** builds on RDT 2.2 by adding timers to handle packet loss in addition to error detection.

The simulations are designed to be easy to understand and modify, with detailed logging and color-coded outputs to visualize the protocol behaviors.

---

## Table of Contents

- [Introduction](#introduction)
- [Implementation Overview](#implementation-overview)
- [RDT 2.2](#rdt-22)
  - [Features](#features-22)
  - [Parameter Choices](#parameter-choices-22)
  - [Sample Output](#sample-output-22)
- [RDT 3.0](#rdt-30)
  - [Features](#features-30)
  - [Parameter Choices](#parameter-choices-30)
  - [Sample Output](#sample-output-30)
- [Running the Simulations](#running-the-simulations)
- [Dependencies](#dependencies)

---

## Introduction

Reliable Data Transfer (RDT) protocols ensure that data is delivered correctly and in order over unreliable channels. This project simulates two such protocols:

- **RDT 2.2**: Implements error detection using checksums and retransmission based on ACKs. It handles packet corruption but assumes no packet loss.
- **RDT 3.0**: Extends RDT 2.2 by adding timers to handle both packet corruption and loss, ensuring reliability even when packets or ACKs are lost.

These simulations help illustrate the fundamental concepts of reliable communication in computer networks.

---

## Implementation Overview

Both RDT 2.2 and RDT 3.0 are implemented using three main components:

- **Client**: Sends packets containing data to the server via the unreliable channel.
- **Server**: Receives packets, verifies their integrity, and sends ACKs back to the client.
- **Unreliable Channel**: Simulates a communication medium that can corrupt or lose packets with configurable probabilities.

The simulations use Python's `queue` module to model the communication between the client and server, avoiding the need for actual network sockets. Color-coded logging (using `colorama`) provides clear insights into the protocol's behavior.

---

## RDT 2.2

### Features

- **Packet Structure**: Each packet includes a 1-bit sequence number, payload data, and a checksum for error detection.
- **Client Behavior**:
  - Sends packets and waits for ACKs.
  - Retransmits the current packet if a duplicate or corrupted ACK is received.
- **Server Behavior**:
  - Verifies the checksum and sequence number of received packets.
  - Delivers data to the upper layer and sends an ACK if the packet is correct and in order.
  - Sends a duplicate ACK for the last correctly received packet if the received packet is corrupted or out of order.
- **Unreliable Channel**:
  - Randomly corrupts packets (sequence number or payload) with a configurable probability.

### Parameter Choices

- **Corruption Probability (`corruption_prob`)**: Set to 0.2 (20%) by default. This value was chosen to frequently trigger error scenarios without overwhelming the system, allowing users to observe retransmissions and error handling.
- **Loss Probability**: Not applicable in RDT 2.2, as it assumes no packet loss.

### Sample Output

Below is a sample output snippet from the RDT 2.2 simulation, showing a packet being sent, corrupted, and retransmitted:

```plaintext
Client sent packet with seq_num 0, payload: 'Hello', checksum: 12345678
Channel corrupted DATA packet payload: 'Hello' -> 'Hellp'
Server received packet with seq_num 0, payload: 'Hellp', checksum: 12345678, corrupt: True
Server: Packet is corrupted or out-of-order, sending ACK for seq_num 1
Server sent ACK with seq_num 1, checksum: 87654321
Client received ACK with seq_num 1, checksum: 87654321, corrupt: False
Client: Incorrect or corrupted ACK, retransmitting seq_num 0
Client sent packet with seq_num 0, payload: 'Hello', checksum: 12345678
Server received packet with seq_num 0, payload: 'Hello', checksum: 12345678, corrupt: False
Server: Packet seq_num 0 is correct and in order
Delivered to upper layer: 'Hello'
Server sent ACK with seq_num 0, checksum: 87654321
Client received ACK with seq_num 0, checksum: 87654321, corrupt: False
Client: Correct ACK for seq_num 0 received
Client: seq_num updated to 1
```