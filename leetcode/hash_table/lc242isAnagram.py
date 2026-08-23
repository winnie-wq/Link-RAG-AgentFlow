'''
哈希表的核心思想:把字符(key)映射为下标，统计字符出现次数。

数组实现哈希表
'''
def isAnagram(self, s: str, t: str) -> bool:
        res=[0]*26
        for i in range(len(s)):
            res[ord(s[i])-ord("a")]+=1
        for j in range(len(s)):
            res[ord(t[j])-ord("a")]-=1
        for q in range(26):
            if res[q]!=0:
                return False
        return True