import unittest

import pandas as pd

import table_compositor.table_compositor as pdpr


class TestUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simple_df = pd.DataFrame(
            data=dict(a=[0.1, 0.2, 0.3], b=[100, 200, 300], c=[True, False, True]),
            index=[1, 2, 3],
        )
        cls.simple_pm = pdpr.build_presentation_model(df=cls.simple_df)

        cls.multi_df = pd.DataFrame(
            data=dict(
                a=[0.1, 0.2, 0.3, 0.4],
                b=[100, 200, 300, 100],
                c=[True, False, True, False],
            )
        )
        cls.multi_df.index = pd.MultiIndex.from_tuples(
            [("a", 1), ("a", 2), ("b", 1), ("b", 2)]
        )
        cls.multi_df.columns = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1)])
        cls.multi_df.index.name = "Sample_Index"
        cls.multi_pm = pdpr.build_presentation_model(df=cls.multi_df)

        cls.multi_df_1 = pd.DataFrame(
            data=dict(
                a=[0.1, 0.2, 0.3, 0.4],
                b=[100, 200, 300, 100],
                c=[True, False, True, False],
                d=[10, 20, 40, 30],
            )
        )
        cls.multi_df_1.columns = pd.MultiIndex.from_tuples(
            [("a", 1), ("a", 2), ("b", 1), ("b", 2)]
        )
        cls.multi_df_1.index = pd.MultiIndex.from_tuples(
            [("a", 1), ("a", 2), ("b", 1), ("b", 2)]
        )
        cls.mult_pm_1 = pdpr.build_presentation_model(df=cls.multi_df_1)

        cls.multi_df.index.name = "Sample_Index"

    def test_index_node_construction_simple_index(self):

        root = pdpr.IndexNode.index_to_index_node(self.simple_df.columns)

        self.assertEqual([c.value for c in root.children], ["a", "b", "c"])
        self.assertEqual([c.parent for c in root.children], [root, root, root])
        self.assertEqual([c.key for c in root.children], [("a",), ("b",), ("c",)])

    def test_index_node_construction_multi_hierarchical_columns(self):
        root = pdpr.IndexNode.index_to_index_node(self.multi_df.columns)

        self.assertEqual([c.value for c in root.children], ["a", "b"])
        self.assertEqual([c.value for c in root.children[0].children], [1, 2])
        self.assertEqual([c.value for c in root.children[1].children], [1])
        self.assertEqual([c.parent for c in root.children], [root, root])
        self.assertEqual(
            [c.parent for c in root.children[0].children],
            [root.children[0], root.children[0]],
        )
        self.assertEqual(
            [c.parent for c in root.children[1].children], [root.children[1]]
        )
        self.assertEqual([c.key for c in root.children], [("a",), ("b",)])
        self.assertEqual(
            [c.key for c in root.children[0].children], [("a", 1), ("a", 2)]
        )
        self.assertEqual([c.key for c in root.children[1].children], [("b", 1)])

    def test_index_node_construction_multi_hierarchical_index(self):
        root = pdpr.IndexNode.index_to_index_node(self.multi_df.index)

        self.assertEqual([c.value for c in root.children], ["a", "b"])
        self.assertEqual([c.value for c in root.children[0].children], [1, 2])
        self.assertEqual([c.value for c in root.children[1].children], [1, 2])
        self.assertEqual([c.parent for c in root.children], [root, root])
        self.assertEqual(
            [c.parent for c in root.children[0].children],
            [root.children[0], root.children[0]],
        )
        self.assertEqual(
            [c.parent for c in root.children[1].children],
            [root.children[1], root.children[1]],
        )
        self.assertEqual([c.key for c in root.children], [("a",), ("b",)])
        self.assertEqual(
            [c.key for c in root.children[0].children], [("a", 1), ("a", 2)]
        )
        self.assertEqual(
            [c.key for c in root.children[1].children], [("b", 1), ("b", 2)]
        )

    def assert_simple_index_resolve_loc(self, locs):
        """
        This function used to test resolution loc with Node
        and then used as integration test when called from presentation_mode
        resolution_loc function
        """

        self.assertEqual(locs.children[0].value, 1)
        self.assertEqual(locs.children[0].data, (2, 3, 3, 3))

        self.assertEqual(locs.children[1].value, 2)
        self.assertEqual(locs.children[1].data, (4, 3, 5, 3))

        self.assertEqual(locs.children[2].value, 3)
        self.assertEqual(locs.children[2].data, (6, 3, 8, 3))

    def assert_multi_index_resolve_loc(self, locs):

        # first level
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (2, 3, 5, 3))  # +4 rows

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (6, 3, 10, 3))  # + 5 rows

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (2, 4, 3, 4))  # +4 rows
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (4, 4, 5, 4))  # +4 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (6, 4, 7, 4))  # +4 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (8, 4, 10, 4))  # +4 rows

    def assert_simple_column_resolve_loc(self, locs):

        self.assertEqual(locs.children[0].value, "a")
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (2, 3, 2, 4))

        self.assertEqual(locs.children[1].value, "b")
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (2, 5, 2, 6))

        self.assertEqual(locs.children[2].value, "c")
        self.assertEqual(locs.children[2].key, ("c",))
        self.assertEqual(locs.children[2].data, (2, 7, 2, 9))

    def assert_multi_column_resolve_loc(self, locs):
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (2, 3, 2, 6))  # +4 cols

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (2, 7, 2, 11))  # + 5 rows

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (3, 3, 3, 4))  # +2 rows
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (3, 5, 3, 6))  # +2 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (3, 7, 3, 8))  # +2 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (3, 9, 3, 11))  # +3 rows

    def test_index_node_resolve_loc_simple_index(self):
        root = pdpr.IndexNode.index_to_index_node(self.simple_df.index)
        row_hts = {1: 2, 2: 2, 3: 3}

        locs = pdpr.IndexNode.resolve_loc_vertical(root, (2, 3, 2, 3), row_hts=row_hts)
        self.assert_simple_index_resolve_loc(locs)

    def test_index_node_resolve_loc_multi_hierarchical_index(self):
        df = self.multi_df

        root = pdpr.IndexNode.index_to_index_node(df.index)
        row_hts = {("a", 1): 2, ("a", 2): 2, ("b", 1): 2, ("b", 2): 3}
        locs = pdpr.IndexNode.resolve_loc_vertical(root, (2, 3, 2, 3), row_hts=row_hts)
        self.assert_multi_index_resolve_loc(locs)

    def test_index_node_resolve_loc_simple_column(self):
        root = pdpr.IndexNode.index_to_index_node(self.simple_df.columns)
        col_widths = {"a": 2, "b": 2, "c": 3}
        locs = pdpr.IndexNode.resolve_loc(root, (2, 3, 2, 3), col_widths=col_widths)
        self.assert_simple_column_resolve_loc(locs)

    def test_index_node_resolve_loc_multi_hierarchical_column(self):

        df = self.multi_df_1

        root = pdpr.IndexNode.index_to_index_node(df.columns)
        col_widths = {("a", 1): 2, ("a", 2): 2, ("b", 1): 2, ("b", 2): 3}
        locs = pdpr.IndexNode.resolve_loc(
            root, (2, 3, 2, 3), col_widths=col_widths
        )  # first level
        self.assert_multi_column_resolve_loc(locs)

    def test_index_node_shift_loc(self):
        df = pd.DataFrame(
            data=dict(
                a=[0.1, 0.2, 0.3, 0.4],
                b=[100, 200, 300, 100],
                c=[True, False, True, False],
                d=[10, 20, 40, 30],
            )
        )
        df.columns = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])

        root = pdpr.IndexNode.index_to_index_node(df.columns)
        col_widths = {("a", 1): 2, ("a", 2): 2, ("b", 1): 2, ("b", 2): 3}
        locs = pdpr.IndexNode.resolve_loc(root, (2, 3, 2, 3), col_widths=col_widths)

        # check first level for integrity of test
        # first level
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (2, 3, 2, 6))  # +4 cols

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (2, 7, 2, 11))  # + 5 rows

        # now check shifting
        locs = pdpr.IndexNode.shift_loc(locs, rows=2, cols=4)
        # first level
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (4, 7, 4, 10))  # +4 cols

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (4, 11, 4, 15))  # + 5 rows

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (5, 7, 5, 8))  # +2 cols
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (5, 9, 5, 10))  # +2 cols

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (5, 11, 5, 12))  # +2 cols
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (5, 13, 5, 15))  # +3 cols


if __name__ == "__main__":
    unittest.main()
