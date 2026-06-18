# main_output.py

# This dictionary mimics the exact raw text outputs your live collector 
# will fetch from a Cisco node when running the required show and ping commands.
output = {
    # 1. CPU Load
    "show processes cpu": """
CPU utilization for five seconds: 4%/0%; one minute: 7%; five minutes: 5%
PID Runtime(ms)     Invoked      uSecs   5Sec   1Min   5Min TTY Process
  1          0           4          0  0.00%  0.00%  0.00%   0 Chunk Manager    
  2         32         341         93  0.00%  0.01%  0.00%   0 Load Meter       
""",

    # 2. Interface Up/Down Status
    "show ip interface brief": """
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         192.168.10.1    YES NVRAM  up                    up      
GigabitEthernet0/1         10.1.1.1        YES NVRAM  up                    up      
GigabitEthernet0/2         10.2.2.1        YES NVRAM  administratively down down    
Loopback0                  1.1.1.1         YES NVRAM  up                    up      
""",

    # 3. OSPF Neighbor Count
    "show ip ospf neighbor": """
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/BDR        00:00:36    10.1.1.2        GigabitEthernet0/1
3.3.3.3           1   FULL/DROTHER    00:00:32    10.1.1.3        GigabitEthernet0/1
""",

    # 4. HSRP State
    "show standby brief": """
                     P indicates configured to preempt.
                     |
Interface   Grp  Pri P State    Active          Standby         Virtual IP
Gi0/1       10   100   Active   local           192.168.10.2    192.168.10.1
""",

    # 5. Route Table Size (Summary)
    "show ip route summary": """
IP routing table name is default (0x0)
Route Source    Networks    Subnets     Replicated  Memory (bytes)
connected       0           2           0           256
static          0           0           0           0
ospf 1          2           4           0           768
internal        2                                   2304
Total           4           6           0           3328
""",

    # 6. Ping RTT
    "ping 192.168.10.2": """
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.10.2, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/4/12 ms
"""
}
