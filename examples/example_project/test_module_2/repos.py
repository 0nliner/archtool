from test_module_2.interfaces import TestRepo2Interface
from test_module_1.interfaces import TestRepo1Interface


class TestRepo2(TestRepo2Interface):
    repo1: TestRepo1Interface

    def some_bd_logic(self):
        print(f"Called {type(self).__name__}.some_bd_logic")
        return super().some_bd_logic()
