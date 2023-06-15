from global_types import AppModules
# from .interfaces.di_layer import DILayerInterface
from .dependency_injector.interfaces import 
from .dependency_injector import DependecyInjector

# TODO: переместить
from dependency_injector.interfaces import (
    ReposLayer,
    ServicesLayer,
    ViewsLayer)


class Bundler(BundlerInterface):
    def __init__(self, app_modules: AppModules):
        self.app_modules: AppModules = app_modules
        self._injector = DependecyInjector(layers=self.layers)
        self._dependencies = {}

    def bundle(self):
        # TODO: собрать интерфейсы с каждого слоя
        for layer in self.layers:
            if type(layer) is 
            layer.
                    layer_interfaces = layer.collect_interfaces_from_module(app_module=module)
                    self.register_dependency()
                
