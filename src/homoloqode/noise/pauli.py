from dataclasses import dataclass
import numpy as np 
from numpy.typing import ArrayLike
from homoloqode.algebra.gf2 import as_binary_vector 
#dict to work with for pauli errors :
PAULI_LETTERS = {
     (0, 0): "I",
     (1, 0): "X",
     (1, 1): "Y",
     (0, 1): "Z",
}
_TOLERANCE = 1e-9
       
#dataclass is avoiding __init__, frozen saying cant chaneg, tested in scratch1.py
@dataclass(frozen=True, slots=True)
class PauliError:
    x: ArrayLike
    z: ArrayLike
    # post as in later so adding more stuff
    def __post_init__(self) -> None:
        x = as_binary_vector(self.x, name="X-error support")
        z = as_binary_vector(self.z, name="Z-error support")
        if x.shape[0] != z.shape[0]:
            raise ValueError(
            f"X and Z error supports must have equal length; "
            f"got {x.shape[0]} and {z.shape[0]}."
            )
        object.__setattr__(self, "x", x) #cant do self.x = x because frozen=True, so use object.__setattr__ to bypass
        object.__setattr__(self, "z", z) 
    
    @property 
    def n(self) -> int:
        return self.x.shape[0] #property decorator allows you to access the method as an attribute, so you can do error.n instead of error.n()
    @property
    def weight(self) -> int:
        return int(np.count_nonzero((self.x==1) | (self.z==1))) #count_nonzero counts the number of non-zero elements in an array, so this counts the number of qubits that have either an X or Z error
    def to_pauli_string(self) -> str: #function to convert vector to X,Z,Y format of errros
     letters = []
     for x_bit, z_bit in zip(self.x, self.z):    #zip allows to go through both x and z at the same time
         letters.append(PAULI_LETTERS[(int(x_bit), int(z_bit))])
     return "".join(letters)


@dataclass(frozen=True, slots=True)
class IndependentPauliNoise:
    p_x: float
    p_y: float
    p_z: float

    def __post_init__(self) -> None:
        if isinstance(self.p_x, bool):   # very impo since True acts like 1, check: True==1
               raise ValueError("p_x must be a real number, not a bool.")
        if not (0 <= self.p_x <= 1):
            raise ValueError(f"X error probability must be in [0, 1]; got {self.p_x}.")
        if not (0 <= self.p_y <= 1):
            raise ValueError(f"Y error probability must be in [0, 1]; got {self.p_y}.")
        if not (0 <= self.p_z <= 1):
            raise ValueError(f"Z error probability must be in [0, 1]; got {self.p_z}.")
        total = self.p_x + self.p_y + self.p_z
        if total > 1 + _TOLERANCE:
                raise ValueError(
                    f"Sum of X, Y, and Z error probabilities must be at most 1; got {total}."
                            )    # tolerance important since p_x=0.33, p_y=0.56, p_z=0.11 didnt work bfr
            

    @property
    def p_identity(self) -> float:
        return 1 - (self.p_x + self.p_y + self.p_z)
    

    def sample(self, n: int, *, rng: np.random.Generator) -> PauliError:
        if isinstance(n, bool):
             raise ValueError(f"n must be an integer, not a bool; got {n}.")
        if not isinstance(n, int):
             raise ValueError(f"n must be an integer; got {type(n).__name__}.")
        if n <= 0:
             raise ValueError(f"n must be a positive integer; got {n}.")
        if not isinstance(rng, np.random.Generator):
             raise ValueError("rng must be a numpy.random.Generator.")

        boundary_x = self.p_identity
        boundary_y = boundary_x + self.p_x
        boundary_z = boundary_y + self.p_y
   
        draws = rng.random(n)

        past_x = draws >= boundary_x    #very weird function, converts to boolean for eg [0.3,0.2.0.1] with >= 0.2 is [True, True, False] and >= 0.3 is [True, False, False] and >= 0.4 is [False, False, False]
        past_y = draws >= boundary_y
        past_z = draws >= boundary_z

        x_error = (past_x & ~past_z).astype(np.uint8)
        z_error = past_y.astype(np.uint8)

        return PauliError(x=x_error, z=z_error)