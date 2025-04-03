import pygame
from .game import Game, Pos, directions


class Renderer:
    def __init__(self, src: Game, title: str, w: int, h: int, tile_size: int = 64, fps: int = 10):
        pygame.init()
        pygame.display.set_caption(title)

        self.src = src
        self.fps = fps
        self.w, self.h = w, h
        self.tile_size = tile_size

        self.screen = pygame.display.set_mode((w, h))
        self.surface = pygame.Surface((src.w * tile_size, src.h * tile_size))

        atlas = pygame.image.load("assets/texture_atlas.png").convert_alpha()
        self.sprites = {
            "wall": (0, 0),
            "portal": (1, 0),
            "player": (2, 0),
            "pearl": (0, 1),
            "gem": (1, 1)
        }
        for name, (x, y) in self.sprites.items():
            self.sprites[name] = atlas.subsurface((x * tile_size, y * tile_size, tile_size, tile_size))

        self.clock = pygame.time.Clock()
        self.is_running = True
        self.is_paused = True

        self.path_taken = [src.player]

        self.message = "Press [SPACE] to start!"
        self.is_message_visible = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if len(self.path_taken) == 1:
                    self.is_paused = False
                    self.is_message_visible = False

    def centre_point(self, point: int) -> int:
        return point * self.tile_size + self.tile_size // 2

    def draw_tile(self, sprite_name: str, x: int, y: int, alpha: int = 255):
        modified_sprite = self.sprites[sprite_name].copy()
        modified_sprite.set_alpha(alpha)

        self.surface.blit(modified_sprite, (x * self.tile_size, y * self.tile_size))
    
    def draw_hud(self, game: Game, direction: str, scaled_surface_height: int):
        hud_font = pygame.font.SysFont("monospace", 24, bold=True)

        hud_text = f"Path taken: {len(self.path_taken) - 1:<3}   Ghost turns: {game.ghost_turns}   Direction: {direction}"

        hud = hud_font.render(hud_text, True, pygame.Color("white"))
        hw, hh = hud.get_size()

        self.screen.blit(hud, (40, (self.h - scaled_surface_height - hh) // 2))

    def draw_message(self):
        if self.is_message_visible:
            message_font = pygame.font.SysFont("monospace", 48, bold=True)
            message_text = message_font.render(self.message, True, pygame.Color("white"))

            message_surface = pygame.Surface(message_text.get_size(), pygame.SRCALPHA)
            message_surface_width, _ = message_surface.get_size()
            message_surface.fill((0, 0, 0, 128))
            message_surface.blit(message_text, (0, 0))
            
            self.screen.blit(message_surface, (
                (self.w - message_surface_width) // 2,
                550
            ))

    def render(self, game: Game, direction: Pos, direction_name: str):
        self.screen.fill(pygame.Color("black"))
        self.surface.fill(pygame.Color("steelblue"))

        for x, y in game.portals:
            self.draw_tile("portal", x, y)
        for x, y in game.walls:
            is_boundary = x == 0 or x == game.w - 1 or y == 0 or y == game.h - 1
            self.draw_tile("wall", x, y, 128 if game.ghost_turns > 0 and not is_boundary else 255)
        for x, y in game.pearls:
            self.draw_tile("pearl", x, y)
        for x, y in game.gems:
            self.draw_tile("gem", x, y)

        for i in range(len(self.path_taken) - 1):
            sx, sy = self.path_taken[i]
            ex, ey = self.path_taken[i + 1]

            start_pos = self.centre_point(sx), self.centre_point(sy)
            end_pos = self.centre_point(ex), self.centre_point(ey)

            pygame.draw.line(self.surface, pygame.Color("midnightblue"), start_pos, end_pos, 4)

        px, py = game.player
        self.surface.blit(
            pygame.transform.rotate(
                pygame.transform.flip(self.sprites["player"], direction[0] == 1, False),
                90 * direction[1]
            ),
            (px * self.tile_size, py * self.tile_size)
        )

        scaled_surface = pygame.transform.smoothscale_by(self.surface, self.w / (game.w * self.tile_size))
        _, scaled_surface_height = scaled_surface.get_size()

        self.screen.blit(scaled_surface, (0, self.h - scaled_surface_height))

        self.draw_hud(game, direction_name, scaled_surface_height)
        self.draw_message()

        pygame.display.flip()

    def run(self, path: list[str]):
        game = self.src
        direction = "WEST"

        while self.is_running:
            self.clock.tick(self.fps)
            self.handle_input()
            self.render(game, directions[direction], direction)

            if not self.is_paused:
                if len(self.path_taken) < len(path) + 1:
                    direction = path[len(self.path_taken) - 1]
                    game = game.move_to(game.get_moves()[direction])

                    self.path_taken.append(game.player)
                else:
                    self.message = "All pearls collected!"
                    self.is_message_visible = True

                    self.is_paused = True
