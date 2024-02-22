import itertools

import search_325028967_213125164
import random
import math



ids = ["325028967", "213125164"]


class OnePieceProblem(search_325028967_21312564.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        for i, row in enumerate(initial["map"]):  # find base location
            for j, loc in enumerate(row):
                if loc == "B":
                    self.base = (i, j)
        self.ship_to_index = {}  # convert ship names and treasure names to indexes
        self.treasure_to_index = {}
        self.map = initial["map"]  # map as is in initial
        self.pirates = initial["pirate_ships"]
        for i, key in enumerate(self.pirates.keys()):
            self.ship_to_index[i] = key

        self.num_of_pirates = len(self.pirates)
        self.treasures = list(initial["treasures"].items())
        for i, item in enumerate(self.treasures):
            self.treasure_to_index[i] = item[0]
        marines = list(initial["marine_ships"].values())
        for i in range(len(marines)):  # fix marines route so its circular
            if len(marines[i]) > 1:
                ret_path = []
                for j in marines[i][-2:0:-1]:
                    ret_path.append(j)
                marines[i] += ret_path
        self.marine_ships = marines
        marines_state = tuple(0 for i in range(len(self.marine_ships)))
        pirate_state = tuple(self.pirates.values())
        treasure_state = tuple((-1,) for i in range(len(self.treasures)))
        initial_state = (pirate_state, marines_state, treasure_state)
        self.distances = floyd_warshall(self.map)  # implemented least distance matrix
        self.impossible = check_impossible(self.treasures, self.map)
        search_325028967_21312564.Problem.__init__(self, initial_state)
        
    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        # state = (ships=(loc),marines=(loc),treasures=())
        ships = state[0]
        treasures_ = state[2]
        generators = []
        for i in range(len(ships)):
            generators.append(self.atomic_action(i, ships[i], treasures_))
        #  cartesean product of atomic actions
        for action in itertools.product(*generators):
            yield action

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        list_state = list(state)
        ships = list(list_state[0])
        marines = list(list_state[1])
        treasures_ = list(list_state[2])
        ship_num = 0
        treasure_num = 0
        # convert name to index
        for atomic_action in action:
            for i, name in self.ship_to_index.items():
                if atomic_action[1] == name:
                    ship_num = i
                    break
            #  change location
            if atomic_action[0] == "sail":
                ships[ship_num] = atomic_action[2]
            # deposit: remove info about ship carrying treasure
            if atomic_action[0] == "deposit_treasures":
                for i in range(len(treasures_)):
                    cur_treasure = list(treasures_[i])
                    if ship_num+1 in cur_treasure:
                        if 0 not in cur_treasure:
                            cur_treasure.append(0)
                        cur_treasure.remove(ship_num+1)
                    treasures_[i] = tuple(sorted(cur_treasure))
            # add information about ship carrying treasure
            if atomic_action[0] == "collect":
                for i, name in self.treasure_to_index.items():
                    if atomic_action[2] == name:
                        treasure_num = i
                        break
                new_treasure = list(treasures_[treasure_num])
                new_treasure.append(ship_num+1)
                if -1 in new_treasure:
                    new_treasure.remove(-1)
                treasures_[treasure_num] = tuple(sorted(new_treasure))
        # advance marine ships
        for i in range(len(self.marine_ships)):
            if marines[i] == len(self.marine_ships[i])-1:
                marines[i] = 0
            else:
                loc = marines[i]
                marines[i] = loc+1
        # check if marines removes treasure
        for i in range(len(ships)):
            for j in range(len(marines)):
                if self.marine_ships[j][marines[j]] == ships[i]:
                    for k in range(len(treasures_)):
                        if i+1 in treasures_[k]:
                            lost_treasure = list(treasures_[k])
                            if len(lost_treasure) == 1 and 0 not in lost_treasure:
                                lost_treasure.append(-1)
                            lost_treasure.remove(i+1)
                            treasures_[k] = tuple(sorted(lost_treasure))
        next_state = (tuple(ships), tuple(marines), tuple(treasures_))
        return next_state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        # if every treasure is in base
        for places in state[2]:
            if 0 not in places:
                return False
        return True

    def h(self, node):
        if self.num_of_pirates == 1:
            return self.h1plus(node)
        return max(self.h3(node), self.h4(node))

    def h4(self, node):
        state = node.state
        ships = state[0]
        treasures_ = state[2]
        sum_of_dist = 0
        treasure_in_ships = [0] * len(ships)
        uncollected = []
        for i in range(len(treasures_)):
            if 0 not in treasures_[i]:
                if treasures_[i][0] != -1:
                    for ship in treasures_[i]:
                        treasure_in_ships[ship - 1] += 1
                else:
                    uncollected.append(i)
        uncollected_locations = []
        space_locations = []
        for name, loc in self.treasures:
            cur_treasure = 0
            for id_, name_ in self.treasure_to_index.items():
                if name == name_:
                    cur_treasure = id_
                    break
            if cur_treasure in uncollected:
                uncollected_locations.append(loc)

        for i, loc in enumerate(ships):
            treasure_in_ship = treasure_in_ships[i]
            if treasure_in_ship == 2 or (treasure_in_ship == 1 and len(uncollected) == 0):
                sum_of_dist += l1(self.base, ships[i])
            else:
                space_locations.append(loc)
        if len(uncollected) > 0:
            for loc in uncollected_locations:
                if len(space_locations) > 0:
                    sum_of_dist += l1(self.base, loc) + min(l1(loc, ship) for ship in space_locations)
        return float(sum_of_dist)

    def h3(self, node):
        # distance of the num of pirates farthest treasures
        if self.impossible:
            return float("inf")
        state = node.state
        ships = state[0]
        treasures_ = state[2]
        dist_to_base = []
        uncollected = 0
        for i, treasure in enumerate(treasures_):
            if 0 in treasure:
                continue
            check = []
            if -1 in treasure:
                loc = self.treasures[i][1]
                if not loc[0] == 0:  # up
                    if self.map[loc[0] - 1][loc[1]] == 'S':
                        check.append((loc[0] - 1, loc[1]))
                if not loc[0] == len(self.map) - 1:  # down
                    if self.map[loc[0] + 1][loc[1]] == 'S':
                        check.append((loc[0] + 1, loc[1]))
                if not loc[1] == 0:  # left
                    if self.map[loc[0]][loc[1] - 1] == 'S':
                        check.append((loc[0], loc[1] - 1))
                if not loc[1] == len(self.map[0]) - 1:  # right
                    if self.map[loc[0]][loc[1] + 1] == 'S':
                        check.append((loc[0], loc[1] + 1))
            else:
                for j in treasure:
                    check.append(ships[j-1])
            dist_to_base.append(min(self.distances[self.base][place] for place in check))
        dist_to_base = sorted(dist_to_base, reverse=True)
        if len(dist_to_base) > self.num_of_pirates:
            return sum(dist_to_base[:self.num_of_pirates]) + self.num_of_pirates
        return sum(dist_to_base) + 1

    def h_1(self, node):
        """ number of uncollected treasures divided by number of pirates"""
        treasures_ = node.state[2]
        counter = 0
        for treasure in treasures_:
            if -1 in treasure:
                counter += 1
        return float(counter) / self.num_of_pirates

    def h1plus(self, node):
        """ number of uncollected treasures divided by number of pirates"""
        treasures_ = node.state[2]
        counter = 0.0
        for treasure in treasures_:
            if -1 in treasure:
                counter += 1.5
            elif 0 not in treasure:
                counter += 0.5
        return float(counter)

    def h_2(self, node):
        """ Sum of the distances from the pirate base to the closest sea
         cell adjacent to a treasure - for each treasure, divided by the
          number of pirates. If there is a treasure which all the adjacent cells are islands – return infinity. """
        if self.impossible:
            return float('inf')
        state = node.state
        ships = state[0]
        treasures_ = state[2]
        sum_of_dist = 0
        for i in range(len(treasures_)):
            if 0 not in treasures_[i]:
                if -1 in treasures_[i]:
                    for j in range(len(self.treasures)):
                        cur_treasure = 0
                        for id_, name in self.treasure_to_index.items():
                            if self.treasures[j][0] == name:
                                cur_treasure = id_
                                break
                        if cur_treasure == i:
                            check = []
                            loc = self.treasures[j][1]
                            if not loc[0] == 0:  # up
                                if self.map[loc[0]-1][loc[1]] == 'S':
                                    check.append((loc[0]-1, loc[1]))
                            if not loc[0] == len(self.map) - 1:  # down
                                if self.map[loc[0]+1][loc[1]] == 'S':
                                    check.append((loc[0]+1, loc[1]))
                            if not loc[1] == 0:  # left
                                if self.map[loc[0]][loc[1]-1] == 'S':
                                    check.append((loc[0], loc[1]-1))
                            if not loc[1] == len(self.map[0]) - 1:  # right
                                if self.map[loc[0]][loc[1]+1] == 'S':
                                    check.append((loc[0], loc[1]+1))
                            sum_of_dist += min(l1(self.base, k) for k in check)
                else:
                    check = []
                    for j in range(len(treasures_[i])):
                        loc = ships[treasures_[i][j]-1]
                        if not loc[0] == 0:  # up
                            if self.map[loc[0] - 1][loc[1]] == 'S':
                                check.append((loc[0] - 1, loc[1]))
                        if not loc[0] == len(self.map) - 1:  # down
                            if self.map[loc[0] + 1][loc[1]] == 'S':
                                check.append((loc[0] + 1, loc[1]))
                        if not loc[1] == 0:  # left
                            if self.map[loc[0]][loc[1] - 1] == 'S':
                                check.append((loc[0], loc[1] - 1))
                        if not loc[1] == len(self.map[0]) - 1:  # right
                            if self.map[loc[0]][loc[1] + 1] == 'S':
                                check.append((loc[0], loc[1] + 1))
                    sum_of_dist += min(l1(self.base, k) for k in check)
        return float(sum_of_dist)/self.num_of_pirates

    def atomic_action(self, i, ship, treasures_):
        # returns all actions for a singles ship
        loc = ship
        # sail actions
        if not loc[0] == 0:  # up
            if self.map[loc[0]-1][loc[1]] != 'I':
                action = ("sail", self.ship_to_index[i], (loc[0]-1, loc[1]))
                yield action
        if not loc[0] == len(self.map) - 1:  # down
            if self.map[loc[0]+1][loc[1]] != 'I':
                action = ("sail", self.ship_to_index[i], (loc[0]+1, loc[1]))
                yield action
        if not loc[1] == 0:  # left
            if self.map[loc[0]][loc[1]-1] != 'I':
                action = ("sail", self.ship_to_index[i], (loc[0], loc[1]-1))
                yield action
        if not loc[1] == len(self.map[0]) - 1:  # right
            if self.map[loc[0]][loc[1]+1] != 'I':
                action = ("sail", self.ship_to_index[i], (loc[0], loc[1]+1))
                yield action

        # collect actions
        counter = 0
        space = True
        for j in range(len(treasures_)):
            if i+1 in treasures_[j]:
                counter += 1
            if counter == 2:
                space = False
                break
        if space:

            for name, loc in self.treasures:
                next_iter = False
                for j, name_ in self.treasure_to_index.items():
                    if i+1 in treasures_[j] and name == name_:
                        next_iter = True
                        break
                if next_iter:
                    continue
                if abs(ship[0] - loc[0]) == 1 and \
                        ship[1] - loc[1] == 0:
                    action = ("collect", self.ship_to_index[i], name)
                    yield action
                elif abs(ship[1] - loc[1]) == 1 and \
                        ship[0] - loc[0] == 0:
                    action = ("collect", self.ship_to_index[i], name)
                    yield action
        # deposit and wait actions
        if ship[0] - self.base[0] == 0 and \
                ship[1] - self.base[1] == 0:
            for cur in treasures_:
                if i+1 in cur:
                    action = ("deposit_treasures", self.ship_to_index[i])
            yield action
        action = ("wait", self.ship_to_index[i])
        yield action


def check_impossible(treasures, map_):
    # check if there is no way to retrieve all the treasures
    for name, loc in treasures:
        if not loc[0] == 0:  # up
            if map_[loc[0] - 1][loc[1]] != 'I':
                continue
        if not loc[0] == len(map_) - 1:  # down
            if map_[loc[0] + 1][loc[1]] != 'I':
                continue
        if not loc[1] == 0:  # left
            if map_[loc[0]][loc[1] - 1] != 'I':
                continue
        if not loc[1] == len(map_[0]) - 1:  # right
            if map_[loc[0]][loc[1] + 1] != 'I':
                continue
        return True
    return False


def l1(a, b):  # manhattan distance
    xa, ya = a
    xb, yb = b
    dist = abs(xa-xb)+abs(ya-yb)
    return dist


def floyd_warshall(map):
    dist = {} # matrix of distances from points on the map
    # create main dict keys
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] != 'I':
                dist[(i, j)] = {}
    # init distances
    for start in dist:
        i, j = start
        for end in dist:
            k, l = end
            dist[start][end] = float('inf')
            if i == k:
                if j == l:
                    dist[start][end] = 0
                elif l == j+1 or l == j-1:
                    dist[start][end] = 1
            elif j == l and (k == i+1 or k == i-1):
                dist[start][end] = 1
    for point1 in dist:
        for point2 in dist:
            for point3 in dist:
                if dist[point2][point3] > dist[point2][point1] + dist[point1][point3]:
                    dist[point2][point3] = dist[point2][point1] + dist[point1][point3]
    return dist


def create_onepiece_problem(game):
    return OnePieceProblem(game)
