import builtins
import importlib
import sys


def test_email_phishing_service_handles_missing_ai_dependencies(monkeypatch):
    sys.modules.pop("app.services.email_phishing_service", None)

    real_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("torch") or name.startswith("transformers"):
            raise ModuleNotFoundError(f"No module named '{name}'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    module = importlib.import_module("app.services.email_phishing_service")
    service = module.EmailPhishingService()

    result = service.detect_phishing("Hello world")

    assert result["is_phishing"] is False
    assert result["risk_level"] == "low"
    assert "Detection service unavailable" in result["explanations"][0]["message"]
