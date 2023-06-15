import pathlib
import pytest
from .dependency_injector import DependecyInjector, AppModule


@pytest.fixture
def base_dir():
    return pathlib.Path.cwd()


@pytest.fixture
def modules_list():
    modules_list = [
        AppModule("")
    ]
    return modules_list


@pytest.fixture
def injector(app_modules, base_dir):
    injector = DependecyInjector(modules_list=app_modules,
                                 base_dir=base_dir)
    return injector
