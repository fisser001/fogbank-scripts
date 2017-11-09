===============
Fogbank Scripts
===============
This repository contains scripts used for a computational cluster running `Hadoop <http://hadoop.apache.org/>`_. Learn how to use these scripts in `docs/script_usage.rst </docs/script_usage.rst>`_

The overall goal is to collect statistics while the Hadoop cluster executes tasks. These statistics should be about the network and each node's utilisation. This will then be used to infer information about how the tasks affect the nodes. 

There are three components to help achieve this goal. These are:

1. Providing connectivity (and monitoring capabilities) between nodes 
2. Creating a custom image that can be loaded onto each node 
3. Automated collection of statistics when a task is run

1. Connectivity and monitoring
------------------------------
The nodes are connected by a SDN (Software Defined Networking) switch. The software for controlling the switch behaviour (the controller) is on the master node/control PC. Through an SDN protocol (OpenFlow), the switch monitors the network traffic and relays the information back to the controller. 

A more detailed explanation can be found in `docs/1_concept_explanation.rst </docs/1_concept_explanation.rst>`_. Installation instructions can be found in `docs/1_installation.rst </docs/1_installation.rst>`_.  

2. Custom image for nodes
-------------------------
To provide an easily scalable cluster, a custom image is created for slave nodes. The image runs Xubuntu and comes with Hadoop installed. A node is then able to boot the image from the PXE (Preboot eXecution Environment) server on the master node/control PC. The topology of the setup is described in `docs/2_topology.rst </docs/2_topology.rst>`_.

Create image and PXE server
***************************
Instructions for creating a custom image and setting up the PXE server can be seen in `docs/3_pxe_boot.rst </docs/3_pxe_boot.rst>`_. 

Install Hadoop
**************
Install Hadoop on the image (and on the master node) using the instructions from `docs/4_1_single_node_hadoop.rst </docs/4_1_single_node_hadoop.rst>`_. 

Running Hadoop on the cluster
-----------------------------
Run Hadoop on the cluster by following  `docs/4_2_multi_node_hadoop.rst </docs/4_2_multi_node_hadoop.rst>`_. Start the cluster up with instructions from `docs/5_node_setup.rst </docs/5_node_setup.rst>`_

Install Hive and Tez on master node
***********************************
Hive provides a way to manage databases on Hadoop. Tez processes data for Hive. Install them both on the master node by following `docs/4_3_hive_tez.rst </docs/4_3_hive_tez.rst>`_

3. Automated statistics collection
-----------------------------------
The automated collection of statistics during a task is done through the `run_multiple_queries.py <run_multiple_queries.py>`_ script. It runs a Hive query multiple times, and generates graphs from the statistics collected during the query. 

More details can be found in `docs/6_automated_queries.rst </docs/6_automated_queries.rst>`_.
