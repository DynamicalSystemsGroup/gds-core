# SysML v2: ideas and interoperability with GDS

Initial research: 2026-09-24. Status updated: 2026-10-04.

The original source study below informed an experimental structural exporter.
The [thermostat export](../examples/sysml/README.md) subsequently passed the
official Pilot validator on 2026-09-25. See the
[interoperability guide](../guides/sysml-v2.md) for current tool roles and limits.

## Assessment

The strongest opportunity is to connect SysML architecture and engineering context to GDS specifications and analysis through a deliberately bounded mapping. Shared concepts include typed interfaces, composition, state, behavior, validation, and multiple views. Those similarities do **not** establish interchangeable semantics. GDS's four block roles, directional composition, and canonical dynamical decomposition need an explicit interpretation in a SysML model; a generic SysML model does not automatically supply one. Evidence and proposed mappings are separated below.

Scope: the official [Pilot Implementation][pilot], its [release distribution][release], and the separate [API and Services implementation][api]. Pilot source links below are pinned to commit `5cca16d846016e62bb1e54e0e50e675254a022ef`; release/API documentation was read on the research date. Local comparison uses the current working tree.

## What to study in the reference implementation

| Layer | Evidence | Relevance to GDS |
|---|---|---|
| Textual language | [KerML grammar][kerml-grammar], [SysML grammar][sysml-grammar] | A broad modeling language built around reusable semantic concepts. Both grammars use the KerML expression grammar and reference the EMF model; do not mistake the SysML grammar for a direct subclass of the KerML grammar. Compare with GDS's Python DSLs and shared compilation target. |
| Semantic objects | [Definition][definition], [Usage][usage] | Reusable definitions and contextual usages, including nested usages. This distinction is richer than merely repeating a block name or copying a Python object. |
| Semantic processing | [FeatureAdapter][feature-adapter] | Derived features and relationships require semantic processing beyond parsing surface syntax. An importer needs resolved meanings, not just keyword matching. |
| Validation | [SysMLValidator][validator] | Checks definition/usage typing, ports, and other language constraints. Compare its separation from the model with GDS's [generic checks](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/verification/generic_checks.py) and [spec checks](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/verification/spec_checks.py). |
| Evaluation | [ExpressionEvaluator][evaluator] | The inspected execution module evaluates expressions and function invocations, with numerical/collection library functions. This establishes expression evaluation, not a demonstrated general event simulator or ODE solver. No execution equivalence with GDS was established. |
| Distribution and persistence | [Release documentation][release], [API documentation][api] | Examples, normative libraries, editors, and model archives are distinct from the REST service. A file exchange experiment need not introduce the service or its PostgreSQL deployment. |

## Overlap and the important mismatches

| Topic | GDS evidence | Interpretation for interoperability |
|---|---|---|
| Types and reusable components | [TypeDef](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/types/typedef.py), [Interface](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/types/interface.py), [blocks](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/blocks/base.py) | SysML definition/usage is an idea worth borrowing for repeated component instances. A GDS `TypeDef` is a data type, not a universal equivalent of a SysML definition. |
| Ports and connections | [Interface](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/types/interface.py), [IR](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/ir/models.py); SysML [port validation][validator] | GDS uses four forward/backward input/output slots and token sets. SysML has typed port usages and conjugation. Similar names or opposite arrow directions do not prove equivalent type or variance semantics. |
| State and behavior | [state](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/state.py), [canonical projection](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/canonical.py); SysML [grammar][sysml-grammar] | SysML parts, attributes, actions, states, and transitions can describe relevant context, but mapping them to `Entity`, `Policy`, or `Mechanism` requires a modeling convention. A SysML action need not be a GDS policy or state updater. |
| Time | [ExecutionContract](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/execution.py), [composition](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/blocks/composition.py); SysML [successions/transitions][sysml-grammar] | GDS temporal loops and within-evaluation feedback differ; neither automatically means a SysML succession or state transition. Require an explicit time interpretation before importing executable behavior. |
| Simulation | [analysis adapter](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-analysis/gds_analysis/adapter.py) | The current adapter groups policies and state updates into one update block and documents that sequential tier dependencies are not yet modeled. It does not enforce the `ExecutionContract` requirement stated in that class's documentation. A syntactically valid structural import therefore cannot promise preserved execution. |
| Constraints and results | [TypeDef](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/types/typedef.py), [OWL importer](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-interchange/gds_interchange/owl/import_.py); SysML [requirements/constraints/analysis cases][sysml-grammar] | Recognized bounds and enumerations are plausible portable subsets. Arbitrary Python predicates and transitions need external implementations or an agreed expression subset. A linked GDS check result is evidence about its stated check, not automatic satisfaction of a SysML requirement. |
| Identity and interchange | [OWL export](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-interchange/gds_interchange/owl/export.py), [IR serialization](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/ir/serialization.py) | GDS already exports model structure and findings. Its RDF URIs are derived from names; a bridge should preserve source identity and revision independently of display names. RDF output alone does not confer SysML API compatibility. |

