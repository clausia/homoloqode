
from homoloqode.noise.pauli import IndependentPauliNoise
import numpy as np

noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)
rng = np.random.default_rng(12345)
error = noise.sample(5, rng=rng)
print(error.x, error.z)

import numpy as np
b = np.array([True, False, True])
print(b)
print(b.astype(np.uint8))

# this is what we usedin the random sampling function to convert boolean arrays to binary arrays

noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
#noise.sample(0, rng=np.random.default_rng(0))        did not
#noise.sample(True, rng=np.random.default_rng(0))     did not
#noise.sample(5, rng=12345)                          did not 
noise.sample(5, rng=np.random.default_rng(0))   #ran
