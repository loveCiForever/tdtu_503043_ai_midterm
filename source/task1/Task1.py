from collections import deque
from copy import deepcopy
from graphviz import Digraph
import heapq

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

class PuzzleAgent:
    @classmethod
    def solve(cls, initial_state, goal_state, heuristic_func, graph_depth=20):
        dot = Digraph()
        explored = set()
        drawn = set()

        puzzle = Puzzle(initial_state, g=0, h=heuristic_func(initial_state, goal_state))
        open_set = [puzzle]
        heapq.heapify(open_set)

        while open_set:
            curr = heapq.heappop(open_set)
            if curr.state == goal_state:
                node = curr
                while node:
                    if node.get_id() not in drawn:
                        node.draw(dot)
                        drawn.add(node.get_id())
                    node = node.parent
                return {"goal_node": curr, "cost": curr.g, "actions": curr.get_solution_path()}, dot

            explored.add(str(curr.state))
            if curr.g < graph_depth and curr.get_id() not in drawn:
                curr.draw(dot)
                drawn.add(curr.get_id())

            for n in curr.get_successors():
                if str(n.state) in explored:
                    continue
                if any(str(n.state) == str(x.state) for x in open_set):
                    continue
                n.g = curr.g + 1
                n.h = heuristic_func(n.state, goal_state)
                n.f = n.g + n.h
                heapq.heappush(open_set, n)

        return None, dot

def h_manhattan(state, goal):
    distance = 0
    for i in range(1, 9):
        pos1, pos2 = Puzzle.get_pos(state, i), Puzzle.get_pos(goal, i)
        if pos1 and pos2:
            distance += abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    return distance

def export_solution_steps(result, filename="solution_steps.txt"):
    def flatten(state):
        return ''.join(str(x) if x != 0 else '_' for row in state for x in row)

    def check_swap(prev, curr):
        for a, b in [(1, 3), (2, 4)]:
            pos_a = Puzzle.get_pos(prev, a)
            pos_b = Puzzle.get_pos(prev, b)
            if pos_a and pos_b and \
               curr[pos_a[0]][pos_a[1]] == b and curr[pos_b[0]][pos_b[1]] == a:
                return True
        return False

    path, node = [], result["goal_node"]
    while node:
        path.append(node)
        node = node.parent
    path.reverse()

    lines = [f"{'Step':<5} {'State':<12} {'Action':<8} {'Swap'}", "-" * 35]
    for i in range(len(path)):
        state_str = flatten(path[i].state)
        action = path[i].action or ""
        swap = "Yes" if i > 0 and check_swap(path[i-1].state, path[i].state) else ""
        lines.append(f"{i:<5} {state_str:<12} {action:<8} {swap}")

    with open(filename, "w") as f:
        f.write("\n".join(lines))
    for line in lines:
        print(line)


initial_state = [
    [4, 5, 0],
    [8, 1, 3],
    [7, 2, 6]
]

goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

result, dot = PuzzleAgent.solve(initial_state, goal_state, h_manhattan)
if result:
    export_solution_steps(result)
    dot.render("result", format="png", cleanup=True)
else:
    print("No solution found.")
