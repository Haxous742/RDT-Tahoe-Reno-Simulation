import matplotlib.pyplot as plt
import numpy as np
import random
import argparse

class TCPRenoSimulation:
    def __init__(self, mss=1, initial_ssthresh=16, rtt=1, loss_type='interval', 
                 loss_param=10, total_time=100, random_seed=None):
        """
        Initialize TCP Reno congestion control simulation.
        
        Parameters:
        - mss: Maximum Segment Size (in arbitrary units)
        - initial_ssthresh: Initial slow-start threshold (in MSS units)
        - rtt: Round-trip time (in arbitrary time units)
        - loss_type: 'interval' (loss every N RTTs) or 'probability' (random loss)
        - loss_param: For 'interval', the number of RTTs between losses
                      For 'probability', the probability of loss per RTT
        - total_time: Total simulation time in RTTs
        - random_seed: Seed for random number generator (for reproducibility)
        """
        self.mss = mss
        self.initial_ssthresh = initial_ssthresh * mss  # Convert to bytes
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
        self.ssthresh = self.initial_ssthresh
        self.state = "slow_start"  # Start in slow start mode
        
        # History trackers for visualization
        self.time_points = []
        self.cwnd_history = []
        self.ssthresh_history = []
        self.state_history = []
        self.dup_acks = 0
        self.events = []  # To mark loss events on the graph
        
        # Analysis metrics
        self.packets_sent = 0
        self.packets_lost = 0
        self.timeouts = 0
        self.triple_dup_acks = 0
        self.fast_recoveries = 0
        
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
        """Handle a timeout event according to TCP Reno rules."""
        self.timeouts += 1
        # Update ssthresh to half of current cwnd (minimum 2*MSS)
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        # Reset cwnd to 1 MSS
        self.cwnd = self.mss
        # Reset duplicate ACK counter
        self.dup_acks = 0
        # Reset to slow start
        self.state = "slow_start"
        # Record event
        self.events.append((current_time, "Timeout"))
        
        print(f"Time {current_time}: TIMEOUT - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
    
    def handle_triple_duplicate_ack(self, current_time):
        """Handle triple duplicate ACK (fast retransmit/recovery) according to TCP Reno rules."""
        self.triple_dup_acks += 1
        self.fast_recoveries += 1
        # Update ssthresh to half of current cwnd
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        # Set cwnd to ssthresh + 3*MSS (Fast Recovery)
        self.cwnd = self.ssthresh + 3 * self.mss
        # Reset duplicate ACK counter
        self.dup_acks = 3  # We're in Fast Recovery state with 3 duplicate ACKs
        # Switch to fast recovery
        self.state = "fast_recovery"
        # Record event
        self.events.append((current_time, "Triple Dup ACK"))
        
        print(f"Time {current_time}: TRIPLE DUP ACK - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}, entering Fast Recovery")
    
    def recover_from_fast_recovery(self, current_time):
        """Recover from Fast Recovery state."""
        # Set cwnd to ssthresh
        self.cwnd = self.ssthresh
        # Reset duplicate ACK counter
        self.dup_acks = 0
        # Switch to congestion avoidance
        self.state = "congestion_avoidance"
        
        print(f"Time {current_time}: RECOVERY COMPLETE - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
    
    def update_congestion_window(self, current_time):
        """Update the congestion window based on current state."""
        # Record current state
        self.time_points.append(current_time)
        self.cwnd_history.append(self.cwnd)
        self.ssthresh_history.append(self.ssthresh)
        self.state_history.append(self.state)
        
        # Simulate packet transmission
        self.packets_sent += 1
        
        # Check for packet loss
        if self.will_packet_be_lost(current_time):
            self.packets_lost += 1
            
            # Determine if this is a timeout or triple duplicate ACK
            if self.state == "fast_recovery" or random.random() < 0.25:  # 25% chance of timeout
                self.handle_timeout(current_time)
            else:
                self.handle_triple_duplicate_ack(current_time)
        else:
            # No loss - update cwnd according to current state
            if self.state == "slow_start":
                print(f"Time {current_time}: Slow Start - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
                # In slow start, cwnd increases by 1 MSS for each ACK
                # Simplified: increase by cwnd (doubles every RTT)
                self.cwnd += self.cwnd
                
                # Check if we should transition to congestion avoidance
                if self.cwnd >= self.ssthresh:
                    print(f"Time {current_time}: Transitioning to Congestion Avoidance")
                    self.state = "congestion_avoidance"
            
            elif self.state == "congestion_avoidance":
                print(f"Time {current_time}: Congestion Avoidance - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
                # In congestion avoidance, cwnd increases by MSS*MSS/cwnd per RTT
                # This is approximately 1 MSS per RTT
                self.cwnd += max(1, (self.mss * self.mss) // self.cwnd)
            
            elif self.state == "fast_recovery":
                # For each duplicate ACK, increase cwnd by 1 MSS
                self.dup_acks += 1
                self.cwnd += self.mss
                print(f"Time {current_time}: Fast Recovery - cwnd = {self.cwnd}, dup_acks = {self.dup_acks}")
                
                # After a certain number of RTTs in fast recovery, we'll recover
                # In a real implementation, this would happen when a new ACK arrives
                if self.dup_acks >= 5:  # Arbitrary number for simulation purposes
                    self.recover_from_fast_recovery(current_time)
    
    def run_simulation(self):
        """Run the TCP Reno congestion control simulation for the specified time."""
        for t in range(self.total_time):
            self.update_congestion_window(t)
            
        return {
            'time': self.time_points,
            'cwnd': self.cwnd_history,
            'ssthresh': self.ssthresh_history,
            'state': self.state_history,
            'events': self.events
        }
    
    def plot_results(self, filename='tcp_reno_simulation.png'):
        """Plot the simulation results."""
        plt.figure(figsize=(14, 10))
        
        # Main plot: cwnd and ssthresh
        plt.subplot(2, 1, 1)
        plt.plot(self.time_points, self.cwnd_history, label='cwnd', color='blue', linewidth=2)
        plt.plot(self.time_points, self.ssthresh_history, label='ssthresh', color='red', linestyle='--', linewidth=1.5)
        
        # Create a colormap for different states
        colors = {'slow_start': 'lightskyblue', 'congestion_avoidance': 'lightgreen', 'fast_recovery': 'lightsalmon'}
        
        # Add background colors for different states
        for i in range(len(self.state_history) - 1):
            plt.axvspan(self.time_points[i], self.time_points[i+1], 
                        alpha=0.2, color=colors.get(self.state_history[i], 'white'))
        
        # Mark loss events
        for time, event_type in self.events:
            if event_type == "Timeout":
                plt.axvline(x=time, color='orange', linestyle='-', alpha=0.7)
                plt.text(time, max(self.cwnd_history) * 0.9, "TO", rotation=90)
            else:  # Triple Duplicate ACK
                plt.axvline(x=time, color='green', linestyle='-', alpha=0.7)
                plt.text(time, max(self.cwnd_history) * 0.9, "3DA", rotation=90)
        
        plt.xlabel('Time (RTTs)')
        plt.ylabel('Window Size (bytes)')
        plt.title('TCP Reno Congestion Window Evolution')
        plt.legend()
        plt.grid(True)
        
        # Second plot: TCP state
        plt.subplot(2, 1, 2)
        
        # Convert states to numeric values for plotting
        state_values = {'slow_start': 1, 'congestion_avoidance': 2, 'fast_recovery': 3}
        numeric_states = [state_values.get(state, 0) for state in self.state_history]
        
        # Plot the state transition timeline
        plt.step(self.time_points, numeric_states, where='post')
        plt.yticks([1, 2, 3], ['Slow Start', 'Congestion Avoidance', 'Fast Recovery'])
        plt.xlabel('Time (RTTs)')
        plt.ylabel('TCP State')
        plt.title('TCP Reno State Transitions')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(filename)
        plt.show()
        
        # Return the filename for reference
        return filename
    
    def print_statistics(self):
        """Print summary statistics about the simulation."""
        print("\n=== TCP Reno Simulation Statistics ===")
        print(f"Total simulation time: {self.total_time} RTTs")
        print(f"Final cwnd: {self.cwnd}")
        print(f"Final ssthresh: {self.ssthresh}")
        print(f"Packets sent: {self.packets_sent}")
        print(f"Packets lost: {self.packets_lost} ({self.packets_lost/self.packets_sent*100:.2f}%)")
        print(f"Timeouts: {self.timeouts}")
        print(f"Triple duplicate ACKs: {self.triple_dup_acks}")
        print(f"Fast recovery events: {self.fast_recoveries}")
        
        # Calculate average throughput (simplified)
        avg_cwnd = sum(self.cwnd_history) / len(self.cwnd_history)
        print(f"Average cwnd: {avg_cwnd:.2f}")
        
        # Calculate time spent in each state
        state_counts = {s: self.state_history.count(s) for s in set(self.state_history)}
        print("\nTime spent in each state:")
        for state, count in state_counts.items():
            print(f"  {state}: {count} RTTs ({count/self.total_time*100:.2f}%)")

def parse_arguments():
    """Parse command line arguments for the TCP Reno simulation."""
    parser = argparse.ArgumentParser(description='TCP Reno Congestion Control Simulation')
    parser.add_argument('--mss', type=int, default=1, help='Maximum Segment Size')
    parser.add_argument('--ssthresh', type=int, default=16, help='Initial slow-start threshold (in MSS units)')
    parser.add_argument('--rtt', type=float, default=1, help='Round-trip time')
    parser.add_argument('--loss_type', choices=['interval', 'probability'], default='interval', 
                        help='Type of loss model: interval or probability')
    parser.add_argument('--loss_param', type=float, default=10, 
                        help='Loss parameter: interval length or probability')
    parser.add_argument('--time', type=int, default=100, help='Total simulation time (in RTTs)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--output', type=str, default='tcp_reno_simulation.png', help='Output filename for the plot')
    return parser.parse_args()

def main():
    """Main function to run the TCP Reno congestion control simulation."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Create and run the simulation
    tcp_sim = TCPRenoSimulation(
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
    output_file = tcp_sim.plot_results(args.output)
    
    # Print statistics
    tcp_sim.print_statistics()
    print(f"Plot saved as '{output_file}'")

if __name__ == "__main__":
    main()