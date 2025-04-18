import copy

'''
Basic solution to the in-class backup power problem!

- Note: This code does not implement many optimizations! Many more possible!
'''


class ProblemState:
    def __init__(self):
        self.included = set()   # Buildings decided to have a generator
        self.excluded = set()   # Buildings decided to have no generator
        self.undecided = set()  # Undecided buildings
        self.covered = set()    # Buildings covered by a placed generator

    def IsCovered(self, v):
        return v in self.covered

class Solver:
    def __init__(self):
        self.best = 0
        self.graph_adj = []
        self.graph_mat = []

    def Load(self, filename):
        '''
        Load graph from file
        - First line of file gives number of vertices
        - Each pair of lines after the first describe the connections for a vertex.
            - Number of connections, then vertex ids of vertices connected
        '''
        with open(filename, "r") as fp:
            num_vertices = int(fp.readline().strip())
            self.graph_adj = [None for i in range(num_vertices)]
            self.graph_mat = [[False for j in range(num_vertices)] for i in range(num_vertices)]
            for v in range(num_vertices):
                num_connections = int(fp.readline().strip())
                self.graph_adj[v] = frozenset({int(conn) for conn in fp.readline().split(" ")})
                for conn in self.graph_adj[v]:
                    self.graph_mat[v][conn] = True

    def IncludeVertex(self, state: ProblemState, id: int):
        # Add building to included
        state.included.add(id)
        # Remove building from undecided
        state.undecided.remove(id)
        # Cover included building
        state.covered.add(id)
        # Cover all buildings adjacent to included id
        state.covered.update(self.graph_adj[id])

    def ExcludeVertex(self, state: ProblemState, id: int):
        state.excluded.add(id)
        state.undecided.remove(id)

    def FindNextVertex(self, state: ProblemState):
        '''
        Pick building that would add the most additional coverage
        '''
        max_cov = None
        next_v = None
        for v in state.undecided:
            # Additional coverage if v is included: any connections not already
            #  covered plus 1 if v is not covered
            additional_cov = len(self.graph_adj[v] - state.covered) + int(not state.IsCovered(v))
            if max_cov is None or additional_cov > max_cov:
                max_cov = additional_cov
                next_v = v
        return next_v

    def Solve(self):
        '''
        Solve for loaded graph
        '''
        # Create initial problem state
        init_state = ProblemState()
        init_state.undecided = {i for i in range(len(self.graph_adj))}

        # Use FindNextVertex to get a decent initial best-so-far solution
        # to help with bounding
        greedy_state = copy.deepcopy(init_state)
        while len(greedy_state.covered) < len(self.graph_adj):
            self.IncludeVertex(
                greedy_state,
                self.FindNextVertex(greedy_state)
            )
        self.best = len(greedy_state.included)
        # self.best = len(self.graph_adj)

        return self.Branch(init_state)

    def Branch(self, state: ProblemState):
        '''
        Given a state (i.e., candidate solution) with some decision made,
            return the best possible solution
        '''
        # Have we covered everything?
        if (len(state.covered) == len(self.graph_adj)):
            if len(state.included) < self.best:
                self.best = len(state.included)
            return self.best

        # If we've made all possible decisions
        if (len(state.undecided) == 0):
            return self.best

        # Bounding based on best found so far
        if (len(state.included) + 1 >= self.best):
            return self.best

        # <--- any optimizations to make the problem smaller that you want to run
        #      many times ---->

        # <--- Maybe? Re-run your greedy algorithm to see if it does better --->

        # Figure out next vertex to decide include vs exclude
        next_node = self.FindNextVertex(state)
        # Include
        inc_state = copy.deepcopy(state)
        self.IncludeVertex(inc_state, next_node)
        best_inc = self.Branch(inc_state)
        # Exclude
        self.ExcludeVertex(state, next_node)
        best_exc = self.Branch(state)

        # if best_inc is None and best_exc is None: return None
        # if best_inc is None: return best_exc
        # if best_exc is None: return best_inc
        return min(best_inc, best_exc)
        # return best_inc if len(best_inc) <= len(best_exc) else best_exc

if __name__ == "__main__":

    solver = Solver()
    solver.Load("chain.txt")
    print(solver.Solve())
