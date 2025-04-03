import pygame
import sys
import ast
from pygame.locals import *
from copy import deepcopy
goal_states = [
    [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 0]],

    [[8, 7, 6],
     [5, 4, 3],
     [2, 1, 0]],

    [[0, 1, 2],
     [3, 4, 5],
     [6, 7, 8]],

    [[0, 8, 7],
     [6, 5, 4],
     [3, 2, 1]]
]
class Puzzle:
    def __init__(self, state, action=None, parent=None, g=0, h=0):
        self.state = state
        self.id = str(self.state)
        self.action = action
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(str(self.state))

    def __lt__(self, other):
        return self.f < other.f

    def __str__(self):
        return "\n".join("".join(str(e) for e in r) for r in self.state)

    @staticmethod
    def get_pos(state, val):
        for i in range(3):
            for j in range(3):
                if state[i][j] == val:
                    return i, j
        return None

    @staticmethod
    def check_neighbor(state, a, b):
        pos_a, pos_b = Puzzle.get_pos(state, a), Puzzle.get_pos(state, b)
        if not pos_a or not pos_b:
            return False
        return (pos_a[0] == pos_b[0] and abs(pos_a[1] - pos_b[1]) == 1) or \
               (pos_a[1] == pos_b[1] and abs(pos_a[0] - pos_b[0]) == 1)

    @staticmethod
    def swap(state, a, b):
        a_i, a_j = Puzzle.get_pos(state, a)
        b_i, b_j = Puzzle.get_pos(state, b)
        state[a_i][a_j], state[b_i][b_j] = state[b_i][b_j], state[a_i][a_j]

    def get_dest_pos(self, action, pi, pj):
        return {
            'L': (pi, pj + 1),
            'R': (pi, pj - 1),
            'U': (pi + 1, pj),
            'D': (pi - 1, pj),
        }.get(action, (pi, pj))

    def get_successor(self, action, state):
        pi, pj = Puzzle.get_pos(state, 0)
        ni, nj = self.get_dest_pos(action, pi, pj)
        if 0 <= ni < 3 and 0 <= nj < 3:
            state[pi][pj], state[ni][nj] = state[ni][nj], 0
            return state
        return None

    def get_successors(self):
        was_13 = Puzzle.check_neighbor(self.state, 1, 3)
        was_24 = Puzzle.check_neighbor(self.state, 2, 4)
        successors = []

        for act in ['L', 'R', 'U', 'D']:
            new_state = self.get_successor(act, deepcopy(self.state))
            if new_state is None:
                continue
            if Puzzle.check_neighbor(new_state, 1, 3) and not was_13:
                Puzzle.swap(new_state, 1, 3)
            if Puzzle.check_neighbor(new_state, 2, 4) and not was_24:
                Puzzle.swap(new_state, 2, 4)
            successors.append(Puzzle(new_state, act, self))

        return successors

    def get_id(self):
        return self.id

    def get_action(self):
        return self.action

    def get_solution_path(self):
        path, node = [], self
        while node.parent:
            path.append(node.action)
            node = node.parent
        return path[::-1]

    def draw(self, dot):
        label = self.get_id()
        flat = [x for row in self.state for x in row]
        tile = lambda x: " " if x == 0 else str(x)
        table = f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD>{tile(flat[0])}</TD><TD>{tile(flat[1])}</TD><TD>{tile(flat[2])}</TD></TR>
            <TR><TD>{tile(flat[3])}</TD><TD>{tile(flat[4])}</TD><TD>{tile(flat[5])}</TD></TR>
            <TR><TD>{tile(flat[6])}</TD><TD>{tile(flat[7])}</TD><TD>{tile(flat[8])}</TD></TR>
            </TABLE>>'''
        dot.node(label, table, shape="plaintext")
        if self.parent:
            dot.edge(self.parent.get_id(), self.get_id(), label=self.get_action())
class PuzzleGame:
    def __init__(self, puzzle):
        pygame.init()
        self.puzzle = puzzle
        self.screen = pygame.display.set_mode((300, 300))
        pygame.display.set_caption('8 Puzzle Game')
        self.font = pygame.font.SysFont(None, 60)
        self.goal_font = pygame.font.SysFont(None, 40)
        self.running = True
        self.completed = False

    def draw_board(self):
        self.screen.fill((255, 255, 255))
        for i in range(3):
            for j in range(3):
                value = self.puzzle.state[i][j]
                rect = pygame.Rect(j * 100, i * 100, 100, 100)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 3)
                if value != 0:
                    text = self.font.render(str(value), True, (0, 0, 0))
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
        if self.completed:
            msg = self.goal_font.render("Complete", True, (0, 128, 0))
            self.screen.blit(msg, (30, 130))
        pygame.display.flip()

    def is_goal_state(self):
        return any(self.puzzle.state == goal for goal in goal_states)

    def handle_key(self, key):
        if self.completed:
            return
        move_map = {
            K_LEFT: 'L',
            K_RIGHT: 'R',
            K_UP: 'U',
            K_DOWN: 'D'
        }
        if key in move_map:
            action = move_map[key]
            for next_puzzle in self.puzzle.get_successors():
                if next_puzzle.action == action:
                    self.puzzle = next_puzzle
                    if self.is_goal_state():
                        self.completed = True
                    break

    def run(self):
        while self.running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    self.handle_key(event.key)
        pygame.quit()
        sys.exit()

def get_initial_state():
    print("Import intial state ([[1,2,3],[4,5,6],[7,8,0]]):")
    while True:
        try:
            input_str = input(">>> ")
            state = ast.literal_eval(input_str)
            flat = [cell for row in state for cell in row]
            if isinstance(state, list) and len(state) == 3 and all(len(row) == 3 for row in state) and sorted(flat) == list(range(9)):
                return state
        except:
            pass
        print("Error")

if __name__ == '__main__':
    initial_state = get_initial_state()
    puzzle = Puzzle(initial_state)
    game = PuzzleGame(puzzle)
    game.run()