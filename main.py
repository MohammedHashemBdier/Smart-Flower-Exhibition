import collections
import collections.abc
import time

collections.Mapping = collections.abc.Mapping

from rules import SmartFlowerEngine


def run_project():
    engine = SmartFlowerEngine()
    engine.solution_stats = {
        "path_steps": 0,
        "moves": 0,
        "loads": 0,
        "unloads": 0,
        "move_right": 0,
        "move_left": 0,
        "move_up": 0,
        "move_down": 0,
        "load_rose": 0,
        "load_tulip": 0,
        "load_orchid": 0,
        "load_goliat": 0,
        "unload_rose": 0,
        "unload_tulip": 0,
        "unload_orchid": 0,
        "unload_goliat": 0,
    }
    engine.solution_path_actions = []
    engine.reset()  # DefFacts will seed initial facts

    start_time = time.perf_counter()

    print("Smart Flower Exhibition Knowledge-Based System")
    print("----------------------------------------------")

    print("A* search started.")
    engine.run()

    elapsed_seconds = time.perf_counter() - start_time
    print(f"Execution time: {elapsed_seconds:.6f} seconds")


run_project()
