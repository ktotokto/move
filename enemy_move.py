from tools import load_level
import heapq


def load_level_move(level, walls):
    grid = []
    for y in range(len(level)):
        line = []
        for x in range(len(level[y])):
            line.append(9) if level[y][x] in walls else line.append(0)
        grid.append(line)
    return grid


cols, rows = 20, 8
TILE = 64
grid = load_level_move(load_level('maps/level_test.txt'), "#!")


def get_neighbours(x, y, grid):
    check_neighbour = lambda x, y: True if 0 <= x < cols and 0 <= y < rows else False
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


def move_a(start, end):
    graph = {}
    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            graph[(x, y)] = graph.get((x, y), []) + get_neighbours(x, y, grid)
    visited = dijkstra(start, end, graph)
    return visited[end] if end in visited else (0, 0)
