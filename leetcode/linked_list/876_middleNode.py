'''
快指针每次走两步,慢指针每次走一步,fast 的步数恒为 slow 的 2 倍，因此当快指针遍历完链表时，慢指针就指向链表中间节点。而由于长度为偶数的链表有两个中间节点，因此需要分两种情况考虑：

链表长度为奇数： 当 fast 走到链表「尾节点」时,slow 正好走到「中间节点」。
链表长度为偶数： 当 fast 走到「null」时(越过「尾节点」后),slow 正好走到「第二个中间节点」。


'''


def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        fast=slow=head
        while fast and fast.next:
            fast=fast.next.next
            slow=slow.next
        return slow