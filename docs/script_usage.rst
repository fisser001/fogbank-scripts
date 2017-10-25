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

.. code:: bash

  python generate_graphs.py <directory> <graph_title>

For example: 

.. code:: bash

  python generate_graphs.py ~/logs/2017-10-17-11\:27\:38/ "Selecting the Max time"

