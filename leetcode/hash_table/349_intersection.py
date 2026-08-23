'''
return self.intersection(nums2,nums1)是把原来的第二个数组当成新的 nums1,原来第一个数组当成新的 nums2,
重新进入这个函数从头执行一遍，它本身不会修改、调换数组内部的数据，只是换了参数位置。


'''


def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
        if len(nums1)>len(nums2):
            return self.intersection(nums2,nums1)
        
        set1=set(nums1)
        set2=set()
        for v in nums2:
            if v in set1:
                set2.add(v)
        return list(set2)