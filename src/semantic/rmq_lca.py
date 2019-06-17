import unittest, random, math


class RangeMin:
    """RangeMin in O(n^2) space and constant query time."""
    def __init__(self, data):
        self.A = data
        self.N = len(data)
        self.M = [[-1]*self.N for i in range(self.N)]
        self.build_rmq()

    def build_rmq(self):
        for i in range(self.N):
            self.M[i][i] = i
        for i in range(self.N):
            for j in range(i+1, self.N):
                if self.A[j] < self.A[self.M[i][j-1]]:
                    self.M[i][j] = j
                else:
                    self.M[i][j] = self.M[i][j-1]

    def query(self, i, j):
        return self.M[i][j]

class LogaritmicRangeMin:
    """RangeMin in O(n log n) space and constant query time."""
    def __init__(self, data):
        self.A = data
        self.N = len(data)
        self.logN = _log2(self.N)
        self.M = [] # M[i][j] represents the minimun value in the subarray [i; i + 2^j - 1] 
        self.build_rmq()

    def build_rmq(self):
        # initializate M for the intervals with length 1
        for i in range(self.N):
            self.M.append([i])
        # compute from smaller to bigger interval
        j = 1
        while (1<<j) <= self.N:
            i = 0
            while i+(1<<j) <= self.N:
                self.M[i].append(min(self.M[i][j-1],self.M[i+(1<<(j-1))][j-1]))
                i += 1
            j += 1
 
    def query(self, i, j):
        k = math.floor(math.log2(j-i))
        return self.A[min(self.M[i][k],self.M[j-(1<<k)+1][k])]

_logtable = [None, 0]
def _log2(n):
    for i in range(2, n+1):
        _logtable.append(_logtable[i//2] + 1)
    return _logtable[n]

class LCA:
    def __init__(self, graph):
        self._graph = graph
        self.E = []
        self.L = []
        self.R = [-1]*len(graph)
        self.build_lca(0)
        self.rmq = RangeMin(self.L)

    def build_lca(self, v, p=0):
        self.R[v] = len(self.E)
        self.E.append(v)
        self.L.append(p)
        for u in self._graph[v]:
            self.build_lca(u, p+1)
            self.E.append(v)
            self.L.append(p)
    
    def query(self, i, j):
        if self.R[i] > self.R[j]:
            i,j = j,i
        return self.E[self.rmq.query(self.R[i],self.R[j])]

class RandomRangeMinTest(unittest.TestCase):
    def testRangeMin(self):
        for trial in range(20):
            data = [random.choice(range(1000000))
                    for i in range(random.randint(1,100))]
            # R = RangeMin(data)
            R = LogaritmicRangeMin(data)
            for sample in range(100):
                i = random.randint(0,len(data)-1)
                j = random.randint(i,len(data)-1)
                self.assertEqual(R.query(i,j),min(data[i:j+1]))


if __name__ == "__main__":
    # unittest.main()
    graph = [[1,2,3],
    [],[4,5,6],[],
    [],[7,8],[9,10],
    [],[],[11,12],[],
    [],[]]

    lca = LCA(graph)
    print(lca.query(8, 11))