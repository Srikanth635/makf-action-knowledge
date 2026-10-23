# E1 acceptance criteria and limitations

## Fulfilled

- [x] Canonical, action-neutral LinkML extraction contract, with nested descriptions and explicit statuses
- [x] Source passage anchors and optional verified exact offsets
- [x] Separate epistemic, derivation and evidence statuses
- [x] Ontology class references checked against AICOR/CRAM/MAKF/pouring/grasping source OWL
- [x] MAKF object-property domain/range checked against local named subclass chains
- [x] Conditional hypotheses require explicit condition and predicted-effect links
- [x] No physical scene or execution fields admitted by the JSON contract
- [x] Pouring and grasping action profiles reuse one generic schema
- [x] Generatable ontology guidance package for downstream extraction prompts
- [x] Offline test suite with rejection tests

## Not implemented / gates for later phases

- [ ] Official LinkML metamodel validation and comparison to LinkML-generated JSON Schema (LinkML not installed offline)
- [ ] OWL 2 DL imported-closure satisfiability check (official DUL not locally resolved)
- [ ] LLM extraction from real text (E2)
- [ ] Source-paraphrase semantic entailment evaluation (E2/E3)
- [ ] RDF knowledge-object serialization, PROV-O graph generation and SHACL (E3)
- [ ] Ontology term alias resolution and uncertain-grounding confidence ranking (future)
- [ ] TigerGraph import and GraphRAG retrieval (E4)
- [ ] Automated detection of concrete named physical entities within free-text statements (future; extra safety gate)

## Principles

The boundary is **candidate extraction → checked structure → scientific evidence assessment → accepted action knowledge**. A valid JSON document is **not** a validated theory about action. Frames contain abstract descriptions, not specific physical acts or world states.
