import os

from hypothesis import given
from hypothesis.strategies import integers

from TreeMaps import TreeMap, FileSystemTree

# This should be the path to the "workshop" folder in the sample data.
# May need to modify this, depending on where you downloaded and
# extracted the files.
EXAMPLE_PATH = os.path.join(os.getcwd(), 'example-directory', 'workshop')


# TEST 1 -----------------------------------------------------------------------
def test_single_file() -> None:
    """Test a tree with a single file.
    This is a test for the TMTree and FileSystemTree initializers.
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    assert tree._name == 'draft.pptx'
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 58
    assert is_valid_colour(tree._colour)


# TEST 2 -----------------------------------------------------------------------
def test_example_data() -> None:
    """Test the root of the tree at the 'workshop' folder in the example data
    This is a test for the TMTree and FileSystemTree initializers.
    """
    tree = FileSystemTree(EXAMPLE_PATH)

    assert tree._name == 'workshop'
    assert tree._parent_tree is None
    assert tree.data_size == 151
    assert is_valid_colour(tree._colour)

    assert len(tree._subtrees) == 3
    for subtree in tree._subtrees:
        assert subtree._parent_tree is tree


# TEST 3 -----------------------------------------------------------------------
@given(integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000))
def test_single_file_rectangles(x, y, width, height) -> None:
    """Test that the correct rectangle is produced for a single file.
    This is a test for the update_rectangles and the get_rectangles methods.
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.update_rectangles((x, y, width, height))
    rects = tree.get_rectangles()
    assert len(rects) == 1
    rect, colour = rects[0]
    assert rect == (x, y, width, height)
    assert is_valid_colour(colour)


# # TEST 4 -----------------------------------------------------------------------
# def test_example_data_rectangles() -> None:
#     """This test sorts the subtrees, because different operating systems have
#     different behaviours with os.listdir.
#     """
#     tree = FileSystemTree(EXAMPLE_PATH)
#     _sort_subtrees(tree)
#
#     tree.update_rectangles((0, 0, 200, 100))
#     rects = tree.get_rectangles()
#
#     assert len(rects) == 6
#
#     actual_rects = [r[0] for r in rects]
#     expected_rects = [(0, 0, 94, 2), (0, 2, 94, 28), (0, 30, 94, 70),
#                       (94, 0, 76, 100), (170, 0, 30, 72), (170, 72, 30, 28)]
#
#     assert len(actual_rects) == len(expected_rects)
#     for i in range(len(actual_rects)):
#         assert expected_rects[i] == actual_rects[i]


# TEST 5 -----------------------------------------------------------------------
def test_update_colours_and_depths() -> None:
    """Builds a tree using the example path, and sorts it for testing purposes.
    Tests that the update_colours_and_depths successfully updated the _colours
    and _depths attributes for internal tree nodes.
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    tree.update_colours_and_depths()
    results = tree.tree_traversal()
    assert results == [('workshop', 0, (0, 0, 0)),
                       ('activities', 1, (100, 100, 100)),
                       ('images', 2, (200, 200, 200)),
                       ('prep', 1, (100, 100, 100)),
                       ('images', 2, (200, 200, 200))]


# TEST 6 -----------------------------------------------------------------------
def test_extra_test() -> None:
    """This is an extra test added for your own testing purposes. You may find
    it useful to modify the tree_traversal() method to show you different
    attributes from the nodes.
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    # print(tree.tree_traversal())
    assert 1 == 1


##############################################################################
# Helpers
##############################################################################

def is_valid_colour(colour: tuple[int, int, int]) -> bool:
    """Return True iff <colour> is a valid colour. That is, if all of its
    values are between 0 and 255, inclusive.
    """
    for i in range(3):
        if not 0 <= colour[i] <= 255:
            return False
    return True


def _sort_subtrees(tree: TreeMap) -> None:
    """Sort the subtrees of <tree> in alphabetical order.
    THIS IS FOR THE PURPOSES OF THE SAMPLE TEST ONLY; YOU SHOULD NOT SORT
    YOUR SUBTREES IN THIS WAY. This allows the sample test to run on different
    operating systems.

    This is recursive, and affects all levels of the tree.
    """
    if not tree.is_empty():
        for subtree in tree._subtrees:
            _sort_subtrees(subtree)

        tree._subtrees.sort(key=lambda t: t._name)


if __name__ == '__main__':
    import pytest
    pytest.main(['TreeMap_test.py'])