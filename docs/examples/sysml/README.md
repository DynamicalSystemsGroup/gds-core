# Thermostat SysML v2 structural export

This first interoperability experiment projects the existing
[thermostat](../examples/thermostat.md) into a
flat architecture view. It generates [thermostat.sysml](thermostat.sysml) and
[thermostat.mapping.json](thermostat.mapping.json). Keep the two files together.

## Generate

Generation requires a development checkout containing the experimental
`gds_interchange.sysml` exporter and `thermostat.export_sysml` example; a released
PyPI package is not sufficient. The downloadable artifacts above can be
inspected without installing the exporter.

Run from that repository root with the workspace environment already installed:

```bash
PYTHONPATH=packages/gds-examples/control uv run --no-sync python -m thermostat.export_sysml --output-dir docs/examples/sysml
```

The command replaces these two generated files in the selected directory.
The source revision is the SHA-256 of `model.py`; it identifies those source
bytes, not the complete Python environment. The manifest records the mapping
version and all caller-supplied wire mappings.

## What the view means

| Generated part | GDS block |
|---|---|
| `block0` | PID Controller |
| `block1` | Room Plant |
| `block2` | Temperature Sensor |
| `block3` | Update Room |

Three `connect` relationships describe forward connectivity. Payload spaces
become item definitions containing scalar attributes; outgoing ports use a
channel definition and incoming ports use its conjugate. These connections do
not encode transfer scheduling or state updates. The representation deliberately
chooses parts as an architecture view, rather than claiming GDS blocks are
universally equivalent to SysML parts.

The manifest maps generated identifiers back to source registry entries and
port slots using JSON pointers. Names appear as data in the manifest, so spaces,
punctuation, keywords, and repeated port names cannot inject syntax or merge
elements. Generated identifiers are snapshot-local and may change after edits;
they are not persistent SysML repository identities. All exports currently use
the `GDSExport` package name; load them separately to avoid namespace collisions.

## Explicit limits

- The backward Energy Cost ports and feedback connection are omitted with
  diagnostics. Temporal connections are likewise unsupported.
- Entities, state, parameters, execution contracts, admissibility constraints,
  metrics, and transition signatures are outside this projection.
- Only built-in Python `bool`, `int`, `float`, and `str` payloads are projected.
  `Real` does not preserve IEEE floating-point behavior. Units and value
  constraints are not enforced; custom payload types are rejected from the view
  with diagnostics. Unbound forward ports are emitted untyped with diagnostics.
- Only flat atomic-block registries are accepted. Hierarchical composition and
  reusable component definitions/usages remain future work.
- There is no importer, API synchronization, or execution-equivalence claim.

## Validation status

The exported thermostat was accepted by the official SysML v2 Pilot on
**2026-09-25**, using release `2026-08`, editor build
`0.62.0.202609111953`, and Temurin Java `21.0.12.1+1`. The validator loaded
94 standard-library resources and reported **0 errors and 0 diagnostics**.
Malformed syntax and an unresolved type were rejected as negative controls.

The [validation evidence](validation/README.md) includes the original logs,
artifact hashes, negative-control models, and Java harness. The recorded model
hash matches the downloadable `thermostat.sysml` above. This is a recorded
validation of one structural artifact, not a claim that every generated model
passes or that GDS and SysML execution are equivalent.

Python tests separately cover endpoint preservation, manifest serialization,
identifier safety, unsupported semantics, and rejection of invalid or ambiguous
mappings. They do not substitute for a SysML validator.

The manifest's `validation` field describes generation-time status. Exporting
alone does not invoke a validator, so that field remains unchanged; subsequent
validation belongs in a separate record associated with the artifact hash.

The next gate is to load the same file and negative controls in a pinned
OpenSysML version, compare diagnostics, and inspect the four parts and three
connection endpoints. OpenSysML, repository synchronization, and reverse import
remain untested integrations.

See the [SysML interoperability guide](../../guides/sysml-v2.md) for the tool
roles and next steps, and the [comparison study](../../research/sysml-v2-overlap.md)
for the mapping rationale.
