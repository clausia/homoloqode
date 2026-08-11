from homoloqode import toric_code
from homoloqode.codes.distance import CSSDistance
result = CSSDistance.exact_distance(toric_code(3), max_weight=4)
print(result)