==================
Overview of Hadoop
==================
Hadoop allows for distributed file storage and computation. Hadoop Distributed File System (HDFS) provides the storage, the computation is done through MapReduce tasks, and the resource management and allocations are handled by Yet Another Resource Negotiator (YARN). 

HDFS
-----
HDFS uses two components: a Name Node and Data Nodes. The Name Node stores metadata about the file system such as file IDs, and transaction IDs. The Data Node stores the actual file contents. This means that HDFS employs a master/slave architecture. The master runs the Name Node and optionally a Data Node, while the slaves run Data Nodes.

YARN
-----
Similarly, YARN also uses two components: a Resource Manager and Node Manager. The Resource Manager handles resources at a global level (i.e. all nodes in the cluster) while a Node Manager only handles its own node’s resources. 

Read more `here <https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/YARN.html>`_.

=========================
Hadoop Single Node Setup
=========================

Install Java
-------------
Hadoop is written in Java, so it needs to be installed. 

.. code:: bash

  sudo apt-get update
  sudo apt-get install default-jdk

Check this was successful by checking the current java version:

.. code:: bash

  java -version

Add a new user 
--------------
To keep components separate, a new user dedicated to using Hadoop is created. This step can be skipped but it seems that most tutorials online use a separate Hadoop user. 

Create a hadoop group: 

.. code:: bash

  sudo addgroup hadoop

Then create the user:

.. code:: bash

  sudo adduser --ingroup hadoop hduser

Give the new user sudo rights:

.. code:: bash

  sudo adduser hduser sudo

Switch to the new user:

.. code:: bash

  su hduser

Configure SSH
------------------
The master node in the Hadoop cluster requires being able to SSH into the slave nodes. Install using: 

.. code:: bash

  sudo apt-get install ssh

Check that it installed properly using: 

.. code:: bash

  which ssh
  which sshd

The two commands should output something like ``/usr/bin/ssh`` and ``/usr/bin/sshd``

Create SSH keys:

.. code:: bash

  ssh-keygen -t rsa -P ""

Add key to authorised list

.. code:: bash

  cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys

Check that it’s working:

.. code:: bash

  ssh localhost

The ``ssh`` command above should not have prompted for a password. Otherwise, check that the user owns the ``.ssh/authorized_keys`` file.

Install & Configure Hadoop
---------------------------
Download Hadoop binary tarball from here: http://hadoop.apache.org/releases.html 

Unzip using: 

.. code:: bash

  tar xvzf hadoop*.tar.gz

Move the hadoop directory to ``/usr/local`` (change ``hadoop-2.8.0`` to the version being installed): 

.. code:: bash

  sudo mv hadoop-2.8.0/ /usr/local/hadoop
  sudo chown -R hduser:hadoop /usr/local/hadoop

To configure Hadoop, the following files need to be modified:

- ~/.bashrc
- /usr/local/hadoop/etc/hadoop/hadoop-env.sh
- /usr/local/hadoop/etc/hadoop/core-site.xml
- /usr/local/hadoop/etc/hadoop/mapred-site.xml
- /usr/local/hadoop/etc/hadoop/hdfs-site.xml
- /usr/local/hadoop/etc/hadoop/yarn-site.xml

~/.bashrc
^^^^^^^^^
Modify ~/.bashrc to include: 

