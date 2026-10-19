import ast
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from types import SimpleNamespace
import pytest

TREE = ast.parse(Path("contracts/CoalitionEvidenceAttribution.py").read_text())
NS = {"json": json, "hashlib": hashlib, "re": re, "LIMIT": 5000,
      "LABELS": ("SUPPORT", "REFUTE", "NEITHER", "UNKNOWN"), "UTILITY": {"SUPPORT": 1, "REFUTE": -1, "NEITHER": 0}}
exec(compile(ast.Module(body=[x for x in TREE.body if isinstance(x, ast.FunctionDef)], type_ignores=[]), "actual-helpers", "exec"), NS)
CLAIM = "Every stored archive is encrypted at rest and deleted after thirty days."
BODIES = [Path("examples/" + x + ".txt").read_bytes() for x in ("encryption", "deletion", "ambiguity")]
SOURCE = "\n".join("ehsandto/coalition-evidence-attribution/" + "a" * 40 + "/examples/" + name + ".txt|" + hashlib.sha256(body).hexdigest()
                   for name, body in zip(("encryption", "deletion", "ambiguity"), BODIES))


def model(labels):
    return json.dumps({"coalitions": [{"mask": i, "label": label} for i, label in enumerate(labels, 1)]})


def setup(vm, labels=("NEITHER", "NEITHER", "SUPPORT"), sources=None):
    vm.clear_mocks()
    specs = NS["sources_from_text"](sources or "\n".join(SOURCE.splitlines()[:2]))
    for spec, body in zip(specs, BODIES):
        vm.mock_web(re.escape(spec["url"]), {"response": {"status": 200, "headers": {}, "body": body}, "method": "GET"})
    vm.mock_llm(r"(?s).*COALITION EVIDENCE ATTRIBUTION.*", model(labels))


