import matplotlib.pyplot as plt
import random
import math

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def simulate_tcp_tahoe(initial_ssthresh, p, num_rtts):
    cwnd = 1
    ssthresh = initial_ssthresh
    cwnd_list = []
    ssthresh_list = []
    loss_rtts = []
    loss_types = []
    in_recovery = False

    def is_power_of_2(n):
        return n != 0 and (n & (n - 1)) == 0

    for rtt in range(num_rtts):
        print(f"{GREEN}RTT {rtt}: cwnd = {cwnd}, ssthresh = {ssthresh}{RESET}")
        cwnd_list.append(cwnd)
        ssthresh_list.append(ssthresh)

        if cwnd >= ssthresh and not in_recovery:
            if random.random() < p:
                if random.random() < 0.5:
                    ssthresh = max(cwnd // 2, 2)
                    cwnd = 1  
                    loss_rtts.append(rtt)
                    loss_types.append(0)
                    in_recovery = True
                    print(f"{RED}Triple Duplicate ACK at RTT {rtt}: ssthresh set to {ssthresh}, cwnd set to {cwnd}{RESET}")
                else:
                    ssthresh = max(cwnd // 2, 2)
                    cwnd = 1
                    loss_rtts.append(rtt)
                    loss_types.append(1)
                    in_recovery = True
                    print(f"{RED}Timeout at RTT {rtt}: ssthresh set to {ssthresh}, cwnd set to {cwnd}{RESET}")
            else:
                cwnd += 1
                print(f"{BLUE}Congestion Avoidance: cwnd increased to {cwnd}{RESET}")
        else:
            if cwnd < ssthresh:
                next_cwnd = cwnd * 2
                if next_cwnd < ssthresh:
                    cwnd = next_cwnd
                    print(f"{YELLOW}Slow Start: cwnd doubled to {cwnd}{RESET}")
                else:
                    if not is_power_of_2(ssthresh):
                        largest_power = 1 << int(math.log2(ssthresh))
                        if cwnd == largest_power:
                            cwnd = ssthresh
                            print(f"{YELLOW}Slow Start: cwnd set to ssthresh = {cwnd} (transition to congestion avoidance){RESET}")
                        elif cwnd < largest_power:
                            cwnd = next_cwnd
                            print(f"{YELLOW}Slow Start: cwnd doubled to {cwnd}{RESET}")
                    else:
                        cwnd = next_cwnd
                        print(f"{YELLOW}Slow Start: cwnd doubled to {cwnd}{RESET}")
            else:
                cwnd += 1
                print(f"{BLUE}Congestion Avoidance (post-loss): cwnd increased to {cwnd}{RESET}")
                in_recovery = False

    plt.plot(range(num_rtts), cwnd_list, label='cwnd', color='green')
    plt.plot(range(num_rtts), ssthresh_list, label='ssthresh', linestyle='--', color='orange')
    triple_dup_rtts = [rtt for rtt, typ in zip(loss_rtts, loss_types) if typ == 0]
    triple_dup_cwnds = [cwnd_list[rtt] for rtt in triple_dup_rtts]
    timeout_rtts = [rtt for rtt, typ in zip(loss_rtts, loss_types) if typ == 1]
    timeout_cwnds = [cwnd_list[rtt] for rtt in timeout_rtts]
    if triple_dup_rtts:
        plt.scatter(triple_dup_rtts, triple_dup_cwnds, color='red', label='Triple Dup ACK')
    if timeout_rtts:
        plt.scatter(timeout_rtts, timeout_cwnds, color='blue', label='Timeout')
    plt.xlabel('RTT')
    plt.ylabel('Congestion Window (MSS)')
    plt.title('TCP Tahoe Congestion Control Simulation')  
    plt.grid(True)
    plt.show()

def main():
    print("Enter RTT (in seconds): ")
    rtt = float(input())
    print("Enter MSS size (in bytes): ")
    mss = int(input())
    print("Enter initial ssthresh (in MSS): ")
    initial_ssthresh = int(input())
    print("Enter probability of loss events per RTT during congestion avoidance (0 to 1): ")
    p = float(input())
    print("Enter number of RTTs to simulate: ")
    num_rtts = int(input())
    simulate_tcp_tahoe(initial_ssthresh, p, num_rtts)  

if __name__ == "__main__":
    main()