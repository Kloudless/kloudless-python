import kloudless

def test_configure():
    """
    This is a basic test to make sure that the configuration mechanism works.
    """
    default_configs = kloudless.config.configure()
    configs = {"api_key": "TESTKEY",
               "api_version": 31337,
               "base_url": "example.com"}
    kloudless.configure(**configs)
    for key in configs.iterkeys():
        assert configs[key] == kloudless.config._configuration[key]
    kloudless.configure(**default_configs)
