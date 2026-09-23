"""Checkpointed StudioNet lifecycle matrix. Signed writes are never silently retried."""
import base64
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from genlayer_py import create_account, create_client
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.chains import studionet

ROOT = Path(__file__).resolve().parents[1]
ADDRESS = "0x51Ae7fB61612c31931607F21f8D74be4D7E2f8BA"
RPC = "https://studio.genlayer.com/api"
SOURCE_HASH = "8c0f3431af3aa007c9a4a570ef5ee310a12210ba1b82fdfe63b7ac6e26fe8988"
OWNER, REPO = "dearmore5382", "ClauseRoute"
COMMIT = "ea3d3c260712838092e7704a62f5840281f09b52"
MANIFEST_PATH = "fixtures/happy/manifest.json"
MANIFEST_HASH = "ed90c72fd0278706bfb610de688eeeb16d9ff0d9c00d20dfa2e48ddaaacf0fe3"
POLICY = ("Read authenticated documents in precedence order. Treat court clauses limited to interim relief or "
          "award enforcement as not controlling merits. Do not decide enforceability, liability, or damages.")
PRIVATE = ROOT / ".private" / ("live-" + ADDRESS.lower() + ".json")
PUBLIC = ROOT / "verification" / ("live-" + ADDRESS.lower() + ".json")
TEST_ENV = ROOT.parent / "EvidenceBasedGrantEscrow" / ".env.lifecycle"


def rpc(method, params):
    allowed = {"eth_chainId", "eth_getBalance", "eth_getTransactionByHash", "gen_getContractCode", "gen_call"}
    if method not in allowed:
        raise RuntimeError("RPC_METHOD_NOT_ALLOWED")
    last = None
    for attempt in range(5):
        try:
            response = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=45)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise RuntimeError("RPC_ERROR:" + str(data["error"].get("message")))
            return data["result"]
        except (requests.RequestException, ValueError) as error:
            last = error
            if attempt < 4:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError("RPC_READ_UNAVAILABLE:" + str(last))


def view(method, args=None, sender="0x0000000000000000000000000000000000000001"):
    encoded = serialize([calldata.encode({"method": method, "args": args or []}), b"\x00"])
    raw = rpc("gen_call", [{"type": "read", "to": ADDRESS, "from": sender, "value": "0x0",
                            "data": encoded, "transaction_hash_variant": "latest-final"}])
    return str(calldata.decode(bytes.fromhex(raw.removeprefix("0x"))))


def load_keys():
    values = {}
    for raw in TEST_ENV.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    result = [os.environ.get("WALLET_A_PRIVATE_KEY") or values.get("WALLET_A_PRIVATE_KEY"),
              os.environ.get("WALLET_B_PRIVATE_KEY") or values.get("WALLET_B_PRIVATE_KEY")]
    if not all(result):
        raise RuntimeError("TWO_LOCAL_TEST_KEYS_REQUIRED")
    return result


def parity():
    if int(rpc("eth_chainId", []), 16) != 61999:
        raise RuntimeError("WRONG_CHAIN")
    deployed = base64.b64decode(rpc("gen_getContractCode", [ADDRESS]))
    local = (ROOT / "contracts" / "ClauseRoute.py").read_bytes()
    if deployed != local:
        raise RuntimeError("SOURCE_PARITY_FAILED")
    if hashlib.sha256(deployed).hexdigest() != SOURCE_HASH:
        raise RuntimeError("SOURCE_HASH_FAILED")


def tx_return(tx):
    receipts = (tx.get("consensus_data") or {}).get("leader_receipt") or []
    receipts = [receipts] if isinstance(receipts, dict) else receipts
    leaders = [receipt for receipt in receipts if receipt.get("mode") == "leader"]
    if not leaders or leaders[-1].get("execution_result") != "SUCCESS":
        raise RuntimeError("LEADER_EXECUTION_FAILED")
    result = leaders[-1].get("result")
    raw = base64.b64decode(result["raw"] if isinstance(result, dict) else result)
    if not raw or raw[0] != 0:
        raise RuntimeError("CONTRACT_EXECUTION_ERROR")
    return str(calldata.decode(raw[1:]))


def save(record):
    PRIVATE.parent.mkdir(exist_ok=True)
    PRIVATE.write_text(json.dumps(record, indent=2), encoding="utf-8")
    public = json.loads(json.dumps(record))
    public.pop("balances", None)
    for step in public["steps"]:
        step.pop("receipt", None)
    PUBLIC.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")


