# ssh_polling.py
import time
from datetime import datetime
from netmiko import ConnectHandler

# Import our updated 6-feature collector engine
import collector

# Active inventory list for the CML nodes
DEVICES = {
    "R1-Core": {
        "device_type": "cisco_ios",
        "host": "10.0.0.1", 
        "username": "admin",
        "password": "",
        "secret": "",
    },
    # Add the nodes
}

COMMANDS = [
    "show processes cpu",
    "show ip interface brief",
    "show ip ospf neighbor",
    "show standby brief",
    "show ip route summary",
    "ping 192.168.10.2"
]

def poll_network():
    """Loops through devices, harvests all 6 raw text blocks, and sends them to the collector."""
    for device_name, device_config in DEVICES.items():
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Polling {device_name} via SSH...")
        raw_responses = {}
        
        try:
            with ConnectHandler(**device_config) as net_connect:
                net_connect.enable()
                for cmd in COMMANDS:
                    raw_responses[cmd] = net_connect.send_command(cmd)
            
            # Handoff full dictionary to collector.py
            collector.process_and_store(device_name, raw_responses)
            
        except Exception as e:
            print(f" Network Connection Error for {device_name}: {e}")

if __name__ == "__main__":
    print("Starting Comprehensive SSH Polling Loop (30s intervals). Press Ctrl+C to stop.")
    
    while True:
        start_time = time.time()
        
        poll_network()
        
        # Execution time is subtracted from 30 and then system again ssh's to collect the data
        execution_time = time.time() - start_time 
        sleep_duration = max(0.1, 30.0 - execution_time)
        
        time.sleep(sleep_duration)