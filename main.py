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

    def clone(self, state):
        # Create new instance with copied values -- more efficient than deepcopy
        return ProblemState(state.next_id, set(state.include_set))

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
    
    def GreedyPreprocess(self):
        mustHaveStations = set()
        
        # First identify nodes with highest degree (most connections)
        # These are often good candidates for toll stations
        nodes_by_degree = sorted(range(self.N), key=lambda x: len(self.graph[x]), reverse=True)
        
        # Process leaf nodes first (must be covered by their only neighbor)
        for system_id in range(self.N):
            if len(self.graph[system_id]) == 1:
                neighbor = next(iter(self.graph[system_id]))
                mustHaveStations.add(neighbor)
        
        # Add high-degree nodes that would cover many uncovered edges
        covered_edges = set()
        for node in nodes_by_degree:
            if node in mustHaveStations:
                continue
                
            # Count how many new edges this node would cover
            new_edges = 0
            for neighbor in self.graph[node]:
                edge = tuple(sorted([node, neighbor]))
                if edge not in covered_edges:
                    new_edges += 1
                    
            # If this node covers many new edges, add it
            if new_edges > 2:  # Threshold can be adjusted
                mustHaveStations.add(node)
                # Mark all edges from this node as covered
                for neighbor in self.graph[node]:
                    covered_edges.add(tuple(sorted([node, neighbor])))
        
        return mustHaveStations
         
    # Entry point to running the solver
    def Solve(self):
        # Greedy Preprocess to find must-have stations
        mustHaveStations = self.GreedyPreprocess()

        # Build initial problem state.
        initial_state = ProblemState(0, set(mustHaveStations))
        
        # If already found a solution, return it.
        if self.TestValid(initial_state):
            self.best = len(initial_state.include_set)
            return self.best
        
        cur_system = initial_state.next_id
        
        # Skip over systems that are already in the include set
        while cur_system < self.N and cur_system in initial_state.include_set:
            initial_state.next_id += 1
            cur_system = initial_state.next_id
        
        # Return the best solution found so far   
        if cur_system >= self.N:
            return self.best

        # Try excluding the current system under consideration
        exc_state = self.clone(initial_state)
        exc_state.next_id += 1
        self.IncludeSystem(exc_state, cur_system)
        self.Branch(exc_state)

        # Try including the current system under consideration
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
        exc_state = self.clone(state)                # Make a deep copy so changes don't affect other branches
        self.IncludeSystem(exc_state, cur_system)       # Add the system to the toll station set
        exc_state.next_id += 1                          # Move to the next system
        best_exc = self.Branch(exc_state)                          # Recursively explore with this inclusion

        # Try excluding the current system under consideration *
        
        # Try excluding the current system under consideration (Polynomial time optimization)  #FIXME add comments
        state.next_id += 1
        best_inc = self.Branch(state)   
        return min(best_inc, best_exc)


if __name__ == "__main__":
    
    # Python's cProfile module to analyze where time is being spent in the program.
    profiler = cProfile.Profile()
    profiler.enable()
    
    solver = Solver()
    result = solver.Solve()
    print(result)
    
    profiler.disable()
    profiler.dump_stats("main.prof")  # Save stats for SnakeViz
    
# python3 main.py < input.txt
# snakeviz main.prof

# Required tasks:
# Added backtracking
# Added bounding
# Profile code

# Polynomial time optimization: Changed deepcopy to clone
# SHOW: unoptimized.py vs deepcopy_optimized.py, deepcopy_benchmark.txt

# Consider order of branching decisions: Changed the order of excluding first and then including
# SHOW: include_first.py vs exclude_first.py, include.prof vs exclude.prof

# Profile your code after making one or more change(s)
# unoptimized.prof vs deepcopy.prof

# Fast approximization algorithm to improve bounding
# GreedyPreprocess method -> benchmark vs exclude_first.py