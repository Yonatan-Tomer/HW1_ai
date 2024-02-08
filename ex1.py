import itertools

import search
import random
import math
from itertools import product


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
        self.treasures = initial["treasures"].items()
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
        treasure_state = tuple(-1 for i in range(len(self.treasures)))
        initial_state = (pirate_state, marines_state, treasure_state)
        search.Problem.__init__(self, initial_state)
        
    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        # state = (ships=(loc),marines=(loc),treasures=())
        ships = state[0]
        treasures = state[2]
        generators = []
        for i in range(len(ships)):
            generators.append(self.atomic_action(i, ships[i], treasures))

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
                    if treasures_[i] == ship_num+1:
                        treasures_[i] = 0
            if atomic_action[0] == "collect":
                treasure_num = int(atomic_action[2][-1])-1
                treasures_[treasure_num] = ship_num+1

        for i in range(len(self.marine_ships)):
            if marines[i] == len(self.marine_ships[i])-1:
                marines[i] = 0
            else:
                marines[i] = marines[i]+1

        for i in range(len(ships)):
            for j in range(len(marines)):
                if self.marine_ships[j][marines[j]] == ships[i]:
                    for k in range(len(treasures_)):
                        if treasures_[k] == i+1:
                            treasures_[k] = -1
        next_state = (tuple(ships), tuple(marines), tuple(treasures_))
        return next_state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for num in state[2]:
            if num != 0:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0

    def h1(self, node):
        """ number of uncollected treasures divided by number of pirates"""
        treasures_ = node.state[2]
        counter = 0
        for treasure in treasures_:
            if treasure != 0:
                counter += 1
        return float(counter) / self.num_of_pirates

    def h2(self, node):
        """ Sum of the distances from the pirate base to the closest sea
         cell adjacent to a treasure - for each treasure, divided by the
          number of pirates. If there is a treasure which all the adjacent cells are islands – return infinity. """
        state = node.state


    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def atomic_action(self, i, ship, treasures_):
        loc = ship
        # sail actions
        if not loc[0] == 0:  # up
            if self.map[loc[0]-1][loc[1]] == 'S':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0]-1, loc[1]))
                yield action
        if not loc[0] == len(self.map) - 1:  # down
            if self.map[loc[0]+1][loc[1]] == 'S':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0]+1, loc[1]))
                yield action
        if not loc[1] == 0:  # left
            if self.map[loc[0]][loc[1]-1] == 'S':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0], loc[1]-1))
                yield action
        if not loc[1] == len(self.map[0]) - 1:  # right
            if self.map[loc[0]][loc[1]+1] == 'S':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0], loc[1]+1))
                yield action

        # collect actions
        counter = 0
        space = True
        for j in treasures_:
            if j == i + 1:
                counter += 1
            if counter == 2:
                space = False
                break
        if space:
            for name, loc in self.treasures:
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

    def sail_actions(self, i, ship):

        loc = ship
        # sail actions
        if not loc[0] == 0:  # up
            if self.map[loc[0]][loc[1]-1] == 'S':
                action = ("sail", "pirate_ship_"+str(i+1), (loc[0], loc[1]-1))
                yield action
        if not loc[0] == len(self.map)-1:  # down
            if self.map[loc[0]][loc[1]+1] == 'S':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0], loc[1] + 1))
                yield action
        if not loc[1] == 0:  # left
            if self.map[loc[0]-1][loc[1]] == 'S':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0]-1, loc[1]))
                yield action
        if not loc[1] == len(self.map[0])-1:  # right
            if self.map[loc[0]+1][loc[1]] == 'S':
                action = ("sail", "pirate_ship_" + str(i + 1), (loc[0]+1, loc[1]))
                yield action

    def collect_actions(self, i,  ship, treasures):
        counter = 0
        space = True
        for j in treasures:
            if treasures[j] == i+1:
                counter += 1
            if counter == 2:
                space = False
        if space:
            for treasure in self.treasures:
                if abs(ship[0] - treasure[0]) == 1 and\
                   ship[1] - treasure[1] == 0:
                    action = ("collect", "pirate_ship_" + str(i + 1), treasure)
                    yield action
                elif abs(ship[1] - treasure[1]) == 1 and\
                        ship[0] - treasure[0] == 0:
                    action = ("collect", "pirate_ship_" + str(i + 1), treasure)
                    yield action

    def deposit_wait_actions(self, i, ship):

        if ship[0] - self.base[0] == 0 and \
                ship[1] - self.base[1] == 0:
            action = ("deposit", "pirate_ship_" + str(i+1))
            yield action
        action = ("wait", "pirate_ship_"+ str(i+1))
        yield action


def create_onepiece_problem(game):
    return OnePieceProblem(game)
