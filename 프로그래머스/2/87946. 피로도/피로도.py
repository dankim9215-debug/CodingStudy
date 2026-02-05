def solution(k, dungeons):
    check = [False] * len(dungeons)
    
    def dfs(current_k, count):
        max_count = count
        
        for i in range(len(dungeons)):
            if not check[i] and current_k >= dungeons[i][0]:
                check[i] = True
                res = dfs(current_k - dungeons[i][1], count+1)
                max_count = max(max_count, res)
                check[i] = False
                
        return max_count
    
    return dfs(k, 0)