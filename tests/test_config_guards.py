# tests/test_config_guards.py
"""Guard'ы конфига: небезопасные сочетания OTP/SMS не должны стартовать в prod."""
import importlib
import os

import pytest


def _load_settings(monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    import app.core.config as config_mod

    return importlib.reload(config_mod)


@pytest.fixture(autouse=True)
def _restore_config():
    """После каждого теста возвращаем конфиг под тестовое окружение conftest.

    Намеренно НЕ зависит от monkeypatch: его откат происходит позже нашего
    teardown'а, поэтому валидное окружение выставляем руками до reload —
    иначе reload сам упадёт на guard'е с ещё "прод"-переменными.
    """
    yield
    os.environ.update(ENVIRONMENT="development", OTP_ENABLED="true", SMS_MODE="mock")
    os.environ.pop("OTP_DISABLED_ACK", None)
    import app.core.config as config_mod

    importlib.reload(config_mod)


def test_dev_mock_allowed(monkeypatch):
    mod = _load_settings(monkeypatch, ENVIRONMENT="development",
                         OTP_ENABLED="true", SMS_MODE="mock")
    assert mod.settings.OTP_ENABLED is True


def test_prod_otp_disabled_requires_ack(monkeypatch):
    with pytest.raises(Exception, match="OTP_ENABLED=false"):
        _load_settings(monkeypatch, ENVIRONMENT="production",
                       OTP_ENABLED="false", OTP_DISABLED_ACK="false", SMS_MODE="mock")


def test_prod_otp_disabled_with_ack_starts(monkeypatch):
    mod = _load_settings(monkeypatch, ENVIRONMENT="production",
                         OTP_ENABLED="false", OTP_DISABLED_ACK="true", SMS_MODE="mock")
    assert mod.settings.OTP_ENABLED is False


def test_prod_mock_provider_with_otp_enabled_fails(monkeypatch):
    """SMS_MODE=mock в prod при включённом OTP = раздача кодов любому -> не стартуем."""
    with pytest.raises(Exception, match="SMS_MODE=mock"):
        _load_settings(monkeypatch, ENVIRONMENT="production",
                       OTP_ENABLED="true", SMS_MODE="mock")


def test_prod_live_provider_starts(monkeypatch):
    mod = _load_settings(monkeypatch, ENVIRONMENT="production",
                         OTP_ENABLED="true", SMS_MODE="live")
    assert mod.settings.SMS_MODE == "live"


def test_cookie_secure_forced_in_prod(monkeypatch):
    mod = _load_settings(monkeypatch, ENVIRONMENT="production",
                         OTP_ENABLED="true", SMS_MODE="live", COOKIE_SECURE="false")
    assert mod.settings.COOKIE_SECURE is True
