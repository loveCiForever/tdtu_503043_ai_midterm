from itertools import groupby
from heapq import heappop, heappush
from .game import Game


class Pathfinder:
    def __init__(self, src: Game):
        self.src = src

    def estimate(self, game: Game) -> int:
        nodes = list(game.pearls) + list(game.gems) + [game.player]

        if not nodes:
            return 0
        
        mst_cost = 0
        visited = set()
        min_heap = [(0, nodes[0])]

        while min_heap and len(visited) < len(nodes):
            cost, (x, y) = heappop(min_heap)

            if (x, y) in visited:
                continue
            visited.add((x, y))

            mst_cost += cost

            for nx, ny in nodes:
                if (nx, ny) in visited:
                    continue

                heappush(min_heap, (abs(nx - x) + abs(ny - y), (nx, ny)))

        return mst_cost

    def find(self) -> list[str]:
        frontier = [(self.estimate(self.src), 0, self.src.player, self.src.pearls, self.src.gems, self.src.ghost_turns, [])]
        visited = set()

        while frontier:
            _, g_cost, player, pearls, gems, ghost_turns, path = heappop(frontier)
            game = Game(self.src.w, self.src.h, player, pearls, gems, self.src.walls, ghost_turns)

            if hash(game) in visited:
                continue
            visited.add(hash(game))

            if not game.pearls:
                return path
            
            for direction, new_pos in game.get_moves().items():
                new_game = game.move_to(new_pos)
                new_g_cost = g_cost + 1
                new_f_cost = new_g_cost + self.estimate(new_game)
                new_path = path + [direction]

                if hash(new_game) in visited:
                    continue
                
                heappush(frontier, (new_f_cost, new_g_cost, new_game.player, new_game.pearls, new_game.gems, new_game.ghost_turns, new_path))

        return []
    

def compress_path(path: list[str]) -> str:
    return " ".join(f"{direction[0]}{len(list(group))}" for direction, group in groupby(path))
