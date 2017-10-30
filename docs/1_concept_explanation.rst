=================================
Software Defined Networking (SDN)
=================================
Traditional networking devices are largely proprietary, and as a result there is a dependence on the vendor. The software on the device is unmodifiable, so implementing new features is only possible if done by the vendor. The main problem is that the control and data plane are tightly coupled together. The control plane is responsible for deciding where the traffic needs to go in the network. Then the data plane is responsible for sending out and forwarding the traffic based on the control plane logic. 

The concept of SDN is based around the physical separation of the control and data plane. The network devices simply become switches which forward traffic without partaking in the decision. This removes the dependence on the vendors. The control plane is moved to a central "controller" that the SDN switches connect to. Each device no longer has its own control plane, which means the controller has a global view of the network. As a result, the controller is able to react to events happening in the network. This could be beneficial for detecting congested links and diverting the traffic to an alternate path.

Further reading: `Software-Defined Networking: A Comprehensive Survey <https://doi.org/10.1109/JPROC.2014.2371999>`_, `The Road to SDN <https://doi.org/10.1145/2559899.2560327>`_

=========
OpenFlow
=========
OpenFlow is a protocol which realises SDN. It provides a way for the controller to communicate with the switches. The controller installs flow rules to a switch’s flow table to forward traffic. Each flow entry in the table consists of three main aspects: the match, instructions, and counters. The match specifies which packets this flow will apply to. Examples of possible matches include: the switch port the packet came in on, the source IP address, or if it is a UDP packet. The instructions specify what will be done to the packet. It could be dropped, output through a switch port, modified with a VLAN tag, or be sent to another table. The counters are the statistics of the flow. This includes the number of packets matched to the entry, and the number of bytes.

The switch pipeline is the flow tables a packet can traverse through. The pipeline may only move forward (i.e. a packet can go from table 1 to table 4, but it cannot go from table 3 to table 2). The purpose of multiple flow tables is to simplify the flow entries and allow them to be more modular. For example, each table could focus on a different aspect of the packet. Table 1 may focus on the layer 2 aspects: checking the MAC address, VLAN tags etc. Then table 2 may focus on layer 3: checking on the IP address and so forth.

Further reading: `OpenFlow 1.3 specification <https://www.opennetworking.org/images/stories/downloads/sdn-resources/onf-specifications/openflow/openflow-spec-v1.3.0.pdf>`_

=================
Faucet and Gauge 
=================
`Faucet <https://github.com/faucetsdn/faucet>`_ is a OpenFlow controller, which is based on `Ryu <http://osrg.github.io/ryu/>`_ and `Valve <https://github.com/wandsdn/valve>`_ (both are also OpenFlow controllers). It allows for easy configuration of the network using yaml files. Faucet provides the forwarding logic for the switches. To collect statistics about the network, Gauge is used alongside Faucet. Gauge is also an OpenFlow controller.

Gauge collects three types of statistics: port_status, port_stats, and flow_stats. Port status indicates a change of a switch port. The new status of a port can either be added, deleted, or modified. 
Another statistic that can be collected is the port stat. This contains information about port counters: the rx_bytes, tx_bytes, dropped rx_packets, dropped tx_packets, errors, rx_packets, and tx_packets. 

The statistics can be stored in three ways: using `InfluxDB <https://docs.influxdata.com/influxdb/>`_, `Prometheus <https://prometheus.io/docs/introduction/overview/>`_, or a regular text file. InfluxDB is a time series database which stores all three types of statistics. Prometheus is a monitoring and alerting tool to obtain real time data about the system. It can be used to display port stats data from Gauge. It is also used by Faucet to display data collected from the controller and the switch. 

The statistics obtained from both Faucet and Gauge can be displayed in `Grafana <http://docs.grafana.org/>`_. This displays time series data in graphs which can be compiled into dashboards. The data sources in this case are Prometheus and InfluxDB.

Application Architecture
-------------------------
An explanation on how all of these concepts come together is detailed in this section. Both Faucet and Gauge are both OpenFlow controllers. However Gauge must be operated with Faucet, since it can only monitor Faucet controlled switches. Gauge only collects statistics, whereas Faucet defines the switch behaviour through OpenFlow messages. 

Because of this, Faucet and Gauge collects different information from the switch. Faucet processes asynchronous messages from the switch, which includes packet ins, flow removal, and error messages. The switch sends the controller these types of messages on its own, without a request from the controller. This information, as well as others (number of yaml reload requests, BGP neighbours etc) is monitored for Prometheus. On the other hand, Gauge has to continuously request for port and flow statistics.

Both Gauge and Faucet can use Prometheus. Faucet has a HTTP server running on port 9302, and Gauge has one running on 9303. Prometheus pulls information off both servers to collect the statistics.

To display the data, Grafana obtains it from both Prometheus and InfluxDB.

.. image:: /docs/images/application_desc.png
  :align: center

==================
Table of TCP Ports
==================
+----------------------------+----------+
| Application                | TCP Port |
+============================+==========+
| OpenFlow controller        | 6653     |
+----------------------------+----------+
| Faucet                     | 6653     |
+----------------------------+----------+
| Gauge                      | 6654     |
+----------------------------+----------+
| InfluxDB (HTTP API)        | 8086     |
+----------------------------+----------+
| InfluxDB (RPC service)     | 8088     |
+----------------------------+----------+
| Prometheus client (Faucet) | 9302     |
+----------------------------+----------+
| Prometheus client (Gauge)  | 9303     |
+----------------------------+----------+
| Grafana                    | 3000     |
+----------------------------+----------+

Note that the official IANA assigned port for OpenFlow is 6653 but 6633 was used before this was obtained.
