from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


def get_colour() -> Tuple[int, int, int]:
    """This function picks a random colour selectively such that it is
    not on the grey scale. The colour is close to the grey scale if the
    r g b values have a small variance. This function checks if all the
    numbers are close to the mean, if so, it shifts the last digit by 150.

    This way you can't confuse the leaf rectangles with folder rectangles,
    because the leaves will always be a colour, never close to black / white.
    """
    rgb = [randint(0, 255), randint(0, 255), randint(0, 255)]
    avg = sum(rgb) // 3
    count = 0
    for item in rgb:
        if abs(item - avg) < 20:
            count += 1
    if count == 3:
        rgb[2] = (rgb[2] + 150) % 255
    return tuple(rgb)


class TreeMap:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    === Public Attributes ===
    rect: The pygame rectangle representing this node in the visualization.
    data_size: The size of the data represented by this tree.

    === Private Attributes ===
    _colour: The RGB colour value of the root of this tree.
    _name: The root value of this tree, or None if this tree is empty.
    _subtrees: The subtrees of this tree.
    _parent_tree: The parent tree of this tree; i.e., the tree that contains
    this tree as a subtree, or None if this tree is not part of a larger tree.
    _expanded: Whether this tree is considered expanded for visualization.
    _depth: The depth of this tree node in relation to the root.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - _colour's elements are each in the range 0-255.
    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - if _parent_tree is not None, then self is in _parent_tree._subtrees
    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TreeMap]
    _parent_tree: Optional[TreeMap]
    _expanded: bool
    _depth: int

    def __init__(self, name: str, subtrees: List[TreeMap],
                 data_size: int = 0) -> None:
        """Initializes a new TMTree with a random colour, the provided name
        and sets the subtrees to the list of provided subtrees. Sets this tree
        as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._parent_tree = None
        self._depth = 0

        self._expanded = False

        self._name = name
        self._colour = get_colour()
        self._subtrees = subtrees
        self.data_size = data_size
        if self.is_empty():
            self._subtrees = []

        if subtrees:
            self.data_size = 0
            for i in subtrees:
                i._parent_tree = self
                self.data_size += i.data_size

    def is_empty(self) -> bool:
        """Returns True iff this tree is empty.
        """
        return self._name is None

    def get_parent(self) -> Optional[TreeMap]:
        """Returns the parent of this tree.
        """
        return self._parent_tree

    def _update_rect_helper(self, div: str, rect:
                            Tuple[int, int, int, int]) -> None:
        """Helper method for update_rectangles."""
        position = 0
        x, y, width, height = rect
        if div == "width":
            for subtree in self._subtrees[:-1]:
                z1 = subtree.data_size / self.data_size
                z = math.floor(z1 * width)
                subtree.update_rectangles((x + position, y,
                                           z, height))
                position += z
            self._subtrees[-1].update_rectangles((x + position, y,
                                                  width - position, height))
        elif div == "height":
            for subtree in self._subtrees[:-1]:
                z1 = subtree.data_size / self.data_size
                z = math.floor(z1 * height)
                subtree.update_rectangles((x, y + position,
                                           width, z))
                position += z
            self._subtrees[-1].update_rectangles((x, y + position,
                                                  width, height - position))

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Updates the rectangles in this tree and its descendants using the
        treemap algorithm to fill the area defined by the <rect> parameter.
        """
        if self.data_size == 0 or self.is_empty():
            self.rect = (0, 0, 0, 0)
        elif not self._subtrees:
            self.rect = rect
        else:
            self.rect = rect
            width, height = rect[2], rect[3]
            if width > height:
                self._update_rect_helper("width", rect)
            else:
                self._update_rect_helper("height", rect)

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Returns a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        #
        x = []
        if not self._expanded or self.is_empty():
            x.append((self.rect, self._colour))
        elif not self._subtrees:
            x.append((self.rect, self._colour))
        else:
            for i in self._subtrees:
                x.extend(i.get_rectangles())
        return x

    def _position_helper(self, pos: Tuple[int, int],
                         rect: Tuple[int, int, int, int]) -> Optional[TreeMap]:
        """Helper method for get_tree_at_position."""
        a, b = pos
        x, y, width, height = rect
        if x <= a <= (x + width) and y <= b <= (y + height):
            return self
        return None

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TreeMap]:
        """Returns the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two or more rectangles,
        always return the leftmost and topmost rectangle (wherever applicable).
        """
        #
        if self.is_empty():
            return None
        elif not self._subtrees or not self._expanded:
            return self._position_helper(pos, self.rect)

        temp = self._position_helper(pos, self.rect)
        if not temp:
            return None
        possible = []
        for i in self._subtrees:
            rectangle = i.get_tree_at_position(pos)
            if rectangle:
                possible.append(rectangle)
        if len(possible) >= 1:
            out = possible[0]
            for i in possible:
                if i.rect[0] < out.rect[0] or (i.rect[0] == out.rect[0]
                                               and i.rect[1] < out.rect[1]):
                    out = i
            return out
        else:
            return None

    def update_data_sizes(self) -> int:
        """Updates the data_size attribute for this tree and all its subtrees,
        based on the size of their leaves, and return the new size of the given
        tree node after updating.

        If this tree is a leaf, return its size unchanged.
        """
        #
        if self.is_empty():
            self.data_size = 0
            return 0
        elif not self._subtrees:
            return self.data_size
        else:
            self.data_size = 0
            for i in self._subtrees:
                self.data_size += i.update_data_sizes()
            return self.data_size

    def change_size(self, factor: float) -> None:
        """Changes the value of this tree's data_size attribute by <factor>.
        Always rounds up the amount to change, so that it's an int, and
        some change is made. If the tree is not a leaf, this method does
        nothing.
        """
        #
        if self._subtrees or self.is_empty():
            return
        else:
            fact = abs(factor)
            change = math.ceil(self.data_size * fact)
            if factor < 0:
                if self.data_size - change < 1:
                    self.data_size = 1
                else:
                    self.data_size -= change
            else:
                self.data_size += change

    def _remove(self) -> None:
        """Helper method for delete_self and move"""
        parent = self.get_parent()
        if parent:
            parent._subtrees.remove(self)

    def delete_self(self) -> bool:
        """Removes the current node from the visualization and
        returns whether the deletion was successful. Only do this if this node
        has a parent tree.
        """
        parent = self.get_parent()
        if not parent:
            return False
        elif len(parent._subtrees) > 1:
            self._remove()
            return True
        else:
            parent._subtrees = []
            return parent.delete_self()

    def update_depths(self) -> None:
        """Updates the depths of the nodes, starting with a depth of 0 at this
        tree node.
        """
        self._depth = 0
        self._update_depths_helper()

    def _update_depths_helper(self) -> None:
        """Helper method for update_depths."""
        for i in self._subtrees:
            parent = i.get_parent()
            i._depth = parent._depth + 1
            i._update_depths_helper()

    def max_depth(self) -> int:
        """Returns the maximum depth of the tree, which is the maximum length
        between a leaf node and the root node.
        """
        if self.is_empty():
            return 0
        elif not self._subtrees:
            return 0
        else:
            x = [1]
            for i in self._subtrees:
                x.append(i.max_depth() + 1)
            return max(x)

    def update_colours(self, step_size: int) -> None:
        """Updates the colours so that the internal tree nodes are
        shades of grey depending on their depth. The root node will be black
        (0, 0, 0) and all internal nodes will be shades of grey depending on
        their depth, where the step size determines the shade of grey.
        Leaf nodes should not be updated.
        """
        if not self._subtrees or self.is_empty():
            return
        parent = self.get_parent()
        if not parent:
            self._colour = (0, 0, 0)
        else:
            x = step_size * self._depth
            if x <= 200:
                self._colour = (x, x, x)
        for i in self._subtrees:
            i.update_colours(step_size)

    def update_colours_and_depths(self) -> None:
        """This method is called any time the tree is manipulated or right after
        instantiation. Updates the _depth and _colour attributes throughout
        the tree.
        """
        self.update_depths()
        max_d = self.max_depth()
        if max_d <= 1:
            step_size = 200
        else:
            step_size = math.floor(200 / (max_d - 1))
        self.update_colours(step_size)

    def expand(self) -> None:
        """Sets this tree to be expanded. But not if it is a leaf.
        """
        if self._subtrees:
            self._expanded = True

    def expand_all(self) -> None:
        """Sets this tree and all its descendants to be expanded, apart from the
        leaf nodes.
        """
        if self._subtrees:
            self._expanded = True
            for i in self._subtrees:
                i.expand_all()

    def collapse(self) -> None:
        """Collapses the parent tree of the given tree node and also collapse
        all of its descendants.
        """
        #
        self._expanded = False
        parent = self.get_parent()
        if parent and parent._expanded:
            parent._expanded = False
            for i in parent._subtrees:
                i.collapse()
        for i in self._subtrees:
            i.collapse()

    def _root_node(self) -> TreeMap:
        """Helper method for collapse_all."""
        parent = self.get_parent()
        if parent:
            return parent._root_node()
        else:
            return self

    def _helper_collapse(self) -> None:
        """Helper method for collapse_all."""
        for i in self._subtrees:
            i._expanded = False
            i._helper_collapse()

    def collapse_all(self) -> None:
        """ Collapses ALL nodes in the tree.
        """
        parent = self._root_node()
        parent._expanded = False
        parent._helper_collapse()

    def move(self, destination: TreeMap) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, moves this
        tree to be the last subtree of <destination>. Otherwise, does nothing.
        """
        if self._subtrees or not destination._subtrees:
            return
        else:
            parent = self.get_parent()
            self._remove()
            if not parent._subtrees:
                parent.data_size = 0
            destination._subtrees.append(self)
            self._parent_tree = destination

    def duplicate(self) -> Optional[TreeMap]:
        """Duplicates the given tree, if it is a leaf node. It stores
        the new tree with the same parent as the given leaf. Returns the
        new node. If the given tree is not a leaf, does nothing.
        """
        #
        if self._subtrees:
            return None
        else:
            x = self.get_full_path()
            new = FileSystemTree(x)
            parent = self.get_parent()
            if parent:
                parent._subtrees.append(new)
                new._parent_tree = parent
            return new

    def copy_paste(self, destination: TreeMap) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, this method
        copies the given, and moves the copy to the last subtree of
        <destination>. Otherwise, does nothing.
        """
        if self._subtrees or not destination._subtrees:
            return
        else:
            new = self.duplicate()
            new.move(destination)

    def tree_traversal(self) -> List[Tuple[str, int, Tuple[int, int, int]]]:
        """For testing purposes to see the depth and colour attributes for each
        internal node in the tree. Used for passing test case 5.
        """
        if len(self._subtrees) > 0:
            output_list = [(self._name, self._depth, self._colour)]
            for tree in self._subtrees:
                output_list += tree.tree_traversal()
            return output_list
        else:
            return []

    def get_path_string(self) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                   self.get_separator() + self._name

    def get_separator(self) -> str:
        """Returns the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Returns the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_full_path(self) -> str:
        """Returns the path attribute for this tree.
        """
        raise NotImplementedError


class FileSystemTree(TreeMap):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.

    === Private Attributes ===
    _path: the path that was used to instantiate this tree.
    """
    _path: str

    def __init__(self, my_path: str) -> None:
        """Stores the directory given by <my_path> into a tree data structure
        using the TMTree class.

        Precondition: <my_path> is a valid path for this computer.
        """
        self._path = my_path
        name = os.path.basename(my_path)
        if not os.path.isdir(my_path):
            subtrees = []
            size = os.path.getsize(my_path)
            TreeMap.__init__(self, name, subtrees, size)
        else:
            x = os.listdir(my_path)
            subtrees = []
            for i in x:
                y = os.path.join(my_path, i)
                subtrees.append(FileSystemTree(y))
            TreeMap.__init__(self, name, subtrees)

    def get_full_path(self) -> str:
        """Returns the file path for the tree object.
        """
        return self._path

    def get_separator(self) -> str:
        """Returns the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Returns the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })