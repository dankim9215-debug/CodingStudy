def solution(s, n):
    answer = ''

    for text in s:
        if text.isupper():
            answer += chr((ord(text) - ord('A') + n)% 26 + ord('A') )
        elif text.islower():
            answer += chr((ord(text) - ord('a') + n) % 26 + ord('a'))
        else:
            answer += text

    return answer