@pytest.fixture
def contract(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    return direct_deploy("contracts/CoalitionEvidenceAttribution.py")


def open_case(c, nonce="demo", sources=None):
    key = c.open_case(nonce, CLAIM, sources or "\n".join(SOURCE.splitlines()[:2]))
    return key, c.get_case(key)["input_root"]


def test_complementary_sources_and_permissionless_resolution(contract, direct_vm, direct_bob):
    from genlayer import Address
    key, root = open_case(contract)
    before = contract.get_case(key)
    setup(direct_vm)
    direct_vm.sender = Address(str(direct_bob))
    contract.resolve(key, root)
    record = contract.get_resolution(key)
    assert record["output"]["status"] == "EXACT"
    assert [(x["lower"], x["upper"], x["denominator"]) for x in record["output"]["intervals"]] == [(1, 1, 2), (1, 1, 2)]
    assert record["report"]["labels"] == ["NEITHER", "NEITHER", "NEITHER", "SUPPORT"]
    body = {k: v for k, v in record.items() if k != "root"}
    assert NS["digest"](body) == record["root"]
    assert before == contract.get_case(key)
    assert contract.exact_attribution(key, root)["root"] == record["root"]
    with direct_vm.expect_revert("No exact attribution"):
        contract.exact_attribution(key, "f" * 64)


def test_unknown_never_gets_point_credit(contract, direct_vm):
    key, root = open_case(contract)
    setup(direct_vm, ["NEITHER", "UNKNOWN", "UNKNOWN"])
    contract.resolve(key, root)
    result = contract.get_resolution(key)
    assert result["output"]["status"] == "BOUNDED"
    assert any(x["lower"] != x["upper"] for x in result["output"]["intervals"])
    with direct_vm.expect_revert("No exact attribution"):
        contract.exact_attribution(key, root)


def test_negative_attribution_not_clamped():
    output = NS["attribution"](["NEITHER", "NEITHER", "REFUTE", "REFUTE"], 2)
    assert [x["lower"] for x in output["intervals"]] == [0, -2]
    assert sum(x["lower"] for x in output["intervals"]) == -2


def test_every_exact_two_and_three_source_table_conserves_efficiency():
    cases = 0
    for n in (2, 3):
        for tail in itertools.product(("SUPPORT", "REFUTE", "NEITHER"), repeat=(1 << n) - 1):
            result = NS["attribution"](["NEITHER", *tail], n)
            assert result["status"] == "EXACT"
            assert sum(x["lower"] for x in result["intervals"]) == NS["UTILITY"][tail[-1]] * math.factorial(n)
            assert all(x["lower"] == x["upper"] for x in result["intervals"])
            cases += 1
    assert cases == 2214


def test_all_two_source_interval_tables_enclose_every_completion():
    cases = 0
    for labels in itertools.product(NS["LABELS"], repeat=3):
        table = ["NEITHER", *labels]
        bounded = NS["attribution"](table, 2)["intervals"]
        unknown = [i for i, x in enumerate(table) if x == "UNKNOWN"]
        endpoints = [[] for _ in range(2)]
        for replacement in itertools.product(("SUPPORT", "REFUTE", "NEITHER"), repeat=len(unknown)):
            complete = list(table)
            for i, value in zip(unknown, replacement):
                complete[i] = value
            exact = NS["attribution"](complete, 2)["intervals"]
            for i in range(2):
                value = exact[i]["lower"]
                assert bounded[i]["lower"] <= value <= bounded[i]["upper"]
                endpoints[i].append(value)
            cases += 1
        for interval, values in zip(bounded, endpoints):
            assert interval["lower"] == min(values) and interval["upper"] == max(values)
    assert cases == 216


def test_symmetry_and_dummy_source():
    symmetric = NS["attribution"](["NEITHER"] + ["SUPPORT"] * 7, 3)
    assert [x["lower"] for x in symmetric["intervals"]] == [2, 2, 2]
    # Only source zero affects utility; the others are dummy players.
    labels = ["SUPPORT" if mask & 1 else "NEITHER" for mask in range(8)]
    result = NS["attribution"](labels, 3)
    assert [x["lower"] for x in result["intervals"]] == [6, 0, 0]


def test_three_source_permutation_equivariance():
    labels = ["NEITHER", "SUPPORT", "REFUTE", "UNKNOWN", "NEITHER", "SUPPORT", "REFUTE", "UNKNOWN"]
    original = NS["attribution"](labels, 3)["intervals"]
    for permutation in itertools.permutations(range(3)):
        permuted = []
        for mask in range(8):
            old_mask = sum(1 << permutation[i] for i in range(3) if mask & (1 << i))
            permuted.append(labels[old_mask])
        result = NS["attribution"](permuted, 3)["intervals"]
        for i in range(3):
            assert (result[i]["lower"], result[i]["upper"]) == (original[permutation[i]]["lower"], original[permutation[i]]["upper"])


@pytest.mark.parametrize("bad", ["{}", '{"coalitions":[]}', model(["SUPPORT"]),
    '{"coalitions":[{"mask":true,"label":"SUPPORT"},{"mask":2,"label":"NEITHER"},{"mask":3,"label":"SUPPORT"}]}',
    model(["YES", "NEITHER", "SUPPORT"]), model(["SUPPORT", "NEITHER", "SUPPORT"])[:-1] + ',"coalitions":[]}'])
def test_malformed_model_aborts_without_result(contract, direct_vm, bad):
    key, root = open_case(contract)
    setup(direct_vm)
    direct_vm.clear_mocks()
    for spec, body in zip(NS["sources_from_text"]("\n".join(SOURCE.splitlines()[:2])), BODIES):
        direct_vm.mock_web(re.escape(spec["url"]), {"response": {"status": 200, "headers": {}, "body": body}, "method": "GET"})
    direct_vm.mock_llm(r"(?s).*COALITION EVIDENCE ATTRIBUTION.*", bad)
    with direct_vm.expect_revert("Malformed coalition labels"):
        contract.resolve(key, root)
    with direct_vm.expect_revert("Unresolved case"):
        contract.get_resolution(key)


@pytest.mark.parametrize("kind", ["HASH_MISMATCH", "HTTP_ERROR", "SIZE_ERROR", "ENCODING_ERROR", "TEXT_ERROR"])
def test_failed_evidence_held_without_attribution(contract, direct_vm, kind):
    key, root = open_case(contract)
    specs = NS["sources_from_text"]("\n".join(SOURCE.splitlines()[:2]))
    direct_vm.clear_mocks()
    bad = {"HASH_MISMATCH": b"uncommitted different body", "HTTP_ERROR": b"not found", "SIZE_ERROR": b"a" * 5001,
           "ENCODING_ERROR": b"\xff", "TEXT_ERROR": b"\x00"}[kind]
    direct_vm.mock_web(re.escape(specs[0]["url"]), {"response": {"status": 404 if kind == "HTTP_ERROR" else 200, "headers": {}, "body": bad}, "method": "GET"})
    direct_vm.mock_web(re.escape(specs[1]["url"]), {"response": {"status": 200, "headers": {}, "body": BODIES[1]}, "method": "GET"})
    contract.resolve(key, root)
    record = contract.get_resolution(key)
    assert record["output"]["status"] == "HELD" and record["output"]["intervals"] == []
    assert record["report"]["sources"][0]["status"] == kind
    assert record["report"]["labels"] == ["NEITHER", "UNKNOWN", "UNKNOWN", "UNKNOWN"]
    with direct_vm.expect_revert("No exact attribution"):
        contract.exact_attribution(key, root)


def test_normalized_duplicate_held(contract, direct_vm):
    bodies = [b"Identical  content.\n", b"Identical content."]
    specs = NS["sources_from_text"]("\n".join(SOURCE.splitlines()[:2]))
    for spec, body in zip(specs, bodies):
        spec["sha256"] = hashlib.sha256(body).hexdigest()
    source_text = "\n".join(x["url"].split("https://raw.githubusercontent.com/")[1] + "|" + x["sha256"] for x in specs)
    key, root = open_case(contract, sources=source_text)
    for spec, body in zip(specs, bodies):
        direct_vm.mock_web(re.escape(spec["url"]), {"response": {"status": 200, "headers": {}, "body": body}, "method": "GET"})
    contract.resolve(key, root)
    assert contract.get_resolution(key)["output"] == {"status": "HELD", "intervals": [], "reason": "DUPLICATE", "document_attribution_only": True}


def test_replay_and_root_fencing(contract, direct_vm):
    key, root = open_case(contract)
    with direct_vm.expect_revert("Nonce used"):
        open_case(contract)
    with direct_vm.expect_revert("Input root mismatch"):
        contract.resolve(key, "f" * 64)
    setup(direct_vm)
    contract.resolve(key, root)
    before = contract.get_resolution(key)
    with direct_vm.expect_revert("Already resolved"):
        contract.resolve(key, root)
    assert before == contract.get_resolution(key)


def test_cross_case_binding(contract, direct_vm):
    a, ar = open_case(contract, "one")
    b, br = open_case(contract, "two")
    assert ar != br
    with direct_vm.expect_revert("Input root mismatch"):
        contract.resolve(b, ar)
    setup(direct_vm)
    contract.resolve(a, ar)
    with direct_vm.expect_revert("Unresolved case"):
        contract.get_resolution(b)


@pytest.mark.parametrize("bad", ["", SOURCE.splitlines()[0], SOURCE + "\n" + SOURCE.splitlines()[0],
    SOURCE.replace("examples/encryption.txt", "../encryption.txt"), SOURCE.replace("a" * 40, "main"),
    SOURCE.replace("examples/encryption.txt", "examples/encryption.txt?token=x")])
def test_invalid_source_specification(contract, direct_vm, bad):
    with direct_vm.expect_revert("Invalid source specification"):
        contract.open_case("bad", CLAIM, bad)


def callback_tree():
    cls = next(x for x in TREE.body if isinstance(x, ast.ClassDef))
    resolve = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == "resolve")
    return next(x for x in resolve.body if isinstance(x, ast.FunctionDef) and x.name == "validator")


