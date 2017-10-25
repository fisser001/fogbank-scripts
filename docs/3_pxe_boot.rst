.. contents:: Table of Contents
  :depth: 2
  
=================================
Creating PXE boot image (Xubuntu)
=================================

Creating a new Virtual Machine
-------------------------------
Download Guest additions to allow for a shared clipboard between the VM and your machine.

.. code:: bash

  sudo apt-get install virtualbox-guest-additions-iso

Download the Xubuntu .iso file from https://xubuntu.org/getxubuntu. If you want something slimmed down, download Xubuntu core: https://xubuntu.org/news/introducing-xubuntu-core/. 

Download and install `VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.

Open up VirtualBox, and click on New. 
The settings that were used is shown below. Click Create to move onto the next step.

.. image:: /docs/images/vm_1.png

For the File size, have it as 20 GB. Click Create once again. The VM’s name should now appear on VirtualBox.

.. image:: /docs/images/vm_2.png

To be able to SSH/SCP into the VM from the host, the following steps are followed. Click on File > Preferences > Network > Host-only Networks. If this list is empty, click on the icon with the + to create a new interface. Click OK. 

.. image:: /docs/images/vm_3.png

Right click on the new VM’s name and select Settings > Network > Adapter 2. Select to enable the network adaptor, and attach to a Host-only Adapter. 

.. image:: /docs/images/vm_4.png

Finally, start the VM. You should be prompted to select a start-up disk, so select the .iso that you have downloaded. Install Xubuntu on the VM. It should ask for a reboot once everything is finished. 

Install Guest additions on the VM
-----------------------------------
In the running VM window, click on Devices > Optical Drives > Choose disk image. 

.. image:: /docs/images/vm_5.png

The Guest Additions image should be in ``/usr/share/virtualbox/VBoxGuestAdditions.iso``

The CD icon should appear on the VM’s desktop. Double click on it to mount the cd. 

Open up a terminal window by pressing Ctrl Alt T.

Go into the CD folder: 

.. code:: bash

  cd /media/username/VBOXADDITIONS_5.1.14_112924

``username`` should be changed to your username and the ``VBOXADDITIONS`` version should correspond to the one you have downloaded.

Install Guest additions:

.. code:: bash

  sudo ./VBoxLinuxAdditions.run 

In the running VM window, click Devices > Shared Clipboard > Bidirectional

.. image:: /docs/images/vm_6.png

Restart the VM so the changes can take into effect:

.. code:: bash

  sudo reboot

Creating a PXE image of the VM
-------------------------------

The following instructions use PinguyBuilder. Alternatives to this are:

- `Customizer <https://github.com/kamilion/customizer>`_
- `Using the command line <https://help.ubuntu.com/community/LiveCDCustomization>`_

In the VM, download `PinguyBuilder <https://sourceforge.net/projects/pinguy-os/files/ISO_Builder/pinguybuilder_4.3-8_all-beta.deb/download>`_.

Install gdebi (a deb file installer)

.. code:: bash

  sudo apt-get install gdebi

Install PinguyBuilder

.. code:: bash

  sudo gdebi pinguybuilder_4.3-8_all-beta.deb

Run using

.. code:: bash

  PinguyBuilder-gtk

Go to the Settings tab and change the username to be your own. Also uncheck the “Show install icon on Backup mode desktop” option. 

.. image:: /docs/images/vm_7.png

Go to the Actions tab and click on “Select User, whose current settings will be used as default.” Then click on “Backup” to create the ISO image.                                                                                                       

.. image:: /docs/images/vm_8.png

The image will be under the path that was listed in the Working directory section of the Settings tab. In the previous screenshot, the working directory was ``/home/``, so the image will be in ``/home/PinguyBuilder/``. 

Getting the image from the VM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This can be done in two ways: either using SCP or drag and drop via Guest Additions.

To use scp, check that ssh is enabled on the VM: 

.. code:: bash

  ssh localhost
If it says something along the lines of ``Port 22 connection refused``, install ssh using:

.. code:: bash

  sudo apt-get install ssh

Find the VM IP address:

.. code:: bash

  ifconfig

The IP address should be in the ``192.168.56.x`` range. 

In the original machine (not the VM), copy the file:

.. code:: bash

  scp username@192.168.56.x:~/home/PinguyBuilder/xubuntu_core.iso ~/Documents  


To enable drag and drop, Guest additions must be installed. 

In the VM, click on Devices > Drag and Drop > Guest to Host. 

Restart the VM to change this setting. 

Check that this works by dragging and dropping a small file first before the ISO image.

Proxy settings
--------------
If the VM is going through a proxy, the http proxy settings needs to be set up in the VM. 
Open up ~/.bashrc

.. code:: bash

  vim ~/.bashrc
Add the following lines (fill out the details required):

.. code:: bash

  export http_proxy=http://<username>:<password>@<proxy-address>:<proxy-port>
  export https_proxy=http://<username>:<password>@<proxy-address>:<proxy-port>
  export HTTP_PROXY=http://<username>:<password>@<proxy-address>:<proxy-port>
  export HTTPS_PROXY=http://<username>:<password>@<proxy-address>:<proxy-port>

For example, your username could be bob and your password is pwd123:

.. code:: bash

  export http_proxy=http://bob:pwd123@http-proxy.vuw.ac.nz:8080

Apply the changes:

.. code:: bash

  source ~/.bashrc

======================
Configuring PXE server
======================

Installing new packages
------------------------
This section will detail how to start up a PXE server. It assumes that the IP address of the server is ``10.0.10.1``. We need a TFTP and a DHCP server to host a PXE server. 

Install these and other required packages using: 

