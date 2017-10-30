.. contents:: Table of Contents
  :depth: 2

==========
Hive Setup
==========
Hive allows for the storage of large datasets on Hadoop. These datasets can be queried and modified with HiveQL, which is similar to SQL. Unlike Hadoop, it does not have to be installed on the nodes, but instead on the devices which are sending HiveQL commands. For simplicity, the Hive client was the master node and so Hive was only installed on that node.

Follow the installation instructions from `here <http://www.bogotobogo.com/Hadoop/BigData_hadoop_Hive_Install_On_Ubuntu_16_04.php>`_. 

For the "Configuring Hive Metastore" step, also modify the existing properties in ``hive-site.xml``:

.. code:: xml
  
  <property>
    <name>hive.exec.scratchdir</name>
    <value>/tmp/hive-${user.name}</value> 
  </property>

  <property>
    <name>hive.exec.local.scratchdir</name>
    <value>/tmp/${user.name}</value> 
  </property>
  
  <property>
    <name>hive.downloaded.resources.dir</name>
    <value>/tmp/${user.name}_resources</value> 
  </property>

  <property>
    <name>hive.scratch.dir.permission</name> 
    <value>733</value>
  </property>

  <property>
    <name>hive.exec.compress.output</name>
    <value>true</value>
  </property>

  <property>
    <name>hive.exec.compress.intermediate</name>
    <value>true</value>
  </property>

Notes
------
If the query is running quite slowly, there might be a way to improve it. Check if the query falls under these `categories <https://docs.treasuredata.com/articles/performance-tuning>`_.  

=========
Tez setup
=========
Tez is a framework that sits on top of YARN. It aims to run faster than the regular Mapreduce. Read more about it `here <https://hortonworks.com/apache/tez/>`_. Similar to Hive, Tez only needs to be installed on the client devices. 

Check dependencies
------------------
To install Tez, first check that Maven 3 is installed.

.. code:: bash

  mvn -v

Install protobuf 2.5.0

.. code:: bash

  wget  https://github.com/google/protobuf/releases/download/v2.5.0/protobuf-2.5.0.tar.gz
  tar -xvzf protobuf-2.5.0.tar.gz 
  cd protobuf-2.5.0.tar.gz
  sudo ./configure
  sudo make
  sudo make check
  sudo make install
  protoc –version
  sudo ldconfig

Installation
-------------
Download the tez src ``tar.gz`` file from `here <https://tez.apache.org/releases/>`_

Extract the files (replace x.y..z with the tez version number)

.. code:: bash

  tar -xvzf apache-tez-x.y.z-src.tar.gz

Alternatively, the tez github repository could be cloned instead:

.. code:: bash

  git clone https://github.com/apache/tez 

Go into the tez directory:

Either ``cd apache-tez-x.y.z-src`` (from the tar.gz file) or ``cd tez`` (from github). 

Get the hadoop version and change the ``hadoop.version`` property in the ``pom.xml`` file.

.. code:: bash

  hadoop version

Build tez using:

.. code:: bash

  mvn clean package -DskipTests=true -Dmaven.javadoc.skip=true

When the build finishes, there should be ``tar.gz`` files in ``tez-dist/target/``. The ``tez-x.y.z.tar.gz`` file (or the ``tez-x.y.z-SNAPSHOT.tar.gz`` if built using the github files) should be put into HDFS.

This can be done by:

.. code:: bash

  hdfs dfs -mkdir -p /apps/tez
  hdfs dfs -put tez-x.y.z.tar.gz /apps/tez

Configuration
--------------
Configure tez by editing ``~/.bashrc`` to include:

.. code:: bash

  #tez environment variables
  export TEZ_HOME=/usr/local/tez
  export TEZ_CONF_DIR=$TEZ_HOME/conf
  export TEZ_JARS="$TEZ_HOME"

  if [ -z "$HIVE_AUX_JARS_PATH" ]; then
  export HIVE_AUX_JARS_PATH="$TEZ_JARS"
  else
  export HIVE_AUX_JARS_PATH="$HIVE_AUX_JARS_PATH:$TEZ_JARS"
  fi

  export HADOOP_CLASSPATH=${TEZ_CONF_DIR}:${TEZ_JARS}/*:${TEZ_JARS}/lib/*

Apply the changes:

.. code:: bash

  source ~/.bashrc
  
Create the folder to hold the tez files:

.. code:: bash

  sudo mkdir $TEZ_HOME
  sudo chown -R hduser:hadoop $TEZ_HOME

Now untar the minimal.tar.gz from tez-dist/target/ into /usr/local/tez

.. code:: bash

  tar -xvzf tez-x.y.z-minimal.tar.gz -C $TEZ_HOME

Create a tez config directory:

.. code:: bash

  cd $TEZ_HOME
  mkdir conf

Create the config file:

.. code:: bash

  touch conf/tez-site.xml

Append the following properties in tez-site.xml:

.. code:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
  <configuration>
    <property>
     <name>tez.lib.uris</name>
     <value>${fs.defaultFS}/apps/tez/tez-x.y.z.tar.gz</value>
     /property>
  </configuration>

Then restart Hadoop:

.. code:: bash

  stop-dfs.sh
  stop-yarn.sh
  mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ stop historyserver
  start-dfs.sh
  start-yarn.sh
  mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ start historyserver

===========
Running Tez
===========
Test if the installation was successful using the word count example in the `Single Node Hadoop Word Count <docs/4_1_single_node_hadoop.rst#running-word-count>`_. 

Run with this command instead:

.. code:: bash

  hadoop jar tez-examples.jar orderedwordcount /wordcount/input /wordcount/output

It may also be necessary to remove the output folder if it is not empty.

.. code:: bash

  hdfs dfs -rm -r /wordcount/output

====================
Running Hive on Tez
====================
Copy the Hive execution jar (where a.b.c is the Hive version) into HDFS

.. code:: bash

  hdfs dfs -put $HIVE_HOME/lib/hive-exec-a.b.c.jar /apps/tez
Modify the ``hive.execution.engine`` property to ``tez`` in ``$HIVE_HOME/conf/hive-site.xml``

.. code:: xml

  <property>
    <name>hive.execution.engine</name>
    <value>tez</value>
  </property>

If you want to go back to using Mapreduce, change the property above to ``mr`` and remove the ``HADOOP_CLASSPATH`` environment variable.

.. code:: bash

  export HADOOP_CLASSPATH=""