## Ideas worth borrowing

These are design proposals inferred from the comparison, not features already implemented here.

1. **Separate reusable definitions from usages where reuse becomes painful.** Start in a bridge's mapping records: component definition, contextual occurrence, and qualified owner. This avoids changing the whole GDS core before a repeated-component example proves the need. Study [Usage][usage] alongside GDS's [block/IR identity model](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/ir/models.py).
2. **Make semantic libraries explicit and versioned.** A small mapping library can declare which GDS roles, data types, units, and execution conventions a SysML model assumes. SysML's release already distributes normative libraries; GDS already records type units and constraint metadata. Those are foundations for a mapping, not automatic unit conversion. Sources: [release][release], [TypeDef](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/types/typedef.py).
3. **Treat provenance and unsupported semantics as data.** Carry source element identity, source revision, mapping version, and diagnostics alongside exported/imported objects. Distinguish preserved, approximated, and unsupported fields. Existing [IR metadata](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/ir/serialization.py) and [OWL loss handling](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-interchange/gds_interchange/owl/import_.py) give useful local precedents.
4. **Preserve separate structural and behavioral claims.** Successfully resolving and validating a SysML model proves neither GDS role correctness nor simulation equivalence. Run each validator at its own boundary and retain its findings. Sources: [SysMLValidator][validator], [GDS checks](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-framework/gds/verification/spec_checks.py), [analysis adapter](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-analysis/gds_analysis/adapter.py).

## Practical interoperability routes

| Route | Proposed scope | Main boundary | Priority |
|---|---|---|---|
| GDS → `.sysml` architecture view | Export a declared subset of hierarchy, components, port payloads, and explicit connections; retain GDS roles and wire classifications in mapping metadata. | This is a structural projection. Choosing parts versus actions is an explicit view decision, not a universal mapping. Validate with the Pilot and matching libraries. | First |
| SysML → GDS analysis input | Select a model subset, preserve its source IDs, bind supported attributes/parameters and approved GDS functions, run a specified analysis, and produce source-linked findings/results. | Arbitrary actions, transitions, units, inheritance, multiplicity, and timing cannot be silently collapsed. Resolve or reject each unsupported case. | After one structural example |
| API-backed exchange | Read model elements from a chosen repository and exchange selected model/result artifacts using its supported API. | REST is transport/persistence; it does not solve the semantic mapping. Pin server/schema versions and test actual capabilities before designing synchronization. | Later, if a real tool requires it |

The experiment now lives in the `gds_interchange.sysml` subpackage. It is an experimental one-way structural exporter alongside the existing OWL tooling, with a mapping/loss manifest. See the [thermostat example](../examples/sysml/README.md). Reuse GDS's structural serializers where appropriate, but keep mapping decisions explicit rather than routing everything through RDF by default.

