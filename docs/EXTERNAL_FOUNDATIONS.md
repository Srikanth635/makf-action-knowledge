# Foundational ontology handling

**Included:** both user-provided AICOR files, draft DUL–AICOR bridge, MAKF, pouring and grasping modules. Their import IRIs are preserved.

**Not included:** the upstream official DUL file. The bridge declares `owl:imports <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl>`, but RDFLib-based offline validation does not resolve remote imports. DUL redistribution licensing was not established during packaging. Obtain the canonical ontology from the [Ontology Design Patterns portal](http://www.ontologydesignpatterns.org/ont/dul/DUL.owl) and verify its license and source version before using it in a formal OWL reasoning workflow.

Recommended integration path: pin a local DUL copy after review, add it to a local import catalog, and run a reasoner (such as ROBOT/HermiT) on the complete import closure. Do not assume current local structural checks establish global OWL-DL consistency.

Other previously discussed foundations—PROV-O, OWL-Time, SOSA/SSN and QUDT—are future candidate integrations, not yet formal imports or modules in this package. SOMA is intentionally excluded.
