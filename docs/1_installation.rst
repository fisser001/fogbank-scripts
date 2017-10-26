======
FAUCET 
======
Installation instructions can be found `here <https://github.com/faucetsdn/faucet/blob/master/docs/README_install.rst>`_. An example configuration file is shown `here </docs/1_installation.rst#faucetyaml-example>`_.

To always get the most recent code, clone the github repository instead of using the pip package installation.

.. code:: bash

  git clone https://github.com/faucetsdn/faucet.git
Run the faucet controller using:

.. code:: bash

  ryu-manager faucet.faucet --verbose
It may be necessary to run the command above using ``sudo``, since the default FAUCET log files are in /var/log which needs root access to modify.

======
Gauge
======
A sample yaml file is given `here </docs/1_installation.rst#gaugeyaml-example>`_.

Gauge acts as a separate controller to Faucet, and only collects statistics.                        
To run the gauge controller:

.. code:: bash

  ryu-manager --ofp-tcp-listen-port 6654 faucet.gauge  
The ``--ofp-tcp-listen-port`` is to run gauge on a different TCP port than the faucet controller. Like with running faucet.py, this command may also need root access.

**NOTE**

**If Gauge is being used with Faucet, you need to make sure that your switch is able to connect to two controllers.**

For example, the `Zodiac <https://github.com/faucetsdn/faucet/blob/3f94cd8dc555687e0b0b4c10dbafccba7d1e5514/docs/vendors/northboundnetworks/README_ZodiacFX.rst>`_ switch only allows for one controller, so Gauge cannot be used. By default, an OpenFlow switch may only connect to one controller, so you may have to change the switch configuration. Instructions to configure an Allied-Telesis switch is detailed `here </docs/faucet_troubleshooting.rst#switch-configuration>`_.

========
InfluxDB
========
Installation instructions can be found `here <https://docs.influxdata.com/influxdb/v1.3/introduction/installation/>`_. InfluxDB can be used through the `HTTP API <https://docs.influxdata.com/influxdb/v1.3/guides/writing_data/>`_ or the `CLI <https://docs.influxdata.com/influxdb/v1.2/tools/shell/>`_. 

Create a database using the CLI using:

.. code:: bash

  influx
  CREATE DATABASE faucet
View information about a particular measurement:

.. code:: bash

  precision rfc3339       #Displays date in readable format (UTC timezone)
  SELECT * FROM bytes_in  #Show all the details from the bytes_in measurement

==========
Prometheus
==========
Installation notes can be found `here <https://prometheus.io/docs/introduction/install/>`_. Prometheus also uses yaml files for configuration. To get Prometheus scraping information off Faucet, add the following lines to the prometheus.yml under scrape_configs:

.. code:: yaml

  scrape_configs:
    - job_name: 'faucet'
    static_configs:
      - targets: ['127.0.0.1:9302']
    - job_name: 'gauge'
    static_configs:
      - targets: ['127.0.0.1:9303']
Change the IP address in targets to 172.17.0.1 if Faucet is running within Docker.
To start up Prometheus, go to the directory containing the prometheus script:
 
.. code:: bash

  cd prometheus
  ./prometheus
The command above assumes that the yaml file is in the prometheus directory. To change this, indicate the location of the yaml file using the -config.file option:
 
.. code:: bash

  ./prometheus -config.file=/home/user/new_prom_config.yml
View the data being scraped by going to http://localhost:9090/ in a browser.

=======
Grafana
=======
Installation notes can be found `here <http://docs.grafana.org/installation/>`_. Once the grafana-server is running, go to http://localhost:3000/ in a browser.

Add a data source by clicking the Grafana logo on the top left corner. Click on Data Source > Add data source and fill in the appropriate details. 

Add a Dashboard by clicking on the logo again, choosing Dashboards > New. Select graph, and click on the panel title to edit. 

This is the end of this document. If you wish to read an example of how all these components were used together, proceed to the next document.

========
Appendix
========
faucet.yaml example
************
 
.. code:: yaml

  version: 2                        # The current FAUCET config version
  vlans:                            # VLANs that will be used. Each port must be in at least 1 VLAN.
    100:
      name: "default-vlan"
  
  acls:                             # Access Control List:
    101:                            # What rules will be applied to packets.  
      - rule:                       # Each rule has matches and actions.
        dl_type: 0x0800             # The action can either be: allow, mirror, or output.
        actions:                    # Allow is either 0 or 1, and the other two actions 
          allow: 1                  # are followed by a port number. 
      - rule                        # In this yaml file, the two rules match on
        dl_type: 0x0806             # the ethernet type of ARP and IPv4. 
        actions:                    # Packets which match this are allowed.
          allow: 1                  
  dps:
    windscale-faucet-1:             # Datapaths:
      dp_id: 0x0000e01aeb24e893     # The name of the datapath will be used 
      description: "SDN Switch"     # by the data collected by Faucet and Gauge.
      hardware: "Allied-Telesis"    # In this case, the dp name is windscale-faucet-1
      interfaces:                   #
        1:                          #
          native_vlan: 100          # If a port does not tag traffic with VLAN tags,
          name: "port1"             # then it must have a native_vlan field 
          acl_in: 101               # corresponding to a VLAN in the vlans section.
        2:                          # Each interface should also have a unique name
          native_vlan: 100          # 
          name: "port2"             # The acl_in section is what acls will be 
          acl_in: 101               # applied to the interface.

gauge.yaml example
************
 
.. code:: yaml

  version: 2                            # Current FAUCET config version
  faucet_configs:                       
    - '/etc/ryu/faucet/faucet.yaml'     # Where the faucet config file is located

  watchers:                             # This section configures the data collection.
    port_stats:                         # The statistics that may be collected are 
      dps: ['windscale-faucet-1']       # port stats, port state, and flow stats. 
      type: 'port_stats'                # 
      interval: 10                      # The interval field specifies how often
      db: 'prometheus'                  # Gauge will poll the statistic. For example, 
    port_state:                         # an interval of 10 will poll every 10 seconds
      dps: ['windscale-faucet-1']       # 
      type: 'port_state'                # The db field specifies which database from 
      interval: 10                      # the dbs section will be used. 
      db: 'influx'                      
    flow_table_poller:                  
      dps: ['windscale-faucet-1']       
      type: 'flow_table'                
      interval: 40                      
      db: 'influx'                      
  
   dbs:                                 # This section configures the databases  
    prometheus:                         # that the data will be stored in.
        type: 'prometheus'              
        prometheus_addr: 'localhost'    # Prometheus can only save port_stats.
        prometheus_port: 9303
    influx:
        type: 'influx'                  # influx is saved to an InfluxDB database.
        influx_db: 'faucet'             # The name of the database is configured 
        influx_host: 'localhost'        # through the influx_db field.
        influx_port: 8086               # You must create the database in Gauge first.
        influx_user: 'faucet'
        influx_pwd: 'faucet'
        influx_timeout: 10
    ft_file:                            # The stats is saved to a file.  
        type: 'text'                    # The file name is specified in the file field.
        file: 'gauge_stats'
