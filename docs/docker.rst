=============
Using Docker
=============
It is possible to run Hadoop, Hive, and Tez on Docker. Install Docker by following the instructions from the `official Docker page <https://docs.docker.com/engine/installation/>`_.

Faucet and Gauge can also be run on Docker containers. The instructions can be found on their `GitHub page <https://github.com/faucetsdn/faucet/blob/master/docs/README.docker.md>`_.

================================================
Running Docker containers on different machines
================================================
To set up communication between Docker containers between different machines, we need to set up a Docker network for this. 

Set up a key value store in one of the machines: 

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

Create an overlay network. The subnet should not overlap with any existing ones.

.. code:: bash

  docker network create --driver overlay --subnet=10.0.9.0/24 hadoop-net

Check the network was successfully created. The network should appear on all the machines configured to be in the swarm.

.. code:: bash

  docker network ls
