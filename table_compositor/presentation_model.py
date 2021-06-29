"""
Module that supports operations to map a dataframe to an excel worksheet like entity
and also create Excel files with all fancy formatting.
"""

# TODO:
# a. Feature to Hide columns/indices
# b. Tests
# c. HTML Writer (non-nested, and then nested tables)
# e. Revisit _convert method


from collections import (
    defaultdict,
    deque,
    namedtuple,
)
from itertools import groupby

import pandas as pd
import static_frame as sf

import numpy as np

StyleWrapper = namedtuple("StyleWrapper", ["user_style"])

PresentationAndLoc = namedtuple("PresentationAndLoc", ["model", "locs"])
Locs = namedtuple(
    "Locs", ["header_loc", "index_loc", "data_loc", "index_name_loc", "nesting_level"]
)

PresentationElements = namedtuple("PresentationElements", ["values", "style"])

# The header, index_label, data and index_name attributes in the presentation
# model will be of type PresentationElements
PresentationModel = namedtuple(
    "PresentationModel", ["header", "index_label", "data", "index_name", "kwargs"]
)

LocOffsets = namedtuple("LocOffsets", ["start_row", "start_col", "end_row", "end_col"])

ValueAndStyleAttributes = namedtuple(
    "ValueAndStyleAttributes", ["value", "style_wrapper", "nesting_level"]
)


class InternalFrame:
    def __init__(self, frame):
        self._frame = frame
        self.index = InternalIndex(self._frame.index)
        self.columns = InternalIndex(self._frame.columns)

    def copy(self):
        return self._frame.copy()


class InternalIndex:
    def __init__(self, index):
        self._index = index
        if isinstance(
            self._index,
            (
                sf.IndexHierarchy,
                sf.IndexGO,
                sf.Index,
            ),
        ):
            self._index = index.to_pandas()

    @property
    def labels(self):
        if isinstance(self._index, pd.MultiIndex):
            return self._index.labels
        raise NotImplementedError()

    @property
    def name(self):
        return self._index.name

    @property
    def values(self):
        return self._index.values

    @property
    def levels(self):
        return self._index.levels

    def __len__(self):
        return len(self._index)

    def __iter__(self):
        return iter(self._index)


def default_offsets(start_row, start_col):
    return LocOffsets(
        start_row=start_row, start_col=start_col, end_row=start_row, end_col=start_col
    )


def shift_presentation_model(presentation_and_loc, rows, cols):
    return PresentationLayoutManager.shift_loc(
        presentation_and_loc, rows=rows, cols=cols
    )


def get_presentation_model_max_rows(presentation_model_and_loc):
    return PresentationLayoutManager.height(
        presentation_model_and_loc.model.data.values,
        presentation_model_and_loc.model.kwargs["hide_header"],
    )


def get_presentation_model_max_cols(presentation_model_and_loc):
    return PresentationLayoutManager.width(
        presentation_model_and_loc.model.data.values,
        presentation_model_and_loc.model.kwargs["hide_index"],
    )


def to_row_col_dict(
    presentation_and_loc, row_col_dict=None, nesting_level=0, nested=False
):
    """ """
    presentation_model = presentation_and_loc.model
    locs = presentation_and_loc.locs

    row_col_dict = row_col_dict if row_col_dict is not None else {}
    header_locs = locs.header_loc
    data_locs = locs.data_loc
    index_locs = locs.index_loc
    index_name_loc = locs.index_name_loc

    if index_name_loc:
        row_col_dict[LocOffsets(*index_name_loc)] = ValueAndStyleAttributes(
            presentation_model.index_name.values,
            presentation_model.index_name.style,
            nesting_level,
        )

    if header_locs:
        data = IndexNode.gather_data(
            header_locs,
            presentation_model.header.values,
            presentation_model.header.style,
        ).values()
        data = {
            LocOffsets(*offsets): ValueAndStyleAttributes(value, style, nesting_level)
            for offsets, value, style in data
        }
        row_col_dict.update(data)

    if index_locs:
        data = IndexNode.gather_data(
            index_locs,
            presentation_model.index_label.values,
            presentation_model.index_label.style,
        ).values()
        data = {
            LocOffsets(*offsets): ValueAndStyleAttributes(value, style, nesting_level)
            for offsets, value, style in data
        }
        row_col_dict.update(data)

    data_locs_array = data_locs.values
    pm_data_value_array = presentation_model.data.values.values
    pm_data_style_array = presentation_model.data.style.values
    for ix, _ in enumerate(presentation_model.data.values.index):
        for j, _ in enumerate(presentation_model.data.values.columns):
            offsets = data_locs_array[ix, j]
            if isinstance(offsets, PresentationAndLoc):
                inner_view_and_locs = data_locs_array[ix, j]
                if nested:
                    row_col_dict[offsets] = to_row_col_dict(
                        inner_view_and_locs, None, nesting_level, nested
                    )
                else:
                    row_col_dict.update(
                        to_row_col_dict(
                            inner_view_and_locs, None, nesting_level, nested
                        )
                    )
            else:
                loc_offsets = LocOffsets(*offsets)
                value = pm_data_value_array[ix, j]
                style = pm_data_style_array[ix, j]
                row_col_dict[loc_offsets] = ValueAndStyleAttributes(
                    value, style, nesting_level
                )

    return row_col_dict


