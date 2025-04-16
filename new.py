import copy
import time  # ✅ Added for profiling

'''
Starter Python solution.
- This code is not at all optimized!
'''

class ProblemState:
    def __init__(
        self,
        next_id = 0,
        include_set = set()
    ):
        self.next_id = next_id
        self.include_set = include_set


class Solver:

    def __init__(self):
        self.N = 0
        self.M = 0
        self.graph = None
        self.best = None
        self.Load()

    def Load(self):
        self.N, self.M = map(int, input().split(" "))
        self.graph = {vertex_id: set() for vertex_id in range(self.N)}
        for _ in range(self.M):
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

    def IncludeSystem(self, state: ProblemState, system_id: int):
        state.include_set.add(system_id)

    # Entry point to running the solver
    def Solve(self):
        start_time = time.time()  # ✅ Start profiling

        # Build initial problem state
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

        end_time = time.time()  # ✅ End profiling
        elapsed_time = end_time - start_time

        print(f"# Profile: Total execution time = {elapsed_time:.6f} seconds")  # ✅ Profiling output
        return self.best

    def Branch(self, state: ProblemState):
        # Current count of systems with stations
        num_stations = len(state.include_set)

        # ✅ BOUNDING: prune if already worse than current best
        if num_stations >= self.best:
            return

        # Is this a valid solution?
        valid_sol = self.TestValid(state)

        # If so, if better than best, update best and bail out of this branch.
        if (valid_sol and num_stations < self.best):
            self.best = num_stations
            return

        # Not a solution. If next_id is not valid, return.
        if (state.next_id >= self.N):
            return

        # If we're here, next_id is valid and we don't yet have a solution on this branch.
        cur_system = state.next_id

        # Try including the current system under consideration
        inc_state = copy.deepcopy(state)
        self.IncludeSystem(inc_state, cur_system)
        inc_state.next_id += 1
        self.Branch(inc_state)

        # Try excluding the current system under consideration
        state.next_id += 1
        self.Branch(state)


if __name__ == "__main__":
    solver = Solver()
    result = solver.Solve()
    print(result)
