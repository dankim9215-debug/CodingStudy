origin = [1, 1, 2, 2, 2, 8]

found = list(map(int, input().split()))

result = [origin[i] - found[i] for i in range(6)]

print(*(result))


# import numpy as np

# origin = np.array([1, 1, 2, 2, 2, 8])

# found = np.array(list(map(int, input().split())))

# result = origin - found

# print(*result)