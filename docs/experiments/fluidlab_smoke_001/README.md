# FluidLab native-unit forward smoke test

**Result: PASS on CPU**, 2026-10-25. This executes a modified, pinned FluidLab setup,
not a paper-result reproduction, successful pouring policy or SI-calibrated run.

## What ran

- Upstream commit `7295eb6ed7ee92b2be471fd30b432238577f28ce`.
- 109 source/config/glass input files (18,022,110 bytes), verified against Git blob
  and SHA-256 hashes. The 128³ precomputed glass collision SDF was used unchanged.
- Isolated Docker image with Python 3.7.17, Taichi 1.1.0, Gym 0.21.0, NumPy 1.21.5
  and PyTorch 1.12.1 CPU. Upstream recommends Python 3.7.13/CUDA PyTorch; this is a
  compatibility smoke environment, not a byte-identical historical environment.
- Four CPU limit, 8 GiB memory limit, no network access during execution. Container
  hostname `matrix-makf-smoke` selects upstream's existing headless-server guard.
- `ti.gpu` was requested as in upstream. CUDA/OpenGL backends were unavailable and
  Taichi fell back to **Arch.x64**. The backend probe computed `[0, 1, 4, 9]` correctly.
- Registered `Pouring-v0`, seed 0, diff loss, no optimizer. Two zero six-component
  actions, then a reset and replay of the first zero action: three forward steps.
  The default constructed agent pose was used; the optimizer's initial-pose/action
  configuration was not applied. No rendering or backward-gradient test was run.

## Measurements

| Check | Result |
| --- | --- |
| Initialized particles | 40,604: 20,302 per fluid body |
| Grid | 64 × 64 × 64 |
| Integration | dt=0.0002, ten substeps per environment step, in code units |
| Positions, velocities and observations | Finite in both tested steps |
| Reward | Finite: 4.999, then approximately 4.99643; not a success probability |
| Active particle count | 40,604 after both steps |
| Active particle mass ledger | 1.85870361328125 code units, unchanged within tolerance |
| Reset/replay max coordinate difference | 1.1920928955078125e-7, below the 1e-5 tolerance |
| Initialization + test time | Approximately 19.24 seconds in this run |

The first step took about 13.79 seconds, including JIT compilation; the second took
about 0.52 seconds. Those timings do not establish long-horizon/optimization speed.
Mass here is the retained active-particle ledger; this short check does not verify
all grid/particle transfer conservation, physical incompressibility or calibration.
The two-step trajectory is only 0.004 code-time units; it does not test liquid
transfer, spillage performance or sustained stability.

## Changes and attempts

[runtime.patch](runtime.patch) changes two files:

1. Accept/store/forward `renderer_type` in `PouringEnv`, addressing the previous
   static constructor mismatch.
2. Defer importing the optional `mesh_to_sdf` generator until SDF regeneration.
   Regeneration was not requested; the pinned existing SDF was loaded.

No MPM integration equations, material parameters, timestep, particle density,
gravity or backend-selection code were changed. CPU selection was Taichi's fallback.
The test uses the upstream headless guard; compiled GL rendering is not tested.

Failed attempts are retained. Initial Taichi import needed libX11; Debian package
retrieval/trust issues were resolved with a readable build-time CA secret and the
minimal X11 libraries. Gym required the upstream-pinned importlib-metadata 4.12.0.
The optimizer module's import required OpenCV; opencv-python-headless 4.6.0.66 was
installed. No private keys were mounted into execution containers, TLS checks stayed
enabled, and no access-policy denial was bypassed.

## Artifacts

[smoke-report.json](smoke-report.json) contains assertions and measurements.
[backend.json](backend.json), attempt logs, Dockerfile, exact test scripts and
[provenance.json](provenance.json) preserve environment/source/patch identity.
The Docker image ID and base digest are recorded. Python dependency versions are
in `pip-freeze.txt`. Full build logs, cached source and output remain at
`/workspace/makf-simulation-runs/fluidlab-smoke-001/`.

The archived paper/evidence execution flags are unchanged: that contract is still
archival and the paper/configuration/unit questions remain open. This new runtime
evidence establishes forward-smoke capability of this specific patched CPU setup.

## Repeat

The preparation command fetches pinned public files and requires network access:

```bash
.venv/bin/python docs/experiments/fluidlab_smoke_001/prepare_source.py \
  --out-dir /workspace/fluidlab-smoke-repeat
```

Use a new directory. It validates source hashes and applies only the recorded patch.
Build with the managed local Docker daemon, preserving the session proxy and CA:

```bash
BUILDX_CONFIG=/workspace/.cache/makf-buildx docker --host=unix:///var/run/docker.sock build \
  --secret id=ca,src=/etc/ssl/certs/ca-certificates.crt \
  -t makf-fluidlab-smoke-repeat /workspace/fluidlab-smoke-repeat

docker --host=unix:///var/run/docker.sock run --rm --network none \
  --hostname matrix-makf-smoke --memory 8g --cpus 4 --pids-limit 256 \
  -e OMP_NUM_THREADS=4 -e MKL_NUM_THREADS=4 -e OPENBLAS_NUM_THREADS=4 \
  --mount type=bind,src=/workspace/fluidlab-smoke-repeat/source,dst=/work \
  --mount type=bind,src=/workspace/fluidlab-smoke-repeat/output,dst=/out \
  makf-fluidlab-smoke-repeat python smoke.py
```

GPU fallback availability can differ on another machine; record the actual backend
and keep backend comparisons separate. The image ID identifies this built image;
OS-package repository updates can change a rebuilt image despite the pinned base.

## Next experiments

1. Run longer forward checks with both zero action and a small tilt, using the
   config's initial pose and a declared finite horizon. Track active particles,
   finite state, loss, motion and termination without claiming pouring success yet.
2. Check gradients against finite differences on a small, reproducible case before
   using the differentiable optimizer. Record tolerance, contact behavior and CPU
   nondeterminism; forward success alone does not validate backpropagation.
3. Run bounded baseline/tilt trials, then a small optimization pilot if the preceding
   checks pass. Verify runtime/memory needs before attempting the full 500-iteration
   experiment; a compatible GPU environment may be more practical.
4. Preserve raw outputs and native units, then ingest qualified summaries as
   `local_simulation` evidence. Physical calibration and exact published-result
   matching remain separate tasks; do not replace the paper values with these runs.
