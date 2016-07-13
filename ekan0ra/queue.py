# -*- coding: utf-8 -*-
"""
    ekan0ra.queue
    ~~~~~~~~~~~~~

    A basic implementation of a generic use-case queue.

    :copyright: 
    :license:
"""


class Queue(list):
    """A basic FIFO queue implementation.

    This is implemented as an extension of the `list` datatype.
    
    New items come in at the TAIL and go out (popped) at the HEAD.

        Head is at index 0
        Tail is at index -1
    """

    def enqueue(self, nick):
        """Add nick to queue."""
        self.append(nick)

    def dequeue(self, nick):
        """
        Remove first item matching `nick` in queue.
        """
        try:
            self.remove(nick)
            return True
        except ValueError:
            return False

    def has_next(self):
        """Check if queue has at least one item."""
        return len(self) > 0

    def peek_next(self):
        """
        Get a look at the next item to be popped from the queue,
        but don't remove it from queue.
        """
        if self.has_next():
            return self[0]
        else:
            return None

    def pop_next(self):
        """Get next queue item from the head."""
        if self.has_next():
            return self.pop(0)
        else:
            return None

    def clear(self):
        """Clear all items from queue."""
        del self[:]


