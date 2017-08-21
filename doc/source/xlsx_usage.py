'''
This module is referred to by the Sphinx documentation. If you need to run this
module, install table_compositor in an separate  environment and then run this module
in that environment. This helps the imports find the modules in the right place
'''

# start_imports
import tempfile
import zipfile
import collections
import os
import webbrowser

import requests
import pandas as pd

import table_compositor.table_compositor as tc
import table_compositor.xlsx_writer as xlsxw
import table_compositor.xlsx_styles as xlsstyle
# end_imports

# start_data_routine
# code snippet adapted from http://function-pipe.readthedocs.io/en/latest/usage_df.html
# source url
URL_NAMES = 'https://www.ssa.gov/oact/babynames/names.zip'
ZIP_NAME = 'names.zip'

def load_names_data():
    fp = os.path.join(tempfile.gettempdir(), ZIP_NAME)
    if not os.path.exists(fp):
        r = requests.get(URL_NAMES)
        with open(fp, 'wb') as f:
            f.write(r.content)

    post = collections.OrderedDict()
    with zipfile.ZipFile(fp) as zf:
        # get ZipInfo instances
        for zi in sorted(zf.infolist(), key=lambda zi: zi.filename):
            fn = zi.filename
            if fn.startswith('yob'):
                year = int(fn[3:7])
                df = pd.read_csv(
                    zf.open(zi),
                    header=None,
                    names=('name', 'gender', 'count'))
                df['year'] = year
                post[year] = df

        df = pd.concat(post.values())
        df.set_index('name', inplace=True, drop=True)
        return df

def sample_names_data():
    df = load_names_data()
    df = df[(df['year'] == 2015) & (df['count'] > 1000)]
    return df.sample(100, random_state=0).sort_values('count')

def top_names_for_year(year=2015, gender='F', top_n=5):
    df = load_names_data()
    df = df[(df['year'] == year) & (df['gender'] == gender)]
    df = df.sort_values('count')[:top_n]
    return df
# end_data_routine

# start_XLSXExample1
class XLSXExample1:
    '''
    Demonstrates rendering a simple dataframe to a xlsx file
    using the default styles
    '''
    @classmethod
    def render_xlsx(cls):
        '''
        Render the df to a xlsx file.
        '''

        # load data
        df = sample_names_data()
        # build presentation model
        pm = tc.build_presentation_model(df=df, output_format='xlsx')

        # render to xlsx
        tempdir = tempfile.gettempdir()
        fp = os.path.join(tempdir, 'example1.xlsx')
        layout = [pm]
        print('Writing to ' + fp)
        xlsxw.XLSXWriter.to_xlsx(layout, output_fp=fp)
# end_XLSXExample1


# start_XLSXExample2
class XLSXExample2:
    '''
    Demonstrates using call-backs that help set the display and style
    properties of each cell in the xlsx sheet.
    '''

    @staticmethod
    def data_value_func(df):
        def _inner(idx, col):
            if col == 'gender':
                if df.loc[idx, col] == 'F':
                    return "Female"
                return 'Male'
            return df.loc[idx, col]
        return _inner

    @staticmethod
    def data_style_func(df):
        def _inner(idx, col):
            bg_color = None
            number_format='General'
            if col == 'count':
                number_format='#,##0'
            if df.loc[idx, 'gender'] == 'F':
                bg_color = 'bbdef8'
            else:
                bg_color = 'e3f2fd'
            return xlsstyle.OpenPyxlStyleHelper.get_style(
                bg_color=bg_color,
                number_format=number_format)
        return _inner

    @staticmethod
    def index_name_value_func(value):
        return value.capitalize()

    @staticmethod
    def index_name_style_func(value):
        return xlsstyle.OpenPyxlStyleHelper.default_header_style()

    @staticmethod
    def header_value_func(node):
        return node.value.capitalize()

    @staticmethod
    def header_style_func(node):
        return xlsstyle.OpenPyxlStyleHelper.default_header_style()

    @staticmethod
    def index_value_func(node):
        return node.value.capitalize()

    @staticmethod
    def index_style_func(df):
        def _inner(node):
            bg_color = None
            if df.loc[node.value, 'gender'] == 'F':
                bg_color = 'bbdef8'
            else:
                bg_color = 'e3f2fd'
            return xlsstyle.OpenPyxlStyleHelper.get_style(bg_color=bg_color)
        return _inner

    @classmethod
    def render_xlsx(cls):
        # load data
        df = sample_names_data()
        # build presentation model
        klass_ = XLSXExample2
        pm = tc.build_presentation_model(
            df=df,
            output_format='xlsx',
            data_value_func=klass_.data_value_func(df),
            data_style_func=klass_.data_style_func(df),
            header_value_func=klass_.header_value_func,
            header_style_func=klass_.header_style_func,
            index_style_func=klass_.index_style_func(df),
            index_value_func=klass_.index_value_func,
            index_name_style_func=klass_.index_name_style_func,
            index_name_func=klass_.index_name_value_func)

        # render to xlsx
        tempdir = tempfile.gettempdir()
        fp = os.path.join(tempdir, 'example2.xlsx')
        layout = [pm]
        print('Writing to ' + fp)
        xlsxw.XLSXWriter.to_xlsx(layout, output_fp=fp)
