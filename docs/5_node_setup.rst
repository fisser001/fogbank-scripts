=====================
Start up instructions
=====================

Optional:
---------
If you want to clear the harddrive of each node, follow the steps below.

Check the list of hard drives attached using: 

.. code:: bash

  sudo fdisk -l

If there is a harddrive, it should be attached to ``/dev/sda``

Format the drive using: 

.. code:: bash

  sudo fdisk /dev/sda

Then press the following letters:

.. code:: bash

  o # to create a new partition table
  n # create new partition, then accept all the proposed values
  t # specify type of the new partition, choose type 83
  w # write data and leave

To make kernel read changes:

.. code:: bash

  sudo partprobe 

Format the drive

.. code:: bash

  sudo mkfs.ext4 -L Home /dev/sda1

Install master’s ssh key on slave nodes
---------------------------------------
On the master node, run the ``ssh_key_copy.py`` script to allow for password-less ssh.

.. code:: bash

  ./ssh_key_copy.py

Run the command manually using: 

.. code:: bash

  ssh-copy-id hduser@<node_hostname>

e.g. ``ssh-copy-id hduser@slave1``

Hostname changes
----------------
Each node's hostname must be unique and the node must know about the other nodes in the cluster. 
This can be done using the ``modify_etc_host.py`` script. The ``node_ip_hostname.txt`` file must be modified to match your setup, and the information in the txt file should also be appended to the master node's ``/etc/hosts``

.. code:: bash

  ./modify_etc_host.py

The script follows the steps below. You do not have to run these commands if the script has already been run.

Change each node’s hostname to be unique (e.g. ``slave1``, ``slave2`` etc.)

.. code:: bash

  sudo hostname <name of host>

e.g. ``sudo hostname slave1``

To check the current hostname use:

.. code:: bash

  sudo hostname

Change the ``/etc/hostname`` file to match the new hostname

.. code:: bash

  sudo vi /etc/hostname

Modify ``/etc/hosts`` to have the hostnames and IP addresses of all the nodes. For example add in:

.. code:: bash

  10.0.10.1    master
  10.0.10.2    slave1
  10.0.10.3    slave2

You may also have to comment out the line containing ``127.0.1.1``.


Mount harddrive
----------------
If the node's hard drive is not mounted, use the commands below. Change the folder name & location if desired.

.. code:: bash

  mkdir $HOME/harddrive
  sudo mount /dev/sda1 $HOME/harddrive
  sudo chown -R $USER.$USER $HOME/harddrive

Configuring multiple nodes at once
----------------------------------
There are ways to prevent having to enter the same commands into different nodes. One way is to use `ClusterSSH <https://github.com/duncs/clusterssh>`_, which opens up a terminal to multiple hosts. This would need to be installed on the master. 

Install using:

.. code:: bash

  sudo apt-get install clusterssh

Create a config file:

.. code:: bash

  sudo vim /etc/clusters

Add the following lines:

.. code:: bash

  clusters = hadoop-cluster
  hadoop-cluster = slave1 slave2 

``hadoop-cluster`` is an arbitary name for the cluster. IP addresses can also be used instead of hostnames, so the last line could also have been defined as ``hadoop-cluster = 10.0.10.2 10.0.10.3``

On the master, enter the following command to start it up:

.. code:: bash

  cssh -l <username> <cluster_name>

In our case, it should be ``cssh -l hduser hadoop-cluster``.

An example of what you might see is shown below. Any commands typed in the little grey window will be executed on all the nodes. You can run a command on an individual node by clicking on the node’s terminal window. 

.. image:: /docs/images/clusterssh.png

An alternative would be to use the scripts provided in this repository.

Start up components on the master node
--------------------------------------
Check that the datapaths are configured properly:

.. code:: bash

  ./check_openflow.py

Start up Faucet and Gauge in the background:

.. code:: bash

  nohup ryu-manager --verbose --ofp-tcp-listen-port 6653 ~/faucet/faucet.py > faucet.out 2>&1&
  nohup ryu-manager --verbose --ofp-tcp-listen-port 6654 ~/faucet/gauge.py > gauge.out 2>&1&

``faucet.out`` and ``gauge.out`` is where the output will be written to. You may need to use sudo if Faucet or Gauge is logging somewhere that needs root access (i.e. ``/var/log``)

Run Prometheus in the background:

.. code:: bash

  nohup ./prometheus -config.file=~/prometheus.yaml > prom.out 2>&1&

Please change the prometheus paths to the appropriate locations on your file system. 

Start up Grafana and Influx

.. code:: bash

  sudo service grafana-server start
  sudo service influxdb start

Sometimes Grafana fails to start, but usually it starts up when the command is issued a second time.

Start up the node utilisation monitor:

.. code:: bash
  
  ./start_monitor.py

Modify the Hadoop slave file (``/usr/local/hadoop/etc/hadoop/slaves``) to include the hostnames of all the data nodes (all the slave nodes)

Copy the Hadoop config files into the new nodes:

.. code:: bash
  
  ./copy_files.py

Check node reachability, java and hadoop versions, and time skew:

.. code:: bash
  
  ./check_slaves.py

Start up Hadoop:

.. code:: bash
  
  ./run_dfs.py

Check that the Hadoop daemons are up:

.. code:: bash
  
  ./check_hadoop.py

Shutting down components
-------------------------
Stop Hadoop:

.. code:: bash
  
  ./kill_dfs.sh

Stop Grafana and Influx:

.. code:: bash

  sudo service grafana-server stop
  sudo service influxdb stop

Stop Prometheus by searching for the Prometheus process:

.. code:: bash

  ps ax | grep prometheus

This should produce output similar to:

.. code:: bash

   7955 ?        Sl   241:39 /home/hduser/prometheus/prometheus -config.file=/home/fogbank/prometheus/prometheus.yml
  15727 pts/12   S+     0:00 grep --color=auto prometheus

In this case, the process ID (PID) for Prometheus is 7955. 

To stop Prometheus:

.. code:: bash

  kill <PID>

Check that it has stopped by running this command again:

.. code:: bash

  ps ax | grep prometheus

If it is still not stopped, run this command, which forces it to stop.

.. code:: bash

  kill -9 <PID>

Faucet and Gauge can be stopped in the same way as Prometheus except to find the PID, use the command below instead:

.. code:: bash

  ps ax | grep ryu-manager
