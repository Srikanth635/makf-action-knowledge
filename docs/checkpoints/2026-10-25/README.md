# Portable session artifacts

[artifact-inventory.json](artifact-inventory.json) inventories 583 files from the
external live, corpus, RDF, audit and simulation working directories. It preserves
426 file references, reusing byte-identical experiment copies already in this
repository; 224 additional files, including the inventory, were initially copied
into this checkpoint. The folder also contains this explanatory README.

Created prompts, raw model responses, quarantine/review results, RDF/SHACL bundles,
research metadata, source-audit snapshots and simulation/build logs are preserved.
The inventory gives each original path, SHA-256, and portable repository location.
No credentials or virtual environments are part of the checkpoint.

Downloaded full papers/images/text caches and upstream runtime dependencies are
listed by hashes and recovery references rather than duplicated. Paper download
URLs/hashes and bounded evidence passages remain available. The pinned FluidLab
manifest and `prepare_source.py` recover its source/meshes; the Dockerfile and
dependency records recover the runtime. Disposable Python caches are excluded.

Run `python scripts/restore_checkpoint.py --verify-only` from the repository to
verify preserved references. Use `--out-dir /workspace` in a fresh environment to
restore the historical external paths, or choose another parent. Existing differing
files are never overwritten. Restoration does not launch Docker, fetch papers,
call models, promote claims or modify original ontologies.

For objectives, completed milestones and the exact next task, start at
[RESUME_HANDOFF.md](../../RESUME_HANDOFF.md).