# end_XLSXExample2

# start_XLSXExample3
class XLSXExample3:
    '''
    Demonstrates using call-backs and also rendering multiple tables to single
    worksheet.
    '''

    @staticmethod
    def data_value_func(df):
        def _inner(idx, col):
            if col == 'gender':
                if df.loc[idx, col] == 'F':
                    return "Female"
                return 'Male'
            return df.loc[idx, col]
        return _inner

    @staticmethod
    def data_style_func(df):
        def _inner(idx, col):
            bg_color = None
            number_format='General'
            if col == 'count':
                number_format='#,##0'
            if df.loc[idx, 'gender'] == 'F':
                bg_color = 'bbdef8'
            else:
                bg_color = 'e3f2fd'
            return xlsstyle.OpenPyxlStyleHelper.get_style(
                bg_color=bg_color,
                number_format=number_format)
        return _inner

    @staticmethod
    def index_name_value_func(value):
        return value.capitalize()

    @staticmethod
    def index_name_style_func(value):
        return xlsstyle.OpenPyxlStyleHelper.default_header_style()

    @staticmethod
    def header_value_func(node):
        return node.value.capitalize()

    @staticmethod
    def header_style_func(node):
        return xlsstyle.OpenPyxlStyleHelper.default_header_style()

    @staticmethod
    def index_value_func(node):
        return node.value.capitalize()

    @staticmethod
    def index_style_func(df):
        def _inner(node):
            bg_color = None
            if df.loc[node.value, 'gender'] == 'F':
                bg_color = 'bbdef8'
            else:
                bg_color = 'e3f2fd'
            return xlsstyle.OpenPyxlStyleHelper.get_style(bg_color=bg_color)
        return _inner


    @classmethod
    def render_xlsx(cls):
        # Prepare first data frame (same as in render_xlsx)
        df = sample_names_data()
        # build presentation model
        klass_ = XLSXExample3
        pm_all = tc.build_presentation_model(
            df=df,
            output_format='xlsx',
            data_value_func=klass_.data_value_func(df),
            data_style_func=klass_.data_style_func(df),
            header_value_func=klass_.header_value_func,
            header_style_func=klass_.header_style_func,
            index_style_func=klass_.index_style_func(df),
            index_value_func=klass_.index_value_func,
            index_name_style_func=klass_.index_name_style_func,
            index_name_func=klass_.index_name_value_func)

        male_df = top_names_for_year(gender='M')
        pm_top_male = tc.build_presentation_model(
            df=male_df,
            output_format='xlsx',
            data_value_func=klass_.data_value_func(male_df),
            data_style_func=klass_.data_style_func(male_df),
            header_value_func=klass_.header_value_func,
            header_style_func=klass_.header_style_func,
            index_style_func=klass_.index_style_func(male_df),
            index_value_func=klass_.index_value_func,
            index_name_style_func=klass_.index_name_style_func,
            index_name_func=klass_.index_name_value_func)

        female_df = top_names_for_year(gender='F')
        pm_top_female = tc.build_presentation_model(
            df=female_df,
            output_format='xlsx',
            data_value_func=klass_.data_value_func(female_df),
            data_style_func=klass_.data_style_func(female_df),
            header_value_func=klass_.header_value_func,
            header_style_func=klass_.header_style_func,
            index_style_func=klass_.index_style_func(female_df),
            index_value_func=klass_.index_value_func,
            index_name_style_func=klass_.index_name_style_func,
            index_name_func=klass_.index_name_value_func)


        layout = [pm_all, [pm_top_female, pm_top_male]]
        # render to xlsx
        tempdir = tempfile.gettempdir()
        fp = os.path.join(tempdir, 'example3.xlsx')
        print('Writing to ' + fp)
        xlsxw.XLSXWriter.to_xlsx(layout, output_fp=fp, orientation='horizontal')
