from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "contracts" / "ClauseRoute.py").read_text(encoding="utf-8")


def test_contract_derives_pinned_github_origin_and_hashes_every_document():
    assert "https://raw.githubusercontent.com/" in SOURCE
    assert 'gl.nondet.web.request(url, method="GET")' in SOURCE
    assert "hashlib.sha256(manifest_bytes).hexdigest()" in SOURCE
    assert "hashlib.sha256(body).hexdigest()" in SOURCE
    assert "gl.vm.run_nondet_unsafe" in SOURCE


def test_no_money_frontend_or_arbitrary_url_surface():
    assert "gl.message.value" not in SOURCE
    assert "emit_transfer" not in SOURCE
    assert "manifest_url: str" not in SOURCE
    assert "genlayer-js" not in SOURCE


def test_case_capsule_surface_is_present():
    for method in ("register_authority", "open_case", "attach_document_set", "seal_case",
                   "assess_route", "get_authority", "get_case", "get_finding", "get_counts"):
        assert f"def {method}(" in SOURCE


def test_ai_cannot_return_final_route():
    assert "Do not return prose" in SOURCE
    assert "Do not decide legal enforceability" in SOURCE
    assert "def _derive(observation" in SOURCE
    for verdict in ("ARBITRATION", "COURT", "NEGOTIATION_FIRST", "CONFLICTING_CLAUSES",
                    "NO_DOCUMENTED_ROUTE", "INSUFFICIENT_EVIDENCE"):
        assert verdict in SOURCE
