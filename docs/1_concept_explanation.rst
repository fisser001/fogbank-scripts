=================================
Software Defined Networking (SDN)
=================================
Traditional networking devices are largely proprietary, and as a result there is a dependence on the vendor. The software on the device is unmodifiable, so implementing new features is only possible if done by the vendor. The main problem is that the control and data plane are tightly coupled together. The control plane is responsible for deciding where the traffic needs to go in the network. Then the data plane is responsible for sending out and forwarding the traffic based on the control plane logic. 

The concept of SDN is based around the physical separation of the control and data plane. The network devices simply become switches which forward traffic without partaking in the decision. This removes the dependence on the vendors. The control plane is moved to a central “controller” that the SDN switches connect to. Each device no longer has its own control plane, which means the controller has a global view of the network. As a result, the controller is able to react to events happening in the network. This could be beneficial for detecting congested links and diverting the traffic to an alternate path.

Further reading: `Software-Defined Networking: A Comprehensive Survey <https://doi.org/10.1109/JPROC.2014.2371999>`_, `The Road to SDN <https://doi.org/10.1145/2559899.2560327>`_

=========
OpenFlow
=========
OpenFlow is a protocol which realises SDN. It provides a way for the controller to communicate with the switches. The controller installs flow rules to a switch’s flow table to forward traffic. Each flow entry in the table consists of three main aspects: the match, instructions, and counters. The match specifies which packets this flow will apply to. Examples of possible matches include: the switch port the packet came in on, the source IP address, or if it is a UDP packet. The instructions specify what will be done to the packet. It could be dropped, output through a switch port, modified with a VLAN tag, or be sent to another table. The counters are the statistics of the flow. This includes the number of packets matched to the entry, and the number of bytes.

The switch pipeline is the flow tables a packet can traverse through. The pipeline may only move forward (i.e. a packet can go from table 1 to table 4, but it cannot go from table 3 to table 2). The purpose of multiple flow tables is to simplify the flow entries and allow them to be more modular. For example, each table could focus on a different aspect of the packet. Table 1 may focus on the layer 2 aspects: checking the MAC address, VLAN tags etc. Then table 2 may focus on layer 3: checking on the IP address and so forth.

Further reading: `OpenFlow 1.3 specification <https://www.opennetworking.org/images/stories/downloads/sdn-resources/onf-specifications/openflow/openflow-spec-v1.3.0.pdf>`_