# Core Library Functions


class PresentationLayoutManager:
    @staticmethod
    def apply(f, df):
        # lets change this to an internal representation to support multiple types of dataframes
        if not isinstance(df, InternalFrame):
            df = InternalFrame(df)

        # we short circuit this if no changes are required
        # this is useful for value_func where values rarely change
        if f is None:
            if hasattr(
                df, "copy"
            ):  # we only need the copy operation for dataframe. For SF we get that for free!
                return df.copy()

        df_new = pd.DataFrame(index=df.index._index, columns=df.columns._index)
        index_length = len(df_new.index)
        for c in df_new.columns.values:
            a = np.empty(index_length, dtype=object)
            for ix, i in enumerate(df_new.index.values):
                a[ix] = f(i, c)
            df_new.loc[:, c] = a
        return df_new

    @staticmethod
    def apply_at_column_level(f, df):

        if not isinstance(df, InternalFrame):
            df = InternalFrame(df)

        new_df = pd.DataFrame(index=df.index._index, columns=df.columns._index)
        index_length = len(df.index)
        for c in df.columns.values:
            a = np.empty(index_length, dtype=object)
            column_level_value = f(c)
            a.fill(column_level_value)
            new_df.loc[:, c] = a
        return new_df

    @staticmethod
    def resolve_loc(presentation_model, offsets=(0, 0, 0, 0), nesting_level=0):
        """
        Return a DF View with cell populated with ((r,c),(r,c)) range.
        """

        df_view = presentation_model.data.values
        header = presentation_model.header
        index_label = presentation_model.index_label

        col_widths = PresentationLayoutManager.widths(presentation_model.data.values)
        row_hts = PresentationLayoutManager.heights(presentation_model.data.values)
        header_length = (
            1 if not hasattr(df_view.columns, "levels") else len(df_view.columns.levels)
        )
        index_length = (
            1 if not hasattr(df_view.index, "levels") else len(df_view.index.levels)
        )

        if presentation_model.kwargs["hide_index"]:
            index_length = 0
        if presentation_model.kwargs["hide_header"]:
            header_length = 0

        index_name_loc = None
        if header_length != 0 and index_length != 0:
            index_name_loc = (
                offsets[0],
                offsets[1],
                offsets[0] + header_length - 1,
                offsets[1] + index_length - 1,
            )

        # handle columns
        header_loc = None
        if header_length != 0:
            header_offsets = tuple(
                x + index_length if i % 2 != 0 else x for i, x in enumerate(offsets)
            )
            header_loc = IndexNode.resolve_loc(
                header.values, header_offsets, col_widths
            )

        # handle index
        index_loc = None
        if index_length != 0:
            index_offsets = tuple(
                x + header_length if i % 2 == 0 else x for i, x in enumerate(offsets)
            )
            index_loc = IndexNode.resolve_loc_vertical(
                index_label.values, index_offsets, row_hts
            )

        # handle the df
        df_offsets = tuple(
            x + header_length if i % 2 == 0 else x + index_length
            for i, x in enumerate(offsets)
        )

        start_row, start_col, end_row, end_col = df_offsets
        df = pd.DataFrame(index=df_view.index, columns=df_view.columns)
        df_view_array = df_view.values
        all_offsets = np.empty(
            [len(df.index.values), len(df.columns.values)], dtype=object
        )
        for ix, i in enumerate(df.index.values):
            end_col, start_col = df_offsets[1], df_offsets[1]
            for j, c in enumerate(df.columns.values):
                end_row = start_row + row_hts[i] - 1
                end_col = start_col + col_widths[c] - 1
                all_offsets[ix, j] = (start_row, start_col, end_row, end_col)
                if isinstance(df_view_array[ix, j], PresentationModel):
                    inner_df = PresentationLayoutManager.resolve_loc(
                        df_view_array[ix, j],
                        (start_row, start_col, start_row, start_col),
                        nesting_level + 1,
                    )
                    all_offsets[ix, j] = inner_df
                    # assert all_offsets[ix, j] == inner_df
                start_col = end_col + 1
            start_row = end_row + 1
        df.loc[:, df.columns.values] = all_offsets

        locs = Locs(
            header_loc=header_loc,
            index_loc=index_loc,
            data_loc=df,
            index_name_loc=index_name_loc,
            nesting_level=nesting_level,
        )
        # print('Returning presenation and loc')
        return PresentationAndLoc(model=presentation_model, locs=locs)

    @staticmethod
    def shift_loc(presentation_and_loc, rows=0, cols=0):
        """
        Return a DF View with cell populated with ((r,c),(r,c)) range.
        """

        new_header_loc = None
        if presentation_and_loc.locs.header_loc:
            new_header_loc = IndexNode.shift_loc(
                presentation_and_loc.locs.header_loc, rows, cols
            )

        new_index_loc = None
        if presentation_and_loc.locs.index_loc:
            new_index_loc = IndexNode.shift_loc(
                presentation_and_loc.locs.index_loc, rows, cols
            )

        new_index_name_loc = None
        if presentation_and_loc.locs.index_name_loc:
            new_index_name_loc = tuple(
                x + rows if i % 2 == 0 else x + cols
                for i, x in enumerate(presentation_and_loc.locs.index_name_loc)
            )

        data_loc = presentation_and_loc.locs.data_loc
        data_loc_array = data_loc.values
        df = pd.DataFrame(index=data_loc.index, columns=data_loc.columns)
        new_locs = np.empty([len(df.index), len(df.columns)], dtype=object)
        for ix, _ in enumerate(df.index.values):
            for j, _ in enumerate(df.columns.values):
                try:
                    # usually we are only dealing with non-nested
                    # data frames, If we fail due to Type
                    # error it is mostly due to nested data frames
                    new_locs[ix, j] = (
                        data_loc_array[ix, j][0] + rows,
                        data_loc_array[ix, j][1] + cols,
                        data_loc_array[ix, j][2] + rows,
                        data_loc_array[ix, j][3] + cols,
                    )
                except TypeError:
                    # we assume we get here because we were
                    # adding int to nested PresentationAndLoc
                    # objects
                    # hasattr(data_loc_array[ix, j], 'locs') == True
                    inner_view_and_loc = data_loc_array[ix, j]
                    x = PresentationLayoutManager.shift_loc(
                        inner_view_and_loc, rows, cols
                    )
                    new_locs[ix, j] = x
        df.loc[:, df.columns.values] = new_locs
        # print('Done shifting')
        return PresentationAndLoc(
            model=presentation_and_loc.model,
            locs=Locs(
                header_loc=new_header_loc,
                index_loc=new_index_loc,
                data_loc=df,
                index_name_loc=new_index_name_loc,
                nesting_level=presentation_and_loc.locs.nesting_level,
            ),
        )
        # return (new_index_loc_view, new_header_loc_view, df,
        # new_index_name_loc)

    @staticmethod
    def widths(df_view):
        col_widths = {}
        for col in df_view.columns:
            s = df_view[col]
            max_width = 1
            for v in s.values:
                if isinstance(v, PresentationModel):
                    inner_width = PresentationLayoutManager.width(
                        v.data.values, v.kwargs["hide_index"]
                    )
                    max_width = max(max_width, inner_width)
            col_widths[col] = max_width
        return col_widths

    @staticmethod
    def heights(df_view):
        row_hts = {}
        for i, r in df_view.iterrows():
            max_ht = 1
            for v in r.values:
                if isinstance(v, PresentationModel):
                    inner_ht = PresentationLayoutManager.height(
                        v.data.values, v.kwargs["hide_header"]
                    )
                    max_ht = max(max_ht, inner_ht)
            row_hts[i] = max_ht
        return row_hts

    @staticmethod
    def width(df_view, hide_index):
        widths = PresentationLayoutManager.widths(df_view)
        w = 0
        if not hide_index:
            w = 1 if not hasattr(df_view.index, "levels") else len(df_view.index.levels)
        return sum(w for w in widths.values()) + w

    @staticmethod
    def height(df_view, hide_header):
        heights = PresentationLayoutManager.heights(df_view)
        col_ht = 0
        if not hide_header:
            col_ht = (
                1
                if not hasattr(df_view.columns, "levels")
                else len(df_view.columns.levels)
            )
        return sum(w for w in heights.values()) + col_ht


