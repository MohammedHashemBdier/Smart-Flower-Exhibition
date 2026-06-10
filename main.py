import collections
import collections.abc
import time

collections.Mapping = collections.abc.Mapping

from rules import SmartFlowerEngine

def run_project(mode):
    print(f"\n{'='*50}")
    print(f"Running with mode: {mode.upper()}")
    print('='*50)
    
    engine = SmartFlowerEngine(mode=mode)   # تغيير strategy إلى mode
    engine.solution_stats = {
        "path_steps": 0, "moves": 0, "loads": 0, "unloads": 0,
        "move_right": 0, "move_left": 0, "move_up": 0, "move_down": 0,
        "load_rose": 0, "load_tulip": 0, "load_orchid": 0, "load_goliat": 0,
        "unload_rose": 0, "unload_tulip": 0, "unload_orchid": 0, "unload_goliat": 0,
    }
    engine.solution_path_actions = []
    engine.reset()

    start_time = time.perf_counter()
    engine.run()
    elapsed = time.perf_counter() - start_time
    print(f"Execution time: {elapsed:.6f} seconds\n")

if __name__ == "__main__":
    run_project("dfs")     # Depth-First Search
    run_project("astar")   # A* Search