#Copyright (c) 2024  Cenk Sasmaztin <cenk@oxoonetworkscom>
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#1. Redistributions of source code must retain the above copyright
#notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright
#notice, this list of conditions and the following disclaimer in the
#documentation and/or other materials provided with the distribution.

#THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#SUCH DAMAGE.


VLAN-Based Loop and Root Bridge Change Detection Tool

This project contains a Python application that monitors Layer 2 (L2) packets via a SPAN port to detect VLAN-based loops and root bridge MAC address changes. The code automatically detects the active network interface and performs monitoring through this interface, making it easier for users to start monitoring by simply connecting the monitoring device to the network and running the code.

1. Requirements

Software Requirements
Python 3.x: Python 3.x is required to run this project.
Scapy: A Python packet analysis library. To install:
pip install scapy
psutil: Used to detect network interfaces automatically. To install:
pip install psutil
Hardware Requirements
Due to the high traffic flow, it is recommended that the device running this tool meets the following specifications:

High-Performance CPU: A multi-core processor (Intel i5 or better) is recommended for rapid packet processing.
Adequate Memory (RAM): At least 8GB of RAM is suggested due to the large number of packets in a substantial network.
High Bandwidth NIC: To handle traffic from many VLANs in trunk mode, a network interface card (NIC) with at least 1 Gbps speed is required.
2. Switch Configuration

To use this tool, you must configure a SPAN port on the switch. A SPAN port mirrors traffic from designated source ports to a monitoring device. When configured in trunk mode, traffic from all VLANs will be sent over this port. Below are Cisco switch commands for SPAN port configuration.

SPAN Port Configuration
Define SPAN Source Ports: Select the traffic source ports to be monitored. For example, if you want to monitor traffic from interface Fa0/1 and Fa0/2:
monitor session 1 source interface Fa0/1 - 2
Set SPAN Destination Port (Trunk Mode): Specify the port connected to the monitoring device as the destination port. In this example, we use interface Fa0/3 as the monitoring port:
monitor session 1 destination interface Fa0/3
Transmit All VLANs in Trunk Mode:
interface Fa0/3
switchport mode trunk
switchport trunk allowed vlan all
Important Notes
If you want to monitor traffic only from specific VLANs, you can restrict the VLANs using the switchport trunk allowed vlan command. For example:
switchport trunk allowed vlan 10,20
It is important to monitor performance under high traffic conditions. To prevent excessive packet loss in your monitoring system, consider limiting traffic mirrored to the SPAN port.
3. Python Code and Functions

The functionality of the Python code in this project is explained below.

Functions
get_active_interface()

This function automatically detects the active network interface (with link status UP) in the system. It checks the link status and MAC addresses of the interfaces using the psutil library and returns the first suitable interface.

detect_vlan_loop_and_root_bridge(packet)

This function analyzes each packet from the SPAN port, detecting both VLAN-based loops and root bridge changes.

Loop Detection:
Repeated packets with the same MAC address within the same VLAN over short intervals are detected as potential loops. If detected, a warning message appears in the terminal.
The TIME_THRESHOLD value (default 1 second) specifies the minimum time difference between monitored packets for loop detection.
Root Bridge Detection:
If a Spanning Tree Protocol (STP) frame is detected, it checks the root bridge MAC address for each VLAN.
When a root bridge address is observed for the first time, it is saved. If a root bridge address change is detected for the same VLAN, a message indicating the change is printed to the terminal.
Example Terminal Output
When the code is running, if a loop or root bridge change is detected, messages similar to the following will appear in the terminal:

Loop detected! MAC Address: 00:1A:2B:3C:4D:5E, VLAN: 10, Interval: 0.80 seconds
Root Bridge MAC changed for VLAN 20: 00:1A:2B:3C:4D:5E -> 00:5E:4D:3C:2B:1A
4. Running Instructions

Set up your Python environment and install the necessary libraries:
pip install scapy psutil
Run the Python script:
python detect_vlan_loop.py
The code will automatically detect the active network interface and start monitoring packets on that interface. While running, the tool will display detected loops or root bridge changes in the terminal.

Error Handling
If no active network interface is found, the following message will appear in the terminal:

No active network interface found. Please connect to the network and try again.
This guide will help you set up and use the tool to detect VLAN-based loops and root bridge changes. If you have any questions regarding the code or configuration, please feel free to ask for assistance.




