dan = int(input())

print(*[f"{dan} * {i} = {dan*i}" for i in range(1, 10)], sep='\n')