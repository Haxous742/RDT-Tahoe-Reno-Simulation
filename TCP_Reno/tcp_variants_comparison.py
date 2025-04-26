import matplotlib.pyplot as plt
import numpy as np
import random
from tcp_reno_simulation import TCPRenoSimulation

class TCPTahoeSimulation(TCPRenoSimulation):
    """TCP Tahoe variant that doesn't implement fast recovery"""
    
    def handle_triple_duplicate_ack(self, current_time):
        """Handle triple duplicate ACK according to TCP Tahoe rules (no fast recovery)."""
        self.triple_dup_acks += 1
        
        # Update ssthresh to half of current cwnd
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        
        # Unlike Reno, Tahoe sets cwnd to 1 MSS (same as timeout)
        self.cwnd = self.mss
        
        # Reset duplicate ACK counter
        self.dup_acks = 0
        
        # Switch to slow start (no fast recovery in Tahoe)
        self.state = "slow_start"
        
        # Record event
        self.events.append((current_time, "Triple Dup ACK"))
        
        print(f"Time {current_time}: TRIPLE DUP ACK (Tahoe) - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}, entering Slow Start")

class TCPNewRenoSimulation(TCPRenoSimulation):
    """TCP New Reno variant with improved fast recovery"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recovery_start_time = 0
        self.partial_acks = 0
    
    def handle_triple_duplicate_ack(self, current_time):
        """Handle triple duplicate ACK with New Reno's improved fast recovery."""
        self.triple_dup_acks += 1
        self.fast_recoveries += 1
        
        # Update ssthresh to half of current cwnd
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        
        # Set cwnd to ssthresh + 3*MSS (Fast Recovery)
        self.cwnd = self.ssthresh + 3 * self.mss
        
        # Set duplicate ACK counter
        self.dup_acks = 3
        
        # Track when we entered recovery
        self.recovery_start_time = current_time
        self.partial_acks = 0
        
        # Switch to fast recovery
        self.state = "fast_recovery"
        
        # Record event
        self.events.append((current_time, "Triple Dup ACK"))
        
        print(f"Time {current_time}: TRIPLE DUP ACK (New Reno) - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}, entering Fast Recovery")
    
    def update_congestion_window(self, current_time):
        """Update congestion window with New Reno's improved behavior."""
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
            
            # Determine loss type
            if self.state == "fast_recovery":
                # In fast recovery, simulate a partial ACK
                self.partial_acks += 1
                print(f"Time {current_time}: Partial ACK received in Fast Recovery - cwnd = {self.cwnd}")
                
                # Stay in fast recovery but don't inflate cwnd as much
                if self.partial_acks >= 3:  # After some partial ACKs, exit recovery
                    self.recover_from_fast_recovery(current_time)
            elif random.random() < 0.25:  # 25% chance of timeout
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
                self.cwnd += max(1, (self.mss * self.mss) // self.cwnd)
            
            elif self.state == "fast_recovery":
                # For each duplicate ACK, increase cwnd by 1 MSS
                self.dup_acks += 1
                self.cwnd += self.mss
                
                print(f"Time {current_time}: Fast Recovery - cwnd = {self.cwnd}, dup_acks = {self.dup_acks}")
                
                # Check if we've been in recovery for a while or received enough ACKs
                time_in_recovery = current_time - self.recovery_start_time
                if time_in_recovery >= 5 or self.dup_acks >= 8:  # Arbitrary thresholds
                    self.recover_from_fast_recovery(current_time)

def compare_tcp_variants():
    """Compare different TCP variants side by side."""
    
    # Base parameters for all simulations
    params = {
        'mss': 1,
        'initial_ssthresh': 16,
        'rtt': 1,
        'loss_type': 'interval',
        'loss_param': 12,
        'total_time': 100,
        'random_seed': 42
    }
    
    # Create simulations for each variant
    tcp_tahoe = TCPTahoeSimulation(**params)
    tcp_reno = TCPRenoSimulation(**params)
    tcp_newreno = TCPNewRenoSimulation(**params)
    
    # Run simulations
    tahoe_results = tcp_tahoe.run_simulation()
    reno_results = tcp_reno.run_simulation()
    newreno_results = tcp_newreno.run_simulation()
    
    # Plot comparison
    plt.figure(figsize=(15, 10))
    
    # Plot cwnd comparison
    plt.subplot(2, 1, 1)
    plt.plot(tahoe_results['time'], tahoe_results['cwnd'], label='TCP Tahoe', color='blue')
    plt.plot(reno_results['time'], reno_results['cwnd'], label='TCP Reno', color='green')
    plt.plot(newreno_results['time'], newreno_results['cwnd'], label='TCP New Reno', color='red')
    
    # Add vertical lines for Tahoe loss events
    for time, event_type in tahoe_results['events']:
        plt.axvline(x=time, color='blue', linestyle='--', alpha=0.3)
    
    plt.title('Comparison of TCP Variants: Congestion Window')
    plt.xlabel('Time (RTTs)')
    plt.ylabel('Congestion Window (bytes)')
    plt.grid(True)
    plt.legend()
    
    # Plot state comparison
    plt.subplot(2, 1, 2)
    
    # Convert states to numeric values for plotting
    state_values = {'slow_start': 1, 'congestion_avoidance': 2, 'fast_recovery': 3}
    
    # Plot state timelines
    tahoe_numeric = [state_values.get(state, 0) for state in tahoe_results['state']]
    reno_numeric = [state_values.get(state, 0) for state in reno_results['state']]
    newreno_numeric = [state_values.get(state, 0) for state in newreno_results['state']]
    
    plt.step(tahoe_results['time'], tahoe_numeric, where='post', label='TCP Tahoe', color='blue')
    plt.step(reno_results['time'], reno_numeric, where='post', label='TCP Reno', color='green')
    plt.step(newreno_results['time'], newreno_numeric, where='post', label='TCP New Reno', color='red')
    
    plt.yticks([1, 2, 3], ['Slow Start', 'Congestion Avoidance', 'Fast Recovery'])
    plt.title('Comparison of TCP Variants: State Transitions')
    plt.xlabel('Time (RTTs)')
    plt.ylabel('TCP State')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('tcp_variants_comparison.png')
    plt.show()
    
    # Print statistics for comparison
    print("\n=== TCP Variants Comparison ===")
    
    # Average cwnd
    avg_cwnd_tahoe = sum(tahoe_results['cwnd']) / len(tahoe_results['cwnd'])
    avg_cwnd_reno = sum(reno_results['cwnd']) / len(reno_results['cwnd'])
    avg_cwnd_newreno = sum(newreno_results['cwnd']) / len(newreno_results['cwnd'])
    
    print(f"Average cwnd - Tahoe: {avg_cwnd_tahoe:.2f}, Reno: {avg_cwnd_reno:.2f}, New Reno: {avg_cwnd_newreno:.2f}")
    
    # Time in fast recovery
    tahoe_fr = tahoe_results['state'].count('fast_recovery')
    reno_fr = reno_results['state'].count('fast_recovery')
    newreno_fr = newreno_results['state'].count('fast_recovery')
    
    print(f"Time in Fast Recovery - Tahoe: {tahoe_fr} RTTs, Reno: {reno_fr} RTTs, New Reno: {newreno_fr} RTTs")
    
    # Loss events
    print(f"Loss events - Tahoe: {len(tahoe_results['events'])}, Reno: {len(reno_results['events'])}, New Reno: {len(newreno_results['events'])}")
    
    # Relative performance
    print(f"\nRelative Performance (avg cwnd):")
    print(f"Reno vs Tahoe: {(avg_cwnd_reno/avg_cwnd_tahoe - 1)*100:.2f}% improvement")
    print(f"New Reno vs Reno: {(avg_cwnd_newreno/avg_cwnd_reno - 1)*100:.2f}% improvement")
    print(f"New Reno vs Tahoe: {(avg_cwnd_newreno/avg_cwnd_tahoe - 1)*100:.2f}% improvement")

def analyze_parameter_effects():
    """Analyze the effects of different parameters on TCP Reno performance."""
    
    # Base parameters
    base_params = {
        'mss': 1,
        'initial_ssthresh': 16,
        'rtt': 1,
        'loss_type': 'interval',
        'total_time': 100,
        'random_seed': 42
    }
    
    # Test different loss frequencies
    loss_params = [5, 10, 20, 40]
    avg_cwnd_values = []
    
    plt.figure(figsize=(15, 6))
    
    for loss_param in loss_params:
        # Create simulation with current loss parameter
        tcp_sim = TCPRenoSimulation(**base_params, loss_param=loss_param)
        results = tcp_sim.run_simulation()
        
        # Plot cwnd
        plt.plot(results['time'], results['cwnd'], label=f'Loss interval = {loss_param} RTTs')
        
        # Calculate average cwnd
        avg_cwnd = sum(results['cwnd']) / len(results['cwnd'])
        avg_cwnd_values.append(avg_cwnd)
    
    plt.title('Effect of Loss Frequency on TCP Reno Performance')
    plt.xlabel('Time (RTTs)')
    plt.ylabel('Congestion Window (bytes)')
    plt.grid(True)
    plt.legend()
    
    plt.savefig('tcp_loss_frequency_analysis.png')
    plt.show()
    
    # Print analysis results
    print("\n=== Effect of Loss Frequency on TCP Reno Performance ===")
    for i, loss_param in enumerate(loss_params):
        print(f"Loss interval = {loss_param} RTTs: Average cwnd = {avg_cwnd_values[i]:.2f}")

if __name__ == "__main__":
    print("Running TCP variants comparison...")
    compare_tcp_variants()
    
    print("\nAnalyzing parameter effects...")
    analyze_parameter_effects()