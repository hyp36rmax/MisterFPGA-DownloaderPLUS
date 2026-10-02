# Coin-Op Midway release eligibility

The official Coin-Op Downloader database remains the authority for managed downloads. Absence from that database does not imply an implementation is unreleased: a reviewed, authoritative released MiSTer package can establish a usable core/MRA pair for a Reserve presentation. Package evidence is an eligibility attestation, not a payload inventory or permission to redistribute content.

| Hardware family | Core / compatible MRA evidence | Approved public DB | State | Presentation |
|---|---|---|---|---|
| MIDWAY Z-UNIT | Coin-Op released Z/Y MiSTer package | No | RESERVE | `_MIDWAY Z-UNIT/` |
| MIDWAY Y-UNIT | Coin-Op released Z/Y MiSTer package | No | RESERVE | `_MIDWAY Y-UNIT/` |
| MIDWAY T-UNIT | Coin-Op released T-Unit DCS MiSTer package | No | RESERVE | `_MIDWAY T-UNIT/` |
| MIDWAY WOLF UNIT | No confirmed Coin-Op usable MiSTer pair found | No | ABSENT | None |

Release evidence: Coin-Op's [Z/Y MiSTer release](https://www.patreon.com/atrac17/posts/coin-op-presents-155890167) and [T-Unit DCS MiSTer release](https://www.patreon.com/atrac17/posts/coin-op-presents-157759538) expose publisher-owned release titles and named MiSTer package attachments. Restricted archive members were not downloaded or inspected. Wolf Unit development discussion and releases from other authors do not establish a Coin-Op release. ABSENT here means no confirmed eligible pair, not proof that no implementation exists anywhere.

Each Reserve presentation contains only `_READ ME.txt`, directly beneath its canonical `_Arcade/_Arcade Systems/_<SYSTEM>/` folder. It is approved under Coin-Op authority and included in Complete, under its existing database ID; the shared Reserve subscription does not claim these destinations. There are no restricted payload records or private download URLs. Guidance directs users to authorized sources and `_Arcade/cores/` for required cores.

The existing `confirmed_releases` metadata accepts either a reviewed filename inventory or a reviewed authoritative released-package attestation. A package record must identify a MiSTer release, its public Coin-Op post, its actual attachment name, and explicitly confirmed core and compatible-MRA availability. Known incomplete pairs remain absent; unknown availability, ambiguous evidence, and attempts to present a roadmap as a release fail for review. Such attestations never select payloads from an outside source.

When reviewed Coin-Op public classifications become available, the same family can become managed at the same destination. A new or ambiguous upstream classification still requires review. Release-backed guidance remains in place through promotion. Run `python tools/audit_arcade_systems.py` for the complete current state matrix.
