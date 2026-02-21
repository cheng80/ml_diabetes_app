#!/usr/bin/env python3
"""NAS FastAPI health check + smoke tests.

Usage:
  python3 fastapi/smoke_test_nas.py
  python3 fastapi/smoke_test_nas.py --base-url http://host:port
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "http://cheng80.myqnapcloud.com:18002"


@dataclass
class TestResult:
    name: str
    ok: bool
    message: str


def http_get_json(url: str, timeout: int = 15) -> tuple[int, dict[str, Any]]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = resp.status
        body = json.loads(resp.read().decode("utf-8"))
        return status, body


def http_post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> tuple[int, dict[str, Any]]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = resp.status
        body = json.loads(resp.read().decode("utf-8"))
        return status, body


def assert_keys(
    input_obj: dict[str, Any],
    must_have: set[str] | None = None,
    must_not_have: set[str] | None = None,
) -> tuple[bool, str]:
    must_have = must_have or set()
    must_not_have = must_not_have or set()

    missing = sorted(list(must_have - set(input_obj.keys())))
    bad = sorted(list(must_not_have & set(input_obj.keys())))

    if missing:
        return False, f"missing keys={missing}"
    if bad:
        return False, f"unexpected keys={bad}"
    return True, "key checks passed"


def run_tests(base_url: str) -> list[TestResult]:
    results: list[TestResult] = []
    predict_url = f"{base_url.rstrip('/')}/predict"
    health_url = f"{base_url.rstrip('/')}/health"

    # 1) Health check
    try:
        status, body = http_get_json(health_url)
        ok = status == 200 and body.get("status") == "ok"
        msg = f"status={status}, api_status={body.get('status')}, model_sugar={body.get('model_sugar')}"
        results.append(TestResult("health", ok, msg))
    except urllib.error.URLError as e:
        results.append(TestResult("health", False, f"request failed: {e}"))
        return results

    # 2) KNHANES with glucose + optional F1/F2
    payload_knhanes_glu = {
        "성별": 1,
        "나이": 47,
        "키": 170,
        "BMI": 28.0,
        "허리둘레": 94.0,
        "혈당": 95,
        "가족력": 1,
        "고혈압/혈압약": 0,
    }
    try:
        status, body = http_post_json(predict_url, payload_knhanes_glu)
        input_obj = body.get("input", {})
        key_ok, key_msg = assert_keys(
            input_obj,
            must_have={"sex", "age", "height_cm", "bmi", "waist_cm", "glucose", "htn_or_med"},
            must_not_have={"family_history_dm"},
        )
        ok = status == 200 and key_ok
        msg = (
            f"status={status}, label={body.get('label')}, prob={body.get('probability')}, "
            f"used_model={body.get('used_model')}, {key_msg}"
        )
        results.append(TestResult("knhanes_with_glucose_policy", ok, msg))
    except urllib.error.URLError as e:
        results.append(TestResult("knhanes_with_glucose_policy", False, f"request failed: {e}"))

    # 3) Pima path with optional sent (must be ignored)
    payload_pima_with_optional = {
        "나이": 47,
        "BMI": 28.0,
        "혈당": 95,
        "임신횟수": 2,
        "가족력": 1,
        "고혈압/혈압약": 1,
    }
    try:
        status, body = http_post_json(predict_url, payload_pima_with_optional)
        input_obj = body.get("input", {})
        key_ok, key_msg = assert_keys(
            input_obj,
            must_have={"age", "bmi", "glucose", "pregnancies"},
            must_not_have={"family_history_dm", "htn_or_med"},
        )
        ok = status == 200 and key_ok
        msg = (
            f"status={status}, label={body.get('label')}, prob={body.get('probability')}, "
            f"used_model={body.get('used_model')}, {key_msg}"
        )
        results.append(TestResult("pima_optional_ignored_policy", ok, msg))
    except urllib.error.URLError as e:
        results.append(TestResult("pima_optional_ignored_policy", False, f"request failed: {e}"))

    # 4) KNHANES without glucose + optional F1/F2 (must include both)
    payload_knhanes_no_glu = {
        "성별": 1,
        "나이": 47,
        "키": 170,
        "BMI": 28.0,
        "허리둘레": 94.0,
        "가족력": 1,
        "고혈압/혈압약": 1,
    }
    try:
        status, body = http_post_json(predict_url, payload_knhanes_no_glu)
        input_obj = body.get("input", {})
        key_ok, key_msg = assert_keys(
            input_obj,
            must_have={"sex", "age", "height_cm", "bmi", "waist_cm", "family_history_dm", "htn_or_med"},
        )
        ok = status == 200 and key_ok
        msg = (
            f"status={status}, label={body.get('label')}, prob={body.get('probability')}, "
            f"used_model={body.get('used_model')}, {key_msg}"
        )
        results.append(TestResult("knhanes_without_glucose_policy", ok, msg))
    except urllib.error.URLError as e:
        results.append(TestResult("knhanes_without_glucose_policy", False, f"request failed: {e}"))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NAS FastAPI health and smoke tests.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL (default: %(default)s)")
    args = parser.parse_args()

    print(f"[INFO] base_url={args.base_url}")
    results = run_tests(args.base_url)

    all_ok = True
    for result in results:
        flag = "PASS" if result.ok else "FAIL"
        if not result.ok:
            all_ok = False
        print(f"[{flag}] {result.name}: {result.message}")

    if all_ok:
        print("[DONE] all tests passed")
        return 0
    print("[DONE] failures detected")
    return 1


if __name__ == "__main__":
    sys.exit(main())
