#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from components import Channel, Node, NetDevice
from util import exec_cmd
from application import ApplicationFactory
from appimpls import set_default_apps


def load_json(json_filepath):
    obj = {}
    with open(json_filepath, 'r') as f:
        rdata = f.read()
        obj = json.loads(rdata)
    return obj 


class Topology:
    def __init__(self):
        self.channelDict = {}
        self.nodeDict = {}
        self.netDevices = []

        self.app_factory = ApplicationFactory()
        set_default_apps(self.app_factory)

    def load(self, json_filepath=None):
        if json_filepath != None:
            obj = load_json(json_filepath)
        else:
            obj = {}
        def load_channel(jsonobj):
            name = jsonobj['name']
            opts = jsonobj['opts']
            self.channelDict[name] = Channel(name, opts)
        def load_net_device(jsonobj, node):
            name = jsonobj['name']
            opts = jsonobj['opts']
            netdev = NetDevice(name, opts)
            self.netDevices.append(netdev)
            node.install_net_device(netdev)
            if jsonobj.has_key('channel'):
                channel_name = jsonobj['channel']
                netdev.connect_to(self.channelDict[channel_name])
        def load_application(jsonobj, node):
            app_name = jsonobj['app_name']
            opts = jsonobj['opts']
            app = self.app_factory.create_application(app_name, opts)
            node.install_application(app)
        def load_node(jsonobj):
            name = jsonobj['name']
            opts = jsonobj['opts']
            node = Node(name, opts)
            self.nodeDict[name] = node
            if jsonobj.has_key('net_devices'):
                for nd_jsonobj in jsonobj['net_devices']:
                    load_net_device(nd_jsonobj, node)
            if jsonobj.has_key('applications'):
                for app_jsonobj in jsonobj['applications']:
                    load_application(app_jsonobj, node)
        if obj.has_key('channels'):
            for ch_jsonobj in obj['channels']:
                load_channel(ch_jsonobj)
        if obj.has_key('nodes'):
            for node_jsonobj in obj['nodes']:
                load_node(node_jsonobj)

    def create(self):
        for name, channel in self.channelDict.iteritems():
            channel.create()
        for name, node in self.nodeDict.iteritems():
            node.create()

    def delete(self):
        for name, node in self.nodeDict.iteritems():
            node.delete()
        for name, channel in self.channelDict.iteritems():
            channel.delete()

if __name__ == '__main__':
    pass

