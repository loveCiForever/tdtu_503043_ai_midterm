Pos = tuple[int, int]

directions = {
    "WEST": (-1, 0),
    "EAST": (1, 0),
    "NORTH": (0, -1),
    "SOUTH": (0, 1)
}


class Game:
    def __init__(self, w: int, h: int, player: Pos, pearls: set[Pos], gems: set[Pos], walls: set[Pos], ghost_turns: int = 0):
        self.w, self.h = w, h
        self.player = player
        self.pearls = pearls
        self.gems = gems
        self.walls = walls
        self.ghost_turns = ghost_turns
        self.portals = [(1, 1), (self.w - 2, 1), (self.w - 2, self.h - 2), (1, self.h - 2)]

    @classmethod
    def load_map(cls, map_str: str) -> "Game":
        lines = map_str.strip().splitlines()
        w, h = len(lines[0]), len(lines)
        pearls, gems, walls = set(), set(), set()
        player = None
        
        for y, row in enumerate(lines):
            for x, char in enumerate(row):
                pos = (x, y)
                match (char):
                    case "P": player = pos
                    case ".": pearls.add(pos)
                    case "O": gems.add(pos)
                    case "%": walls.add(pos)

        return cls(w, h, player, pearls, gems, walls)
    
    def get_moves(self) -> dict[str, Pos]:
        x, y = self.player
        moves = {}

        for direction, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            new_pos = nx, ny

            if not (0 <= nx < self.w and 0 <= ny < self.h):
                continue
            if new_pos in self.walls and self.ghost_turns == 0:
                continue

            if new_pos in self.portals:
                new_pos = self.portals[(self.portals.index(new_pos) + 2) % 4]

            moves[direction] = new_pos

        return moves
    
    def move_to(self, new_pos: Pos) -> "Game":
        if new_pos == self.player:
            return self
        
        pearls = self.pearls.copy()
        gems = self.gems.copy()
        ghost_turns = max(self.ghost_turns - 1, 0)

        if new_pos in pearls:
            pearls.remove(new_pos)
        if new_pos in gems:
            ghost_turns = 5
            gems.remove(new_pos)

        return Game(self.w, self.h, new_pos, pearls, gems, self.walls, ghost_turns)
    
    def __hash__(self) -> int:
        return hash((self.player, frozenset(self.pearls), frozenset(self.gems), self.ghost_turns))

    def __str__(self) -> str:
        grid = [[" " for _ in range(self.w)] for _ in range(self.h)]

        for x, y in self.walls:
            grid[y][x] = "%"
        for x, y in self.pearls:
            grid[y][x] = "."
        for x, y in self.gems:
            grid[y][x] = "O"

        px, py = self.player
        grid[py][px] = "P"

        return "\n".join("".join(row) for row in grid)
