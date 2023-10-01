class _Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def is_empty(self):
        return self.head is None

    def append(self, data):
        new_node = _Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def prepend(self, data):
        new_node = _Node(data)
        new_node.next = self.head
        self.head = new_node
        if self.tail is None:
            self.tail = new_node

    def delete(self, data):
        if self.head is None:
            return

        if self.head.data == data:
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            return

        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                if current.next is None:
                    self.tail = current
                return
            current = current.next

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        print(" -> ".join(map(str, elements)))
    
    def print_as_list(self, parameter: tuple = None):
      current = self.head
      counter = 0
        
      while current:
        if parameter is None:
            print(f"{counter + 1}) {current.data}")
            counter += 1
        else:
            key, value = parameter

            if key == "processed":
                if current.data.processed is bool(value):
                    print(f"{counter + 1}) {current.data}")
                    counter += 1

        current = current.next
        
    
      return counter

    def get_elem_by_position(self, position: int):
        current = self.head

        counter = 1
        while current:
            if counter == int(position):
                return current
            current = current.next
            counter += 1

        return None