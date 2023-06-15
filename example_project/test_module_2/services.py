from example_project.test_module_2.interfaces import (TestService2Interface,
                                                      TestRepo2Interface)

from example_project.test_module_1.interfaces import (TestRepo1Interface,
                                                      TestService1Interface)


class TestService2(TestService2Interface):
    test_service_1: TestService1Interface
    test_repo_2: TestRepo2Interface
    test_repo_1: TestRepo1Interface

    def some_buiness_logic(self):
        self.test_repo_1.some_bd_logic()
        self.test_repo_2.some_bd_logic()
        print(f"{self.test_service_1} can be accessed")
        return super().some_buiness_logic()
