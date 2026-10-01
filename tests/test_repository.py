import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.build import build
from tools.common.database import ValidationError, canonical_json, package, unpack
from tools.common.engine import ROOT, discover_modules, load_module, transform, validate_module_collisions, validate_output
from tools.common.repository import discover, inspect_repository, raw_url, source_database

MODULES = ("namco-system11", "taito-fx1b", "capcom-zn1")


def mock_source(config, payloads=None, head="a" * 40):
    root = config["distribution_root"]
    if payloads is None:
        mra = b'<misterromdescription><rbf>TestCore</rbf><rom zip="user-supplied.zip" /></misterromdescription>'
        payloads = {root + "/Game (World) - One.mra": mra,
                    root + "/_alternatives/_Game/Variant.mra": mra,
                    root + "/cores/Arcade-TestCore_20260102.rbf": b"synthetic-core"}
    entries = [{"path": path, "type": "blob", "mode": "100644", "size": len(data),
                "sha": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()}
               for path, data in payloads.items()]
    tree = {"truncated": False, "tree": entries}
    api = "https://api.github.com/repos/" + config["repository"]

    def fetcher(url):
        if url.startswith(api + "/commits/"):
            return canonical_json({"sha": head, "commit": {"committer": {"date": "2026-01-02T00:00:00Z"}}})
        if url.startswith(api + "/git/trees/"):
            return canonical_json(tree)
        if url.startswith(api + "/releases"):
            return b"[]"
        for path, data in payloads.items():
            if url.endswith(raw_url(config, head, path).split(head + "/", 1)[1]):
                return data
        raise AssertionError("Unexpected synthetic URL")
    return payloads, tree, fetcher


