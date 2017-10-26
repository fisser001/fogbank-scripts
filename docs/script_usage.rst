Script Usage
============
This document explains how each script is run and the appropriate uses for the script. 

clean.sh
*********
Removes all Hadoop files on all nodes. Also reformats the name node.

.. code:: bash

  ./clean.sh

copy_files.py
**************
The master node holds the Hadoop configuration files for the slave nodes in ``/usr/local/hadoop/etc/hadoop/slave_conf/``. This script copies those files into the slave nodes. 

.. code:: bash

  ./copy_files.py

cpu_ram_monitor.py
******************
Used to monitor a slave node's CPU, RAM, and disk utilisation. These statistics are presented as percentages and are collected every second. This is used with cpu_ram_monitor_main.py. Uses TCP port 12345 to receive requests from cpu_ram_monitor_main.py. 

.. code:: bash

  python cpu_ram_monitor.py

cpu_ram_monitor_main.py
***********************
Used to monitor the cluster utilisation. This should be run on the master node. The script saves the statistics to csv files in a given directory. Run using:

.. code:: bash

  python cpu_ram_monitor_main.py

The statistics collection can be initiated by sending a HTTP POST request, with the directory the statistics should be written to.

.. code:: bash

  curl -H "Content-Type: application/json" -X POST -d '{"directory": "/home/hduser/"}' http://localhost:12345/start-monitoring
  
To stop monitoring, send another HTTP POST request:

.. code:: bash

  curl -X POST http://localhost:12345/end-monitoring

delete.py
*********
This script logs into the slave nodes and deletes the Hadoop folder. 

.. code:: bash

  ./delete.py

generate_graphs.py
*******************
Used with run_multiple_queries.py to generate graphs from statistics collected during a query.

See the `automated_queries <docs/6_automated_queries.rst#generate-graphs-from-the-data>`_ doc for more details.

kill_dfs.sh
************
Stops the Hadoop name nodes, data nodes, node managers, resource managers, historyserver, and timeline server. 

.. code:: bash

  ./kill _dfs.sh

modify_etc_host.py
*******************
Change the contents of /etc/hosts to match the contents of node_ip_hostname.txt. This is done to each slave node. The slave node's hostname is also changed to match the one specified in node_ip_hostname.txt.

.. code:: bash

  ./modify_etc_host.py

run_dfs.py
***********
Starts up the Hadoop components. It first checks that Faucet and Gauge are running and exits if it isn't running. Then checks if Hadoop is already running, and exits if at least one component is already running. 

Then it starts up the Hadoop name nodes, data nodes, node managers, resource managers, historyserver, and timeline server. 

.. code:: bash

  ./run_dfs.py
 
run_multiple_queries.py
************************
Repeats a certain Hive query multiple times. Statistics about the cluster is collected then graphed.

See the `automated_queries <docs/6_automated_queries.rst>`_ doc for more details.

ssh_key_copy.sh
****************
Copies the master node's SSH key to the slaves. 

Requires sshpass to be installed:

.. code:: bash

  sudo apt-get install sshpass

To run:

.. code:: bash

  ./ssh_key_copy.sh

start_monitor.py
*****************
Start up cpu_ram_monitor.py on the slave nodes, and cpu_ram_monitor_main.py on the master. 

It first kills previous cpu_ram_monitor processes, before starting up the script again.

.. code:: bash

  ./start_monitor.py



 
