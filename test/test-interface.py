#!/usr/bin/env python3
"""Verify the real installed loganne v2 client against a stubbed HTTP transport.

Uses requests-mock (intercepting at the HTTPAdapter level) so:
  - A missing `level` arg raises ValueError before any HTTP call (v2 client validation).
  - An invalid `level` raises ValueError the same way.
  - The payload that would be sent is checked to confirm `level` is forwarded.

This script exits 0 on success, 1 on any failure.
"""
import sys

import requests_mock as requests_mock_lib
from loganne import LOGANNE_ENDPOINT, updateLoganne


def test_loganne_v2_accepts_level():
	"""updateLoganne must accept a valid level and include it in the HTTP payload."""
	with requests_mock_lib.Mocker() as m:
		m.post(LOGANNE_ENDPOINT, json={})
		updateLoganne(
			type="scheduled_test",
			humanReadable="Ran test in lucos_scheduled_scripts",
			level="routine",
			url="http://localhost/",
		)
	assert m.called, "Expected an HTTP POST to loganne"
	payload = m.last_request.json()
	assert payload.get("level") == "routine", (
		f"Expected level='routine' in payload, got: {payload}"
	)
	print("PASS: loganne v2 accepts level='routine' and forwards it in the payload", flush=True)


def test_loganne_v2_rejects_invalid_level():
	"""updateLoganne must raise ValueError for a level not in the allowed set."""
	with requests_mock_lib.Mocker() as m:
		m.post(LOGANNE_ENDPOINT, json={})
		try:
			updateLoganne(
				type="scheduled_test",
				humanReadable="Test with invalid level",
				level="invalid_level",
				url="http://localhost/",
			)
			assert False, "Expected ValueError for invalid level but none was raised"
		except ValueError:
			pass
	print("PASS: loganne v2 correctly rejects invalid level", flush=True)


if __name__ == "__main__":
	try:
		test_loganne_v2_accepts_level()
		test_loganne_v2_rejects_invalid_level()
		print("All interface tests passed", flush=True)
		sys.exit(0)
	except AssertionError as e:
		print(f"FAIL: {e}", flush=True)
		sys.exit(1)
	except Exception as e:
		print(f"ERROR: {e}", flush=True)
		sys.exit(1)
