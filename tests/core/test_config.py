from fauth.core import AuthConfig


def test_auth_config_defaults(default_config: AuthConfig) -> None:
    assert default_config.secret_key == "mysecret"
    assert default_config.algorithm == "HS256"
    assert default_config.access_token_expire_minutes == 15
    assert default_config.refresh_token_expire_minutes == 10080  # 60 * 24 * 7
    assert default_config.token_type == "bearer"


def test_auth_config_overrides(custom_config: AuthConfig) -> None:
    assert custom_config.secret_key == "newsecret"
    assert custom_config.algorithm == "RS256"
    assert custom_config.access_token_expire_minutes == 5
    assert custom_config.refresh_token_expire_minutes == 1440
