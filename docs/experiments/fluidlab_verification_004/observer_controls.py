"""Synthetic positive controls of the real observer; no FluidLab rollout."""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import taichi as ti
from collision_observer_v2 import CollisionObserver

ti.init(arch=ti.cpu, cpu_max_num_threads=1, offline_cache=False)


@ti.data_oriented
class ContactFixture:
    softness = 0

    @ti.func
    def sdf(self, f, position):
        return -1.0

    @ti.func
    def collider_v(self, f, position, dt):
        return ti.Vector([0.0, 0.0, 0.0])

    @ti.func
    def normal(self, f, position):
        return ti.Vector([0.0, 1.0, 0.0])


@ti.data_oriented
class Controls:
    def __init__(self):
        def unused(f):
            pass
        unused.grad = unused
        sim = SimpleNamespace(agent=SimpleNamespace(rigid=SimpleNamespace(mesh=ContactFixture())),
                              res=(1, 1, 1), n_particles=1, dt=0.0002,
                              grid_op=unused, g2p=unused)
        self.observer = CollisionObserver(sim, max_frames=2)
        self.codes = ti.field(ti.i32, shape=2)
        self.observer.clear()

    @ti.kernel
    def run(self):
        # Same local index, distinct global recording indices.
        self.codes[0] = self.observer.inspect(0, 0, 0, ti.Vector([0.0, 0.0, 0.0]), ti.Vector([0.0, 0.0, 0.0]))
        self.codes[1] = self.observer.inspect(0, 1, 0, ti.Vector([0.0, 0.0, 0.0]), ti.Vector([1.0, -1.0, 0.0]))


controls = Controls()
controls.run()
counts = controls.observer.counts.to_numpy()[:, 0, :]
minimum = controls.observer.minimum.to_numpy()[:, 0]
expected = np.asarray([[1, 1, 1, 1, 0, 0, 0], [1, 1, 0, 0, 0, 1, 1]])
if not (np.array_equal(counts, expected) and controls.codes.to_numpy().tolist() == [2, 3]
        and minimum.tolist() == [0.0, 1.0]):
    raise ValueError('Observer positive controls failed')
Path('/out/observer-controls.json').write_text(json.dumps({
    'passed': True, 'scope': 'Synthetic fixture exercises actual observer function, not native collision physics or simulation trajectories.',
    'checks': ['Zero tangential norm is detected', 'Nonzero inward friction flag is detected',
               'Repeated local index retains separate global recording slots'],
    'counts': counts.tolist(), 'minimum_norm': minimum.tolist()}, indent=2) + '\n')
print('Observer positive controls passed')
