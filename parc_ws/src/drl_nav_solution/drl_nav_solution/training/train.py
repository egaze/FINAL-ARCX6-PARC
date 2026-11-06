"""Train the PEEMEF-DARC navigation policy in the 2D PARC arenas.

    python3 -m drl_nav_solution.training.train --steps 150000 --out weights/darc_policy.npz

Stages:
  1. Demonstrations ("excellent experience"): the privileged expert drives
     `--demo-episodes` legs; the transitions go into the replay buffer, marked.
  2. Behaviour-cloning warm start of both actors on those demonstrations
     (addition to the paper: it makes 2-CPU training practical).
  3. DARC with PEEM sampling and decaying epsilon-random exploration, as in the paper.
Every `--eval-every` steps the deterministic policy is scored on fixed legs in
held-out arenas; the best one is saved.
"""

import argparse
import json
import math
import time

import numpy as np

from drl_nav_solution import policy as P
from drl_nav_solution.training.darc import DARC, ReplayBuffer
from drl_nav_solution.training.env import NavEnv

TRAIN_SEEDS = range(100, 400)
VAL_SEEDS = range(1000, 1020)


def evaluate(agent, env, tasks):
    out = {'arrived': 0, 'crashed': 0, 'timeout': 0, 'time': [], 'ratio': []}
    for seed, task in tasks:
        s = env.reset(seed=seed, task=task)
        plan_len = sum(math.hypot(b[0] - a[0], b[1] - a[1])
                       for a, b in zip(env.path[:-1], env.path[1:])) if env.path else None
        while True:
            s, r, done, info = env.step(agent.act(s))
            if done or info['timeout']:
                break
        for k in ('arrived', 'crashed', 'timeout'):
            out[k] += int(info[k])
        if info['arrived']:
            out['time'].append(env.steps * 0.1)
            if plan_len:
                out['ratio'].append(env.steps * 0.1 / (plan_len / P.V_MAX))
    n = len(tasks)
    return {'success': out['arrived'] / n, 'crash': out['crashed'] / n,
            'timeout': out['timeout'] / n,
            'mean_time_s': float(np.mean(out['time'])) if out['time'] else None,
            'time_vs_ideal': float(np.mean(out['ratio'])) if out['ratio'] else None}


def make_val_tasks(n, rng):
    env = NavEnv(VAL_SEEDS, rng)
    tasks = []
    while len(tasks) < n:
        env.reset()
        if env.path is None:
            continue
        r = env.robot
        tasks.append((env.seed, ((r.x, r.y, r.yaw), env.goal)))
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--steps', type=int, default=150000)
    ap.add_argument('--demo-episodes', type=int, default=250)
    ap.add_argument('--bc-steps', type=int, default=4000)
    ap.add_argument('--batch', type=int, default=128)
    ap.add_argument('--eval-every', type=int, default=10000)
    ap.add_argument('--val-tasks', type=int, default=60)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default='darc_policy.npz')
    ap.add_argument('--log', default='train_log.jsonl')
    ap.add_argument('--resume', default=None)
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    env = NavEnv(TRAIN_SEEDS, rng)
    val_env = NavEnv(VAL_SEEDS, np.random.default_rng(123))
    val_tasks = make_val_tasks(a.val_tasks, np.random.default_rng(7))
    agent = DARC(P.STATE_DIM, P.ACTION_DIM, seed=a.seed)
    buf = ReplayBuffer(P.STATE_DIM, P.ACTION_DIM, 400000, rng)
    log = open(a.log, 'a')

    def record(entry):
        entry['wall_s'] = round(time.time() - t0, 1)
        print(json.dumps(entry), flush=True)
        log.write(json.dumps(entry) + '\n')
        log.flush()

    t0 = time.time()
    if a.resume:
        agent.load(np.load(a.resume))
    # 1. demonstrations
    for ep in range(a.demo_episodes):
        s = env.reset()
        while True:
            act = env.expert_action()
            act = np.clip(act + rng.normal(0, 0.05, 2), -1, 1)   # a little variety
            s2, r, done, info = env.step(act)
            buf.add(s, act, s2, r, done, demo=True)
            s = s2
            if done or info['timeout']:
                break
    record({'stage': 'demos', 'transitions': buf.size})
    # 2. behaviour cloning warm start
    if not a.resume and a.bc_steps:
        agent.behaviour_clone(buf, a.bc_steps)
        record({'stage': 'bc', **evaluate(agent, val_env, val_tasks)})
    # 3. DARC + PEEM
    buf.refresh_top()
    best = -1e9
    epsilon, eps_decay, eps_min = 0.15, 0.99997, 0.01
    s = env.reset()
    ep_ret, returns, outcomes = 0.0, [], []
    for step in range(1, a.steps + 1):
        epsilon = max(eps_min, epsilon * eps_decay)
        if rng.random() < epsilon:
            act = rng.uniform(-1, 1, 2)
        else:
            act = np.clip(agent.act(s) + rng.normal(0, 0.1, 2), -1, 1)
        s2, r, done, info = env.step(act)
        buf.add(s, act, s2, r, done)
        ep_ret += r
        s = s2
        if done or info['timeout']:
            returns.append(ep_ret)
            outcomes.append('A' if info['arrived'] else 'C' if info['crashed'] else 'T')
            ep_ret = 0.0
            s = env.reset()
        share = 0.4 * max(0.0, 1.0 - step / (0.6 * a.steps)) + 0.1
        agent.train(buf, a.batch, share)
        if step % 2000 == 0:
            buf.refresh_top()
        if step % a.eval_every == 0:
            ev = evaluate(agent, val_env, val_tasks)
            last = outcomes[-100:]
            record({'stage': 'darc', 'step': step, 'epsilon': round(epsilon, 3),
                    'train_success': round(last.count('A') / max(1, len(last)), 2),
                    'train_crash': round(last.count('C') / max(1, len(last)), 2),
                    'train_return': round(float(np.mean(returns[-100:])), 1), **ev})
            score = ev['success'] - 2 * ev['crash']
            np.savez(a.out.replace('.npz', '_last.npz'), **agent.export())
            if score > best:
                best = score
                np.savez(a.out, **agent.export())
                record({'saved': a.out, 'score': score, 'step': step})


if __name__ == '__main__':
    main()
