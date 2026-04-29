#!/usr/bin/env python3
"""
Backward-compatibility shim — delegates to tests/run_all.py.

The actual test suite lives in the tests/ directory:
  tests/test_health.py
  tests/test_companies.py
  tests/test_conversations.py
  tests/test_sec_filings.py
  tests/test_transcripts.py
  tests/test_db_coverage.py
  tests/test_chat_rag.py   (slow — LLM)
  tests/run_all.py         (orchestrator)

Usage (same as before):
  python test_apis.py            # all tests
  python test_apis.py --fast     # skip slow LLM tests
  python tests/run_all.py        # same thing, preferred going forward
"""
import sys
import os
import runpy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))
runpy.run_path(os.path.join(os.path.dirname(__file__), "tests", "run_all.py"), run_name="__main__")
