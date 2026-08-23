'''
迭代法
当前current指向之前prev,指向之前prev之前先有个next指向current.next不然断了,最后移动prev=current,current=next
'''
def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev, curr = None, head
        while curr is not None:
            next = curr.next
            curr.next = prev
            prev = curr
            curr = next
        return prev


'''
递归法
大问题可以拆解为小问题
小问题的解决办法跟大问题一样
有最小子问题
'''
def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head is None or head.next is None:
            return head

        p=self.reverseList(head.next)
        head.next.next=head
        head.next=None

        return p