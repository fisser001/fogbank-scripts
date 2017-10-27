Adding a new Hadoop data node
==============================

To add a new data node to an already running Hadoop cluster, first set up the new data node. This can be done by following the steps detailed in `/docs/5_node_setup.rst </docs/5_node_setup.rst>`_. Skip starting up the components for the master node if it is already running.

1. Update the slaves configuration on the master to include the new datanode's hostname:

.. code:: bash
  
  vim /usr/local/hadoop/etc/hadoop/slaves

2. In the new data node, execute the following commands:

.. code:: bash
  
  hadoop-daemon.sh start datanode
  yarn-daemon.sh start nodemanager

3. On the master, check http://master_hostname:50070/dfshealth.html#tab-datanode to see if the data node has been added. 

It may be necessary to rebalance the data held in HDFS, so run the command:

.. code:: bash
  
  hdfs balancer

Decommissioning (removing) a data node
=======================================
This section provides details on how to safely remove a data node without losing data. 

**Note**: the number of live data nodes must not fall below the replication factor. Otherwise, the replication factor can no longer be met and the HDFS blocks would be under replicated.

1. Check if you have an exclude file in the Hadoop config folder on the master. If yes, skip to step 6. Otherwise go to step 2.

2. Stop the Hadoop cluster

.. code:: bash
  
  ./kill_dfs.sh

3. Create an exclude file

.. code:: bash
  
  touch /usr/local/hadoop/etc/hadoop/exclude

4. Add the following config to ``/usr/local/hadoop/etc/hadoop/hdfs-site.xml``

.. code:: xml
  
    <property>
      <name>dfs.hosts.exclude</name>
      <value>/usr/local/hadoop/etc/hadoop/exclude</value>
      <final>true</final>
    </property>
  
5. Start the Hadoop cluster

.. code:: bash
  
  ./run_dfs.py

6. Add the data node host name in the exclude file, and execute the following command:

.. code:: bash
  
  hdfs dfsadmin -refreshNodes

7. Check http://master_hostname:50070/dfshealth.html#tab-datanode to see when the data node has been decommissioned. This may take some time since the data contained within the node must be written somewhere else.  

8. Remove the data node from the slaves config file (``/usr/local/hadoop/etc/hadoop/slaves``)