### A bounded first experiment

Use the existing [thermostat example](https://github.com/DynamicalSystemsGroup/gds-core/blob/2d5d3c7/packages/gds-examples/control/thermostat/model.py) to answer: *Can an engineering architecture tool inspect our components and interfaces while retaining enough provenance to trace back to GDS?*

1. Define the supported structural subset and a mapping manifest. Include declared payload types, ownership, source identity, and wire classification. Do not infer a physical quantity type from a port's display name.
2. Export a forward-connection structural view plus the manifest. Keep backward `Energy Cost` and temporal-loop relationships explicit as unsupported or separately described semantics; do not relabel them as ordinary connections and claim equivalence.
3. Parse, resolve, and validate the output using one pinned Pilot/library version. Check component/port ownership and selected connection endpoints against the original GDS model, including repeated names under different owners.
4. Require an explicit diagnostic for each excluded construct. Successful parsing is the first gate; structural preservation and traceability are separate gates.
5. Only then try a reverse projection of that same bounded subset. Executable import is a separate experiment with an explicit time contract, function bindings, and analysis-adapter limitations.

A successful spike would provide a small `.sysml` artifact, mapping/loss manifest, and validation evidence. It would not claim full SysML support, unrestricted round trips, or simulation equivalence.

## Suggested reading sequence

1. Read release examples and libraries before setting up the full developer environment: [release contents][release]. Pick parts, ports, connections, then actions and states.
2. Follow one definition and its usage through [model objects][usage], [grammar][sysml-grammar], [FeatureAdapter][feature-adapter], and [validator][validator]. Compare against GDS's DSL → spec/IR path.
3. Specify the thermostat mapping and identify each intentional loss before writing an exporter.
4. Read the separate [API service][api] only when a target repository/tool makes API integration concrete.

## Verification and open questions

The original study was based on source/document inspection. Subsequent implementation and the [recorded Pilot validation](../examples/sysml/validation/README.md) establish one structural export accepted by the official validator. OpenSysML validation, runtime equivalence, reverse import, and repository synchronization have not been tested. Outstanding decisions: target engineering tool, whether architecture exchange or executable analysis matters first, required quantity/unit coverage, and whether model editing must round-trip. These determine the mapping scope; the first export proposal can proceed as a disposable experiment without assuming all four answers.

[pilot]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/tree/5cca16d846016e62bb1e54e0e50e675254a022ef
[release]: https://github.com/Systems-Modeling/SysML-v2-Release/blob/master/README.md
[api]: https://github.com/Systems-Modeling/SysML-v2-API-Services/blob/master/README.md
[kerml-grammar]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/5cca16d846016e62bb1e54e0e50e675254a022ef/org.omg.kerml.xtext/src/org/omg/kerml/xtext/KerML.xtext
[sysml-grammar]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/5cca16d846016e62bb1e54e0e50e675254a022ef/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext
[definition]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/5cca16d846016e62bb1e54e0e50e675254a022ef/org.omg.sysml.model/src/main/java/org/omg/sysml/lang/sysml/Definition.java
[usage]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/5cca16d846016e62bb1e54e0e50e675254a022ef/org.omg.sysml.model/src/main/java/org/omg/sysml/lang/sysml/Usage.java
[feature-adapter]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/5cca16d846016e62bb1e54e0e50e675254a022ef/org.omg.sysml.logic/src/main/java/org/omg/sysml/adapter/FeatureAdapter.java
[validator]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/5cca16d846016e62bb1e54e0e50e675254a022ef/org.omg.sysml.xtext/src/org/omg/sysml/xtext/validation/SysMLValidator.xtend
[evaluator]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/5cca16d846016e62bb1e54e0e50e675254a022ef/org.omg.sysml.execution/src/org/omg/sysml/execution/expressions/ExpressionEvaluator.java
