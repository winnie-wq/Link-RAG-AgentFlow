'''
暴力破解
'''
def twoSum(self, nums: List[int], target: int) -> List[int]:
        for i,item in enumerate(nums):
            for j in range(i+1,len(nums)):
                post=nums[j]
                if item+post==target:
                    return[i,j]


'''
基于上述暴力破解,为什么j已经遍历过的值之后还要多次遍历
所以就要引入一个有记忆力的容器,就是哈希表

设计:数字当key,索引当 value → cache[item]=i
'''
def twoSum(self, nums: List[int], target: int) -> List[int]:
        cache={}
        for i,item in enumerate(nums):
            cache[item]=i

        for i,item in enumerate(nums):
            other=target-item
            if other in cache and cache[other]!=i:
                return[i,cache[other]]


'''
哈希表进一步升级
一边遍历,一遍记录
'''
def twoSum(self, nums: List[int], target: int) -> List[int]:
        cache={}
        for i,item in enumerate(nums):
            other=target-item
            if other in cache:
                return[i,cache[other]]
            cache[item]=i
