import matplotlib.pyplot as plt
import numpy as np
import random
import argparse

class TCPCongestionControl:
    def __init__(self, mss=1, initial_ssthresh=16, rtt=1, loss_type='interval', loss_param=10, 
                 total_time=100, random_seed=None):
        """
        Initialize TCP congestion control simulation.
        
        Parameters:
        - mss: Maximum Segment Size (in arbitrary units)
        - initial_ssthresh: Initial slow-start threshold
        - rtt: Round-trip time (in arbitrary time units)
        - loss_type: 'interval' (loss every N RTTs) or 'probability' (random loss)
        - loss_param: For 'interval', this is the number of RTTs between losses
                      For 'probability', this is the probability of loss per RTT
        - total_time: Total simulation time in RTTs
        - random_seed: Seed for random number generator (for reproducibility)
        """
        self.mss = mss
        self.initial_ssthresh = initial_ssthresh
        self.rtt = rtt
        self.loss_type = loss_type
        self.loss_param = loss_param
        self.total_time = total_time
        
        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)
        
        # Initialize TCP state
        self.cwnd = mss  # Start with cwnd = 1 MSS
        self.ssthresh = initial_ssthresh * mss  # Initial ssthresh in bytes
        self.mode = "slow_start"  # Start in slow start mode
        
        # History trackers for visualization
        self.time_points = []
        self.cwnd_history = []
        self.ssthresh_history = []
        self.events = []  # To mark loss events on the graph
        
        # Counters for analysis
        self.dup_ack_count = 0
        self.total_packets_sent = 0
        self.total_packets_acked = 0
        
    def will_packet_be_lost(self, current_time):
        """Determine if a packet will be lost based on the loss model."""
        if self.loss_type == 'interval':
            # Loss occurs every loss_param RTTs
            return current_time > 0 and current_time % self.loss_param == 0
        elif self.loss_type == 'probability':
            # Loss occurs with probability loss_param
            return random.random() < self.loss_param
        return False
    
    def handle_timeout(self, current_time):
        """Handle a timeout event."""
        print(f"Time {current_time}: TIMEOUT detected")
        # Update ssthresh to half of current cwnd (minimum 2*MSS)
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        # Reset cwnd to 1 MSS
        self.cwnd = self.mss
        # Reset to slow start
        self.mode = "slow_start"
        # Record the event for visualization
        self.events.append((current_time, "Timeout"))
    
    def handle_triple_duplicate_ack(self, current_time):
        """Handle triple duplicate ACK (fast retransmit)."""
        print(f"Time {current_time}: TRIPLE DUPLICATE ACK detected")
        # Update ssthresh to half of current cwnd
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        # Set cwnd to ssthresh (fast recovery)
        self.cwnd = self.ssthresh
        # Reset duplicate ACK counter
        self.dup_ack_count = 0
        # Switch to congestion avoidance
        self.mode = "congestion_avoidance"
        # Record the event for visualization
        self.events.append((current_time, "Triple Dup ACK"))
    
    def update_congestion_window(self, current_time):
        """Update the congestion window based on current mode."""
        # Record current state
        self.time_points.append(current_time)
        self.cwnd_history.append(self.cwnd)
        self.ssthresh_history.append(self.ssthresh)
        
        # Check for packet loss
        if self.will_packet_be_lost(current_time):
            # Randomly choose between timeout and triple duplicate ACK
            # In a more advanced simulation, this would depend on network conditions
            loss_type = random.choice(["timeout", "triple_dup_ack"])
            
            if loss_type == "timeout":
                self.handle_timeout(current_time)
            else:
                self.handle_triple_duplicate_ack(current_time)
        else:
            # No loss - update cwnd according to current phase
            if self.mode == "slow_start":
                print(f"Time {current_time}: Slow Start - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
                # In slow start, cwnd increases by 1 MSS for each ACK
                # Simplified to increase by cwnd after each RTT
                self.cwnd += self.cwnd
                
                # Check if we should transition to congestion avoidance
                if self.cwnd >= self.ssthresh:
                    print(f"Time {current_time}: Transitioning to Congestion Avoidance")
                    self.mode = "congestion_avoidance"
            
            elif self.mode == "congestion_avoidance":
                print(f"Time {current_time}: Congestion Avoidance - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
                # In congestion avoidance, cwnd increases by MSS*MSS/cwnd per RTT
                # This is approximately 1 MSS per RTT
                self.cwnd += max(1, (self.mss * self.mss) // self.cwnd)
    
    def run_simulation(self):
        """Run the TCP congestion control simulation for the specified time."""
        for t in range(self.total_time):
            self.update_congestion_window(t)
            
        return {
            'time': self.time_points,
            'cwnd': self.cwnd_history,
            'ssthresh': self.ssthresh_history,
            'events': self.events
        }
    
    def plot_results(self):
        """Plot the simulation results."""
        plt.figure(figsize=(12, 6))
        
        # Plot cwnd
        plt.plot(self.time_points, self.cwnd_history, label='cwnd', color='blue')
        
        # Plot ssthresh
        plt.plot(self.time_points, self.ssthresh_history, label='ssthresh', color='red', linestyle='--')
        
        # Mark loss events
        for time, event_type in self.events:
            if event_type == "Timeout":
                plt.axvline(x=time, color='orange', linestyle='-', alpha=0.5)
                plt.text(time, max(self.cwnd_history) * 0.9, "TO", rotation=90)
            else:  # Triple Duplicate ACK
                plt.axvline(x=time, color='green', linestyle='-', alpha=0.5)
                plt.text(time, max(self.cwnd_history) * 0.9, "3DA", rotation=90)
        
        # Add labels and title
        plt.xlabel('Time (RTTs)')
        plt.ylabel('Congestion Window (bytes)')
        plt.title('TCP Congestion Window Over Time')
        plt.legend()
        plt.grid(True)
        
        # Ensure y-axis starts at 0
        plt.ylim(bottom=0)
        
        # Save the figure
        plt.savefig('tcp_congestion_window.png')
        plt.tight_layout()
        plt.show()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='TCP Congestion Control Simulation')
    parser.add_argument('--mss', type=int, default=1, help='Maximum Segment Size')
    parser.add_argument('--ssthresh', type=int, default=16, help='Initial slow-start threshold (in MSS units)')
    parser.add_argument('--rtt', type=float, default=1, help='Round-trip time')
    parser.add_argument('--loss_type', choices=['interval', 'probability'], default='interval', 
                        help='Type of loss model: interval or probability')
    parser.add_argument('--loss_param', type=float, default=10, 
                        help='Loss parameter: interval length or probability')
    parser.add_argument('--time', type=int, default=100, help='Total simulation time (in RTTs)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    return parser.parse_args()

def main():
    """Main function to run the TCP congestion control simulation."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Create and run the simulation
    tcp_sim = TCPCongestionControl(
        mss=args.mss,
        initial_ssthresh=args.ssthresh,
        rtt=args.rtt,
        loss_type=args.loss_type,
        loss_param=args.loss_param,
        total_time=args.time,
        random_seed=args.seed
    )
    
    # Run the simulation
    results = tcp_sim.run_simulation()
    
    # Plot and save the results
    tcp_sim.plot_results()
    
    # Print final statistics
    print("\nSimulation Complete!")
    print(f"Final cwnd: {tcp_sim.cwnd}")
    print(f"Final ssthresh: {tcp_sim.ssthresh}")
    print(f"Total loss events: {len(tcp_sim.events)}")
    print(f"Timeouts: {sum(1 for _, event in tcp_sim.events if event == 'Timeout')}")
    print(f"Triple duplicate ACKs: {sum(1 for _, event in tcp_sim.events if event == 'Triple Dup ACK')}")
    
    # Calculate average throughput (simplified)
    avg_cwnd = sum(tcp_sim.cwnd_history) / len(tcp_sim.cwnd_history)
    print(f"Average cwnd: {avg_cwnd:.2f}")
    print(f"Simulation time: {args.time} RTTs")
    print(f"Graph saved as 'tcp_congestion_window.png'")

if __name__ == "__main__":
    main()