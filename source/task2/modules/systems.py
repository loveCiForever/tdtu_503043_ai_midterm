from .components import *


class System:
    def update(self, game):
        ...


class MoveAndTeleportSystem(System):
    @classmethod
    def get_next_pos(cls, game, x: int, y: int, dx: int, dy: int, is_ghosting: bool) -> tuple[int, int]:        
        new_x = x + dx
        new_y = y + dy

        for other_entity in game.entities.get_by_comp(ObstacleComp):
            other_pos = other_entity.get(PosComp)

            if (other_pos.x, other_pos.y) == (new_x, new_y) and (
                not other_entity.get(ObstacleComp).ghostable
                or not is_ghosting
            ):
                return x, y

        for portal in game.entities.get_by_comp(TeleportableComp):
            portal_pos = portal.get(PosComp)

            if (portal_pos.x, portal_pos.y) == (new_x, new_y):
                teleport = portal.get(TeleportableComp)
                new_x = teleport.tx
                new_y = teleport.ty
                break

        return new_x, new_y

    def update(self, game):
        for entity in game.entities.get_by_comp(DirectionComp):
            pos = entity.get(PosComp)
            direction = entity.get(DirectionComp)

            pos.x, pos.y = self.get_next_pos(game,
                pos.x, pos.y, direction.dx, direction.dy,
                entity.has(GhostComp) and entity.get(GhostComp).turns > 0
            )


class ConsumeSystem(System):
    def update(self, game) -> int:
        score = 0

        for entity in game.entities.get_by_comp(ConsumerComp):
            player_pos = entity.get(PosComp)

            for consumable in game.entities.get_by_comp(ConsumableComp):
                consumable_pos = consumable.get(PosComp)

                if (consumable_pos.x, consumable_pos.y) == (player_pos.x, player_pos.y):
                    score += consumable.get(ConsumableComp).points

                    if consumable.has(PowerUpComp) and entity.has(GhostComp):
                        entity.get(GhostComp).activate()

                    game.entities.remove(consumable)
        
        return score
    

class GhostSystem(System):
    def update(self, game):
        for entity in game.entities.get_by_comp(GhostComp):
            ghost_comp = entity.get(GhostComp)
            ghost_comp.use()
