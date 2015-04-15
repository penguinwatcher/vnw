#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class ApplicationImplementationBase:
    def start(self, node, opts):
        pass

    def stop(self, node, opts):
        pass

    def application_installed(self, node, opts, context):
        pass

class NullApplicationImplementation (ApplicationImplementationBase):
    def start(self, node, opts):
        logging.info('null application - start')

    def stop(self, node, opts):
        logging.info('null application - stop')

class Application:
    def __init__(self, name, impl, opts, context):
        self.name = name
        self.opts = opts
        self.impl = impl
        self.context = context
        self.node = None
    
    def create(self):
        if self.impl != None:
            self.impl.start(self.node, self.opts)
    
    def delete(self):
        if self.impl != None:
            self.impl.stop(self.node, self.opts)

    def set_node(self, node):
        self.node = node
        if self.impl != None:
            self.impl.application_installed(node, self.opts, self.context)

class ApplicationFactory:
    def __init__(self):
        self.impl_factory_dict = {}
        self.context_dict = {}

    def create_application(self, app_name, opts={}):
        if self.impl_factory_dict.has_key(app_name):
            impl_factory = self.impl_factory_dict[app_name]
            context = self.context_dict[app_name]
        else:
            impl_factory = lambda : NullApplicationImplementation()
            context = {}
        impl = impl_factory()
        return Application(app_name, impl, opts, context)

    def register_app_impl_factory(self, app_name, impl_factory):
        self.impl_factory_dict[app_name] = impl_factory
        self.context_dict[app_name] = {}


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    factory = ApplicationFactory()
    app = factory.create_application('hoge')
    app.create()
    app.delete()