.. code:: bash

  #hadoop environment variables
  export HADOOP_HOME=/usr/local/hadoop
  export HADOOP_MAPRED_HOME=$HADOOP_HOME
  export HADOOP_COMMON_HOME=$HADOOP_HOME
  export HADOOP_HDFS_HOME=$HADOOP_HOME
  export YARN_HOME=$HADOOP_HOME
  export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
  export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
  export HADOOP_INSTALL=$HADOOP_HOME
  export HADOOP_OPTS="-Djava.library.path=$HADOOP_INSTALL/lib/native"
  export CLASSPATH=$CLASSPATH:/usr/local/hadoop/lib/*:.

Apply changes: source ~/.bashrc

/usr/local/hadoop/etc/hadoop/hadoop-env.sh
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configure which Java implementation to use:

Comment out: 

.. code:: bash

  #export JAVA_HOME=${JAVA_HOME}

Add in:

.. code:: bash

  export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")

/usr/local/hadoop/etc/hadoop/core-site.xml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the configuration below to configure the default file system. Change the IP address used in value to match the master node’s IP address.

.. code:: xml

   <property>
    <name>fs.defaultFS</name>
    <value>hdfs://127.0.0.1:54310</value>
   </property>

To store files outside of the default /tmp directory, add this property (change the value to match the desired location): 

.. code:: xml

   <property>
    <name>hadoop.tmp.dir</name>
    <value>/home/hduser/Documents/hadoop-${user.name}</value>
   </property>

/usr/local/hadoop/etc/hadoop/mapred-site.xml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file has to be created using mapred-site.xml.template:

.. code:: bash

  cp /usr/local/hadoop/etc/hadoop/mapred-site.xml.template /usr/local/hadoop/etc/hadoop/mapred-site.xml

Specify where the job tracker is (usually the master):

.. code:: xml

   <property>
    <name>mapreduce.jobhistory.address</name>
    <value>127.0.0.1:10020</value>
   </property>
   <property>
    <name>mapreduce.jobhistory.webapp.address</name>
    <value>127.0.0.1:19888</value>
   </property>

Increase memory allocations. The memory.mb properties are the overall memory assigned to map or reduce and the java.opts are the Java heap space. 

.. code:: xml

   <property>
    <name>mapreduce.map.memory.mb</name>
    <value>3072</value>
   </property>
   <property>
    <name>mapreduce.map.java.opts</name>
    <value>-Xmx2560M</value>
   </property>
   <property>
    <name>mapreduce.reduce.memory.mb</name>
    <value>3072</value>
   </property>
   <property>
    <name>mapreduce.reduce.java.opts</name>
    <value>-Xmx2560M</value>
   </property>

/usr/local/hadoop/etc/hadoop/hdfs-site.xml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change the replication of each block to only be one since there is only one node:

.. code:: xml

   <property>
    <name>dfs.replication</name>
    <value>1</value>
   </property>

To modify where files are saved on the namenode, add this property (multiple locations can be specified as long as they are comma separated):

.. code:: xml

   <property>
    <name>dfs.namenode.name.dir</name>
    <value>/home/hduser/namenode1, /home/hduser/namenode2</value>
   </property>
   
To modify where files are saved on the datanode, add this property (multiple locations can be specified as long as they are comma separated):

.. code:: xml

   <property>
    <name>dfs.datanode.name.dir</name>
    <value>/home/hduser/datanode1, /home/hduser/datanode2</value>
   </property>

/usr/local/hadoop/etc/hadoop/yarn-site.xml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specify the IP address or hostname of the resource manager (usually the master):

.. code:: xml

   <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>127.0.0.1</value>
   </property>
   
Change the port the Web app is on because InfluxDB is already using 8088:

.. code:: xml

   <property>
    <name>yarn.resourcemanager.webapp.address</name>
    <value>${yarn.resourcemanager.hostname}:8089</value>
   </property>

Running Hadoop
---------------
Format the namenode. This deletes all previous Hadoop data:

.. code:: bash

  hdfs namenode -format 
  
Start namenodes and datanodes: 

.. code:: bash

  start-dfs.sh
  
Start resource manager and node managers:

.. code:: bash

  start-yarn.sh
  
Start history server:

.. code:: bash

  mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ start historyserver

Check everything is working: 

.. code:: bash

  jps

This should produce output similar to:

.. code:: bash
  
  19569 Jps
  10805 ResourceManager
  11177 NodeManager
  10123 NameNode
  10604 SecondaryNameNode
  11310 JobHistoryServer
  10351 DataNode

Running Word count
------------------
Download the book Alice’s Adventures in Wonderland, by Lewis Carroll: 

.. code:: bash

  wget http://www.gutenberg.org/files/11/11-0.txt 

Create a directory in Hadoop to store it:

.. code:: bash

  hdfs dfs -mkdir -p /wordcount/input

Copy the file to Hadoop:

.. code:: bash

  hdfs dfs -put 11-0.txt /wordcount/input

Run word count:

.. code:: bash

  hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.8.0.jar wordcount /wordcount/input /wordcount/output

View the results:

.. code:: bash

  hdfs dfs -cat /wordcount/output/*

Stopping Hadoop
---------------
Stop namenodes and datanodes: 

.. code:: bash

  stop-dfs.sh
Stop resource manager and node managers:

.. code:: bash

  stop-yarn.sh
Stop history server: 

.. code:: bash

  mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ stop historyserver

