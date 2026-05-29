import collections
import collections.abc
import argparse
import json
import os
import random
import sys

collections.Mapping = collections.abc.Mapping

from facts import GridConfig, NodeCounter, Pavilion, StateNode
from heuristics import calculate_h
from rules import SmartFlowerEngine


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_random_config(seed=None, width=5, height=5, pavilion_count=4):
    rnd = random.Random(seed)
    grid = {"width": width, "height": height}
    warehouse = {"x": rnd.randint(1, width), "y": rnd.randint(1, height)}
    robot_start = {"x": rnd.randint(1, width), "y": rnd.randint(1, height)}
    # ensure robot not on warehouse
    if robot_start == warehouse:
        robot_start["x"] = max(1, robot_start["x"] - 1)

    coords = set()
    coords.add((warehouse["x"], warehouse["y"]))
    coords.add((robot_start["x"], robot_start["y"]))

    pavilions = []
    for i in range(pavilion_count):
        # find unique coord
        tries = 0
        while True:
            x = rnd.randint(1, width)
            y = rnd.randint(1, height)
            if (x, y) not in coords:
                coords.add((x, y))
                break
            tries += 1
            if tries > 20:
                # fallback: allow overlap
                break

        # small random needs tuple
        need_len = rnd.randint(1, 3)
        needs = tuple(rnd.randint(1, 3) for _ in range(need_len))
        pavilions.append({
            "id": i + 1,
            "name": f"Pavilion_{i+1}",
            "x": x,
            "y": y,
            "need": needs,
        })

    return {"grid": grid, "warehouse": warehouse, "robot_start": robot_start, "pavilions": pavilions}


def run_project(args):
    engine = SmartFlowerEngine()
    engine.reset()

    # Load config (file) or random
    if args.random:
        cfg = make_random_config(seed=args.seed)
    else:
        cfg_path = args.config or "game_config.json"
        if not os.path.exists(cfg_path):
            print(f"Config file not found: {cfg_path}")
            sys.exit(1)
        cfg = load_config(cfg_path)

    grid = cfg.get("grid", {})
    warehouse = cfg.get("warehouse", {})
    robot_start = cfg.get("robot_start", {})
    pavilions = cfg.get("pavilions", [])

    print("Smart Flower Exhibition Knowledge-Based System")
    print("----------------------------------------------")

    engine.declare(GridConfig(max_x=grid.get("width", 5), max_y=grid.get("height", 5),
                              warehouse_x=warehouse.get("x", 3), warehouse_y=warehouse.get("y", 2)))

    # declare up to 4 pavilions (existing code expects 4)
    for i in range(4):
        if i < len(pavilions):
            p = pavilions[i]
            raw_needs = p.get("need", ())
            if isinstance(raw_needs, int):
                needs = (raw_needs,)
            elif isinstance(raw_needs, list):
                needs = tuple(raw_needs)
            elif isinstance(raw_needs, tuple):
                needs = raw_needs
            else:
                try:
                    needs = tuple(raw_needs)
                except Exception:
                    needs = ()
            engine.declare(Pavilion(pavilion_id=p.get("id", i + 1), name=p.get("name", f"P{i+1}"),
                                     x=p.get("x", 1), y=p.get("y", 1), needs=needs))
        else:
            # declare empty pavilion to keep indices
            engine.declare(Pavilion(pavilion_id=i + 1, name=f"P{i+1}", x=0, y=0, needs=()))

    engine.declare(NodeCounter(next_id=1))

    start_x = robot_start.get("x", 1)
    start_y = robot_start.get("y", 1)

    # Prepare needs for calculate_h (fill up to 4)
    needs_list = []
    for p in pavilions:
        raw_needs = p.get("need", ())
        if isinstance(raw_needs, int):
            needs_list.append((raw_needs,))
        elif isinstance(raw_needs, list):
            needs_list.append(tuple(raw_needs))
        elif isinstance(raw_needs, tuple):
            needs_list.append(raw_needs)
        else:
            try:
                needs_list.append(tuple(raw_needs))
            except Exception:
                needs_list.append(())
    while len(needs_list) < 4:
        needs_list.append(())

    p1_needs, p2_needs, p3_needs, p4_needs = needs_list[:4]
    initial_h = calculate_h(start_x, start_y, p1_needs, p2_needs, p3_needs, p4_needs)

    engine.declare(StateNode(
        node_id=0,
        parent_id=-1,
        robot_x=start_x,
        robot_y=start_y,
        target_x=warehouse.get("x", 3),
        target_y=warehouse.get("y", 2),
        carried_pavilion_id=0,
        carried_pavilion_name="",
        carried_load=(),
        p1_needs=p1_needs,
        p2_needs=p2_needs,
        p3_needs=p3_needs,
        p4_needs=p4_needs,
        g=0,
        h=initial_h,
        f=initial_h,
        action="Start at Robot Initial Position",
        status="open",
        printed=False,
    ))

    print("A* search started.")
    engine.run()


def parse_args():
    p = argparse.ArgumentParser(description="Smart Flower Exhibition runner")
    p.add_argument("--config", help="Path to game configuration JSON file")
    p.add_argument("--random", action="store_true", help="Generate a random game instead of reading a config file")
    p.add_argument("--seed", type=int, default=None, help="Seed for random game generator")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_project(args)
