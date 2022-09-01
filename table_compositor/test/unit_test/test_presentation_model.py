import unittest
import warnings

import pandas as pd

import table_compositor.presentation_model as ptm
import table_compositor.table_compositor as tc


class TestUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simple_df = pd.DataFrame(
            data=dict(a=[0.1, 0.2, 0.3], b=[100, 200, 300], c=[True, False, True]),
            index=[1, 2, 3],
        )
        cls.simple_pm = tc.build_presentation_model(df=cls.simple_df)

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
        cls.multi_pm = tc.build_presentation_model(df=cls.multi_df)

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
        cls.multi_pm_1 = tc.build_presentation_model(df=cls.multi_df_1)

        # use for nesting - though we use same df, the instance
        # of presentation model is new
        cls.multi_pm_outer = tc.build_presentation_model(df=cls.multi_df_1)
        cls.multi_pm_2 = tc.build_presentation_model(df=cls.multi_df_1)

        cls.multi_df.index.name = "Sample_Index"

    def assert_simple_index_resolve_loc(self, locs):
        """
        This function used to test resolution loc with Node
        and then used as integration test when called from presentation_mode
        resolution_loc function
        """

        self.assertEqual(locs.children[0].value, 1)
        self.assertEqual(locs.children[0].data, (1, 0, 1, 0))

        self.assertEqual(locs.children[1].value, 2)
        self.assertEqual(locs.children[1].data, (2, 0, 2, 0))

        self.assertEqual(locs.children[2].value, 3)
        self.assertEqual(locs.children[2].data, (3, 0, 3, 0))

    def assert_simple_column_resolve_loc(self, locs):

        self.assertEqual(locs.children[0].value, "a")
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (0, 1, 0, 1))

        self.assertEqual(locs.children[1].value, "b")
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (0, 2, 0, 2))

        self.assertEqual(locs.children[2].value, "c")
        self.assertEqual(locs.children[2].key, ("c",))
        self.assertEqual(locs.children[2].data, (0, 3, 0, 3))

    def assert_multi_index_resolve_loc(self, locs):
        """
        shift_locs: helps use the same test fixture to test
        locs when either index or header or hidden.
        """

        # first level
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (2, 0, 3, 0))  # +4 rows

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (4, 0, 5, 0))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (2, 1, 2, 1))  # +4 rows
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (3, 1, 3, 1))  # +4 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (4, 1, 4, 1))  # +4 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (5, 1, 5, 1))  # +4 rows

    def assert_multi_index_resolve_loc_with_nested_pm(self, locs):
        """
        shift_locs: helps use the same test fixture to test
        locs when either index or header or hidden.
        """

        # first level
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (2, 0, 8, 0))  # +4 rows

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (9, 0, 10, 0))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (2, 1, 2, 1))  # +4 rows
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (3, 1, 8, 1))  # +4 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (9, 1, 9, 1))  # +4 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (10, 1, 10, 1))  # +4 rows

    def assert_multi_index_resolve_loc_of_nested_pm(self, locs):
        """
        shift_locs: helps use the same test fixture to test
        locs when either index or header or hidden.
        """
        # assumes nesting at  [('a', 2), ('a', 1)] of cls.multi_pm_1
        # first level
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (5, 2, 6, 2))

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (7, 2, 8, 2))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (5, 3, 5, 3))  # +4 rows
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (6, 3, 6, 3))  # +4 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (7, 3, 7, 3))  # +4 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (8, 3, 8, 3))  # +4 rows

    def assert_multi_hierarchical_resolve_loc_wo_index(self, locs):
        """
        shift_locs: helps use the same test fixture to test
        locs when either index or header or hidden.
        """
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (0, 0, 0, 1))

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (0, 2, 0, 3))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (1, 0, 1, 0))
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (1, 1, 1, 1))  # +2 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (1, 2, 1, 2))  # +2 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (1, 3, 1, 3))  # +3 rows

    def assert_multi_hierarchical_resolve_loc_wo_header(self, locs):
        """
        shift_locs: helps use the same test fixture to test
        locs when either index or header or hidden.
        """

        # first level
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (0, 0, 1, 0))  # +4 rows

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (2, 0, 3, 0))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (0, 1, 0, 1))  # +4 rows
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (1, 1, 1, 1))  # +4 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (2, 1, 2, 1))  # +4 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (3, 1, 3, 1))  # +4 rows

    def assert_multi_column_resolve_loc(self, locs):
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (0, 2, 0, 3))

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (0, 4, 0, 5))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (1, 2, 1, 2))
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (1, 3, 1, 3))  # +2 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (1, 4, 1, 4))  # +2 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (1, 5, 1, 5))  # +3 rows

    def assert_multi_column_resolve_loc_with_nested_pm(self, locs):
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (0, 2, 0, 8))

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (0, 9, 0, 10))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (1, 2, 1, 7))
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (1, 8, 1, 8))  # +2 rows

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (1, 9, 1, 9))  # +2 rows
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (1, 10, 1, 10))  # +3 rows

    def assert_multi_column_resolve_loc_of_nested_pm(self, locs):

        # assumes nesting at  [('a', 2), ('a', 1)] of cls.multi_pm_1
        # ('a', )
        self.assertEqual(locs.children[0].key, ("a",))
        self.assertEqual(locs.children[0].data, (3, 4, 3, 5))

        # ('b', )
        self.assertEqual(locs.children[1].key, ("b",))
        self.assertEqual(locs.children[1].data, (3, 6, 3, 7))

        # second level
        # ('a', 1)
        self.assertEqual(locs.children[0].children[0].key, ("a", 1))
        self.assertEqual(locs.children[0].children[0].data, (4, 4, 4, 4))
        # ('a', 2)
        self.assertEqual(locs.children[0].children[1].key, ("a", 2))
        self.assertEqual(locs.children[0].children[1].data, (4, 5, 4, 5))

        # ('b', 1)
        self.assertEqual(locs.children[1].children[0].key, ("b", 1))
        self.assertEqual(locs.children[1].children[0].data, (4, 6, 4, 6))
        # ('b', 2)
        self.assertEqual(locs.children[1].children[1].key, ("b", 2))
        self.assertEqual(locs.children[1].children[1].data, (4, 7, 4, 7))

    ###########################################################
    # Tests on presentation model
    ###########################################################
    def test_presentation_model_resolve_loc_simple_df(self):
        pm = self.simple_pm
        locs = ptm.PresentationLayoutManager.resolve_loc(pm).locs
        self.assert_simple_column_resolve_loc(locs.header_loc)
        self.assert_simple_index_resolve_loc(locs.index_loc)

        # asserts in loop here is OK, since this is more
        # an integrity check
        for r, index_label in enumerate(locs.data_loc.index):
            for c, column in enumerate(locs.data_loc.columns):
                offset = (r + 1, c + 1, r + 1, c + 1)
                self.assertEqual(locs.data_loc.loc[index_label, column], offset)

    def test_presentation_model_resolve_loc_multi_hierarchical(self):
        pm = self.multi_pm_1
        locs = ptm.PresentationLayoutManager.resolve_loc(pm).locs
        self.assert_multi_column_resolve_loc(locs.header_loc)
        self.assert_multi_index_resolve_loc(locs.index_loc)

        # asserts in loop here is OK, since this is more
        # an integrity check
        for r, index_label in enumerate(locs.data_loc.index):
            for c, column in enumerate(locs.data_loc.columns):
                offset = (r + 2, c + 2, r + 2, c + 2)
                self.assertEqual(locs.data_loc.loc[index_label, column], offset)

    def test_presentation_model_resolve_loc_multi_df_hide_index_and_columns(self):
        df = pd.DataFrame(
            data=dict(
                a=[0.1, 0.2, 0.3, 0.4],
                b=[100, 200, 300, 100],
                c=[True, False, True, False],
                d=[10, 20, 40, 30],
            )
        )
        df.columns = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])
        df.index = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])
        pm = tc.build_presentation_model(
            df=df, **{"hide_index": True, "hide_header": True}
        )
        locs = ptm.PresentationLayoutManager.resolve_loc(pm).locs

        self.assertIsNone(locs.header_loc, "header_loc not None")
        self.assertIsNone(locs.index_loc, "index_loc not None")

        # asserts in loop here is OK, since this is more
        # an integrity check
        for r, index_label in enumerate(locs.data_loc.index):
            for c, column in enumerate(locs.data_loc.columns):
                offset = (r, c, r, c)
                self.assertEqual(locs.data_loc.loc[index_label, column], offset)

    def test_presentation_model_resolve_loc_multi_df_hide_index(self):
        df = pd.DataFrame(
            data=dict(
                a=[0.1, 0.2, 0.3, 0.4],
                b=[100, 200, 300, 100],
                c=[True, False, True, False],
                d=[10, 20, 40, 30],
            )
        )
        df.columns = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])
        df.index = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])
        pm = tc.build_presentation_model(df=df, **{"hide_index": True})

        locs = ptm.PresentationLayoutManager.resolve_loc(pm).locs

        self.assertIsNone(locs.index_loc, "header_loc not None")
        self.assert_multi_hierarchical_resolve_loc_wo_index(locs.header_loc)

        # asserts in loop here is OK, since this is more
        # an integrity check
        for r, index_label in enumerate(locs.data_loc.index):
            for c, column in enumerate(locs.data_loc.columns):
                offset = (r + 2, c, r + 2, c)
                self.assertEqual(locs.data_loc.loc[index_label, column], offset)

    def test_presentation_model_resolve_loc_multi_df_hide_columns(self):
        df = pd.DataFrame(
            data=dict(
                a=[0.1, 0.2, 0.3, 0.4],
                b=[100, 200, 300, 100],
                c=[True, False, True, False],
                d=[10, 20, 40, 30],
            )
        )
        df.columns = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])
        df.index = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])
        pm = tc.build_presentation_model(df=df, **{"hide_header": True})

        locs = ptm.PresentationLayoutManager.resolve_loc(pm).locs

        self.assertIsNone(locs.header_loc, "header_loc not None")
        self.assert_multi_hierarchical_resolve_loc_wo_header(locs.index_loc)

        # asserts in loop here is OK, since this is more
        # an integrity check
        for r, index_label in enumerate(locs.data_loc.index):
            for c, column in enumerate(locs.data_loc.columns):
                offset = (r, c + 2, r, c + 2)
                self.assertEqual(locs.data_loc.loc[index_label, column], offset)

    def test_presentation_model_resolve_loc_multi_hierarchical_nested(self):
        pm = self.multi_pm_outer
        pm2 = self.multi_pm_2
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pm.data.values.loc[("a", 2), ("a", 1)] = pm2

        locs = ptm.PresentationLayoutManager.resolve_loc(pm).locs
        self.assert_multi_column_resolve_loc_with_nested_pm(locs.header_loc)
        self.assert_multi_index_resolve_loc_with_nested_pm(locs.index_loc)

        # asserts in loop here is OK, since this is more
        # an integrity check
        self.assertTrue(
            isinstance(locs.data_loc.loc[("a", 2), ("a", 1)], ptm.PresentationAndLoc)
        )

        # check merged cells below nested pm
        self.assertEqual(locs.data_loc.loc[("b", 2), ("a", 1)], (10, 2, 10, 7))

        # check some locs of nested pm
        inner_loc = locs.data_loc.loc[("a", 2), ("a", 1)].locs
        self.assert_multi_column_resolve_loc_of_nested_pm(inner_loc.header_loc)
        self.assert_multi_index_resolve_loc_of_nested_pm(inner_loc.index_loc)

        for r, index_label in enumerate(inner_loc.data_loc.index):
            for c, column in enumerate(inner_loc.data_loc.columns):
                offset = (r + 5, c + 4, r + 5, c + 4)
                self.assertEqual(inner_loc.data_loc.loc[index_label, column], offset)

    def test_presentation_model_apply_with_None_as_callback(self):

        df = pd.DataFrame(data=dict(a=[1, 2, 3], b=[4, 5, 6]))
        df_actual = ptm.PresentationLayoutManager.apply(None, df)

        self.assertListEqual(df["a"].values.tolist(), df_actual["a"].tolist())
        self.assertListEqual(df["b"].values.tolist(), df_actual["b"].tolist())

    def test_presentation_model_apply_with_callback(self):

        df = pd.DataFrame(data=dict(a=[1, 2, 3], b=[4, 5, 6]))
        df_actual = ptm.PresentationLayoutManager.apply(
            lambda i, c: df.loc[i, c] * 10, df
        )

        self.assertListEqual((df["a"] * 10).values.tolist(), df_actual["a"].tolist())
        self.assertListEqual((df["b"] * 10).values.tolist(), df_actual["b"].tolist())

    def test_presentation_model_apply_with_callback_at_column_level(self):

        df = pd.DataFrame(data=dict(a=[1, 2, 3], b=[4, 5, 6]))
        df_actual = ptm.PresentationLayoutManager.apply_at_column_level(
            lambda c: 10, df
        )

        self.assertListEqual(df_actual["a"].values.tolist(), [10] * 3)
        self.assertListEqual(df_actual["b"].values.tolist(), [10] * 3)


if __name__ == "__main__":
    unittest.main()
