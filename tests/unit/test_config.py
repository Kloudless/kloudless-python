import helpers

import sdk

def test_configure():
    """
    This is a basic test to make sure that the configuration mechanism works.
    """
    default_configs = sdk.config.configure()
    configs = {"api_key": "TESTKEY",
               "api_version": 31337,
               "base_url": "example.com"}
    sdk.configure(**configs)
    for key in configs.iterkeys():
        assert configs[key] == sdk.config._configuration[key]
    sdk.configure(**default_configs)
