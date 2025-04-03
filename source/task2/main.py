import time
from modules import Game, Pathfinder, Renderer, compress_path

TITLE = "Wilbur's Wavy Waters v2.0"


def main():
    with open("input.txt", "r") as map_file:
        game = Game.load_map(map_file.read())
        pathfinder = Pathfinder(game)

        print("\nComputing path, please wait...")

        pathfind_time = time.time()
        path = pathfinder.find()
        pathfind_duration = time.time() - pathfind_time

        print(
            f"\n{"Pathfinding complete!":^25}\n{"=" * 25}",
            f"\nPathfind duration: {pathfind_duration:.2f}s",
            f"\nTotal cost: {len(path)}"
        )

        print("\nPath:", compress_path(path))

        renderer = Renderer(game, TITLE, 1280, 720)
        renderer.run(path)


if __name__ == "__main__":
    main()
