import matplotlib.pyplot as plt
import random

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
        - loss_param: For 'interval', RTTs between losses; for 'probability', loss probability per RTT
        - total_time: Total simulation time in RTTs
        - random_seed: Seed for random number generator (optional)
        """
        self.mss = mss
        self.initial_ssthresh = initial_ssthresh * mss  # Convert to bytes
        self.rtt = rtt
        self.loss_type = loss_type
        self.loss_param = loss_param
        self.total_time = total_time
        
        if random_seed is not None:
            random.seed(random_seed)
        
        # TCP state
        self.cwnd = mss  # Start with cwnd = 1 MSS
        self.ssthresh = self.initial_ssthresh
        self.state = "slow_start"
        
        # History for plotting
        self.time_points = []
        self.cwnd_history = []
        self.ssthresh_history = []
        self.state_history = []
        self.dup_acks = 0
        self.events = []
        
        # Statistics
        self.packets_sent = 0
        self.packets_lost = 0
        self.timeouts = 0
        self.triple_dup_acks = 0
        self.fast_recoveries = 0
    
    def will_packet_be_lost(self, current_time):
        """Check if a packet is lost based on loss model."""
        if self.loss_type == 'interval':
            return current_time > 0 and current_time % self.loss_param == 0
        elif self.loss_type == 'probability':
            return random.random() < self.loss_param
        return False
    
    def handle_timeout(self, current_time):
        """Handle timeout event per TCP Reno."""
        self.timeouts += 1
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        self.cwnd = self.mss
        self.dup_acks = 0
        self.state = "slow_start"
        self.events.append((current_time, "Timeout"))
        print(f"Time {current_time}: TIMEOUT - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
    
    def handle_triple_duplicate_ack(self, current_time):
        """Handle triple duplicate ACK per TCP Reno."""
        self.triple_dup_acks += 1
        self.fast_recoveries += 1
        self.ssthresh = max(2 * self.mss, self.cwnd // 2)
        self.cwnd = self.ssthresh + 3 * self.mss  # Set cwnd to ssthresh + 3*MSS
        self.dup_acks = 3
        self.state = "fast_recovery"
        self.events.append((current_time, "Triple Dup ACK"))
        print(f"Time {current_time}: TRIPLE DUP ACK - cwnd = {self.cwnd}, ssthresh = {self.ssthresh}")
    
    def recover_from_fast_recovery(self, current_time):
        """Exit fast recovery state."""
        self.cwnd = self.ssthresh
        self.dup_acks = 0
        self.state = "congestion_avoidance"
        print(f"Time {current_time}: RECOVERY COMPLETE - cwnd = {self.cwnd}")
    
    def update_congestion_window(self, current_time):
        """Update cwnd based on current state."""
        self.time_points.append(current_time)
        self.cwnd_history.append(self.cwnd)
        self.ssthresh_history.append(self.ssthresh)
        self.state_history.append(self.state)
        
        self.packets_sent += 1
        
        if self.will_packet_be_lost(current_time):
            self.packets_lost += 1
            # 50% chance for timeout, 50% for triple dup ACK
            if random.random() < 0.5:
                self.handle_timeout(current_time)
            else:
                self.handle_triple_duplicate_ack(current_time)
        else:
            if self.state == "slow_start":
                print(f"Time {current_time}: Slow Start - cwnd = {self.cwnd}")
                self.cwnd += self.cwnd
                if self.cwnd >= self.ssthresh:
                    self.state = "congestion_avoidance"
                    print(f"Time {current_time}: Transition to Congestion Avoidance")
            elif self.state == "congestion_avoidance":
                print(f"Time {current_time}: Congestion Avoidance - cwnd = {self.cwnd}")
                self.cwnd += max(1, (self.mss * self.mss) // self.cwnd)
            elif self.state == "fast_recovery":
                self.dup_acks += 1
                self.cwnd += self.mss
                print(f"Time {current_time}: Fast Recovery - cwnd = {self.cwnd}, dup_acks = {self.dup_acks}")
                if self.dup_acks >= 5:
                    self.recover_from_fast_recovery(current_time)
    
    def run_simulation(self):
        """Run the simulation."""
        for t in range(self.total_time):
            self.update_congestion_window(t)
    
    def plot_results(self, filename=None):
        """Plot simulation results."""
        plt.figure(figsize=(14, 10))
        
        plt.subplot(2, 1, 1)
        plt.plot(self.time_points, self.cwnd_history, label='cwnd', color='blue')
        plt.plot(self.time_points, self.ssthresh_history, label='ssthresh', color='red', linestyle='--')
        
        colors = {'slow_start': 'lightskyblue', 'congestion_avoidance': 'lightgreen', 'fast_recovery': 'lightsalmon'}
        for i in range(len(self.state_history) - 1):
            plt.axvspan(self.time_points[i], self.time_points[i+1], 
                        alpha=0.2, color=colors.get(self.state_history[i], 'white'))
        
        for time, event_type in self.events:
            if event_type == "Timeout":
                plt.axvline(x=time, color='orange', alpha=0.7)
                plt.text(time, max(self.cwnd_history) * 0.9, "TO", rotation=90)
            else:
                plt.axvline(x=time, color='green', alpha=0.7)
                plt.text(time, max(self.cwnd_history) * 0.9, "3DA", rotation=90)
        
        plt.xlabel('Time (RTTs)')
        plt.ylabel('Window Size (bytes)')
        plt.title('TCP Reno Congestion Window')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 1, 2)
        state_values = {'slow_start': 1, 'congestion_avoidance': 2, 'fast_recovery': 3}
        numeric_states = [state_values.get(state, 0) for state in self.state_history]
        plt.step(self.time_points, numeric_states, where='post')
        plt.yticks([1, 2, 3], ['Slow Start', 'Congestion Avoidance', 'Fast Recovery'])
        plt.xlabel('Time (RTTs)')
        plt.ylabel('TCP State')
        plt.title('TCP State Transitions')
        plt.grid(True)
        
        plt.tight_layout()
        if filename:
            plt.savefig(filename)
        plt.show()
    
    def print_statistics(self):
        """Print simulation stats."""
        print("\n=== Simulation Statistics ===")
        print(f"Total time: {self.total_time} RTTs")
        print(f"Final cwnd: {self.cwnd}")
        print(f"Packets sent: {self.packets_sent}")
        print(f"Packets lost: {self.packets_lost} ({self.packets_lost/self.packets_sent*100:.2f}%)")
        print(f"Timeouts: {self.timeouts}")
        print(f"Triple duplicate ACKs: {self.triple_dup_acks}")

def main():
    """Run the simulation with user inputs."""
    print("TCP Reno Simulation")
    
    while True:
        try:
            mss = int(input("Enter MSS (integer): "))
            break
        except ValueError:
            print("Please enter an integer.")
    
    while True:
        try:
            initial_ssthresh = int(input("Enter initial ssthresh (in MSS units, integer): "))
            break
        except ValueError:
            print("Please enter an integer.")
    
    while True:
        try:
            rtt = float(input("Enter RTT (float): "))
            break
        except ValueError:
            print("Please enter a float.")
    
    loss_type = input("Enter loss type ('interval' or 'probability'): ").strip().lower()
    while loss_type not in ['interval', 'probability']:
        print("Invalid. Enter 'interval' or 'probability'.")
        loss_type = input("Enter loss type ('interval' or 'probability'): ").strip().lower()
    
    if loss_type == 'interval':
        while True:
            try:
                loss_param = int(input("Enter loss interval (integer): "))
                break
            except ValueError:
                print("Please enter an integer.")
    else:
        while True:
            try:
                loss_param = float(input("Enter loss probability (0 to 1): "))
                if 0 <= loss_param <= 1:
                    break
                print("Must be between 0 and 1.")
            except ValueError:
                print("Please enter a float.")
    
    while True:
        try:
            total_time = int(input("Enter total time (in RTTs, integer): "))
            break
        except ValueError:
            print("Please enter an integer.")
    
    random_seed_input = input("Enter random seed (integer, or Enter for none): ").strip()
    random_seed = None
    if random_seed_input:
        while True:
            try:
                random_seed = int(random_seed_input)
                break
            except ValueError:
                print("Please enter an integer or press Enter.")
                random_seed_input = input("Enter random seed (integer, or Enter for none): ").strip()
                if not random_seed_input:
                    random_seed = None
                    break
    
    save_plot = input("Save plot? (yes/no): ").strip().lower()
    output_filename = None
    if save_plot == 'yes':
        output_filename = input("Enter filename for plot: ").strip()
    
    sim = TCPRenoSimulation(mss, initial_ssthresh, rtt, loss_type, loss_param, total_time, random_seed)
    sim.run_simulation()
    sim.plot_results(output_filename)
    sim.print_statistics()

if __name__ == "__main__":
    main()