# end_XLSXExample3

# start_XLSXExample4
class XLSXExample4:
    '''
    Demonstrate styling and rendering of multi-hierarchical indexed dataframe
    into a xlsx file.
    '''

    @staticmethod
    def data_style_func(df):
        def _inner(idx, col):
            bg_color = None
            number_format = 'General'
            if col == 'count':
                number_format = '#,##0'
            if idx[1] == 'F':
                bg_color = 'bbdef8'
            else:
                bg_color = 'e3f2fd'
            return xlsstyle.OpenPyxlStyleHelper.get_style(
                bg_color=bg_color,
                number_format=number_format)
        return _inner

    @staticmethod
    def index_name_value_func(value):
        return 'Max By Year'

    @staticmethod
    def index_name_style_func(value):
        return xlsstyle.OpenPyxlStyleHelper.default_header_style()

    @staticmethod
    def header_value_func(node):
        return node.value.capitalize()

    @staticmethod
    def header_style_func(node):
        return xlsstyle.OpenPyxlStyleHelper.default_header_style()

    @staticmethod
    def index_value_func(node):
        if isinstance(node.value, str):
            return node.value.capitalize()
        return node.value

    @staticmethod
    def index_style_func(df):
        def _inner(node):
            bg_color = None
            if len(node.key) == 1:
                bg_color = '4f81bd'
            elif node.key[1] == 'F':
                bg_color = 'bbdef8'
            else:
                bg_color = 'e3f2fd'
            return xlsstyle.OpenPyxlStyleHelper.get_style(bg_color=bg_color)
        return _inner

    @classmethod
    def render_xlsx(cls):

        # Prepare first data frame (same as in render_xlsx)
        data_df = load_names_data()
        data_df = data_df[data_df['year'] >= 2000]
        g = data_df.groupby(('year', 'gender'))
        df = g.max()

        klass_ = cls
        pm = tc.build_presentation_model(
            df=df,
            output_format='xlsx',
            #data_value_func=None,   # use default
            data_style_func=klass_.data_style_func(df),
            header_value_func=klass_.header_value_func,
            header_style_func=klass_.header_style_func,
            index_style_func=klass_.index_style_func(df),
            index_value_func=klass_.index_value_func,
            index_name_style_func=klass_.index_name_style_func,
            index_name_func=klass_.index_name_value_func)

        layout = [pm]
        # render to xlsx
        tempdir = tempfile.gettempdir()
        fp = os.path.join(tempdir, 'example4.xlsx')
        print('Writing to ' + fp)
        xlsxw.XLSXWriter.to_xlsx(layout, output_fp=fp, orientation='horizontal')
# end_XLSXExample4

def main():
    XLSXExample1.render_xlsx()
    XLSXExample2.render_xlsx()
    XLSXExample3.render_xlsx()
    XLSXExample4.render_xlsx()

if __name__ == '__main__':
    main()
