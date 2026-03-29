from django.test.runner import DiscoverRunner

class ManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models managed 
    for the duration of the test run to allow test DB creation.
    """
    def setup_test_environment(self, **kwargs):
        from django.apps import apps
        self.unmanaged_models = [m for m in apps.get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True
        super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        super().teardown_test_environment(**kwargs)
        for m in self.unmanaged_models:
            m._meta.managed = False
