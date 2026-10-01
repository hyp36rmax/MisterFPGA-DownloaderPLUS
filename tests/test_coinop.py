import copy
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.build import build
from tools.common.database import ValidationError, digest, package, parse_json, unpack
from tools.common.engine import ROOT, discover_modules, load_module, transform, validate_output

FIXTURE = ROOT / "tests" / "fixtures" / "coinop-2026-09-30.db.json.zip"


class CoinOpTests(unittest.TestCase):
    def setUp(self):
        self.config, self.policy = load_module("coinop-collection")
        self.upstream = unpack(FIXTURE.read_bytes())
        self.generated = transform(self.upstream, self.config, self.policy)

    def test_inspected_snapshot_acceptance(self):
        self.assertEqual(digest(FIXTURE.read_bytes()),
                         "251c2b9ad771b799754e7c1fa6b1f398a97e9015531ae7c12f3388cb8d1eec57")
        report = validate_output(self.upstream, self.generated, self.config, self.policy)
        self.assertEqual(report, {
            "upstream_files": 332, "generated_files": 332,
            "upstream_folders": 76, "generated_folders": 76,
            "file_destinations_changed": 332, "folder_destinations_changed": 73,
            "non_arcade_destinations_changed": 0, "effective_source_urls_changed": 0,
            "url_fields_materialized": 332, "hashes_changed": 0, "sizes_changed": 0,
            "tags_changed": 0, "tangles_changed": 0, "unexpected_metadata_differences": 0,
            "approved_db_id_changes": 1,
        })

    def test_exact_paths_and_complete_suffix(self):
        pairs = {
            "_Arcade/foo.mra": "_Arcade/_Coin-Op Collection/foo.mra",
            "_Arcade/_alternatives/_A Game/foo.mra": "_Arcade/_Coin-Op Collection/_alternatives/_A Game/foo.mra",
            "_Arcade/cores/a_20260101.rbf": "_Arcade/_Coin-Op Collection/cores/a_20260101.rbf",
            "_ArcadeExtra/foo.mra": "_ArcadeExtra/foo.mra",
        }
        for original, target in pairs.items():
            with self.subTest(path=original):
                self.assertEqual(self.policy.destination(original, "files"), target)
        self.assertEqual(self.policy.destination("_Arcade", "folders"), "_Arcade/_Coin-Op Collection")

    def test_non_arcade_records_are_identical(self):
        for path in ("games", "games/hbmame", "games/mame"):
            self.assertEqual(self.generated["folders"][path], self.upstream["folders"][path])
            self.assertEqual(self.generated["folders"][path]["path"], "pext")
        original = "games/mame/example.zip"
        self.upstream["files"][original] = {"hash": "a" * 32, "size": 0, "tags": [101]}
        result = transform(self.upstream, self.config, self.policy)
        self.assertEqual(result["files"][original], self.upstream["files"][original])

    def test_url_encoding_matches_downloader(self):
        original = "_Arcade/A game (Japan)'s + #%é.mra"
        record = {"hash": "b" * 32, "size": 2, "tags": [18]}
        self.upstream["files"][original] = record
        result = transform(self.upstream, self.config, self.policy)
        expected = self.upstream["base_files_url"] + "_Arcade/A%20game%20%28Japan%29%27s%20%2B%20%23%25%C3%A9.mra"
        self.assertEqual(result["files"][self.policy.destination(original, "files")]["url"], expected)

    def test_explicit_source_preserved(self):
        original = next(iter(self.upstream["files"]))
        url = "https://example.org/immutable/file.mra?revision=1"
        self.upstream["files"][original]["url"] = url
        result = transform(self.upstream, self.config, self.policy)
        self.assertEqual(result["files"][self.policy.destination(original, "files")]["url"], url)
        self.assertEqual(validate_output(self.upstream, result, self.config, self.policy)["url_fields_materialized"], 331)

    def test_filter_tags_tangles_and_all_metadata_preserved(self):
        self.assertEqual(self.generated["default_options"]["filter"],
                         self.upstream["default_options"]["filter"])
        for key in ("v", "timestamp", "tag_dictionary", "base_files_url", "db_url", "default_options"):
            self.assertEqual(self.generated[key], self.upstream[key])
        for path, before in self.upstream["files"].items():
            after = self.generated["files"][self.policy.destination(path, "files")]
            self.assertEqual({key: after[key] for key in before}, before)

    def test_synthetic_filter_terms_and_tag_aliases_preserved(self):
        source = copy.deepcopy(self.upstream)
        source["default_options"]["filter"] = "[MiSTer] !sample-group-one !sample-group-two"
        source["tag_dictionary"].update(samplegroupone=104, samplealias=104, samplegrouptwo=105)
        file_path = next(iter(source["files"]))
        source["files"][file_path]["tags"] = [104, 105]
        source["folders"]["_Arcade"]["tags"] = [104, 105]
        result = transform(source, self.config, self.policy)
        self.assertEqual(result["default_options"], source["default_options"])
        self.assertEqual(result["tag_dictionary"], source["tag_dictionary"])
        self.assertEqual(result["files"][self.policy.destination(file_path, "files")]["tags"], [104, 105])
        self.assertEqual(result["folders"]["_Arcade/_Coin-Op Collection"]["tags"], [104, 105])

    def test_idempotent_and_input_not_mutated(self):
        untouched = copy.deepcopy(self.upstream)
        transform(self.upstream, self.config, self.policy)
        self.assertEqual(self.upstream, untouched)
        self.assertEqual(transform(self.generated, self.config, self.policy), self.generated)

    def test_corrected_prefix_used_for_every_arcade_destination(self):
        for category in ("files", "folders"):
            for path in self.generated[category]:
                if path.startswith("_Arcade/"):
                    self.assertTrue(path == "_Arcade/_Coin-Op Collection"
                                    or path.startswith("_Arcade/_Coin-Op Collection/"))
        path = next(iter(self.generated["files"]))
        old_path = path.replace("_Arcade/_Coin-Op Collection/", "_Arcade/Coin-Op Collection/", 1)
        self.generated["files"][old_path] = self.generated["files"].pop(path)
        with self.assertRaises(ValidationError):
            validate_output(self.upstream, self.generated, self.config, self.policy)

    def test_unique_derived_identity(self):
        self.assertEqual(self.generated["db_id"], "hyp36rmax/MisterFPGA-DownloaderPLUS/coinop-collection")
        self.assertNotEqual(self.generated["db_id"], self.upstream["db_id"])
        self.assertIn("coinop-collection", discover_modules())

    def test_case_insensitive_filesystem_collision(self):
        self.upstream["files"]["_Arcade/CASE.mra"] = {"hash": "a" * 32, "size": 1, "tags": [18]}
        self.upstream["files"]["_Arcade/case.mra"] = {"hash": "b" * 32, "size": 1, "tags": [18]}
        with self.assertRaisesRegex(ValidationError, "collision"):
            transform(self.upstream, self.config, self.policy)

    def test_destination_collisions(self):
        original = next(iter(self.upstream["files"]))
        self.upstream["files"][self.policy.destination(original, "files")] = copy.deepcopy(self.upstream["files"][original])
        with self.assertRaisesRegex(ValidationError, "collision"):
            transform(self.upstream, self.config, self.policy)

    def test_folder_collision(self):
        self.upstream["folders"]["_Arcade/_Coin-Op Collection"] = {"tags": [18]}
        with self.assertRaisesRegex(ValidationError, "collision"):
            transform(self.upstream, self.config, self.policy)

    def test_file_folder_and_parent_collision(self):
        for path in ("_Arcade", "_Arcade/cores"):
            data = copy.deepcopy(self.upstream)
            data["files"][path] = {"hash": "a" * 32, "size": 1, "tags": [18]}
            with self.subTest(path=path), self.assertRaises(ValidationError):
                transform(data, self.config, self.policy)

    def test_double_prefix_rejected(self):
        for path in ("_Arcade/_Coin-Op Collection/_Coin-Op Collection", "_Arcade/_Coin-Op Collection/_Coin-Op Collection/foo.mra"):
            with self.subTest(path=path), self.assertRaises(ValidationError):
                self.policy.destination(path, "folders")

    def test_path_traversal_and_noncanonical_paths(self):
        for path in ("/foo", "_Arcade/../foo", "_Arcade/./foo", "_Arcade//foo", "C:/foo",
                     "_Arcade\\foo", "_Arcade/foo/", "_Arcade/\x00foo", "linux/foo", "MiSTer.ini"):
            with self.subTest(path=path), self.assertRaises(ValidationError):
                self.policy.destination(path, "files")

    def test_unknown_schema_and_malformed_values(self):
        first = next(iter(self.upstream["files"]))
        changes = [
            lambda d: d.update(archives={}), lambda d: d.update(v=2), lambda d: d.update(timestamp=True),
            lambda d: d["default_options"].update(new_option=True),
            lambda d: d["files"][first].update(hash="wrong"),
            lambda d: d["files"][first].update(size=True),
            lambda d: d["files"][first].update(tags=[99999]),
            lambda d: d["files"][first].update(tags=[True]),
            lambda d: d["files"][first].update(overwrite=True),
            lambda d: d["files"][first].update(tangle="core"),
            lambda d: d["files"][first].update(url="http://example.com/a"),
            lambda d: d["folders"]["games"].update(path="unknown"),
        ]
        for change in changes:
            data = copy.deepcopy(self.upstream)
            change(data)
            with self.subTest(change=change), self.assertRaises(ValidationError):
                transform(data, self.config, self.policy)

    def test_duplicate_json_and_invalid_json(self):
        for raw in (b'{"files":{},"files":{}}', b'{"files":{"x":{"tags":[],"tags":[]}}}',
                    b'{"value":NaN}', b'{', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                parse_json(raw)

    def test_archive_structure_and_corruption(self):
        for members in (["other.json"], ["db.json", "extra.txt"], ["db.json", "db.json"], ["../db.json"]):
            data = io.BytesIO()
            with zipfile.ZipFile(data, "w") as archive:
                for member in members:
                    archive.writestr(member, "{}")
            with self.subTest(members=members), self.assertRaises(ValidationError):
                unpack(data.getvalue())
        with self.assertRaises(ValidationError):
            unpack(b"not a zip")

    def test_deterministic_output_and_key_order_independence(self):
        reversed_order = dict(reversed(list(self.generated.items())))
        reversed_order["files"] = dict(reversed(list(self.generated["files"].items())))
        self.assertEqual(package(self.generated), package(reversed_order))
        self.assertEqual(unpack(package(self.generated)), self.generated)

    def test_validator_detects_source_and_metadata_tampering(self):
        first = next(iter(self.generated["files"]))
        changes = [lambda d: d["files"][first].update(url="https://example.com/wrong"),
                   lambda d: d["files"][first].update(hash="f" * 32),
                   lambda d: d["files"][first].update(size=1),
                   lambda d: d["files"][first].update(tags=[]),
                   lambda d: d["files"][first].update(tangle=["unexpected"]),
                   lambda d: d.update(timestamp=d["timestamp"] + 1),
                   lambda d: d.update(db_id=self.config["upstream_db_id"]),
                   lambda d: d["folders"].pop("games"),
                   lambda d: d["files"].pop(first),
                   lambda d: d["folders"]["games"].pop("path")]
        for change in changes:
            data = copy.deepcopy(self.generated)
            change(data)
            with self.subTest(change=change), self.assertRaises(ValidationError):
                validate_output(self.upstream, data, self.config, self.policy)

    def test_future_counts_not_hardcoded(self):
        self.upstream["files"].pop(next(iter(self.upstream["files"])))
        result = transform(self.upstream, self.config, self.policy)
        self.assertEqual(validate_output(self.upstream, result, self.config, self.policy)["generated_files"], 331)

    def test_build_no_op_and_failure_preserves_last_good(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.assertTrue(build("coinop-collection", FIXTURE, directory)["changed"])
            self.assertTrue((directory / "coinop-collection.json.zip").is_file())
            self.assertFalse((directory / "db.json.zip").exists())
            before = {path.name: path.read_bytes() for path in directory.iterdir()}
            self.assertFalse(build("coinop-collection", FIXTURE, directory)["changed"])
            self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})
            invalid = directory / "invalid.zip"
            invalid.write_bytes(package({"v": 2}))
            with self.assertRaises(ValidationError):
                build("coinop-collection", invalid, directory)
            for name, data in before.items():
                self.assertEqual((directory / name).read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
