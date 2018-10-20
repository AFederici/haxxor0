import gamelib
import random
import math
import queue
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

Additional functions are made available by importing the AdvancedGameState
class from gamelib/advanced.py as a replcement for the regular GameState class
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical
board states. Though, we recommended making a copy of the map to preserve
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]

        # index 0 is filter map and index 1 is desctructor map 2 is for encryptors
        self.previous_state = [[],[], []]
        self.attack_PING = True

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.AdvancedGameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.defend(game_state)
        self.attack(game_state)
        game_state.submit_turn()

    def defend(self, gs):
        MAIN_LINE_FILTER = [[0,13], [1,13], [2,13], [26,13],
                            [11,12], [16,12], [25,12],
                            [3,13], [4,12], [5,12],
                            [5,12], [6,12], [7,12], [8,12], [9,12], [10,12], [12,12], [13,12],
                            [14,12], [15,12], [17,12], [18,12], [19,12], [20,12], [21,12], [22,12],
                            [24,11],[23,10],
                            [22,9]]

        MAIN_LINE_DESTRUCTOR = [[-100,-100], [27,13],
                                [1,12], [2,12], [26,12],
                                [11,11], [16,11],
                                [25,11], [3,12], [19,11],
                                [18,11], [20,11], [24,10],
                                [23,9]]

        CORES = gs.get_resource(gs.CORES)

        # --------------------- PRIORITY 1 ---------------------
        #check preevious state for damage and addds to the to_build
        d_map = []
        f_map = []
        e_map = []
        to_build = []
        for j in range(13,-1,-1):
            for i in range(0,28):
                if gs.game_map.in_arena_bounds([i,j]):
                    x = gs.game_map[i, j]
                    if len(x) > 0:
                        if x[0].unit_type == FILTER:
                            f_map.append([i,j])
                        if x[0].unit_type == DESTRUCTOR:
                            d_map.append([i,j])
                        if x[0].unit_type == ENCRYPTOR:
                            e_map.append([i,j])
                    else:
                        if [i,j] in self.previous_state[0]:
                            to_build.append(([i,j], FILTER))
                        if [i,j] in self.previous_state[1]:
                            to_build.append(([i,j], DESTRUCTOR))
                        if [i,j] in self.previous_state[2]:
                            to_build.append(([i,j], ENCRYPTOR))

        if len(to_build) < CORES:
            # ------------------- FIRST TURN STUFF -----------------

            for i in range(7):
                x = MAIN_LINE_FILTER[i][0]
                y = MAIN_LINE_FILTER[i][1]
                #if the unit isn't there
                if gs.game_map.in_arena_bounds([x,y]) and len(gs.game_map[x, y]) == 0:
                    to_build.append(([x,y], FILTER))

                x = MAIN_LINE_DESTRUCTOR[i][0]
                y = MAIN_LINE_DESTRUCTOR[i][1]
                #if the unit isn't there
                if gs.game_map.in_arena_bounds([x,y]) and len(gs.game_map[x, y]) == 0:
                    to_build.append(([x,y], DESTRUCTOR))

        if len(to_build) < CORES:
            # ------------------- SMALL FORTIFICATIONS ----------------
            for i in range(7,10):
                x = MAIN_LINE_FILTER[i][0]
                y = MAIN_LINE_FILTER[i][1]
                #if the unit isn't there
                if gs.game_map.in_arena_bounds([x,y]) and len(gs.game_map[x, y]) == 0:
                    to_build.append(([x,y], FILTER))

                x = MAIN_LINE_DESTRUCTOR[i][0]
                y = MAIN_LINE_DESTRUCTOR[i][1]
                #if the unit isn't there
                if gs.game_map.in_arena_bounds([x,y]) and len(gs.game_map[x, y]) == 0:
                    to_build.append(([x,y], DESTRUCTOR))
        if len(to_build) < CORES:
            # ------------------- BUILD THE MAIN WALL ------------------

            for i in range(10,26):
                x = MAIN_LINE_FILTER[i][0]
                y = MAIN_LINE_FILTER[i][1]
                #if the unit isn't there
                if gs.game_map.in_arena_bounds([x,y]) and len(gs.game_map[x, y]) == 0:
                    to_build.append(([x,y], FILTER))

        if len(to_build) < CORES:
            # ------------------ MINOR STUFF ----------------------------

            #if the unit isn't there
            if gs.game_map.in_arena_bounds(MAIN_LINE_FILTER[26]) and len(gs.game_map[MAIN_LINE_FILTER[26][0], MAIN_LINE_FILTER[26][1]]) == 0:
                to_build.append((MAIN_LINE_FILTER[26], FILTER))
            if gs.game_map.in_arena_bounds(MAIN_LINE_FILTER[27]) and len(gs.game_map[MAIN_LINE_FILTER[27][0], MAIN_LINE_FILTER[27][1]]) == 0:
                to_build.append((MAIN_LINE_FILTER[27], FILTER))

            #if the unit isn't there
            if gs.game_map.in_arena_bounds(MAIN_LINE_DESTRUCTOR[10]) and len(gs.game_map[MAIN_LINE_DESTRUCTOR[10][0], MAIN_LINE_DESTRUCTOR[10][1]]) == 0:
                to_build.append((MAIN_LINE_DESTRUCTOR[10], DESTRUCTOR))
            if gs.game_map.in_arena_bounds(MAIN_LINE_DESTRUCTOR[11]) and len(gs.game_map[MAIN_LINE_DESTRUCTOR[11][0], MAIN_LINE_DESTRUCTOR[11][1]]) == 0:
                to_build.append((MAIN_LINE_DESTRUCTOR[11], DESTRUCTOR))
            if gs.game_map.in_arena_bounds(MAIN_LINE_DESTRUCTOR[12]) and len(gs.game_map[MAIN_LINE_DESTRUCTOR[12][0], MAIN_LINE_DESTRUCTOR[12][1]]) == 0:
                to_build.append((MAIN_LINE_DESTRUCTOR[12], DESTRUCTOR))

        if len(to_build) < CORES:
            # ----------------- FINISH DESCTRUCTORS -----------------------

            for i in range(3,22,2):
                if len(gs.game_map[i,11]) == 0:
                    to_build.append(([i,11], DESTRUCTOR))

            if len(gs.game_map[18,7]) == 0:
                to_build.append(([18,7], ENCRYPTOR))
            if len(gs.game_map[19,7]) == 0:
                to_build.append(([19,7], ENCRYPTOR))
            if len(gs.game_map[18,8]) == 0:
                to_build.append(([18,8], ENCRYPTOR))
            if len(gs.game_map[19,8]) == 0:
                to_build.append(([19,8], ENCRYPTOR))

            # -------------------- FINAL TWEAKS -----------------------------

            if gs.game_map.in_arena_bounds(MAIN_LINE_FILTER[-1]) and len(gs.game_map[MAIN_LINE_FILTER[-1][0], MAIN_LINE_FILTER[-1][1]]) == 0:
                to_build.append((MAIN_LINE_FILTER[-1], FILTER))

            #if the unit isn't there
            if gs.game_map.in_arena_bounds(MAIN_LINE_DESTRUCTOR[-1]) and len(gs.game_map[MAIN_LINE_DESTRUCTOR[-1][0], MAIN_LINE_DESTRUCTOR[-1][1]]) == 0:
                to_build.append((MAIN_LINE_DESTRUCTOR[-1], DESTRUCTOR))


        if len(to_build) < CORES:
            # ------------------- ADD BACK RANKS ----------------------------

            for i in range(22,5,-1):
                #if the unit isn't there
                if len(gs.game_map[i, 9]) == 0:
                    to_build.append(([i,9], FILTER))

                if i % 2 == 0:
                    if len(gs.game_map[i, 8]) == 0:
                        to_build.append(([i,8], DESTRUCTOR))

                else:
                    if len(gs.game_map[i, 8]) == 0:
                        to_build.append(([i,8], ENCRYPTOR))

                if i == 21 or i == 19:
                    if i == 21 and len(gs.game_map[21, 13]) == 0:
                        to_build.append(([21, 13], ENCRYPTOR))
                    if i == 23 and len(gs.game_map[5, 13]) == 0:
                        to_build.append(([5, 13], ENCRYPTOR))


        if len(to_build) < CORES:
            # -------------- IN CASE NONE OF THE ABOVE?? ---------------------


            for i in range(18,8,-1):
                #if the unit isn't there
                if len(gs.game_map[i, 6]) == 0:
                    to_build.append(([i,6], DESTRUCTOR))

            for i in range(16,10,-1):
                #if the unit isn't there
                if len(gs.game_map[i, 4]) == 0:
                    to_build.append(([i,4], DESTRUCTOR))


        for i in to_build:
            cost = 0
            if i[1] == DESTRUCTOR: cost = 3
            if i[1] == FILTER: cost = 1
            if i[1] == ENCRYPTOR: cost = 4
            if CORES >= cost:
                gs.attempt_spawn(i[1], i[0])
                if i[1] == DESTRUCTOR:
                    CORES -= 3
                    d_map.append(i[0])
                if i[1] == FILTER:
                    CORES -= 1
                    f_map.append(i[0])
                if i[1] == ENCRYPTOR:
                    CORES -= 4
                    e_map.append(i[0])

        self.previous_state = [f_map, d_map, e_map]


    def attack(self, gs):
        BITS = gs.get_resource(gs.BITS)

        if self.attack_PING and BITS >= 8:
            while gs.can_spawn(PING, [13, 0]):
                gs.attempt_spawn(PING, [13, 0])
            if len(self.previous_state[2]) > 1:
                self.attack_PING = False

        if not self.attack_PING and BITS >= 13:
            gs.attempt_spawn(EMP, [2, 11])
            gs.attempt_spawn(EMP, [2, 11])
            gs.attempt_spawn(EMP, [2, 11])
            gs.attempt_spawn(EMP, [2, 11])
            gs.attempt_spawn(SCRAMBLER, [3, 10])
            self.attack_PING = True


    def old_attack(self, gs):
        BOTTOM_LEFT = gs.game_map.get_edges()[2]
        BOTTOM_RIGHT = gs.game_map.get_edges()[3]
        valuations = []
        for i in BOTTOM_LEFT:
            if gs.can_spawn(PING, i):
                # 0=right 1=left
                valuations.append((self.calc_valuation(gs, 0, i, 8, 2), i, PING))
        for i in BOTTOM_RIGHT:
            if gs.can_spawn(PING, i):
                valuations.append((self.calc_valuation(gs, 1, i, 8, 2), i, PING))

        valuations.sort(reverse=True)
        if gs.get_resource(gs.BITS) > 8:
            while gs.can_spawn(PING, [14, 0]):
                gs.attempt_spawn(PING, [14, 0])
            else:
                if random.uniform(0, 1) > 0.25:
                    while len(valuations) > 0 and gs.can_spawn(EMP, valuations[0][1]):
                        gs.attempt_spawn(EMP, valuations[0][1])
                else:
                    while len(valuations) > 0 and gs.can_spawn(PING, valuations[0][1]):
                        gs.attempt_spawn(PING, valuations[0][1])


    def calc_valuation(self, gs, edge, loc, initial_health, destruction_power):
        if edge == 0:
            # bottom left
            path = gs.find_path_to_edge(loc, gs.game_map.TOP_RIGHT)
        else:
            # bottom right
            path = gs.find_path_to_edge(loc, gs.game_map.TOP_LEFT)
        score = 10
        health = initial_health
        for i in path:
            target = gs.get_target(gamelib.unit.GameUnit(PING, self.config, x=i[0], y=i[1]))
            if target != None:
                if target.unit_type == DESTRUCTOR:
                    score += 3 * destruction_power
                elif target.unit_type == ENCRYPTOR:
                    score += 4 * destruction_power
                elif target.unit_type == FILTER:
                    score += 2 * destruction_power
                else:
                    score += 1 * destruction_power
            health -= len(gs.get_attackers(i, 0))
            if health <= 0:
                score -= 10 # get rid of the initial bonus for damaging opponent
                break
        return score

    def detect_strategy():
        pass
        #implement this to beat the boss monster
        #or actually if you mimic and make slightly better you'll probably win

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
