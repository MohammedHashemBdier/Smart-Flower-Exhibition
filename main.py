import collections
import collections.abc

collections.Mapping = collections.abc.Mapping

from rules import SmartFlowerEngine


def run_project():
    engine = SmartFlowerEngine()
    engine.reset()  # DefFacts will seed initial facts

    print("Smart Flower Exhibition Knowledge-Based System")
    print("----------------------------------------------")

    print("A* search started.")
    engine.run()


run_project()
