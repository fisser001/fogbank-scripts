==========
Topology
==========
The current topology is illustrated in the diagram below. The switch is an OpenFlow enabled AT-x510 switch from Allied Telesis. 10 blade servers are connected to the switch and acts as the cluster. These servers boot from an image obtained through the PXE (Preboot eXecution Environment) server on the control PC. The control PC has two connections to the switch. One is to link the PXE server to the blade servers, and the other is to act as the controller. The control PC is also connected to the Internet through Wi-Fi.

=========================
Application Architecture
=========================

The structure of the applications running on the control PC is detailed below. Both Faucet and Gauge are both OpenFlow controllers. However, Gauge must be operated with Faucet, since it monitors Faucet controlled switches. Gauge only collects statistics, whereas Faucet defines the switch behaviour through OpenFlow messages. 

Because of this, Faucet and Gauge collects different information from the switch. Faucet processes asynchronous messages from the switch, which includes packet ins, flow removal, and error messages. The switch sends the controller these types of messages on its own, without a request from the controller. This information, as well as others (number of yaml reload requests, BGP neighbours etc) is monitored for Prometheus. On the other hand, Gauge has to continuously request for port and flow statistics. 

Gauge stores the statistics in InfluxDB, regular text files, or Prometheus. Both InfluxDB and text files are able to store port status, port stats, and flow stats. At the moment, Gauge is only able to give Prometheus port stats. 

Both Gauge and Faucet can use Prometheus. Faucet has a HTTP server running on port 9302, and Gauge has one running on 9303. Prometheus pulls information off both servers to collect the statistics.

To display the data, Grafana obtains it from both Prometheus and InfluxDB.
