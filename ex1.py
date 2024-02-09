import itertools

import search
import random
import math
from utils import distance


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
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return self.h2(node)

    def h1(self, node):
        """ number of uncollected treasures divided by number of pirates"""
        treasures_ = node.state[2]
        counter = 0
        for treasure in treasures_:
            if -1 not in treasure:
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
                                if self.map[loc[0]-1][loc[1]] != 'I':
                                    check.append((loc[0]-1, loc[1]))
                            if not loc[0] == len(self.map) - 1:  # down
                                if self.map[loc[0]+1][loc[1]] != 'I':
                                    check.append((loc[0]+1, loc[1]))
                            if not loc[1] == 0:  # left
                                if self.map[loc[0]][loc[1]-1] != 'I':
                                    check.append((loc[0], loc[1]-1))
                            if not loc[1] == len(self.map[0]) - 1:  # right
                                if self.map[loc[0]][loc[1]+1] != 'I':
                                    check.append((loc[0], loc[1]+1))
                            sum_of_dist += min(distance(self.base, k) for k in check)

                elif len(treasures_[i]) == 1:
                    sum_of_dist += distance(ships[treasures_[i][0]-1], self.base)
                elif len(treasures_[i]) > 1:
                    sum_of_dist += min(distance(ships[k-1], self.base) for k in treasures_[i])
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


def create_onepiece_problem(game):
    return OnePieceProblem(game)
