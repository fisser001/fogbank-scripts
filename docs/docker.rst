.. contents:: Table of Contents
  :depth: 2
=============
Using Docker
=============
It is possible to run Hadoop, Hive, and Tez on Docker. Install Docker by following the instructions from the `official Docker page <https://docs.docker.com/engine/installation/>`_.

Faucet and Gauge can also be run on Docker containers. The instructions can be found on their `GitHub page <https://github.com/faucetsdn/faucet/blob/master/docs/README.docker.md>`_.

==============================================
Running Hadoop, Hive and Tez on a Single Node
==============================================

Hadoop
------
The Hadoop Docker commands are based on commands from this `repository <https://github.com/bigdatafoundation/docker-hadoop>`_.

Get the Hadoop Docker image:

.. code:: bash

  docker pull libunamari/hadoop:latest

Set up a network for Docker containers to communicate:

.. code:: bash

  docker network create --driver=bridge single-hadoop-net

Start up the NameNode:

.. code:: bash

  docker run -d --name hdfs-nn \
    -h hdfs-namenode -p 50070:50070 \
    --net single-hadoop-net \
    libunamari/hadoop hdfs namenode

Check if the namenode was successfully started:

.. code:: bash

  docker logs -f hdfs-nn

Start up the ResourceManager:

.. code:: bash

  docker run -d --name yarn-rm \
    -h yarn-rm -p 8088:8088 \
    --net single-hadoop-net \
    libunamari/hadoop yarn resourcemanager 
    
Check it was successfully started:

.. code:: bash

  docker logs -f yarn-rm

Start up the DataNode and NodeManager:

.. code:: bash

  docker run -d --name hdfs-dn \
    -h hdfs-dn -p 50075:50075 -p 8042:8042 \
    --net single-hadoop-net \
    libunamari/hadoop /bin/bash -c \
    "hadoop-daemon.sh start datanode; yarn nodemanager" 

Test it by running word count. First put some data into HDFS:

.. code:: bash

  docker run --rm \
    --net single-hadoop-net \
    libunamari/hadoop \
    hdfs dfs -put /usr/local/hadoop/README.txt /README.txt

Run word count:

.. code:: bash

  docker run --rm \
    --net single-hadoop-net \
    libunamari/hadoop \
    hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.8.0.jar wordcount  /README.txt /README.result

Display the output:

.. code:: bash

  docker run --rm \
    --net single-hadoop-net \
    libunamari/hadoop \
    hadoop fs -cat /README.result/\*

Alternatively, you could also go into one of the Docker containers and run commands from there. Do this using:

.. code:: bash

  docker exec -it <container-name> bash

The following WebUI may be accessed:

+-----------------+------------------------+
| Web UI          | URL                    |
+=================+========================+
| NameNode        | http://localhost:50070 |
+-----------------+------------------------+
| ResourceManager | http://localhost:8088  |
+-----------------+------------------------+
| DataNode        | http://localhost:50075 |
+-----------------+------------------------+
| NodeManager     | http://localhost:8042  |
+-----------------+------------------------+

Hive and Tez
-------------
Grab the Docker container

.. code:: bash

  docker pull libunamari/hive-tez:latest

Run the container. This will give an interactive shell to the container. Once you exit, the container is stopped.

.. code:: bash

  docker run -it \
    --net single-hadoop-net \
    libunamari/hive-tez
 
Run the startup script to configure hive and tez
 
.. code:: bash

  ./start_up.sh

Start up the Hive shell

.. code:: bash

  beeline -u jdbc:hive2://

Load in the sample csv into Hive. First create a table:

.. code:: sql

 CREATE TABLE sample_data 
 (type STRING, tenure STRING, period STRING, value INT) 
 row format delimited fields terminated by ','
 tblproperties("skip.header.line.count"="1");

Then load the csv into the table

.. code:: sql

 LOAD DATA LOCAL INPATH 'dhe-sep17qtr-tables-csv.csv' OVERWRITE INTO TABLE sample_data;

Then type in a query to perform on the new table. For this example, the max value was queried.

.. code:: sql
 
 SELECT max(value) FROM sample_data;

================================================
Running Docker containers on different machines
================================================
This section explains how Docker can be used in a cluster. These instructions are based on the official Docker `standalone swarm instructions <https://docs.docker.com/engine/userguide/networking/overlay-standalone-swarm/>`_. 

From the official Docker page: "An overlay network requires a key-value store. The key-value store holds information about the network state which includes discovery, networks, endpoints, IP addresses, and more. Docker supports Consul, Etcd, and ZooKeeper key-value stores."

Set up a key-value store (Consul) in one of the machines: 

.. code:: bash

  docker run -d \
    --name consul \
    -p "8500:8500" \
    -h "consul" \
    consul agent -server -bootstrap -client "0.0.0.0"
  
Modify the /etc/docker/daemon.json file to set up a swarm. This must be done on all of the machines. If there is no daemon.json file, just make one using:

.. code:: bash

  sudo touch /etc/docker/daemon.json

To configure the swarm, the cluster-store and cluster-advertise properties must be set in the daemon.json file. The cluster-store contains the IP address of the machine running the key value store, and the type of key value store. The cluster-advertise contains the IP address this machine is using to communicate with the rest of the cluster. 

.. code:: json

  {
    "cluster-store": "consul://key-store-ip:8500",
    "cluster-advertise": "external-ip:2377"
  }

Restart Docker so the changes get applied:

.. code:: bash

  sudo service docker restart

Create an overlay network. The subnet should not overlap with any existing ones. Please note that this network only exists within Docker, so you cannot access it from outside a container or a container not set to be this network.

.. code:: bash

  docker network create --driver overlay --subnet=10.0.9.0/24 hadoop-net

Check the network was successfully created. The network should appear on all the machines configured to be in the swarm.

.. code:: bash

  docker network ls

Then you can start up the Docker containers. Remember to bind the containers to the new overlay network you have created. 

There should only be one NameNode since that is how Hadoop was configured on these Docker containers.  The Hadoop configuration can be changed in `/docker/hadoop_conf </docker/hadoop_conf>`_. If changes are made, then the Docker image needs to be built from the Dockerfiles in `/docker </docker>`_.

=========================
Building using Dockerfile
=========================

Instead of pulling the image from the Docker Hub, you can also build the image from the Dockerfile.

.. code:: bash

  docker build -t libunamari/hadoop -f Dockerfile .

=========================
Useful Docker commands
=========================

+-------------------------------------------+---------------------------------------------------------------------------------------------------------+
| Command                                   | Description                                                                                             |
+-------------------------------------------+---------------------------------------------------------------------------------------------------------+
| ``docker ps``                             | Lists the Docker containers (both running and stopped)                                                  |
+-------------------------------------------+---------------------------------------------------------------------------------------------------------+
| ``docker stop <container name>``          | Stop the docker container                                                                               |
+-------------------------------------------+---------------------------------------------------------------------------------------------------------+
| ``docker rm <container name>``            | Delete the docker container (a stopped container isn't automatically deleted)                           |
+-------------------------------------------+---------------------------------------------------------------------------------------------------------+
| ``docker network inspect <network name>`` | Shows details about the network (e.g. what containers are attached, the IP addresses of the containers) |
+-------------------------------------------+---------------------------------------------------------------------------------------------------------+

**NOTE**

Docker may be prone to hoarding, so you may end up losing a lot of disk space. Run the following command to remove unecessary files:

.. code:: bash

  docker system prune
