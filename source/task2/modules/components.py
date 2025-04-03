import pygame


class Comp:
    ...


class NameComp(Comp):
    def __init__(self, name: str):
        self.name = name


class SpriteComp(Comp):
    def __init__(self, texture_atlas: pygame.Surface, sprite_x: int, sprite_y: int, tile_size: int):
        self.sprite = texture_atlas.subsurface((
            sprite_x * tile_size, sprite_y * tile_size, *[tile_size] * 2
        ))


class PosComp(Comp):
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y


class DirectionComp(Comp):
    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy


class TeleportableComp(Comp):
    def __init__(self, tx: int, ty: int):
        self.tx = tx
        self.ty = ty


class ConsumerComp(Comp):
    ...


class ConsumableComp(Comp):
    def __init__(self, points: int):
        self.points = points

    
class PowerUpComp(Comp):
    ...


class GhostComp(Comp):
    def __init__(self, max_turns: int):
        self.max_turns = max_turns
        self.turns = 0

    def activate(self):
        self.turns = self.max_turns

    def use(self):
        if self.turns > 0:
            self.turns -= 1


class ObstacleComp:
    def __init__(self, ghostable: bool=False):
        self.ghostable = ghostable
