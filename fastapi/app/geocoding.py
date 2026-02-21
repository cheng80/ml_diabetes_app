# 주소 → lat/lng 반환 (Nominatim, 가입 불필요)
from __future__ import annotations

import time

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


class GeocodingTemporaryError(Exception):
    """Nominatim 일시 장애/지연으로 좌표 조회에 실패한 경우."""


def geocoding(address: str) -> dict[str, str] | None:
    """주소 → {"lat":, "lng":} 또는 None"""
    if not address or not address.strip():
        return None

    addr = address.strip()
    geolocator = Nominatim(user_agent="diabetes_app_kr", timeout=10)
    had_temporary_error = False

    # 1차: 원본 주소
    geo, temporary_error = _try_geocode(geolocator, addr)
    had_temporary_error = had_temporary_error or temporary_error
    if geo is not None:
        return {"lat": str(geo.latitude), "lng": str(geo.longitude)}

    # 2차: ", 대한민국" 붙여서 재시도
    if "대한민국" not in addr and "South Korea" not in addr and "Korea" not in addr:
        geo, temporary_error = _try_geocode(geolocator, f"{addr}, 대한민국")
        had_temporary_error = had_temporary_error or temporary_error
        if geo is not None:
            return {"lat": str(geo.latitude), "lng": str(geo.longitude)}

    if had_temporary_error:
        raise GeocodingTemporaryError("geocoding service temporary unavailable")

    return None


def _try_geocode(geolocator: Nominatim, query: str):
    """좌표 조회를 짧게 재시도하고, 일시 장애 여부를 함께 반환."""
    for attempt in range(2):
        try:
            return geolocator.geocode(query), False
        except (GeocoderTimedOut, GeocoderServiceError, AttributeError):
            if attempt == 0:
                time.sleep(0.6)
                continue
            return None, True
    return None, True
