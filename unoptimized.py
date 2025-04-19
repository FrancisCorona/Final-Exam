import copy
import cProfile

'''
For profiling original solution with only required tasks completed
'''

class ProblemState:
    def __init__(
        self,
        next_id = 0, # The next system index to consider in branching (e.g., include or exclude it).
        include_set = set() # A set containing the system IDs where toll stations have been placed so far.
    ):
        self.next_id = next_id
        self.include_set = include_set


class Solver:
    def __init__(self):
        self.N = 0          # Number of star systems (nodes)
        self.M = 0          # Number of connections (edges)
        self.graph = None   # Will store graph as adjacency list
        self.best = None    # Best (minimum) toll station count found so far
        self.Load()


    def Load(self):
        self.N, self.M = map(int, input().split(" ")) # Read verts and edges
        self.graph = {vertex_id: set() for vertex_id in range(self.N)} # Initializes an adjacency list for all star systems.
        
        for _ in range(self.M): # Fills the graph: each relay (edge) is undirected, so you add it to both nodes’ sets.
            a, b = map(int, input().split(" "))
            # Add edge between a <---> b
            self.graph[a].add(b)
            self.graph[b].add(a)
        # Update best to a "worst-case" scenario:
        # We know we *could* solve the problem by building a toll station in every
        # star system, so initialize best to N
        self.best = self.N

    def TestValid(self, state: ProblemState):
        for system_id in range(self.N):
            # If system has a station, all of its hyper relays have a toll station.
            if system_id in state.include_set:
                continue
            # Otherwise, we need to check that all hyper relays connected to this system have a toll station on the other end.
            for conn_id in self.graph[system_id]:
                if not conn_id in state.include_set:
                    return False
        return True

    def IncludeSystem(self, state: ProblemState, system_id: int): # Adds a toll station to the given system in the state.
        state.include_set.add(system_id)

    # Entry point to running the solver
    def Solve(self):
        # Build initial problem state. Empty toll set, and begin from system 0.
        initial_state = ProblemState(0, set())

        cur_system = initial_state.next_id

        # Try including the current system under consideration
        inc_state = copy.deepcopy(initial_state)
        inc_state.next_id += 1
        self.IncludeSystem(inc_state, cur_system)
        self.Branch(inc_state)

        # Try excluding the current system under consideration
        initial_state.next_id += 1
        self.Branch(initial_state)

        return self.best

    def Branch(self, state: ProblemState):
        # Current count of systems with stations
        num_stations = len(state.include_set)
        
        # BOUNDING: prune if already worse than current best
        #If the number of toll stations in the current branch is already greater than or equal to
        # the best solution found so far, we stop exploring this branch.
        # This avoids wasting time on worse solutions and helps reduce the exponential search space.
        if num_stations >= self.best:
            return self.best
        # Is this a valid solution?
        valid_sol = self.TestValid(state)
        # If so, if better than best, update best and bail out of this branch.
        if (valid_sol and num_stations < self.best):
            self.best = num_stations
            return self.best
        # Not a solution. If next_id is not valid, return.
        if (state.next_id >= self.N):
            return self.best
        # If we're here, next_id is valid and we don't yet have a solution on this branch.
        cur_system = state.next_id


# (Back Tracking)
        # Try including the current system under consideration *
        
        # We now recursively branch into two cases:
        # Case 1: Include the current system (place a toll station here)
        inc_state = copy.deepcopy(state)                # Make a deep copy so changes don't affect other branches
        self.IncludeSystem(inc_state, cur_system)       # Add the system to the toll station set
        inc_state.next_id += 1                          # Move to the next system
        best_inc = self.Branch(inc_state)                          # Recursively explore with this inclusion

        # Try excluding the current system under consideration *
        
        # Case 2: Exclude the current system (hope a neighbor covers all edges)
        # This assumes future or existing toll stations may cover this system's edges
        state.next_id += 1
        best_exc = self.Branch(state)
        return min(best_inc, best_exc)


if __name__ == "__main__":
    
    # Python's cProfile module to analyze where time is being spent in the program.
    profiler = cProfile.Profile()
    profiler.enable()
    
    solver = Solver()
    result = solver.Solve()
    print(result)
    
    profiler.disable()
    profiler.dump_stats("unoptimized.prof")  # Save stats for SnakeViz
    
# python3 main.py < input.txt
# snakeviz profile_output.prof