.. code:: bash

  sudo apt-get install tftpd-hpa isc-dhcp-server nfs-kernel-server syslinux

Configure the TFTP server by editing ``/etc/default/tftpd-hpa`` to include the section below. If it does not work, change the TFTP_ADDRESS to 0.0.0.0

.. code:: bash

  TFTP_USERNAME="tftp"
  TFTP_DIRECTORY="/var/lib/tftpboot"
  TFTP_ADDRESS="[:10.0.10.1:]:69"
  TFTP_OPTIONS="--secure"
  RUN_DAEMON="yes"

Configure the DHCP server by editing ``/etc/dhcp/dhcpd.conf``. We want it to be the official DHCP server for the local network, so uncomment the line that says ``authoritative;``. Then include the following:

.. code:: bash

  subnet 10.0.10.0 netmask 255.255.255.0 {
  range 10.0.10.2 10.0.10.240;
  option subnet-mask 255.255.255.0;
  option routers 10.0.10.1;
  option broadcast-address 10.0.10.255;
  filename "pxelinux.0";
  next-server 10.0.10.1;
  }

Create the pxelinux config files:

.. code:: bash

  sudo mkdir -p /var/lib/tftpboot/pxelinux.cfg
  sudo touch /var/lib/tftpboot/pxelinux.cfg/default
  sudo touch /var/lib/tftpboot/pxelinux.cfg/pxe.conf

Edit the ``/var/lib/tftpboot/pxelinux.cfg/default`` file by including:

.. code:: conf

  DEFAULT vesamenu.c32
  TIMEOUT 1000
  PROMPT 0
  MENU INCLUDE pxelinux.cfg/PXE.conf
  NOESCAPE 1
 
Edit ``/var/lib/tftpboot/pxelinux.cfg/pxe.conf``:

.. code:: conf

  MENU TITLE PXE Server
  NOESCAPE 1
  ALLOWOPTIONS 1
  PROMPT 0
  MENU WIDTH 80
  MENU ROWS 14
  MENU TABMSGROW 24
  MENU MARGIN 10
  MENU COLOR border 30;44 #ffffffff #00000000 std

Adding bootable images into PXE boot
------------------------------------
This section assumes that the .iso file was called xubuntu_pxe.iso. 
Make a directory for the ISO to mount to and copy the contents of the file to tftpboot.

.. code:: bash

  mkdir /tmp/xubuntu_hadoop
  sudo mount -o loop ~/xubuntu_hadoop.iso /tmp/xubuntu_hadoop
  sudo cp -r /tmp/xubuntu_hadoop /var/lib/tftpboot

Edit ``/var/lib/tftpboot/pxelinux.cfg/default`` to include:

.. code:: bash

  LABEL Xubuntu Hadoop
  MENU LABEL Xubuntu Hadoop
  kernel xubuntu_hadoop/casper/vmlinuz
  append boot=casper netboot=nfs nfsroot=10.0.10.1:/var/lib/tftpboot/xubuntu_hadoop/ initrd=xubuntu_hadoop/casper/initrd.gz
  ENDTEXT

Edit ``/etc/exports`` to include:

.. code:: bash

  /var/lib/tftpboot/xubuntu_hadoop *(ro,async,no_root_squash,no_subtree_check)

Change the file permissions:

.. code:: bash

  cmod 777 -R /var/lib/tftpboot/xubuntu_hadoop

Restart all the services. Alternatively, you can just reboot.

.. code:: bash

  sudo service tftpd-hpa restart
  sudo /etc/init.d/isc-dhcp-server restart
  sudo /etc/init.d/nfs-kernel-server restart

=======================================
Configuring network blades to PXE boot
=======================================
The blade servers that were used are Dell Poweredge 1955 blades. The instructions below are specifically for these blades.

- Reboot the blade
- Press F2 to go to the system setup menu
- Select the Integrated Devices menu item and press Enter
- Press the down arrow key to the Network Interface Controller menu items and press space until “Enabled with PXE” is selected. Only one interface enabled with PXE is needed.
- Save changes and exit
- Press F12 to PXE boot

===============
Troubleshooting
===============

Blade says “No PXE-capable device found”
---------------------------------------

You need to check three components: the blade interface, DHCP server, and switch controller. 
Check that at least one interface is enabled with PXE, this can be done in the “Configuring network blades to PXE boot” section. 

If it is still not working, check the server. Run tcpdump or wireshark to check that you are getting DHCP requests from the blades and DHCP replies from the server. If there is no reply, start up the DHCP server with ``sudo /etc/init.d/isc-dhcp-server start``. 

If the blade and the server are connected through an OpenFlow switch, check that a controller is running and forwarding traffic between the two. 

I’ve chosen to boot an image on a blade but it gets stuck when booting up
-------------------------------------------------------------------------
In my case, it got stuck on:

.. code:: bash

  [7.24765] IPv6:ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
  [198.122] random nonblocking pool is initialized

So I had to modify the ``/var/lib/tftpboot/pxelinux.cfg/default`` file. I had to add ``IPAPPEND 2`` under my image config, so it looks like:

.. code:: bash

  LABEL Xubuntu Cluster
  MENU LABEL Xubuntu Cluster
  kernel xubuntu_cluster/casper/vmlinuz
  append boot=casper netboot=nfs nfsroot=10.0.10.1:/var/lib/tftpboot/xubuntu_cluster/ initrd=xubuntu_cluster/casper/initrd.gz
  IPAPPEND 2
  ENDTEXT

Config files to check
---------------------

- ``/etc/exports``
- ``/var/lib/tftpboot/pxelinux.cfg/default``
- ``/etc/dhcp/dhcpd.conf``

Check that the paths you put in the default config file actually match the file locations in ``/var/lib/tftpboot``
