from tools import load_level
import heapq

TILE = 64
level_matrix = load_level('maps/level_test.txt')
cols, rows = len(level_matrix[0]), len(level_matrix)


class Loader:
    def __init__(self, level, walls):
        self.x_0, self.y_0 = 0, 0
        self.flag_init = True
        self.level = level
        self.walls = walls
        self.grid, self.new_grid = [], []
        for y in range(len(self.level)):
            line = []
            for x in range(len(self.level[y])):
                line.append(1000) if self.level[y][x] in self.walls else line.append(0)
            self.grid.append(line)

    def load_level_move(self, camera):
        global rows, cols
        x_offset, y_offset = camera.w // 64, camera.h // 64
        w_move, h_move = camera.w // 64 // 2 - 1, camera.h // 64 // 2 - 1
        if self.flag_init:
            for i in range(w_move):
                for j in range(rows):
                    self.grid[j].append(1000)
                    self.grid[j].insert(0, 1000)
            cols += (camera.w // 64 - 2)

            for i in range(h_move):
                self.grid.append([1000 for i in range(cols)])
                self.grid.insert(0, [1000 for i in range(cols)])
            cols += (camera.h // 64 - 2)
            self.flag_init = False

        self.new_grid = []
        for y in range(y_offset):
            line = []
            for x in range(x_offset):
                line.append(self.grid[y + h_move - self.y_0][x + w_move - self.x_0])
            self.new_grid.append(line)
        return self.new_grid

    def update_init_coord(self, camera):
        self.x_0 += camera.dx // 64
        self.y_0 += camera.dy // 64


loader_move = Loader(level_matrix, "#!D")


def get_neighbours(x, y, grid):
    check_neighbour = lambda x, y: True if 0 <= x < len(grid[0]) - 1 and 0 <= y < len(grid) - 1 else False
    ways = [-1, 0], [0, -1], [1, 0], [0, 1]
    return [(grid[y + dy][x + dx], (x + dx, y + dy)) for dx, dy in ways if check_neighbour(x + dx, y + dy)]


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def dijkstra(start, goal, graph):
    queue = []
    heapq.heappush(queue, (0, start))
    cost_visited = {start: 0}
    visited = {start: start}

    while queue:
        cur_cost, cur_node = heapq.heappop(queue)
        if cur_node == goal:
            break

        neighbours = graph[cur_node]
        for neighbour in neighbours:
            neigh_cost, neigh_node = neighbour
            new_cost = cost_visited[cur_node] + neigh_cost

            if neigh_node not in cost_visited or new_cost < cost_visited[neigh_node]:
                priority = new_cost + heuristic(neigh_node, goal)
                heapq.heappush(queue, (priority, neigh_node))
                cost_visited[neigh_node] = new_cost
                visited[neigh_node] = cur_node
    return visited


def move_a(start, end, camera):
    graph = {}
    grid = loader_move.load_level_move(camera)
    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            graph[(x, y)] = graph.get((x, y), []) + get_neighbours(x, y, grid)
    visited = dijkstra(start, end, graph)
    return visited[end] if end in visited else end
