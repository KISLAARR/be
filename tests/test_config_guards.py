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
    for var in ("OTP_DISABLED_ACK", "TG_VERIFY_ENABLED", "TG_BOT_TOKEN", "TG_BOT_USERNAME"):
        os.environ.pop(var, None)
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


def test_prod_mock_sms_with_tg_channel_starts(monkeypatch):
    """Telegram-канал (блок 18) — живой канал: prod с mock-СМС стартует."""
    mod = _load_settings(monkeypatch, ENVIRONMENT="production",
                         OTP_ENABLED="true", SMS_MODE="mock",
                         TG_VERIFY_ENABLED="true", TG_BOT_TOKEN="000:x",
                         TG_BOT_USERNAME="rumi_test_bot")
    assert mod.settings.TG_VERIFY_ENABLED is True


def test_tg_enabled_without_token_fails(monkeypatch):
    with pytest.raises(Exception, match="TG_BOT_TOKEN"):
        _load_settings(monkeypatch, ENVIRONMENT="development",
                       OTP_ENABLED="true", SMS_MODE="mock",
                       TG_VERIFY_ENABLED="true")


def test_cookie_secure_forced_in_prod(monkeypatch):
    mod = _load_settings(monkeypatch, ENVIRONMENT="production",
                         OTP_ENABLED="true", SMS_MODE="live", COOKIE_SECURE="false")
    assert mod.settings.COOKIE_SECURE is True