def readback(sender):
    counts = view("get_counts", sender=sender)
    authorities, cases = [int(value) for value in counts.split("|")]
    result = {"counts": counts}
    for object_id in range(authorities):
        result["authority_" + str(object_id)] = json.loads(view("get_authority", [object_id], sender))
    for object_id in range(cases):
        result["case_" + str(object_id)] = json.loads(view("get_case", [object_id], sender))
        finding = view("get_finding", [object_id], sender)
        result["finding_" + str(object_id)] = json.loads(finding) if finding else None
    return result


def main():
    secret_keys = load_keys()
    accounts = [create_account(account_private_key="0x" + key.removeprefix("0x")) for key in secret_keys]
    del secret_keys
    controller, outsider = accounts
    clients = {account.address.lower(): create_client(chain=studionet, account=account) for account in accounts}
    parity()
    balances = {account.address: int(rpc("eth_getBalance", [account.address, "latest"]), 16) for account in accounts}
    if not all(balances.values()):
        raise RuntimeError("TEST_WALLET_BALANCE_EMPTY")
    happy_case = [0, "CASE-2026-001", controller.address, outsider.address,
                  "software-services-payment", "USD-100K-250K", "SG", "DE"]
    failure_case = [0, "CASE-2026-002", controller.address, outsider.address,
                    "software-services-payment", "USD-100K-250K", "SG", "DE"]
    retry_case = [0, "CASE-2026-003", controller.address, outsider.address,
                  "software-services-payment", "USD-100K-250K", "SG", "DE"]
    plan = [
        {"id": "F1-invalid-authority", "actor": controller.address, "method": "register_authority",
         "args": ["Invalid", "bad/owner", REPO, POLICY], "allowed": ["INVALID_AUTHORITY"], "counts": "0|0"},
        {"id": "H1-register-authority", "actor": controller.address, "method": "register_authority",
         "args": ["Cross-border services panel", OWNER, REPO, POLICY], "allowed": ["0"], "counts": "1|0"},
        {"id": "A1-outsider-open", "actor": outsider.address, "method": "open_case",
         "args": happy_case, "allowed": ["CONTROLLER_ONLY"], "counts": "1|0"},
        {"id": "H2-open-happy", "actor": controller.address, "method": "open_case",
         "args": happy_case, "allowed": ["0"], "counts": "1|1"},
        {"id": "A2-outsider-attach", "actor": outsider.address, "method": "attach_document_set",
         "args": [0, COMMIT, MANIFEST_PATH, MANIFEST_HASH], "allowed": ["STEWARD_ONLY"], "counts": "1|1"},
        {"id": "F2-invalid-locator", "actor": controller.address, "method": "attach_document_set",
         "args": [0, "main", MANIFEST_PATH, MANIFEST_HASH], "allowed": ["INVALID_DOCUMENT_LOCATOR"], "counts": "1|1"},
        {"id": "H3-attach-happy", "actor": controller.address, "method": "attach_document_set",
         "args": [0, COMMIT, MANIFEST_PATH, MANIFEST_HASH], "allowed": ["DOCUMENT_SET_ATTACHED"], "counts": "1|1"},
        {"id": "A3-premature-assess", "actor": outsider.address, "method": "assess_route",
         "args": [0], "allowed": ["CASE_NOT_ASSESSABLE"], "counts": "1|1"},
        {"id": "H4-seal-happy", "actor": controller.address, "method": "seal_case",
         "args": [0], "allowed": ["CASE_SEALED"], "counts": "1|1"},
        {"id": "A4-outsider-seal", "actor": outsider.address, "method": "seal_case",
         "args": [0], "allowed": ["STEWARD_ONLY"], "counts": "1|1"},
        {"id": "H5-assess-happy", "actor": outsider.address, "method": "assess_route",
         "args": [0], "allowed": ["ARBITRATION"], "counts": "1|1"},
        {"id": "A5-assessment-replay", "actor": controller.address, "method": "assess_route",
         "args": [0], "allowed": ["CASE_NOT_ASSESSABLE"], "counts": "1|1"},
        {"id": "F3-open-integrity", "actor": controller.address, "method": "open_case",
         "args": failure_case, "allowed": ["1"], "counts": "1|2"},
        {"id": "F4-attach-wrong-digest", "actor": controller.address, "method": "attach_document_set",
         "args": [1, COMMIT, MANIFEST_PATH, "0" * 64], "allowed": ["DOCUMENT_SET_ATTACHED"], "counts": "1|2"},
        {"id": "F5-seal-integrity", "actor": controller.address, "method": "seal_case",
         "args": [1], "allowed": ["CASE_SEALED"], "counts": "1|2"},
        {"id": "F6-assess-integrity", "actor": outsider.address, "method": "assess_route",
         "args": [1], "allowed": ["DOCUMENT_SET_REJECTED"], "counts": "1|2"},
        {"id": "R1-open-retry", "actor": controller.address, "method": "open_case",
         "args": retry_case, "allowed": ["2"], "counts": "1|3"},
        {"id": "R2-attach-missing-source", "actor": controller.address, "method": "attach_document_set",
         "args": [2, COMMIT, "fixtures/happy/missing.json", "1" * 64],
         "allowed": ["DOCUMENT_SET_ATTACHED"], "counts": "1|3"},
        {"id": "R3-seal-retry", "actor": controller.address, "method": "seal_case",
         "args": [2], "allowed": ["CASE_SEALED"], "counts": "1|3"},
        {"id": "R4-assess-missing-source", "actor": outsider.address, "method": "assess_route",
         "args": [2], "allowed": ["ASSESSMENT_RETRYABLE"], "counts": "1|3"},
    ]
    if PRIVATE.exists():
        record = json.loads(PRIVATE.read_text(encoding="utf-8"))
    else:
        if view("get_counts", sender=controller.address) != "0|0":
            raise RuntimeError("EXPECTED_FRESH_CONTRACT")
        record = {"contract": ADDRESS, "network": "StudioNet", "source_sha256": SOURCE_HASH,
                  "fixture_commit": COMMIT, "fixture_manifest_sha256": MANIFEST_HASH,
                  "started_at": datetime.now(timezone.utc).isoformat(),
                  "wallets": [account.address for account in accounts], "balances": balances,
                  "steps": [], "complete": False}
        save(record)
    print(json.dumps({"ready": True, "wallets": record["wallets"],
                      "completed": len(record["steps"]), "total": len(plan)}), flush=True)
    for index, wanted in enumerate(plan):
        parity()
        if index < len(record["steps"]):
            item = record["steps"][index]
            if item["id"] != wanted["id"]:
                raise RuntimeError("JOURNAL_PLAN_MISMATCH")
            if item.get("status") == "READBACK_VERIFIED":
                continue
            if item.get("status") not in ("INTENT_SAVED", "SUBMITTED"):
                raise RuntimeError("UNKNOWN_CHECKPOINT")
        else:
            item = dict(wanted)
            item["status"] = "INTENT_SAVED"
            record["steps"].append(item)
            save(record)
        if item["status"] == "INTENT_SAVED":
            item["hash"] = str(clients[item["actor"].lower()].write_contract(
                address=ADDRESS, function_name=item["method"], args=item["args"], value=0, leader_only=False))
            item["status"] = "SUBMITTED"
            save(record)
            print(json.dumps({"step": item["id"], "hash": item["hash"], "status": "SUBMITTED"}), flush=True)
        deadline = time.monotonic() + 1200
        while time.monotonic() < deadline:
            tx = rpc("eth_getTransactionByHash", [item["hash"]])
            if tx and tx.get("status") == "FINALIZED":
                if tx.get("result_name") != "MAJORITY_AGREE":
                    raise RuntimeError("CONSENSUS_FAILED")
                actual = tx_return(tx)
                if actual not in item["allowed"]:
                    raise RuntimeError("UNEXPECTED_RETURN:" + actual)
                current = readback(controller.address)
                if current["counts"] != item["counts"]:
                    raise RuntimeError("COUNT_MISMATCH")
                if item["id"] == "H5-assess-happy":
                    case, finding = current["case_0"], current["finding_0"]
                    if case["status"] != "CLOSED" or case["route"] != "ARBITRATION" or finding["source_status"] != "VERIFIED":
                        raise RuntimeError("HAPPY_READBACK_FAILED")
                if item["id"] == "F6-assess-integrity":
                    case, finding = current["case_1"], current["finding_1"]
                    if case["status"] != "CLOSED" or case["route"] != "DOCUMENT_SET_REJECTED" or finding["source_status"] != "INTEGRITY_FAILURE":
                        raise RuntimeError("INTEGRITY_READBACK_FAILED")
                if item["id"] == "R4-assess-missing-source":
                    case = current["case_2"]
                    if case["status"] != "SEALED" or case["route"] != "UNDETERMINED" or current["finding_2"] is not None:
                        raise RuntimeError("RETRY_NO_MUTATION_FAILED")
                item.update({"actual": actual, "receipt": tx, "readback": current,
                             "status": "READBACK_VERIFIED",
                             "explorer": "https://explorer-studio.genlayer.com/tx/" + item["hash"]})
                save(record)
                print(json.dumps({"step": item["id"], "actual": actual,
                                  "counts": current["counts"]}), flush=True)
                break
            time.sleep(8)
        else:
            raise RuntimeError("POLL_TIMEOUT_KEEP_HASH")
    record["complete"] = True
    record["completed_at"] = datetime.now(timezone.utc).isoformat()
    save(record)
    print(json.dumps({"complete": True, "steps": len(plan)}), flush=True)


if __name__ == "__main__":
    main()
