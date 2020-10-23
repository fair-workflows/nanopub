def pytest_addoption(parser):
    parser.addoption('--no_rsa_key', action='store_true', default=False,
                     help="enable no_rsa_key decorated tests")


def pytest_configure(config):
    if not config.option.no_rsa_key:
        setattr(config.option, 'markexpr', 'not no_rsa_key')
