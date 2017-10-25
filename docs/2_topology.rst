==========
Topology
==========
The current topology is illustrated in the diagram below. The switch is an OpenFlow enabled AT-x510 switch from Allied Telesis. 10 blade servers are connected to the switch and acts as the cluster. These servers boot from an image obtained through the PXE (Preboot eXecution Environment) server on the control PC. The control PC has two connections to the switch. One is to link the PXE server to the blade servers, and the other is to act as the controller. The control PC is also connected to the Internet through Wi-Fi.

.. image:: /docs/images/topology.png
