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
        for i, row in enumerate(self.map):  # find base location
            for j, loc in enumerate(row):
                if loc == "B":
                    self.base = tuple(i, j)
        self.treasure_in_base = set()
        self.map = initial["map"]  # map as is in initial
        #self.pirate_ships = {}  # list of all ships and treasures they have onboard
        #for ship in initial["pirate_ships"]:
            #self.pirateShips[ship] = {"location": initial["pirate_ships"][ship], "treasures": []}
        self.treasures = initial["treasures"]  # treasures as is in initial
        self.marine_ships = initial["marine_ships"]  #marine ships as is in initial
        search.Problem.__init__(self, initial)
        
    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        # state = {ships, marines}
        actions = []
        # sail

        # collect

        # deposit

        # wait

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        next_state = state
        for atomic_action in action:
            if atomic_action[0] == "sail":
                next_state["ships"][atomic_action[1]]["location"] = atomic_action[2]
            if atomic_action[0] == "deposit":
                self.treasure_in_base.update(next_state["ships"][atomic_action[1]]["treasure"])
                next_state["ships"][atomic_action[1]]["treasure"] = []
            if atomic_action[0] == "collect":
                next_state["ships"][atomic_action[1]]["treasure"].append(self.treasures[atomic_action[2]])

        for name, location in next_state["marines"].items():
            if location == len(self.marine_ships[name])-1:
                location == 0
            else:
                location += 1

        for pirate_name, pirate_data in next_state["ships"].items():
            for marine_name, marine_location in next_state["marines"].items:
                if self.marine_ships[marine_name][marine_location] == pirate_data["location"]:
                    next_state["ships"][pirate_name]["treasure"] = []

        return next_state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        return len(self.treasure_in_base) == len(self.treasures)

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def sail_actions(self, ships):

        for ship in ships:
            loc = ship["location"]
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

    def collect_actions(self, ships):
        for ship in ships:
            if len(ship[treasure]) < 3:
                for treasure in self.treasures:
                    if abs(ship["location"][0] - self.treasures[treasure][0]) == 1 and\
                       ship["location"][1] - self.treasures[treasure][1] == 0:
                        yield
                    if abs(ship["location"][1] - self.treasures[treasure][1]) == 1 and\
                       ship["location"][0] - self.treasures[treasure][0] == 0:
                        yield

    def deposit_actions(self, ships):
        for ship in ships:
            if ship["location"][0] - self.base[0] == 0 and \
                    ship["location"][1] - self.base[1] == 0:
                yield


def create_onepiece_problem(game):
    return OnePieceProblem(game)

