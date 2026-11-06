"""Minimal numpy MLP with manual backprop and Adam (float32). No PyTorch needed."""

import numpy as np


class MLP:
    def __init__(self, sizes, out_tanh, rng):
        self.out_tanh = out_tanh
        self.W, self.b = [], []
        for i, (n_in, n_out) in enumerate(zip(sizes[:-1], sizes[1:])):
            if i == len(sizes) - 2:
                W = rng.uniform(-3e-3, 3e-3, (n_in, n_out))
            else:
                lim = 1.0 / np.sqrt(n_in)          # PyTorch nn.Linear default
                W = rng.uniform(-lim, lim, (n_in, n_out))
            self.W.append(W.astype(np.float32))
            self.b.append(np.zeros(n_out, np.float32))

    @property
    def params(self):
        return self.W + self.b

    def forward(self, x):
        cache = [x]
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            x = x @ W + b
            if i < len(self.W) - 1:
                x = np.maximum(x, 0.0)
            cache.append(x)
        if self.out_tanh:
            x = np.tanh(x)
            cache[-1] = x
        return x, cache

    def __call__(self, x):
        return self.forward(x)[0]

    def backward(self, cache, dy):
        """Returns (grads aligned with params, d input)."""
        n = len(self.W)
        gW, gb = [None] * n, [None] * n
        d = dy * (1.0 - cache[-1] ** 2) if self.out_tanh else dy
        for i in range(n - 1, -1, -1):
            gW[i] = cache[i].T @ d
            gb[i] = d.sum(axis=0)
            d = d @ self.W[i].T
            if i > 0:
                d = d * (cache[i] > 0)
        return gW + gb, d

    def copy_from(self, other):
        for p, q in zip(self.params, other.params):
            p[...] = q

    def soft_update(self, other, tau):
        for p, q in zip(self.params, other.params):
            p *= (1.0 - tau)
            p += tau * q

    def clone(self):
        c = MLP.__new__(MLP)
        c.out_tanh = self.out_tanh
        c.W = [w.copy() for w in self.W]
        c.b = [b.copy() for b in self.b]
        return c

    def export(self, prefix):
        out = {f'{prefix}_n': np.array(len(self.W))}
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            out[f'{prefix}_W{i}'] = W
            out[f'{prefix}_b{i}'] = b
        return out

    def load(self, data, prefix):
        for i in range(len(self.W)):
            self.W[i][...] = data[f'{prefix}_W{i}']
            self.b[i][...] = data[f'{prefix}_b{i}']


class Adam:
    def __init__(self, params, lr, b1=0.9, b2=0.999, eps=1e-8):
        self.params, self.lr, self.b1, self.b2, self.eps = params, lr, b1, b2, eps
        self.m = [np.zeros_like(p) for p in params]
        self.v = [np.zeros_like(p) for p in params]
        self.t = 0

    def step(self, grads):
        self.t += 1
        c1 = 1 - self.b1 ** self.t
        c2 = 1 - self.b2 ** self.t
        for p, g, m, v in zip(self.params, grads, self.m, self.v):
            m *= self.b1
            m += (1 - self.b1) * g
            v *= self.b2
            v += (1 - self.b2) * g * g
            p -= self.lr * (m / c1) / (np.sqrt(v / c2) + self.eps)
