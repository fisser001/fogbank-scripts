.. contents:: Table of Contents
  :depth: 2
=======================
Hadoop Multi-Node Setup
=======================
This section assumes that all nodes in the system have been configured using the `single node setup </docs/4_1_single_node_hadoop.rst>`_. 

Each node should be assigned unique hostnames. 

Assign a node a new hostname using: 

.. code:: bash

  sudo hostname slave1

And modify ``/etc/hostname`` to match this.

The IP address and the hostname of all the other nodes must be put into each node. For example, consider a 3 node cluster with one master and two slaves. The following must be put into each node’s ``/etc/hosts``:

.. code:: bash

  10.0.10.1    master
  10.0.10.2    slave1
  10.0.10.3    slave2

On the master, add its ssh key to the slaves:

.. code:: bash

  ssh-copy-id -i $HOME/.ssh/id_rsa.pub hduser@slave1

Then check you can ssh into the slaves without requiring a password:

.. code:: bash

  ssh slave1
Also check that the master can ssh into the master without a password:

.. code:: bash

  ssh master

Configuration files
-------------------
This section assumes that the configuration files have been modified as shown in the `single node setup </docs/4_1_single_node_hadoop.rst>`_. Ensure that the IP addresses have been changed to the master’s IP address instead of 127.0.0.1.

/usr/local/hadoop/etc/hadoop/slaves (on the master)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Add all the intended slaves in the ``/usr/local/hadoop/etc/hadoop/slaves`` file. For example:

.. code:: bash

  master
  slave1
  slave2

/usr/local/hadoop/etc/hadoop/hdfs-site.xml (all nodes)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Since there is more than one node, increase the replication factor. Ensure that the replication factor is not higher than the number of slaves/datanodes. 

.. code:: xml

  <property>
    <name>dfs.replication</name>
    <value>2</value>
   </property>

/usr/local/hadoop/etc/hadoop/mapred-site.xml (All nodes)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Run Mapreduce using all nodes and not just locally:

.. code:: xml

   <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
   </property>
   
Running Hadoop
---------------
Running Hadoop on a multi-node cluster is the same as the single node cluster, except commands are only run from the master. Refer to `Running Hadoop in a single node cluster </docs/4_1_single_node_hadoop.rst#running-hadoop>`_. Check everything is running using the ``jps`` command.

The master should be running: 

- Name Node
- Resource Manager
- Job History Server
- Data Node (if the master is configured to also be a slave)
- Node Manager (if the master is configured to also be a slave)

The slaves should be running:

- Data Node
- Node Manager

If something is not running, check the logs located at ``/usr/local/hadoop/logs`` or through the web app by visiting http://node-hostname:50075/logs. Replace node-hostname with the actual node’s hostname. Each node should have their own logs. 

You can also start each component individually using:

+--------------------+----------------------------------------------------------------------------------------+
| Component          | Command to start up                                                                    |
+====================+========================================================================================+
| Name Node          | ``hadoop-daemon.sh start namenode``                                                    |
+--------------------+----------------------------------------------------------------------------------------+
| Resource Manager   | ``yarn-daemon.sh start resourcemanager``                                               |
+--------------------+----------------------------------------------------------------------------------------+
| Job History Server | ``mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ start historyserver`` |
+--------------------+----------------------------------------------------------------------------------------+
| Data Node          | ``hadoop-daemon.sh start datanode``                                                    |
+--------------------+----------------------------------------------------------------------------------------+
| Node Manager       | ``yarn-daemon.sh start nodemanager``                                                   |
+--------------------+----------------------------------------------------------------------------------------+

======================
Hadoop Web interfaces 
======================
Hadoop provides Web interfaces for each component

+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Component           | URL                                                                                                                                           |
+=====================+===============================================================================================================================================+
| Name Node           | http://node-hostname:50070                                                                                                                    |
+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Secondary Name Node | http://node-hostname:50090                                                                                                                    |
+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Resource Manager    | http://node-hostname:8088 (default)                                                                                                           |
|                     |                                                                                                                                               |
|                     | http://node-hostname:8089 (if config has been changed as seen `here </docs/4_1_single_node_hadoop.rst#usrlocalhadoopetchadoopyarn-sitexml>`_) |
+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Job History Server  | http://node-hostname:19888                                                                                                                    |
+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Data Node           | http://node-hostname:50075                                                                                                                    |
+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Node Manager        | http://node-hostname:8042                                                                                                                     |
+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
===============
Troubleshooting
===============

- Time not synced between nodes
  
  Install NTP on the nodes so that the clocks are synced. http://knowm.org/how-to-synchronize-time-across-a-linux-cluster/ 

- The logs say something about running out of Java heap space
  
  Increase the ``mapreduce.map.java.opts`` or ``mapreduce.reduce.java`` in the  ``mapred-site.xml`` config file.  
