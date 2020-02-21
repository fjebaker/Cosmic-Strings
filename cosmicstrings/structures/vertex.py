import random
import numpy as np
from typing import List


class Vertex:

    def __init__(self, pos: List[float], su2):
        self.pos = pos
        self.theta = None

        self.su2 = su2
        self._generate_theta()

    def _generate_theta(self):
        if self.su2:
            v = np.array([random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1)], dtype=float)
            self.theta = list(v / np.linalg.norm(v))
        else:
            self.theta = random.choice([0, 2.0/3.0 * np.pi, 4.0/3.0 * np.pi])
        #self.theta = random.uniform(0.0, 2*np.pi)

    def __str__(self):
        return "Vertex pos: {} {} {}; theta: {}".format(*self.pos, self.theta)

    def __eq__(self, othr):
        if self.pos == othr.pos:
            return True
        else:
            return False

    def __hash__(self):
        return hash(str(self.pos))