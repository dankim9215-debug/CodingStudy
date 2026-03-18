def solution(price, money, count):
    money2 = 0
    for i in range(1, count + 1):
        money2 += (i * price)
    
    if money2 > money:
        return money2 - money
    else:
        return 0