import itertools

import search
import random
import math


ids = ["325028967", "213125164"]


class OnePieceProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        for i, row in enumerate(initial["map"]):  # find base location
            for j, loc in enumerate(row):
                if loc == "B":
                    self.base = (i, j)
        self.map = initial["map"]  # map as is in initial
        self.pirates = initial["pirate_ships"]

        self.num_of_pirates = len(self.pirates)
        self.treasures = list(initial["treasures"].items())
        marines = list(initial["marine_ships"].values())
        for i in range(len(marines)):
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
        search.Problem.__init__(self, initial_state)
        
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
        for atomic_action in action:
            ship_num = int(atomic_action[1][-1])-1
            if atomic_action[0] == "sail":
                ships[ship_num] = atomic_action[2]
            if atomic_action[0] == "deposit":
                for i in range(len(treasures_)):
                    cur_treasure = list(treasures_[i])
                    if ship_num+1 in cur_treasure:
                        if 0 not in cur_treasure:
                            cur_treasure.append(0)
                        cur_treasure.remove(ship_num+1)
                    treasures_[i] = tuple(sorted(cur_treasure))
            if atomic_action[0] == "collect":
                treasure_num = int(atomic_action[2][-1])-1
                new_treasure = list(treasures_[treasure_num])
                new_treasure.append(ship_num+1)
                if -1 in new_treasure:
                    new_treasure.remove(-1)
                treasures_[treasure_num] = tuple(sorted(new_treasure))

        for i in range(len(self.marine_ships)):
            if marines[i] == len(self.marine_ships[i])-1:
                marines[i] = 0
            else:
                loc = marines[i]
                marines[i] = loc+1

        for i in range(len(ships)):
            for j in range(len(marines)):
                if self.marine_ships[j][marines[j]] == ships[i]:
                    for k in range(len(treasures_)):
                        if i+1 in treasures_[k]:
                            lost_treasure = list(treasures_[k])
                            if len(lost_treasure) == 1:
                                lost_treasure.append(-1)
                            lost_treasure.remove(i+1)
                            treasures_[k] = tuple(sorted(lost_treasure))
        next_state = (tuple(ships), tuple(marines), tuple(treasures_))
        return next_state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for places in state[2]:
            if 0 not in places:
                return False
        return True

    def h(self, node):
        if self.check_impossible():
            return float('inf')
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
            if (int(name[-1]))-1 in uncollected:
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
        return sum_of_dist/self.num_of_pirates

    def h3(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        if self.check_impossible():
            return float('inf')
        state = node.state
        ships = state[0]
        treasures_ = state[2]
        sum_of_dist = 0
        treasure_in_ships = [0]*len(ships)
        uncollected = []
        for i in range(len(treasures_)):
            if 0 not in treasures_[i]:
                if treasures_[i][0] != -1:
                    for ship in treasures_[i]:
                        treasure_in_ships[ship-1] += 1
                else:
                    uncollected.append(i)
        uncollected_locations = []

        for name, loc in self.treasures:
            if (int(name[-1]))-1 in uncollected:
                uncollected_locations.append(loc)
        for i, treasure_amount in enumerate(treasure_in_ships):
            if treasure_amount == 2 or (treasure_amount == 1 and len(uncollected) == 0):
                sum_of_dist += l1(ships[i], self.base)
            elif treasure_amount == 1:
                if len(uncollected) > 0:
                    dist_to_treasure = min(l1(ships[i], j)+l1(j, self.base) for j in uncollected_locations)
                    if self.num_of_pirates == 1:
                        sum_of_dist += dist_to_treasure
                    else:
                        sum_of_dist += min(dist_to_treasure, l1(self.base, ships[i]))
            else:
                if len(uncollected) > 0:
                    sum_of_dist += min(l1(ships[i], j)+l1(j, self.base) for j in uncollected_locations)
        return float(sum_of_dist)/self.num_of_pirates

    def h1(self, node):
        """ number of uncollected treasures divided by number of pirates"""
        treasures_ = node.state[2]
        counter = 0
        for treasure in treasures_:
            if -1 in treasure:
                counter += 1
        return float(counter) / self.num_of_pirates

    def h2(self, node):
        """ Sum of the distances from the pirate base to the closest sea
         cell adjacent to a treasure - for each treasure, divided by the
          number of pirates. If there is a treasure which all the adjacent cells are islands – return infinity. """
        if self.check_impossible():
            return float('inf')
        state = node.state
        ships = state[0]
        treasures_ = state[2]
        sum_of_dist = 0
        for i in range(len(treasures_)):
            if 0 not in treasures_[i]:
                if -1 in treasures_[i]:
                    for j in range(len(self.treasures)):
                        if int(self.treasures[j][0][-1])-1 == i:
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

                elif len(treasures_[i]) == 1:
                    sum_of_dist += l1(ships[treasures_[i][0]-1], self.base)
                elif len(treasures_[i]) > 1:
                    sum_of_dist += min(l1(ships[k-1], self.base) for k in treasures_[i])
        return float(sum_of_dist)/self.num_of_pirates



    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def atomic_action(self, i, ship, treasures_):
        loc = ship
        # sail actions
        if not loc[0] == 0:  # up
            if self.map[loc[0]-1][loc[1]] != 'I':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0]-1, loc[1]))
                yield action
        if not loc[0] == len(self.map) - 1:  # down
            if self.map[loc[0]+1][loc[1]] != 'I':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0]+1, loc[1]))
                yield action
        if not loc[1] == 0:  # left
            if self.map[loc[0]][loc[1]-1] != 'I':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0], loc[1]-1))
                yield action
        if not loc[1] == len(self.map[0]) - 1:  # right
            if self.map[loc[0]][loc[1]+1] != 'I':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0], loc[1]+1))
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
                if i+1 in treasures_[int(name[-1])-1]:
                    continue
                if abs(ship[0] - loc[0]) == 1 and \
                        ship[1] - loc[1] == 0:
                    action = ("collect", "pirate_ship_" + str(i + 1), name)
                    yield action
                elif abs(ship[1] - loc[1]) == 1 and \
                        ship[0] - loc[0] == 0:
                    action = ("collect", "pirate_ship_" + str(i + 1), name)
                    yield action
        # deposit and wait actions
        if ship[0] - self.base[0] == 0 and \
                ship[1] - self.base[1] == 0:
            action = ("deposit", "pirate_ship_" + str(i + 1))
            yield action
        action = ("wait", "pirate_ship_" + str(i + 1))
        yield action

    def check_impossible(self):
        for name, loc in self.treasures:
            if not loc[0] == 0:  # up
                if self.map[loc[0] - 1][loc[1]] != 'I':
                    continue
            if not loc[0] == len(self.map) - 1:  # down
                if self.map[loc[0] + 1][loc[1]] != 'I':
                    continue
            if not loc[1] == 0:  # left
                if self.map[loc[0]][loc[1] - 1] != 'I':
                    continue
            if not loc[1] == len(self.map[0]) - 1:  # right
                if self.map[loc[0]][loc[1] + 1] != 'I':
                    continue
            return True
        return False


def l1(a, b):
    xa, ya = a
    xb, yb = b
    dist = abs(xa-xb)+abs(ya-yb)
    return dist


def create_onepiece_problem(game):
    return OnePieceProblem(game)