def test_actual_callback_independently_reobserves_and_rejects_substitution():
    specs = NS["sources_from_text"]("\n".join(SOURCE.splitlines()[:2]))
    rows = []
    for spec, body in zip(specs, BODIES):
        text = body.decode()
        rows.append({"url": spec["url"], "http": 200, "status": "OK", "body": text,
                     "hash": spec["sha256"], "fingerprint": hashlib.sha256(" ".join(text.split()).encode()).hexdigest()})
    binding = {"case": "case-a", "input_root": "root-a"}
    original = {"binding": binding, "sources": rows, "acquisition": "READY", "labels": ["NEITHER", "NEITHER", "NEITHER", "SUPPORT"]}
    class Return:
        def __init__(self, value):
            self.calldata = value
    calls = []
    def observe():
        calls.append(True)
        return json.loads(json.dumps(original))
    env = {**NS, "binding": binding, "spec": {"sources": specs}, "observe": observe,
           "gl": SimpleNamespace(vm=SimpleNamespace(Return=Return))}
    exec(compile(ast.Module(body=[callback_tree()], type_ignores=[]), "actual-validator", "exec"), env)
    validator = env["validator"]
    assert validator(Return(original)) and len(calls) == 1
    forged = json.loads(json.dumps(original));forged["labels"][3] = "REFUTE"
    assert not validator(Return(forged)) and len(calls) == 2
    forged = json.loads(json.dumps(original));forged["binding"]["case"] = "case-b"
    assert not validator(Return(forged))
    forged = json.loads(json.dumps(original));forged["sources"][0]["body"] = "substituted"
    assert not validator(Return(forged))
    assert not validator(object())


