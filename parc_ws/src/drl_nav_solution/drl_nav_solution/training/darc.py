"""PEEMEF-DARC in numpy, ported from github.com/nfhe/darc_drl_nav (PEEMEF_DARC.py,
peemef_darc_utils.py).

DARC (double actors, regularised critics):
  * two actors and two critics, updated alternately (cross-update scheme);
  * target: for each target actor the min of both target critics, then a soft
    mix  v = q_weight * min(v1, v2) + (1 - q_weight) * max(v1, v2);
  * critic regularisation: + reg_weight * (Q1 - Q2)^2;
  * acting: both actors propose, the one its critic values higher wins.

PEEM (priority excellent experience): the buffer starts with demonstration
transitions, and each batch mixes "excellent" samples (the highest-reward
transitions) with uniform ones. The paper re-sorts the whole buffer every step
and draws ~70 % excellent samples; here the top set is refreshed every
`refresh` updates and the excellent share decays from `peem_start` to
`peem_end` so the agent can outgrow the demonstrations.
"""

import numpy as np

from drl_nav_solution.training.nn import MLP, Adam


class ReplayBuffer:
    def __init__(self, state_dim, action_dim, size, rng):
        self.s = np.zeros((size, state_dim), np.float32)
        self.a = np.zeros((size, action_dim), np.float32)
        self.s2 = np.zeros((size, state_dim), np.float32)
        self.r = np.zeros((size, 1), np.float32)
        self.nd = np.zeros((size, 1), np.float32)
        self.demo = np.zeros(size, bool)
        self.max, self.ptr, self.size = size, 0, 0
        self.rng = rng
        self.top = None
        self.top_frac = 0.05

    def add(self, s, a, s2, r, done, demo=False):
        i = self.ptr
        self.s[i], self.a[i], self.s2[i], self.r[i], self.nd[i] = s, a, s2, r, 1.0 - done
        self.demo[i] = demo
        self.ptr = (self.ptr + 1) % self.max
        self.size = min(self.size + 1, self.max)

    def refresh_top(self):
        k = max(1, int(self.size * self.top_frac))
        self.top = np.argpartition(-self.r[:self.size, 0], k - 1)[:k]

    def sample(self, n, excellent_share):
        n_ex = int(n * excellent_share) if self.top is not None else 0
        idx = np.concatenate([self.rng.choice(self.top, n_ex),
                              self.rng.integers(0, self.size, n - n_ex)])
        return self.s[idx], self.a[idx], self.s2[idx], self.r[idx], self.nd[idx]


class DARC:
    def __init__(self, state_dim, action_dim, hidden=(256, 256), seed=0,
                 discount=0.99, tau=0.005, policy_noise=0.2, noise_clip=0.5,
                 actor_lr=3e-4, critic_lr=3e-4, q_weight=0.1, reg_weight=0.005):
        self.rng = np.random.default_rng(seed)
        a_sizes = [state_dim, *hidden, action_dim]
        c_sizes = [state_dim + action_dim, *hidden, 1]
        self.actor = [MLP(a_sizes, True, self.rng) for _ in range(2)]
        self.critic = [MLP(c_sizes, False, self.rng) for _ in range(2)]
        self.actor_t = [m.clone() for m in self.actor]
        self.critic_t = [m.clone() for m in self.critic]
        self.actor_opt = [Adam(m.params, actor_lr) for m in self.actor]
        self.critic_opt = [Adam(m.params, critic_lr) for m in self.critic]
        self.state_dim, self.action_dim = state_dim, action_dim
        self.discount, self.tau = discount, tau
        self.policy_noise, self.noise_clip = policy_noise, noise_clip
        self.q_weight, self.reg_weight = q_weight, reg_weight

    # ------------------------------------------------------------- acting
    def act(self, s):
        s = np.asarray(s, np.float32)[None, :]
        a1, a2 = self.actor[0](s), self.actor[1](s)
        q1 = self.critic[0](np.hstack([s, a1]))[0, 0]
        q2 = self.critic[1](np.hstack([s, a2]))[0, 0]
        return (a1 if q1 >= q2 else a2)[0]

    # ----------------------------------------------------------- training
    def train(self, buf, batch, excellent_share):
        for i in (0, 1):                          # cross-update scheme
            self._train_one(buf.sample(batch, excellent_share), i)

    def _train_one(self, batch, i):
        s, a, s2, r, nd = batch
        j = 1 - i
        noise = np.clip(self.rng.normal(0, self.policy_noise, a.shape),
                        -self.noise_clip, self.noise_clip).astype(np.float32)
        na1 = np.clip(self.actor_t[0](s2) + noise, -1, 1)
        na2 = np.clip(self.actor_t[1](s2) + noise, -1, 1)
        x1, x2 = np.hstack([s2, na1]), np.hstack([s2, na2])
        v1 = np.minimum(self.critic_t[0](x1), self.critic_t[1](x1))
        v2 = np.minimum(self.critic_t[0](x2), self.critic_t[1](x2))
        v = self.q_weight * np.minimum(v1, v2) + (1 - self.q_weight) * np.maximum(v1, v2)
        y = r + nd * self.discount * v

        x = np.hstack([s, a])
        qi, cache = self.critic[i].forward(x)
        qj = self.critic[j](x)
        n = len(s)
        dq = (2.0 / n) * (qi - y) + self.reg_weight * (2.0 / n) * (qi - qj)
        g, _ = self.critic[i].backward(cache, dq.astype(np.float32))
        self.critic_opt[i].step(g)

        # actor i maximises critic i
        ai, acache = self.actor[i].forward(s)
        q, qcache = self.critic[i].forward(np.hstack([s, ai]))
        _, dx = self.critic[i].backward(qcache, np.full_like(q, -1.0 / n))
        ga, _ = self.actor[i].backward(acache, dx[:, self.state_dim:])
        self.actor_opt[i].step(ga)

        self.critic_t[i].soft_update(self.critic[i], self.tau)
        self.actor_t[i].soft_update(self.actor[i], self.tau)
        return float(np.mean((qi - y) ** 2))

    def behaviour_clone(self, buf, steps, batch=256):
        """Warm start: both actors regress onto the demonstration actions."""
        idx_demo = np.flatnonzero(buf.demo[:buf.size])
        for _ in range(steps):
            idx = self.rng.choice(idx_demo, batch)
            s, a = buf.s[idx], buf.a[idx]
            for k in (0, 1):
                out, cache = self.actor[k].forward(s)
                g, _ = self.actor[k].backward(cache, (2.0 / batch) * (out - a))
                self.actor_opt[k].step(g)
        for k in (0, 1):
            self.actor_t[k].copy_from(self.actor[k])

    def export(self):
        d = {}
        for k in (0, 1):
            d.update(self.actor[k].export(f'actor{k + 1}'))
            d.update(self.critic[k].export(f'critic{k + 1}'))
        return d

    def load(self, data):
        for k in (0, 1):
            self.actor[k].load(data, f'actor{k + 1}')
            self.critic[k].load(data, f'critic{k + 1}')
            self.actor_t[k].copy_from(self.actor[k])
            self.critic_t[k].copy_from(self.critic[k])
