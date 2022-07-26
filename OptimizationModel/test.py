import argparse
import random

import numpy as np
from sklearn.utils import shuffle
import numpy as np
import pandas as pd


A=np.random.randint(1,3,200)
B=np.random.randint(1,6,200)
C=np.random.randint(1,3,200)
lst = {
        0:A,
        1:B,
        2:C
        }
df = pd.DataFrame(lst)

print(df)

r = 10
M = []
for i in range(r):
        P = []
        for j in range(1):
                Size = random.randint(1, 3)
                Seq = random.randint(1, 6)
                allocationpolicy = random.randint(1, 3)
                P.append(Size)
                P.append(Seq)
                P.append(allocationpolicy)
        M.append(P)
print(M)
shuffled = random.sample(M, len(M))
print(shuffled)