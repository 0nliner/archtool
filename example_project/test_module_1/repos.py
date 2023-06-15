from example_project.test_module_1.interfaces import TestRepo1Interface
from example_project.test_module_2.interfaces import TestRepo2Interface


class TestRepo1(TestRepo1Interface):
    repo2: TestRepo2Interface

    def some_bd_logic(self):
        print(f"Called {type(self).__name__}.some_bd_logic")
        self.repo2.some_bd_logic()
        return super().some_bd_logic()