class RepositoryTests(unittest.TestCase):
    def test_initial_inspection_snapshot(self):
        snapshots = json.loads((ROOT / "tests/fixtures/xela-inspection.json").read_text())
        expected = {"namco-system11": 35, "taito-fx1b": 12, "capcom-zn1": 17}
        for name in MODULES:
            with self.subTest(module=name):
                config, policy = load_module(name)
                snapshot = snapshots[name]
                source = source_database(config, snapshot["source_commit"], snapshot["source_timestamp"], snapshot["source_files"])
                generated = transform(source, config, policy)
                report = validate_output(source, generated, config, policy)
                self.assertEqual(report["file_destinations_changed"], expected[name])
                self.assertEqual(len(generated["files"]), expected[name] + 1)
                self.assertEqual(report["effective_source_urls_changed"], 0)
                self.assertEqual(report["hashes_changed"], 0)
                self.assertNotIn("default_options", generated)
                self.assertNotIn("tag_dictionary", generated)

    def test_parameterized_discovery_and_mapping(self):
        for name in MODULES:
            with self.subTest(module=name):
                config, policy = load_module(name)
                _, _, fetcher = mock_source(config)
                source, _ = inspect_repository(config, fetcher=fetcher)
                generated = transform(source, config, policy)
                prefix = "_Arcade/" + config["target_folder"]
                self.assertIn(prefix + "/Game (World) - One.mra", generated["files"])
                self.assertIn(prefix + "/_alternatives/_Game/Variant.mra", generated["files"])
                core = "_Arcade/cores/Arcade-TestCore_20260102.rbf"
                self.assertIn(core, generated["files"])
                self.assertNotIn(prefix + "/cores", generated["folders"])
                self.assertEqual(generated["files"][core], source["files"][core])
                self.assertEqual(policy.destination("games/mame/example.zip", "files"), "games/mame/example.zip")
                self.assertEqual(transform(generated, config, policy), generated)
                self.assertEqual(package(generated), package(copy.deepcopy(generated)))

    def test_hashes_sizes_and_pinned_encoded_urls(self):
        config, policy = load_module(MODULES[0])
        payloads, _, fetcher = mock_source(config)
        source, basis = inspect_repository(config, fetcher=fetcher)
        for entry in basis["source_files"]:
            data = payloads[entry["path"]]
            self.assertEqual(entry["md5"], hashlib.md5(data).hexdigest())
            self.assertEqual(entry["size"], len(data))
        generated = transform(source, config, policy)
        record = generated["files"]["_Arcade/" + config["target_folder"] + "/Game (World) - One.mra"]
        self.assertIn("/" + "a" * 40 + "/releases/_Arcade/Game%20%28World%29%20-%20One.mra", record["url"])
        self.assertEqual(record["url"], source["files"]["_Arcade/Game (World) - One.mra"]["url"])

    def test_irrelevant_source_files_excluded(self):
        config, _ = load_module(MODULES[0])
        _, tree, _ = mock_source(config)
        for path in ("rtl/test.sv", "README.md", "art/logo.png", "project.qsf", "releases/_Arcade/README.md"):
            tree["tree"].append({"path": path, "type": "blob", "mode": "100644", "size": 1, "sha": "b" * 40})
        self.assertEqual(len(discover(config, tree)), 3)

    def test_latest_dated_core_per_family(self):
        config, _ = load_module(MODULES[0])
        _, tree, _ = mock_source(config)
        original = next(e for e in tree["tree"] if e["path"].endswith(".rbf"))
        tree["tree"].append({**original, "path": original["path"].replace("20260102", "20260103")})
        selected = discover(config, tree)
        self.assertEqual([e["path"] for e in selected if e["path"].endswith(".rbf")],
                         [original["path"].replace("20260102", "20260103")])

    def test_normal_additions_and_removals(self):
        config, _ = load_module(MODULES[0])
        payloads, _, _ = mock_source(config)
        root = config["distribution_root"]
        payloads[root + "/New Game.mra"] = next(data for path, data in payloads.items() if path.endswith(".mra"))
        _, _, fetcher = mock_source(config, payloads)
        source, _ = inspect_repository(config, fetcher=fetcher)
        self.assertEqual(len(source["files"]), 4)
        payloads.pop(root + "/New Game.mra")
        payloads.pop(root + "/_alternatives/_Game/Variant.mra")
        _, _, fetcher = mock_source(config, payloads)
        source, _ = inspect_repository(config, fetcher=fetcher)
        self.assertEqual(len(source["files"]), 2)

    def test_changed_payload_hash_size_and_core_filename(self):
        config, _ = load_module(MODULES[0])
        payloads, _, fetcher = mock_source(config)
        before, _ = inspect_repository(config, fetcher=fetcher)
        root = config["distribution_root"]
        payloads.pop(root + "/cores/Arcade-TestCore_20260102.rbf")
        payloads[root + "/cores/Arcade-TestCore_20260103.rbf"] = b"changed-synthetic-core"
        _, _, fetcher = mock_source(config, payloads, head="b" * 40)
        after, _ = inspect_repository(config, fetcher=fetcher)
        old = before["files"]["_Arcade/cores/Arcade-TestCore_20260102.rbf"]
        new = after["files"]["_Arcade/cores/Arcade-TestCore_20260103.rbf"]
        self.assertNotEqual(old["hash"], new["hash"])
        self.assertNotEqual(old["size"], new["size"])
        self.assertEqual(old["tangle"], new["tangle"])

    def test_irrelevant_commit_reuses_verified_payload_revision(self):
        config, policy = load_module(MODULES[0])
        _, _, fetcher = mock_source(config)
        before, basis = inspect_repository(config, fetcher=fetcher)
        _, _, changed_fetcher = mock_source(config, head="b" * 40)
        after, after_basis = inspect_repository(config, previous=basis, fetcher=changed_fetcher)
        self.assertEqual(before, after)
        self.assertEqual(basis, after_basis)
        self.assertEqual(package(transform(before, config, policy)), package(transform(after, config, policy)))

    def test_duplicate_paths_rejected(self):
        config, _ = load_module(MODULES[0])
        _, tree, _ = mock_source(config)
        tree["tree"].append(copy.deepcopy(tree["tree"][0]))
        with self.assertRaisesRegex(ValidationError, "Duplicate"):
            discover(config, tree)

    def test_structural_changes_fail_closed(self):
        config, _ = load_module(MODULES[0])
        _, original, _ = mock_source(config)
        variants = []
        tree = copy.deepcopy(original); tree["truncated"] = True; variants.append(tree)
        tree = copy.deepcopy(original); tree["tree"] = []; variants.append(tree)
        tree = copy.deepcopy(original); tree["tree"][0]["mode"] = "120000"; variants.append(tree)
        tree = copy.deepcopy(original); tree["tree"][0]["path"] = "releases/_Arcade/../bad.mra"; variants.append(tree)
        tree = copy.deepcopy(original); tree["tree"][-1]["path"] = "releases/_Arcade/Bad.rbf"; variants.append(tree)
        tree = copy.deepcopy(original); tree["tree"][-1]["path"] = "releases/_Arcade/cores/unknown.rbf"; variants.append(tree)
        tree = copy.deepcopy(original); tree["tree"].append({"path": "db.json"}); variants.append(tree)
        tree = copy.deepcopy(original); tree["tree"].append({"path": "releases/_Arcade/runtime.bin", "type": "blob", "mode": "100644"}); variants.append(tree)
        for tree in variants:
            with self.subTest(tree=tree), self.assertRaises(ValidationError):
                discover(config, tree)

    def test_wrong_payload_size_and_blob_rejected(self):
        config, _ = load_module(MODULES[0])
        _, _, fetcher = mock_source(config)
        for preserve_size in (False, True):
            def corrupt(url):
                data = fetcher(url)
                if url.endswith(".rbf"):
                    return b"x" * len(data) if preserve_size else b"wrong"
                return data
            with self.subTest(preserve_size=preserve_size), self.assertRaises(ValidationError):
                inspect_repository(config, fetcher=corrupt)

    def test_new_core_family_and_source_destination_collision(self):
        config, policy = load_module(MODULES[0])
        payloads, _, _ = mock_source(config)
        root = config["distribution_root"]
        payloads[root + "/cores/Arcade-SecondCore_20260103.rbf"] = b"second-synthetic-core"
        payloads[root + "/Second Game.mra"] = b'<misterromdescription><rbf>SecondCore</rbf></misterromdescription>'
        _, _, fetcher = mock_source(config, payloads)
        source, _ = inspect_repository(config, fetcher=fetcher)
        self.assertEqual(sum(path.endswith(".rbf") for path in source["files"]), 2)
        payloads[root + "/" + config["target_folder"] + "/Game (World) - One.mra"] = payloads[root + "/Game (World) - One.mra"]
        _, _, fetcher = mock_source(config, payloads)
        source, _ = inspect_repository(config, fetcher=fetcher)
        with self.assertRaisesRegex(ValidationError, "collision"):
            transform(source, config, policy)

    def test_lfs_pointer_not_installed_as_core(self):
        config, _ = load_module(MODULES[0])
        payloads, _, _ = mock_source(config)
        path = next(path for path in payloads if path.endswith(".rbf"))
        payloads[path] = b'version https://git-lfs.github.com/spec/v1\noid sha256:example\nsize 100\n'
        _, _, fetcher = mock_source(config, payloads)
        with self.assertRaisesRegex(ValidationError, "Git LFS"):
            inspect_repository(config, fetcher=fetcher)

    def test_missing_core_reference_and_malformed_mra_rejected(self):
        config, _ = load_module(MODULES[0])
        for payload in (b'<misterromdescription><rbf>Missing</rbf></misterromdescription>',
                        b'<misterromdescription>', b'<!DOCTYPE x><misterromdescription><rbf>TestCore</rbf></misterromdescription>'):
            payloads, _, _ = mock_source(config)
            for path in list(payloads):
                if path.endswith(".mra"):
                    payloads[path] = payload
            _, _, fetcher = mock_source(config, payloads)
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                inspect_repository(config, fetcher=fetcher)

    def test_github_assets_require_review(self):
        config, _ = load_module(MODULES[0])
        _, _, fetcher = mock_source(config)
        def assets(url):
            return b'[{"assets":[{"name":"distribution.zip"}]}]' if "/releases?" in url else fetcher(url)
        with self.assertRaises(ValidationError):
            inspect_repository(config, fetcher=assets)

    def test_double_prefix_and_core_misplacement(self):
        for name in MODULES:
            config, policy = load_module(name)
            prefix = "_Arcade/" + config["target_folder"]
            with self.subTest(module=name), self.assertRaises(ValidationError):
                policy.destination(prefix + "/" + config["target_folder"] + "/Game.mra", "files")
            _, _, fetcher = mock_source(config)
            source, _ = inspect_repository(config, fetcher=fetcher)
            core = "_Arcade/cores/Arcade-TestCore_20260102.rbf"
            source["files"][prefix + "/cores/Arcade-TestCore_20260102.rbf"] = source["files"].pop(core)
            with self.assertRaises(ValidationError):
                transform(source, config, policy)

    def test_cross_module_core_collisions_and_identical_content(self):
        first = {"files": {"_Arcade/cores/example.rbf": {"hash": "a" * 32, "size": 1}}, "folders": {}}
        same = copy.deepcopy(first)
        validate_module_collisions([first, same])
        same["files"]["_Arcade/cores/example.rbf"]["hash"] = "b" * 32
        with self.assertRaises(ValidationError):
            validate_module_collisions([first, same])
        with self.assertRaises(ValidationError):
            validate_module_collisions([first, {"files": {}, "folders": {"_Arcade/cores/example.rbf": {}}}])

    def test_module_and_artifact_uniqueness_and_external_exception(self):
        configs = [load_module(name)[0] for name in discover_modules()]
        self.assertEqual(len({config["derived_db_id"].casefold() for config in configs}), len(configs))
        self.assertEqual(len({config["name"] + ".json.zip" for config in configs}), len(configs))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "modules" / MODULES[0]
            directory.mkdir(parents=True)
            config = json.loads((ROOT / "modules" / MODULES[0] / "module.json").read_text())
            config["allow_external_repository"] = False
            (directory / "module.json").write_text(json.dumps(config))
            with self.assertRaisesRegex(ValidationError, "explicit exception"):
                load_module(MODULES[0], temporary)

    def test_repository_build_failure_preserves_last_good(self):
        config, _ = load_module(MODULES[0])
        _, _, fetcher = mock_source(config)
        source, basis = inspect_repository(config, fetcher=fetcher)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with patch("tools.build.inspect_repository", return_value=(source, basis)):
                self.assertTrue(build(MODULES[0], output_root=directory)["changed"])
                self.assertFalse(build(MODULES[0], output_root=directory)["changed"])
            before = {path.name: path.read_bytes() for path in directory.iterdir()}
            with patch("tools.build.inspect_repository", side_effect=ValidationError("Unsafe layout")):
                with self.assertRaises(ValidationError):
                    build(MODULES[0], output_root=directory)
            self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})
            self.assertEqual(unpack((directory / (MODULES[0] + ".json.zip")).read_bytes())["db_id"], config["derived_db_id"])


if __name__ == "__main__":
    unittest.main()
