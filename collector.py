# Importing necessary libraries 
import os
import re
import json 
from ntc_templates.parse import parse_output
from main_output import output
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv


# Load variables from the .env file
load_dotenv()

# Secure InfluxDB Configuration
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")


def parse_cpu(raw_text):
    # Looking for 5 seconds
    match = re.search(re.escape("five seconds:") + r"\s+(\d+)%", raw_text)
    return int(match.group(1)) if match else None

def parse_ping(raw_text):
    # Looking for ping statistics
    match = re.search(r"min/avg/max\s*=\s*\d+/(\d+)/\d+\s*ms", raw_text)
    return int(match.group(1)) if match else None

def process_and_store(device_name, raw_data):
    """Accepts raw text data block, parses all 6 required metrics, and writes to InfluxDB."""
    metrics = {}
    
    # 1. CPU Load
    cpu_text = raw_data.get("show processes cpu", "")
    metrics["cpu_utilization_pct"] = parse_cpu(cpu_text)
    
    # 2. Interface Status (Up Count)
    int_text = raw_data.get("show ip interface brief", "")
    try:
        parsed_ints = parse_output(platform="cisco_ios", command="show ip interface brief", data=int_text)
        metrics["interfaces_up_count"] = sum(1 for i in parsed_ints if i['status'] == 'up' and i['proto'] == 'up')
    except Exception:
        metrics["interfaces_up_count"] = None
    
    # 3. OSPF Neighbor Count
    ospf_text = raw_data.get("show ip ospf neighbor", "")
    try:
        parsed_ospf = parse_output(platform="cisco_ios", command="show ip ospf neighbor", data=ospf_text)
        metrics["ospf_neighbor_count"] = len(parsed_ospf)
    except Exception:
        metrics["ospf_neighbor_count"] = None
        
    # 4. HSRP State
    hsrp_text = raw_data.get("show standby brief", "")
    try:
        parsed_hsrp = parse_output(platform="cisco_ios", command="show standby brief", data=hsrp_text)
        metrics["hsrp_state"] = parsed_hsrp[0].get("state") if parsed_hsrp else "Unknown"
    except Exception:
        metrics["hsrp_state"] = "Error"
        
    # 5. Route Table Size (Total Networks)
    route_text = raw_data.get("show ip route summary", "")
    try:
        parsed_routes = parse_output(platform="cisco_ios", command="show ip route summary", data=route_text)
        metrics["route_table_size"] = int(parsed_routes[0].get("total_networks", 0)) if parsed_routes else 0
    except Exception:
        metrics["route_table_size"] = None
    
    # 6. Ping RTT
    ping_key = next((k for k in raw_data.keys() if k.startswith("ping")), None)
    if ping_key:
        metrics["ping_rtt_ms"] = parse_ping(raw_data[ping_key])
        
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Parsed All 6 Metrics for {device_name}: {json.dumps(metrics)}")

    # Write Complete Dataset to InfluxDB
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        point = Point("network_node_telemetry") \
            .tag("device", device_name) \
            .field("cpu_utilization", metrics.get("cpu_utilization_pct")) \
            .field("interfaces_up", metrics.get("interfaces_up_count")) \
            .field("ospf_neighbors", metrics.get("ospf_neighbor_count")) \
            .field("hsrp_state", metrics.get("hsrp_state")) \
            .field("route_table_size", metrics.get("route_table_size")) \
            .field("ping_rtt", metrics.get("ping_rtt_ms")) \
            .time(datetime.utcnow(), WritePrecision.NS)
        
        try:
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print(f" Successfully stored full 6-feature telemetry entry for {device_name}.")
        except Exception as e:
            print(f" Database Write Failed: {e}")

if __name__ == "__main__":
    print("--- Initiating Toy Data Test ---")
    # Pushing the mock data from main_output.py ( For Testing purposes only)
    process_and_store("R1-Core", output)











































# def process_telemetry(raw_data):
     
#     telemetry_profile = {
#     "timestamp": datetime.now(timezone.utc).isoformat(),
#     "metrics": {}
#     }

#     # 1. CPU Load
#     cpu_text = raw_data.get("show processes cpu", "")
#     telemetry_profile["metrics"]["cpu_utilization_pct"] = parse_cpu(cpu_text)
    
#     # 2. Parse Interfaces 
#     int_text = raw_data.get("show ip interface brief", "")
#     parsed_ints = parse_output(platform="cisco_ios", command="show ip interface brief", data=int_text)
#     # Count how many interfaces are fully operational (status 'up' and protocol 'up')
#     up_interfaces = sum(1 for i in parsed_ints if i['status'] == 'up' and i['proto'] == 'up')
#     telemetry_profile["metrics"]["interfaces_up_count"] = up_interfaces
    
#     # 3. Parse OSPF Neighbors (Using ntc-templates TextFSM parsing)
#     ospf_text = raw_data.get("show ip ospf neighbor", "")
#     parsed_ospf = parse_output(platform="cisco_ios", command="show ip ospf neighbor", data=ospf_text)
#     telemetry_profile["metrics"]["ospf_neighbor_count"] = len(parsed_ospf)
    
#     # 4. Parse HSRP State ( This is Redundant )
#     hsrp_text = raw_data.get("show standby brief", "")
#     parsed_hsrp = parse_output(platform="cisco_ios", command="show standby brief", data=hsrp_text)
#     # Extract the state of the first configured group (Active / Standby)
#     telemetry_profile["metrics"]["hsrp_state"] = parsed_hsrp[0].get("state") if parsed_hsrp else "Unknown"
    
#     # 5. Parse Routing Table Size ( This is redundant )
#     route_text = raw_data.get("show ip route summary", "")
#     parsed_routes = parse_output(platform="cisco_ios", command="show ip route summary", data=route_text)
#     # Extract total networks from the summary block
#     total_routes = int(parsed_routes[0].get("total_networks", 0)) if parsed_routes else 0
#     telemetry_profile["metrics"]["route_table_size"] = total_routes
    
#     # 6. Parse Ping RTT
#     ping_key = next((k for k in raw_data.keys() if k.startswith("ping")), None)
#     if ping_key:
#         telemetry_profile["metrics"]["ping_rtt_ms"] = parse_ping(raw_data[ping_key])
        
#     return telemetry_profile

# if __name__ == "__main__":

#     print("--- Processing Mock Telemetry Stream ---")
#     structured_json = process_telemetry(output)
    
#     # Printing to stdout just in case 
#     print(json.dumps(structured_json, indent=4))
    