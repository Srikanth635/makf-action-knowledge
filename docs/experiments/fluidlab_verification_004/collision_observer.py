"""Read-only shadow calculations before the unmodified collision kernels.

These recompute inputs; they do not capture compiled kernel temporaries. Observed
rounding can therefore differ from the original kernel. No observer is run in AD.
"""
import hashlib
import numpy as np
import taichi as ti
from fluidlab.configs.macros import DTYPE_TI, EPS


@ti.data_oriented
class CollisionObserver:
    def __init__(self, sim, max_frames=80):
        self.sim = sim
        self.mesh = sim.agent.rigid.mesh
        self.frames = max_frames
        self.width = int(np.prod(sim.res))
        # query, active, zero norm, norm<=EPS, invalid/huge norm, inward, flag-on
        self.counts = ti.field(ti.i32, shape=(max_frames, 2, 7))
        self.minimum = ti.field(DTYPE_TI, shape=(max_frames, 2))
        self.grid_mask = ti.field(ti.i32, shape=(max_frames, self.width))
        self.particle_mask = ti.field(ti.i32, shape=(max_frames, sim.n_particles))
        self.enabled = False
        original_grid, original_g2p = sim.grid_op, sim.g2p

        def grid(f):
            if self.enabled:
                self.inspect_grid(f)
            original_grid(f)

        def particles(f):
            if self.enabled:
                self.inspect_particles(f)
            original_g2p(f)

        grid.grad = original_grid.grad
        particles.grad = original_g2p.grad
        sim.grid_op, sim.g2p = grid, particles

    def clear(self):
        self.counts.fill(0)
        self.minimum.fill(1e30)
        self.grid_mask.fill(0)
        self.particle_mask.fill(0)

    @ti.func
    def inspect(self, f, domain, position, velocity):
        self.counts[f, domain, 0] += 1
        code = 1
        distance = self.mesh.sdf(f, position)
        influence = min(ti.exp(-distance * self.mesh.softness), 1)
        if distance <= 0 or (self.mesh.softness > 0 and influence > 0.1):
            self.counts[f, domain, 1] += 1
            code = 2
            relative = velocity - self.mesh.collider_v(f, position, self.sim.dt)
            normal = self.mesh.normal(f, position)
            normal_speed = relative.dot(normal)
            tangent = relative - min(normal_speed, 0) * normal
            norm = tangent.norm()
            if norm != norm or ti.abs(norm) > 1e30:
                self.counts[f, domain, 4] += 1
            else:
                ti.atomic_min(self.minimum[f, domain], norm)
                if norm == 0:
                    self.counts[f, domain, 2] += 1
                if norm <= EPS:
                    self.counts[f, domain, 3] += 1
            if normal_speed < 0:
                self.counts[f, domain, 5] += 1
            if normal_speed < 0 and norm > EPS:
                self.counts[f, domain, 6] += 1
                code = 3
        return code

    @ti.kernel
    def inspect_grid(self, f: ti.i32):
        for I in ti.grouped(ti.ndrange(*self.sim.res)):
            if self.sim.grid[f, I].mass > EPS:
                velocity = (1 / self.sim.grid[f, I].mass) * self.sim.grid[f, I].v_in
                velocity += self.sim.dt * self.sim.gravity
                if ti.static(self.sim.n_statics > 0):
                    for i in ti.static(range(self.sim.n_statics)):
                        velocity = self.sim.statics[i].collide(I * self.sim.dx, velocity)
                index = (I[0] * self.sim.res[1] + I[1]) * self.sim.res[2] + I[2]
                self.grid_mask[f, index] = self.inspect(f, 0, I * self.sim.dx, velocity)

    @ti.kernel
    def inspect_particles(self, f: ti.i32):
        for p in range(self.sim.n_particles):
            if self.sim.particles_ng[f, p].used:
                base = (self.sim.particles[f, p].x * self.sim.inv_dx - 0.5).cast(int)
                fx = self.sim.particles[f, p].x * self.sim.inv_dx - base.cast(DTYPE_TI)
                w = [0.5 * (1.5 - fx) ** 2, 0.75 - (fx - 1.0) ** 2, 0.5 * (fx - 0.5) ** 2]
                velocity = ti.Vector.zero(DTYPE_TI, self.sim.dim)
                for offset in ti.static(ti.grouped(self.sim.stencil_range())):
                    weight = ti.cast(1.0, DTYPE_TI)
                    for d in ti.static(range(self.sim.dim)):
                        weight *= w[offset[d]][d]
                    velocity += weight * self.sim.grid[f, base + offset].v_out
                position = self.sim.particles[f, p].x + self.sim.dt * velocity
                self.particle_mask[f, p] = self.inspect(f, 1, position, velocity)

    def export(self, path, horizon):
        frames = horizon * self.sim.n_substeps
        counts = self.counts.to_numpy()[:frames]
        minimum = self.minimum.to_numpy()[:frames]
        grid = self.grid_mask.to_numpy()[:frames].astype(np.uint8)
        particles = self.particle_mask.to_numpy()[:frames].astype(np.uint8)
        np.savez_compressed(str(path), counts=counts, minimum=minimum,
                            grid_mask=grid, particle_mask=particles)
        return {'artifact': path.name, 'frames': frames,
                'counts_grid_particle': counts.sum(axis=0).tolist(),
                'minimum_norm_grid_particle': [float(v) if v < 1e29 else None for v in minimum.min(axis=0)],
                'grid_mask_sha256': hashlib.sha256(grid.tobytes()).hexdigest(),
                'particle_mask_sha256': hashlib.sha256(particles.tobytes()).hexdigest(),
                'scope': 'Recomputed shadow inputs, not original compiled temporaries; forward-only.'}
