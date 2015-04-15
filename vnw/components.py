#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import exec_cmd

class Channel:
    """Channel class"""
    def __init__(self, name, opts={}):
        self.name = name
        self.opts = opts
        self.net_devices = []

    def create(self):
        """Creates this channel as a bridge w/o spanning-tree protocol."""
        exec_cmd("sudo brctl addbr %s" % (self.name,))
        exec_cmd("sudo brctl stp %s off" % (self.name,))
        exec_cmd("sudo ip link set dev %s up" % (self.name,))

    def delete(self):
        """Deletes this channel."""
        exec_cmd("sudo ip link set dev %s down" % (self.name,))
        exec_cmd("sudo brctl delbr %s" % (self.name,))

    def append_net_device(self, net_device):
        self.net_devices.append(net_device)

    def remove_net_device(self, net_device):
        self.net_devices.remove(net_device)

class Node:
    """Node class"""
    def __init__(self, name, opts={}):
        self.name = name
        self.opts = opts
        self.net_devices = {}
        self.is_created = False
        self.applications = []
    
    def create(self):
        """Creates this node as a netns."""
        exec_cmd("sudo ip netns add %s" % (self.name,))
        # Sets all net devices.
        for name, dev in self.net_devices.iteritems():
            dev.create()
        for app in self.applications:
            app.create()
        self.is_created = True

    def delete(self):
        for app in self.applications:
            app.delete()
        # Unsets all net devices.
        for name, dev in self.net_devices.iteritems():
            dev.delete()
        exec_cmd("sudo ip netns delete %s" % (self.name,))
        self.is_created = False

    def install_net_device(self, net_device):
        if not self.net_devices.has_key(net_device.name):
            self.net_devices[net_device.name] = net_device
            net_device.set_node(self)

    def uninstall_net_device(self, net_device):
        if self.net_devices.has_key(net_device.name):
            del self.net_devices[net_device.name]
            net_device.set_node(None)

    def install_application(self, application):
        self.applications.append(application)
        application.set_node(self)

    def uninstall_application(self, application):
        self.applications.remove(application)
        application.set_node(None)

class NetDevice:
    """Net device class."""
    def __init__(self, name, opts={}):
        self.name = name
        self.opts = opts
        self.node = None
        self.channel = None

    def set_node(self, node):
        self.node = node

    def get_port_name(self):
        #return "%s-%s" % (self.node.name, self.name)
        return self.name

    def get_tap_name(self):
        return "%s-%s.t" % (self.node.name, self.name)

    def create(self):
        exec_cmd("sudo ip link add %s type veth peer name %s" 
                % (self.get_port_name(), self.get_tap_name()))
        exec_cmd("sudo ip link set %s netns %s"
                % (self.get_port_name(), self.node.name))
        if self.is_connected():
            tap_name = self.get_tap_name()
            exec_cmd("sudo brctl addif %s %s"
                    % (self.channel.name, tap_name))
            exec_cmd("sudo ip link set dev %s up" % (tap_name,))

    def delete(self):
        if self.is_connected():
            tap_name = self.get_tap_name()
            exec_cmd("sudo ip link set dev %s down" % (tap_name,))
            exec_cmd("sudo brctl delif %s %s"
                    % (self.channel.name, tap_name))
        exec_cmd("sudo ip link delete %s" % (self.get_tap_name(),))

    def is_connected(self):
        return self.channel != None

    def connect_to(self, channel):
        if not self.is_connected():
            self.channel = channel
            channel.append_net_device(self)
            tap_name = self.get_tap_name()

    def disconnect(self):
        if self.is_connected():
            channel = self.channel
            self.channel = None
            channel.remove_net_device(self)


if __name__ == '__main__':
    rc = exec_cmd("ls -la")
    print rc
    
    channel = Channel("vbr-pint")
    channel.create()

    exec_cmd("sudo brctl show")

    channel.delete()

