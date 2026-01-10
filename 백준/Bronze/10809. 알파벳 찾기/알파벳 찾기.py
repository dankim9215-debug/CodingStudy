word = input()
alphabet = [-1 for _ in range(26)]

for i in range(len(word)):
    if alphabet[a := ord(word[i]) - 97] == -1:
        alphabet[a] = i

print(*alphabet)