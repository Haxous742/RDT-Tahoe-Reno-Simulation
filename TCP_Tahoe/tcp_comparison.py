from tcp_congestion_control import TCPCongestionControl
import matplotlib.pyplot as plt
import numpy as np

def compare_loss_models():
    """
    Compare different loss models and their impact on congestion window behavior.
    """
    # Create different simulations
    sim1 = TCPCongestionControl(mss=1, initial_ssthresh=16, 
                               loss_type='interval', loss_param=20, 
                               total_time=100, random_seed=42)
    
    sim2 = TCPCongestionControl(mss=1, initial_ssthresh=16, 
                               loss_type='probability', loss_param=0.05, 
                               total_time=100, random_seed=42)
    
    # Run simulations
    results1 = sim1.run_simulation()
    results2 = sim2.run_simulation()
    
    # Plot comparison
    plt.figure(figsize=(12, 8))
    
    # Plot first simulation
    plt.subplot(2, 1, 1)
    plt.plot(results1['time'], results1['cwnd'], label='cwnd', color='blue')
    plt.plot(results1['time'], results1['ssthresh'], label='ssthresh', color='red', linestyle='--')
    
    # Mark loss events for first simulation
    for time, event_type in results1['events']:
        if event_type == "Timeout":
            plt.axvline(x=time, color='orange', linestyle='-', alpha=0.5)
        else:  # Triple Duplicate ACK
            plt.axvline(x=time, color='green', linestyle='-', alpha=0.5)
    
    plt.title('TCP Congestion Window: Regular Interval Loss')
    plt.ylabel('Window Size (bytes)')
    plt.grid(True)
    plt.legend()
    
    # Plot second simulation
    plt.subplot(2, 1, 2)
    plt.plot(results2['time'], results2['cwnd'], label='cwnd', color='blue')
    plt.plot(results2['time'], results2['ssthresh'], label='ssthresh', color='red', linestyle='--')
    
    # Mark loss events for second simulation
    for time, event_type in results2['events']:
        if event_type == "Timeout":
            plt.axvline(x=time, color='orange', linestyle='-', alpha=0.5)
        else:  # Triple Duplicate ACK
            plt.axvline(x=time, color='green', linestyle='-', alpha=0.5)
    
    plt.title('TCP Congestion Window: Probabilistic Loss')
    plt.xlabel('Time (RTTs)')
    plt.ylabel('Window Size (bytes)')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('tcp_loss_model_comparison.png')
    plt.show()

def compare_tcp_variants():
    """
    Simulate different TCP variants (standard vs more aggressive growth).
    This is a simplified representation for demonstration purposes.
    """
    # Base parameters
    mss = 1
    initial_ssthresh = 16
    total_time = 100
    loss_param = 15
    
    # Standard TCP (Reno-like)
    tcp_standard = TCPCongestionControl(
        mss=mss, 
        initial_ssthresh=initial_ssthresh,
        loss_type='interval', 
        loss_param=loss_param,
        total_time=total_time,
        random_seed=42
    )
    
    # Custom more aggressive TCP variant
    class AggressiveTCP(TCPCongestionControl):
        def update_congestion_window(self, current_time):
            """Override with more aggressive growth behavior."""
            # Record current state
            self.time_points.append(current_time)
            self.cwnd_history.append(self.cwnd)
            self.ssthresh_history.append(self.ssthresh)
            
            # Check for packet loss
            if self.will_packet_be_lost(current_time):
                # More aggressive recovery
                if random.random() < 0.3:  # 30% chance of timeout
                    self.handle_timeout(current_time)
                else:
                    # Less severe penalty for Triple Duplicate ACK
                    print(f"Time {current_time}: TRIPLE DUPLICATE ACK detected (Aggressive TCP)")
                    self.ssthresh = max(2 * self.mss, int(self.cwnd * 0.7))  # Reduce by 30% not 50%
                    self.cwnd = self.ssthresh
                    self.mode = "congestion_avoidance"
                    self.events.append((current_time, "Triple Dup ACK"))
            else:
                # No loss - update cwnd according to current phase
                if self.mode == "slow_start":
                    # Same as standard TCP
                    self.cwnd += self.cwnd
                    if self.cwnd >= self.ssthresh:
                        self.mode = "congestion_avoidance"
                
                elif self.mode == "congestion_avoidance":
                    # More aggressive increase (approximately 1.5 MSS per RTT)
                    self.cwnd += int(1.5 * (self.mss * self.mss) // self.cwnd)
    
    import random
    # Create the aggressive variant
    tcp_aggressive = AggressiveTCP(
        mss=mss, 
        initial_ssthresh=initial_ssthresh,
        loss_type='interval', 
        loss_param=loss_param,
        total_time=total_time,
        random_seed=42
    )
    
    # Run simulations
    results_standard = tcp_standard.run_simulation()
    results_aggressive = tcp_aggressive.run_simulation()
    
    # Plot comparison
    plt.figure(figsize=(12, 6))
    
    plt.plot(results_standard['time'], results_standard['cwnd'], 
             label='Standard TCP', color='blue')
    plt.plot(results_aggressive['time'], results_aggressive['cwnd'], 
             label='Aggressive TCP', color='green')
    
    # Add vertical lines for standard TCP loss events
    for time, event_type in results_standard['events']:
        plt.axvline(x=time, color='blue', linestyle='--', alpha=0.3)
    
    # Add vertical lines for aggressive TCP loss events
    for time, event_type in results_aggressive['events']:
        plt.axvline(x=time, color='green', linestyle='--', alpha=0.3)
    
    plt.title('Comparison of TCP Variants')
    plt.xlabel('Time (RTTs)')
    plt.ylabel('Congestion Window (bytes)')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('tcp_variants_comparison.png')
    plt.show()
    
    # Calculate average throughput
    avg_cwnd_standard = sum(results_standard['cwnd']) / len(results_standard['cwnd'])
    avg_cwnd_aggressive = sum(results_aggressive['cwnd']) / len(results_aggressive['cwnd'])
    
    print(f"Standard TCP - Average cwnd: {avg_cwnd_standard:.2f}")
    print(f"Aggressive TCP - Average cwnd: {avg_cwnd_aggressive:.2f}")
    print(f"Improvement: {((avg_cwnd_aggressive / avg_cwnd_standard) - 1) * 100:.2f}%")

if __name__ == "__main__":
    print("Running TCP loss model comparison...")
    compare_loss_models()
    
    print("\nRunning TCP variants comparison...")
    compare_tcp_variants()