class IndexNode:
    def __init__(self, *, value=None, parent=None, data=None, old_data=None, key=None):
        self.value = value
        self.children = []
        self.parent = parent
        self.data = data  # this is a placehold for clients
        self.old_data = old_data
        self.key = key

    def add_children(self, child_node):
        self.children.extend(child_node)
        for c in self.children:
            c.parent = self

    @staticmethod
    def set_index(tree):
        IndexNode._apply_by_post_pre(
            IndexNode.build_index, tree, order="pre", attr="key"
        )

    @staticmethod
    def accumulate_values(node):
        if not node.parent.parent:
            return (node.value,)
        return (*IndexNode.accumulate_values(node.parent), node.value)

    @staticmethod
    def build_index(node):
        if not node.parent.parent:
            return (node.value,)
        return (*IndexNode.accumulate_values(node.parent), node.value)

    @staticmethod
    def index(node):
        if not node.parent.parent:
            x = (node.value,)
            assert node.key == x
            return node.key
        x = (*IndexNode.accumulate_values(node.parent), node.value)
        assert x == node.key
        return node.key

    @staticmethod
    def leaf_count(node, col_widths):
        # this is for single hierarchical columns
        if not node.children and not node.parent.parent:
            return col_widths[node.value]
        # multi-hierarchicial columns/index

        # leaf in a multi-heirarchical index/column
        if not node.children and node.parent.parent:
            return col_widths[IndexNode.index(node)]
        # FIXME: may not need this condition, for in-between nodes
        if node.children and len(node.children[0].children) == 0:
            return sum(col_widths[IndexNode.index(c)] for c in node.children)
        return sum(IndexNode.leaf_count(n, col_widths) for n in node.children)

    @staticmethod
    def clone(node):
        return IndexNode(
            value=node.value, parent=node.parent, key=node.key, old_data=node.data
        )

    @staticmethod
    def deep_clone(node):
        new_node = IndexNode.clone(node)
        new_node.add_children([IndexNode.deep_clone(n) for n in node.children])
        return new_node

    @staticmethod
    def _apply_by_level(f, root):
        if not root.parent:
            q = deque(root.children)
        else:
            q = deque([root])

        while q:
            n = q.popleft()
            n.data = f(n)
            q.extend(n.children)

    @staticmethod
    def _apply_by_post_pre(f, root, order, attr="data"):
        if root.parent and order == "pre":
            setattr(root, attr, f(root))

        for c in root.children:
            IndexNode._apply_by_post_pre(f, c, order, attr)

        if root.parent and order == "post":
            setattr(root, attr, f(root))

    @staticmethod
    def apply(f, root, order="post"):
        """
        Args:
            root: root of the hierarchical columns/index
            order: apply in pre-order or post-order or inorder
        """
        # clone whole tree
        new_root = IndexNode.deep_clone(root)

        if order == "level":
            IndexNode._apply_by_level(f, new_root)
        else:
            IndexNode._apply_by_post_pre(f, new_root, order)
        return new_root

    @staticmethod
    def index_to_index_node(index):
        """
        Convert a column index to a tree view that can be used for rendering

        Args:
            index: usually df.columns, can all support df.index
        """
        if not isinstance(index, InternalIndex):
            index = InternalIndex(index)

        root = IndexNode()

        # handle frames without an index but only columns
        if len(index) == 0:
            return root
        if not isinstance(index._index, pd.MultiIndex):
            # not an multi-index
            root.add_children(
                IndexNode(value=i, parent=root, key=(i,)) for i in index.values
            )
            return root

        # multi hierarchical index
        values = list(zip(*index.labels))
        tree = IndexNode._build_tree(index, values, level=0)
        root.add_children(tree)

        IndexNode.set_index(root)
        return root

    @staticmethod
    def _build_tree(index, indices, level=0):
        """
        Build a tree of IndexNode that is a tree representtion of
        pandas multi-index
        """
        grps = groupby(indices, key=lambda x: x[0])
        nodes = []
        for k, g in grps:
            g = list(g)
            if len(g[0]) == 1:
                # leaf node
                for i in g:
                    nodes.append(IndexNode(value=index.levels[level][i[0]]))
            else:
                next_level = [i[1:] for i in g]
                children = IndexNode._build_tree(index, next_level, level + 1)
                parent = IndexNode(value=index.levels[level][k])
                parent.add_children(children)
                nodes.append(parent)
        return nodes

    @staticmethod
    def shift_loc(node, rows=0, cols=0):
        def _shift_loc(node):
            return (
                node.old_data[0] + rows,
                node.old_data[1] + cols,
                node.old_data[2] + rows,
                node.old_data[3] + cols,
            )

        return IndexNode.apply(_shift_loc, node)

    # FIXME: offsets can be explicit start_row and start_col
    @staticmethod
    def resolve_loc(tree, offsets, col_widths):
        """
        Args:
            col_widths: dictionary of column width of each column, indexed by column key. For multi-hierarchical columns the key would a tuple where the tuple is the unique index into the column. Eg {('a', 1): 10}
        """

        # make this immutable
        original_offsets = offsets
        current_offsets = [x for x in original_offsets]
        previous_level = 1

        def _resolve_loc(node):
            nonlocal current_offsets
            nonlocal previous_level
            level = len(IndexNode.index(node))
            n_children = IndexNode.leaf_count(node, col_widths)
            n_children = max(1, n_children)
            if level == previous_level:
                new_offsets = [
                    current_offsets[0],
                    current_offsets[1],
                    current_offsets[0],
                    current_offsets[1] + n_children - 1,
                ]
                current_offsets = _shift_cols(new_offsets)
            else:
                new_offsets = [
                    current_offsets[0] + 1,
                    original_offsets[1],
                    current_offsets[0] + 1,
                    original_offsets[1] + n_children - 1,
                ]
                previous_level = level
                current_offsets = _shift_cols(new_offsets)
            return tuple(new_offsets)

        return IndexNode.apply(_resolve_loc, tree, order="level")

    # FIXME: offsets can be explicit start_row and start_col
    @staticmethod
    def resolve_loc_vertical(tree, offsets, row_hts):

        # make this immutable

        original_offsets = offsets
        current_offsets = [x for x in original_offsets]
        previous_level = 1

        def _resolve_loc(node):
            # import ipdb; ipdb.set_trace()
            nonlocal current_offsets
            nonlocal previous_level
            level = len(IndexNode.index(node))
            n_children = IndexNode.leaf_count(node, row_hts)
            n_children = max(1, n_children)
            if level == previous_level:
                new_offsets = [
                    current_offsets[0],
                    current_offsets[1],
                    current_offsets[0] + n_children - 1,
                    current_offsets[1],
                ]
                current_offsets = _shift_row(new_offsets)
            else:
                new_offsets = [
                    original_offsets[0],
                    current_offsets[1] + 1,
                    original_offsets[0] + n_children - 1,
                    current_offsets[1] + 1,
                ]
                previous_level = level
                current_offsets = _shift_row(new_offsets)
            # print(node.value, new_offsets)
            return tuple(new_offsets)

        return IndexNode.apply(_resolve_loc, tree, order="level")

    @staticmethod
    def gather_data(*trees):
        """
        Returns a dict index by index and all data attributes
        from all trees
        """
        data = defaultdict(list)

        def _gather_data(node):
            data[IndexNode.index(node)].append(node.old_data)

        for t in trees:
            IndexNode.apply(_gather_data, t)
        return data


def _shift_cols(offset):
    return (offset[0], offset[3] + 1, offset[2], offset[3] + 1)


def _shift_row(offset):
    return (offset[2] + 1, offset[1], offset[2] + 1, offset[3])
