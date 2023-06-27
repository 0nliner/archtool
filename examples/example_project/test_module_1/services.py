from test_module_1.interfaces import (TestService1Interface,
                                      TestRepo1Interface)

from test_module_2.interfaces import (TestRepo2Interface,
                                      TestService2Interface)


class TestService1(TestService1Interface):
    test_service_2: TestService2Interface
    test_repo_2: TestRepo2Interface
    test_repo_1: TestRepo1Interface

    def some_buiness_logic(self):
        self.test_repo_1.some_bd_logic()
        self.test_repo_2.some_bd_logic()
        print(f"{self.test_service_2} can be accessed")
        return super().some_buiness_logic()
