from functools import lru_cache
import hrpay
from app.core.config import settings

# L'API HR-Skills Pay exige le préfixe /sandbox pour les clés de test,
# malgré ce qu'indique la documentation du SDK (constaté en test réel,
# HTTP 403 "sandbox_path_required" sans ce préfixe).
_BASE_URL_PRODUCTION = "https://api.hrskills-pay.com"
_BASE_URL_SANDBOX = "https://api.hrskills-pay.com/sandbox"


@lru_cache
def get_client() -> hrpay.HRPayClient:
    est_sandbox = "_test_" in settings.HRPAY_PUBLIC_KEY
    return hrpay.HRPayClient(
        settings.HRPAY_PUBLIC_KEY,
        settings.HRPAY_SECRET_KEY,
        base_url=_BASE_URL_SANDBOX if est_sandbox else _BASE_URL_PRODUCTION,
    )


_DEVISE_PAR_PAYS = {info.country.value: info.currency.value for info in hrpay.operators_by_country()}


def devise_pour_pays(country: str) -> str | None:
    return _DEVISE_PAR_PAYS.get(country.upper())
