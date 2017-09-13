# Fogbank Scripts
This repository contains scripts used with an 11 node cluster running Hadoop, Hive, and Tez.

The nodes are connected to an OpenFlow enabled switch. 
The controllers used are [FAUCET and Gauge](https://github.com/REANNZ/faucet).
Gauge obtains network data through OpenFlow messages. 

Additional monitoring of each nodes' usage of RAM, disk, and CPU is done through HTTP Servers found [here](https://github.com/libunamari/fogbank-scripts/blob/master/cpu_ram_monitor.py) and [here](https://github.com/libunamari/fogbank-scripts/blob/master/cpu_ram_monitor_main.py).
