#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from application import ApplicationImplementationBase
from util import exec_cmd

def exec_node_cmd(node, cmd):
    exec_cmd("sudo ip netns exec %s %s" % (node.name, cmd))
    
def makedirs_if_not_exists(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

class IpHelper (ApplicationImplementationBase):
    def __init__(self):
        self.name = 'ip_helper'
        self.context = None

    def start(self, node, opts):
        net_dev_name = opts['net_device_name']
        ipaddr = opts['ip_addr']
        if opts.has_key('default_gw'):
            default_gw = opts['default_gw']
        else:
            default_gw = None
        self.create_hosts_file(node, opts)
        exec_node_cmd(node, 'ip link set lo up')
        exec_node_cmd(node, 
                ("ip addr add %s dev %s" % (ipaddr, net_dev_name)))
        exec_node_cmd(node, 
                ("ip link set %s up" % net_dev_name))
        if (default_gw != None):
            exec_node_cmd(node, 
                    ("route add default gw %s" % default_gw))

    def stop(self, node, opts):
        net_dev_name = opts['net_device_name']
        exec_node_cmd(node, ("ip link set %s down" % net_dev_name))
        exec_node_cmd(node, 'ip link set lo down')

    def application_installed(self, node, opts, context):
        self.context = context
        hostname = node.name
        ipaddr = opts['ip_addr'].split('/')[0]
        if not context.has_key('hosts'):
            context['hosts'] = []
        host = {'hostname': hostname, 'ip_addr': ipaddr}
        context['hosts'].append(host)

    def create_hosts_file(self, node, opts):
        dirpath = ("/etc/netns/%s" % node.name)
        filepath = os.path.join(dirpath, 'hosts')
        if not os.path.exists(dirpath):
            exec_cmd("sudo mkdir -p %s" % dirpath)
        exec_cmd("sudo chmod -R 777 %s" % dirpath)
        if os.path.exists(filepath):
            exec_cmd("sudo rm -f %s" % filepath)
        exec_cmd("sudo touch %s" % filepath)
        exec_cmd("sudo chmod 777 %s" % filepath)
        lines = ["127.0.0.1\t\tlocalhost\n", "\n"]
        for host in self.context['hosts']:
            line = ("%s\t\t%s\n" % (host['ip_addr'], host['hostname']))
            lines.append(line)
        with open(filepath, 'w') as hostsf:
            hostsf.writelines(lines)


class SimpleCommand (ApplicationImplementationBase):
    def __init__(self):
        self.name = "simple_command"

    def start(self, node, opts):
        if opts.has_key('start_cmd'):
            cmd = opts['start_cmd']
            exec_node_cmd(node, cmd)

    def stop(self, node, opts):
        if opts.has_key('stop_cmd'):
            cmd = opts['stop_cmd']
            exec_node_cmd(node, cmd)


class NodejsApp (ApplicationImplementationBase):
    def __init__(self):
        self.name = "nodejs_app"

    def start(self, node, opts):
        forever_base_path = self.get_forever_base_path(node, opts)
        pid_filepath = self.get_pid_filepath(node, opts)
        log_filepath = self.get_log_filepath(node, opts)
        app_filepath = self.get_app_filepath(node, opts)
        cmd = ("forever start -p %s --pidFile %s -l %s -a -d %s"
            % (forever_base_path, pid_filepath, log_filepath, app_filepath))
        exec_node_cmd(node, cmd)

    def stop(self, node, opts):
        pid  = self.get_pid(node, opts)
        if pid != None:
            cmd = ("forever stop %s" % (pid, ))
            exec_node_cmd(node, cmd)
        exec_node_cmd(node, "forever list")

    def get_fs_root_path(self, node, opts):
        key = 'fs_root_path'
        if opts.has_key(key):
            path = opts[key]
        else:
            basepath = os.path.abspath('nodes_fs')
            path = os.path.join(basepath, node.name)
        makedirs_if_not_exists(path)
        return path

    def get_forever_base_path(self, node, opts):
        key = 'forever_base_path'
        subpath = 'var/run/forever'
        path = self.fget_path(key, subpath)(node, opts)
        makedirs_if_not_exists(path)
        return path

    def get_pid_filepath(self, node, opts):
        key = 'pid_filepath'
        subpath = 'var/run/nodejs-app.pid'
        path = self.fget_path(key, subpath)(node, opts)
        dirpath, filename = os.path.split(path)
        makedirs_if_not_exists(dirpath)
        return path

    def get_log_filepath(self, node, opts):
        key = 'log_filepath'
        subpath = 'var/log/nodejs-app.log'
        path = self.fget_path(key, subpath)(node, opts)
        dirpath, filename = os.path.split(path)
        makedirs_if_not_exists(dirpath)
        return path

    def get_app_filepath(self, node, opts):
        key = 'app_filepath'
        return opts[key]

    def get_pid(self, node, opts):
        pid_filepath = self.get_pid_filepath(node, opts)
        pid = None
        if os.path.exists(pid_filepath):
            with open(pid_filepath, 'r') as pidf:
                pid = pidf.read()
        return pid

    def fget_path(self, key, subpath):
        def path_func(node, opts):
            if opts.has_key(key):
                path = opts[key]
            else:
                fs_root_path = self.get_fs_root_path(node, opts)
                path = os.path.join(fs_root_path, subpath)
            return path
        return path_func


def set_default_apps(app_factory):
    def set_app(name, impl_factory):
        app_factory.register_app_impl_factory(name, impl_factory)
    set_app('ip_helper', IpHelper)
    set_app('simple_command', SimpleCommand)
    set_app('nodejs_app', NodejsApp)



if __name__ == '__main__':
    from components import Node
    node = Node('node1')
    app = NodejsApp()
    print app.get_forever_base_path(node, {})
    print app.get_pid_filepath(node, {})
    print app.get_log_filepath(node, {})
    pid_filepath = app.get_pid_filepath(node, {})
    with open(pid_filepath, 'w') as pidf:
        pidf.write('1234')
    print app.get_pid(node, {})

