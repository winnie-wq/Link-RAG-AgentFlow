'''
什么是哈希函数?
取字的unicode的平方,然后在这个数字里取三位
def cal_hash(key):
  square=ord(key)**2
  mid=str(squre)[3:6]
  return int(mid)

哈希表就是存进去不同的参数给出对应不同的数值,存相同的参数给出相同的值
'''


'''
floyd判圈算法
快慢指针,只要相遇就一定有圈

快指针总是比慢指针多走一步
当链表的值的数量为奇数时,fast指针最后走两步一定会报错,所以在判断条件那里要加个补丁fast.next也不能为空
'''
def hasCycle(self, head: Optional[ListNode]) -> bool:
        slow=head
        fast=head
        while fast!=None and fast.next!=None:
            slow=slow.next
            fast=fast.next.next
            
            if slow==fast:
                return True

        return False