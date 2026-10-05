# Thermostat Pilot validation evidence

These files preserve the local validation run from **2026-09-25**. They were
copied from the SysML validation lab on 2026-10-04; validation was not rerun as
part of that documentation update.

| Setting | Recorded value |
|---|---|
| Official Pilot release | `2026-08` |
| Editor build | `0.62.0.202609111953` |
| Java | Temurin `21.0.12.1+1` |
| Loaded standard-library resources | 94 |
| Thermostat result | 0 errors, 0 diagnostics |
| Unresolved-type control | 4 errors; rejected |
| Malformed-syntax control | 1 error; rejected |

## Download the evidence

- [Original validation record and SHA-256 hashes](validation-record.json)
- [Thermostat validator output](thermostat-validation.txt)
- [Unresolved-type output](unresolved.txt) and [input model](unresolved.sysml)
- [Malformed-syntax output](syntax-error.txt) and [input model](syntax-error.sysml)
- [Java validation harness](ValidateSysML.java)
- [Validated thermostat](../thermostat.sysml) and [mapping manifest](../thermostat.mapping.json)

The record retains paths from the original lab. The unresolved-reference log
likewise contains original local file URIs; these are not website endpoints.
The copied logs and harness retain their recorded hashes. The thermostat's
SHA-256 is:

```text
1caafbc77103bfb50312fbf5d696b622da11507eaaab7d9babbd09049be1a1e4
```

## What was checked

The local Java harness invokes the official Pilot's `IResourceValidator` after
loading the matching standard libraries. It validates one user model; it does
not automatically load sibling user models or validate every library file.
The lab recorded nonzero exits for both negative controls.

This evidence establishes acceptance of this structural view by that validator
and version. It does not establish behavior, timing, units, simulation
equivalence, round-trip preservation, or compatibility with OpenSysML.

To repeat the check, use the pinned Pilot distribution and matching libraries
with a compatible Java installation and the supplied harness. The large Java,
Eclipse, and library distributions are not bundled here. A new run should retain
its own tool versions, diagnostics, and artifact hashes.