def test_post_consensus_forgery_rejected(contract, direct_vm, monkeypatch):
    from genlayer import gl
    key, root = open_case(contract)
    setup(direct_vm)
    def forged(leader, validator):
        report = json.loads(json.dumps(leader()))
        report["sources"][0]["status"] = "HASH_MISMATCH"
        return report
    monkeypatch.setattr(gl.vm, "run_nondet_unsafe", forged)
    with direct_vm.expect_revert("Invalid consensus report"):
        contract.resolve(key, root)


def test_source_failure_cannot_be_promoted():
    specs = NS["sources_from_text"]("\n".join(SOURCE.splitlines()[:2]))
    rows = [{"url": x["url"], "http": 0, "status": "UNAVAILABLE", "body": "", "hash": "", "fingerprint": ""} for x in specs]
    report = {"binding": {}, "sources": rows, "acquisition": "HELD", "labels": ["NEITHER", "SUPPORT", "SUPPORT", "SUPPORT"]}
    with pytest.raises(ValueError, match="promoted"):
        NS["check_report"](report, {}, specs)


def test_three_source_whole_coalition_coverage(contract, direct_vm):
    key, root = open_case(contract, sources=SOURCE)
    setup(direct_vm, ["NEITHER", "NEITHER", "SUPPORT", "NEITHER", "NEITHER", "NEITHER", "UNKNOWN"], SOURCE)
    contract.resolve(key, root)
    record = contract.get_resolution(key)
    assert len(record["report"]["labels"]) == 8
    assert record["output"]["status"] == "BOUNDED"
    assert len(record["output"]["intervals"]) == 3
    assert all(x["denominator"] == 6 for x in record["output"]["intervals"])
    with direct_vm.expect_revert("No exact attribution"):
        contract.exact_attribution(key, root)


@pytest.mark.parametrize("claim", ["too short", " leading claim with invalid whitespace", "valid-looking claim\nwith newline", "x" * 501])
def test_claim_bounds(contract, direct_vm, claim):
    with direct_vm.expect_revert("Invalid nonce/claim"):
        contract.open_case("invalid", claim, "\n".join(SOURCE.splitlines()[:2]))


def test_creator_limit_and_unknown_reads(contract, direct_vm):
    for i in range(32):
        open_case(contract, "case-" + str(i))
    with direct_vm.expect_revert("Creator limit"):
        open_case(contract, "overflow")
    with direct_vm.expect_revert("Unknown case"):
        contract.get_case("f" * 64)
    with direct_vm.expect_revert("Unknown case"):
        contract.resolve("f" * 64, "e" * 64)


def test_prompt_contains_bodies_and_every_coalition_not_credit_targets():
    prompt = NS["coalition_prompt"](CLAIM, [{"body": x.decode()} for x in BODIES])
    data = json.loads(prompt.split("DATA=", 1)[1])
    assert data["documents"] == [x.decode() for x in BODIES]
    assert [x["mask"] for x in data["coalitions"]] == list(range(1, 8))
    assert data["coalitions"][-1]["source_indexes"] == [0, 1, 2]
    assert set(data) == {"claim", "documents", "coalitions"}
