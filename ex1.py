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
                    self.base = tuple(i, j)
        self.map = initial["map"]  # map as is in initial
        self.pirates = initial["pirate_ships"]
        self.num_of_pirates = len(self.pirates)
        self.treasures = initial["treasures"].values()
        self.marine_ships = initial["marine_ships"].values()
        search.Problem.__init__(self, initial)
        
    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        # state = (ships=(loc),marines=(loc),treasures=())
        ships = state[0]
        treasures = state[2]
        # sail

        # collect

        # deposit

        # wait

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        list_state = list(state)
        ships = list(list_state[0])
        marines = list(list_state[1])
        treasures = list(list_state[2])
        for atomic_action in action:
            ship_num = int(atomic_action[1][-1])-1
            if atomic_action[0] == "sail":
                ships[ship_num] = atomic_action[2]
            if atomic_action[0] == "deposit":
                for i in range(len(treasures)):
                    if treasures[i] == ship_num+1:
                        treasures[i] = 0
            if atomic_action[0] == "collect":
                treasure_num = int(atomic_action[2][-1])-1
                treasures[treasure_num] = ship_num+1

        for i in range(len(self.marine_ships)):
            if marines[i] == len(self.marine_ships[i])-1:
                marines[i] = 0
            else:
                marines[i] += 1

        for i in range(len(ships)):
            for j in range(len(marines)):
                if self.marine_ships[j][marines[j]] == ships[i]:
                    for k in range(len(treasures)):
                        if treasures[k] == i+1:
                            treasures[k] = -1

        return tuple(tuple(ships), tuple(marines), tuple(treasures))

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
        num_of_pirates = len(self.pirates)
        treasures = node.state[2]
        counter = 0
        for treasure in treasures:
            if treasure != 0:
                counter += 1
        return float(counter) / num_of_pirates

    def h2(self, node):
        """ Sum of the distances from the pirate base to the closest sea
         cell adjacent to a treasure - for each treasure, divided by the
          number of pirates. If there is a treasure which all the adjacent cells are islands – return infinity. """


    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def sail_actions(self, ships):

        for i in range(len(ships)):
            loc = ships[i]
            if not loc[0] == 0:  # up
                if self.map[loc[0]][loc[1]-1] == 'S':
                    yield
            if not loc[0] == len(self.map)-1:  # down
                if self.map[loc[0]][loc[1]+1] == 'S':
                    yield
            if not loc[1] == 0:  # left
                if self.map[loc[0]-1][loc[1]] == 'S':
                    yield
            if not loc[1] == len(self.map[0])-1:  # right
                if self.map[loc[0]+1][loc[1]] == 'S':
                    yield

    def collect_actions(self, ships, treasures):
        for i in range(len(ships)):
            counter = 0
            for j in treasures:
                if treasures[j] == i+1:
                    counter += 1
                if counter == 2:
                    return
            for treasure in self.treasures:
                if abs(ships[i][0] - treasure[0]) == 1 and\
                   ships[i][1] - treasure[1] == 0:
                    yield
                if abs(ships[i][1] - treasure[1]) == 1 and\
                   ships[i][0] - treasure[0] == 0:
                    yield

    def deposit_actions(self, ships):
        for i in range(len(ships)):
            if ships[i][0] - self.base[0] == 0 and \
                    ships[i][1] - self.base[1] == 0:
                yield


def create_onepiece_problem(game):
    return OnePieceProblem(game)
