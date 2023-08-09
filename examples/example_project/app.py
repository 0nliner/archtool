import sys
import pathlib

sys.path.append(pathlib.Path.cwd().as_posix())

from archtool.dependecy_injector import DependecyInjector
from archtool.layers.default_layers import DomainLayer
from archtool.global_types import AppModule


#   ignore=[DomainLayer.Components.services]),
modules_list = [
    AppModule("test_module_1"),
    AppModule("test_module_2")
]

injector = DependecyInjector(modules_list=modules_list)


if __name__ == "__main__":
    injector.inject()
    print("finish")
