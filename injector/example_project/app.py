from injector.dependecy_injector import DependecyInjector
from injector.global_types import AppModule

from layers import (ServicesLayer,
                    ReposLayer)

layers = [ServicesLayer(module_name_pattern="services"),
          ReposLayer(module_name_pattern="repos")]

modules_list = [
    AppModule("test_module_1"),
    AppModule("test_module_2")
]

injector = DependecyInjector(modules_list=modules_list,
                             layers=layers)


if __name__ == "__main__":
    injector.inject()
    print("finish")
