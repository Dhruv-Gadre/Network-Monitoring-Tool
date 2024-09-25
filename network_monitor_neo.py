import psutil
import speedtest
import time
import csv
import os
import socket
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess

def get_network_usage():
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    return bytes_sent, bytes_recv

# Function to test network speed using Speedtest library
def test_network_speed():
    print("Testing network speed")
    try:
        st = speedtest.Speedtest()
        st.get_best_server()  
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        return download_speed, upload_speed
    except speedtest.ConfigRetrievalError as e:
        print(f"Error retrieving Speedtest config: {e}. Retrying in 10 seconds...")
        time.sleep(10)
        return test_network_speed()

def alert_high_usage(download_speed, upload_speed, threshold=100):
    if download_speed > threshold or upload_speed > threshold:
        print(f"Alert! High network usage detected. Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps")

# Function to log  the network data in a csv file
def log_network_data(file_path='network_log.csv', interval=20):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Bytes Sent", "Bytes Received", "Download Speed (Mbps)", "Upload Speed (Mbps)"])

        while True:
            bytes_sent, bytes_recv = get_network_usage()
            download_speed, upload_speed = test_network_speed()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            writer.writerow([timestamp, bytes_sent, bytes_recv, f"{download_speed:.2f}", f"{upload_speed:.2f}"])
            print(f"Logged data at {timestamp}")
            alert_high_usage(download_speed, upload_speed)
            time.sleep(interval)

# Function to get network interfaces and IP addresses (IPv4/IPv6)
def get_network_interfaces():
    addrs = psutil.net_if_addrs()
    interfaces = psutil.net_if_stats()
    for interface, addr_list in addrs.items():
        print(f"Interface: {interface}")
        for addr in addr_list:
            ip_version = "IPv4" if addr.family == socket.AF_INET else "IPv6" if addr.family == socket.AF_INET6 else "Other"
            print(f"  IP Address: {addr.address}, Type: {ip_version}")
        if interface in interfaces:
            print(f"  Status: {'Up' if interfaces[interface].isup else 'Down'}, Speed: {interfaces[interface].speed} Mbps")


# Ping test function to check network latency
def ping_test(host="8.8.8.8"): #google 
    print(f"Pinging {host}...")

    # Cross-platform ping command
    param = '-n' if os.name == 'nt' else '-c'  
    command = ['ping', param, '1', host]

    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if output.returncode == 0:
            print(f"Ping to {host} successful\n{output.stdout}")
        else:
            print(f"Ping to {host} failed\n{output.stderr}")
    except Exception as e:
        print(f"Error executing ping: {e}")


# Real-time Bandwidth Usage Graph using matplotlib
def real_time_bandwidth(interval=1, duration=60):
    plt.ion()  # Interactive mode on
    fig, ax = plt.subplots()
    x_data, y_data = [], []
    start_time = time.time()

    while time.time() - start_time < duration:
        bytes_sent, bytes_recv = get_network_usage()
        bandwidth_usage = (bytes_sent + bytes_recv) / 1_000_000  # Convert to MB

        # Update graph data
        x_data.append(time.time() - start_time)
        y_data.append(bandwidth_usage)

        ax.clear()
        ax.plot(x_data, y_data, label="Bandwidth Usage (MB)", color="blue")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Usage (MB)")
        ax.legend()

        plt.draw()
        plt.pause(interval)
    
    plt.ioff()  # Turn interactive mode off
    plt.show()

# Function to ask the user if they want to continue
def continue_prompt():
    while True:
        choice = input("Do you want to continue? (yes/no): ").strip().lower()
        if choice == 'yes':
            return True
        elif choice == 'no':
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

# Main function for user interaction
def main():
    while True:
        print("\nNetwork Monitoring Tool")
        print("1. View Current Network Usage")
        print("2. Test Network Speed")
        print("3. Start Logging")
        print("4. View Network Interfaces and IP Addresses")
        print("5. Run Ping Test")
        print("6. Real-time Bandwidth Usage Graph")

        choice = input("Enter your choice: ")

        if choice == '1':
            bytes_sent, bytes_recv = get_network_usage()
            print(f"Bytes Sent: {bytes_sent}")
            print(f"Bytes Received: {bytes_recv}")

        elif choice == '2':
            download_speed, upload_speed = test_network_speed()
            print(f"Download Speed: {download_speed:.2f} Mbps")
            print(f"Upload Speed: {upload_speed:.2f} Mbps")

        elif choice == '3':
            log_network_data()

        elif choice == '4':
            get_network_interfaces()

        elif choice == '5':
            host = input("Enter the host IP or domain (default: 8.8.8.8): ")
            if not host:
                host = "8.8.8.8"
            ping_test(host)

        elif choice == '6':
            duration = int(input("Enter the duration of real-time monitoring in seconds (default: 60): ") or 60)
            real_time_bandwidth(duration=duration)

        else:
            print("Invalid choice")

        # Ask user if they want to continue
        if not continue_prompt():
            print("Exiting the program.")
            break

    # Pause before exiting
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
