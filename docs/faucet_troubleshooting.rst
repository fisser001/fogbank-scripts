.. contents:: Table of Contents
  :depth: 2

====================
Log and config files
====================
By default, the log files for both Faucet and Gauge should be stored in ``/var/log/ryu/faucet/``. The config files are in ``/etc/ryu/faucet`` by default. To change what log or config files are used, you can set environment variables, so that the controllers use the specified files instead. An example of how this can be done is as follows: 

.. code:: bash

  export FAUCET_CONFIG=/home/myname/my_faucet_config.yaml

The full list of values you can set can be seen in the table below.

+----------------------+----------------------------------------------+
| Environment Variable | Default location                             |
+======================+==============================================+
| FAUCET_CONFIG        | ``/etc/ryu/faucet/faucet.yaml``              |
+----------------------+----------------------------------------------+
| FAUCET_LOG           | ``/var/log/ryu/faucet/faucet.log``           |
+----------------------+----------------------------------------------+
| FAUCET_EXCEPTION_LOG | ``/var/log/ryu/faucet/faucet_exception.log`` |
+----------------------+----------------------------------------------+
| GAUGE_CONFIG         | ``/etc/ryu/faucet/gauge.yaml``               |
+----------------------+----------------------------------------------+
| GAUGE_LOG            | ``/var/log/ryu/faucet/gauge.log``            |
+----------------------+----------------------------------------------+
| GAUGE_EXCEPTION_LOG  | ``/var/log/ryu/faucet/gauge_exception.log``  |
+----------------------+----------------------------------------------+

More information can be found in the `Faucet readme <https://github.com/faucetsdn/faucet/blob/master/docs/README_config.rst>`_

================
Useful commands
================

Tcpdump
-------
Tcpdump is a way to view what packets are being exchanged. This may be useful to check if the switch is connecting to the controller, or if the database is being written to. Usually root access is needed, so tcpdump commands are usually run with sudo. Some useful tcpdump commands are below. The full list can be found `here <http://www.tcpdump.org/tcpdump_man.html>`_.

+--------------------------------+-----------------------------------------------------------------------------------------+
| Command                        | Description                                                                             |
+================================+=========================================================================================+
| ``tcpdump -D``                 | Lists interfaces tcpdump can capture on                                                 |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``tcpdump -i <interface>``     | Listen on specified interface                                                           |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``tcpdump host <IP_address>``  | Only capture packets where either the destination or the source matches the IP address  |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``tcpdump port <port_number>`` | Only capture packets where either the destination or the source matches the port number |
+--------------------------------+-----------------------------------------------------------------------------------------+

Wireshark
---------
A GUI alternative to tcpdump is wireshark. 

To install:

.. code:: bash

  sudo apt-get install wireshark

To allow capturing packets without needing sudo:

.. code:: bash

  sudo dpkg-reconfigure wireshark-common   #press yes
  sudo usermod -a -G wireshark $USER

Finally, logout to apply the changes.

grep
----
grep is used to display lines which match the given pattern. For example, when trying to see where a given word is used, the following command could be issued: 

.. code:: bash

  grep -r “word” /home/user

The -r is to search recursively and look through each directory under the given path. Another way to use it is to pipe the output from another command. 

An example is when trying to find the process ID of a given program. ``ps ax`` lists all the running processes. To show the process ID of python processes, the following command could be issued:

.. code:: bash

  ps ax | grep python 

Reverse i search
-----------------
Reverse i search provides a way to search previously entered commands in BASH. Press Ctrl + R and type in what to search for. Keep pressing Ctrl + R until the desired command is found.

=====================
Switch configuration
=====================

The documentation for configuring the Faucet supported switches can be found `here <https://github.com/faucetsdn/faucet/tree/master/docs/vendors>`_.
Assuming that the Allied Telesis x510 is being used, the command reference is `here <http://www.alliedtelesis.com/sites/default/files/x510_command_ref_5.4.6-0.x_reva.pdf>`_. The most useful section is OpenFlow.

Use serial to connect to the switch:

.. code:: bash

  sudo screen /dev/ttyS0 9600

You can exit screen by pressing Ctrl + A, then capital K, then finally y. 

Press enter to show the login prompt. 

The username is manager and the password is friend

When configuring switches, usually the following steps are followed:

#. Enter ``enable`` to enter the privileged execution mode
#. Enter ``configure terminal`` (or ``conf term`` as a shorthand) to change the switch configuration
#. Then the configuration commands can be entered. To remove a certain configuration, add ``no`` at the front. 
#. Once the changes have been made, save it using ``write memory`` (or ``write mem`` as a shorthand).
#. Use ``exit`` to go back to the previous level, or ``end`` to immediately go back to the privileged execution mode.

Things to look out for
----------------------
If you suspect that the switch is the problem, check the openflow settings.

Type in ``enable``, then either ``show openflow status`` or ``show openflow config``.

Check that the data ports you are using is listed in either command. The port the controller is connected to is not listed. 

If a certain port is not listed, configure it using: 

.. code:: bash

  awplus> enable
  awplus# configure terminal
  awplus(config)# interface port1.0.x
  awplus(config-if)# openflow
  awplus(config-if)# write memory
  awplus(config-if)# end
  awplus# reboot

A reboot must occur before changes go into effect. If configuring multiple ports, only write memory and reboot after changing the settings for all ports. 

Also check that the switch is connecting to two controllers. An example output is shown below: 

.. code:: bash

  awplus#show openflow config
  9249f4a8-cdd3-4959-aff0-a70e51c02e9d
      Bridge "br0"
          Controller "tcp:10.0.0.1:6654"
              is_connected: true
          Controller "tcp:10.0.0.1:6653"
              is_connected: true
          fail_mode: secure

When using Gauge with Faucet, the switch must be configured to connect to both of them. By default, an OpenFlow switch only tries to connect to one controller, so another must be added for Gauge. 

Configure using:

.. code:: bash

  awplus> enable
  awplus# configure terminal
  awplus(config)# openflow controller tcp 10.0.0.1 6653
  awplus(config)# write memory
  awplus(config)# end
  awplus# 

========================
Using OpenFlow messages
========================
Certain statistics can be obtained from the switch by sending messages from the controller. This can be useful to check if two hosts are communicating or to see the packets being sent. The statistics that can be obtained is listed `here <http://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#multipart-messages>`_. The controller sends the request, and the switch sends back the reply. The most useful statistics are the `flow stats <http://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#ryu.ofproto.ofproto_v1_3_parser.OFPFlowStatsRequest>`_ and the `port stats <http://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#ryu.ofproto.ofproto_v1_3_parser.OFPPortStatsRequest>`_. Both the request and the reply should be handled by the controller. 

Another way to troubleshoot using OpenFlow messages is to install a flow which matches the packets you are looking for. This way, the flow stats for that particular flow can be obtained. Alternatively to view packets being sent on the flow, the flow action could be to send packets up to the controller. This way the controller can print out the received packet ins. This can also be done with Faucet ACLs by mirroring the port to another port. 
