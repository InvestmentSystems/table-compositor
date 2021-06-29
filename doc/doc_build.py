import os
from sphinx.cmd.build import main
#from pygments import lexers
#sphinx.add_lexer('yaml', lexers.YamlLexer())


# Note: The api.rst file will not successfully build
# with this setup, since sphinx to work with ReadTheDocs
# we cannot reference the table_compositor package from `package`
# module as root.
# For example
# package.public.table_compositor.table_compositor.* in api.rst will not work.
# Therefore, those warning can be ignored.


if __name__ == '__main__':
    # must be in this directory
    doc_dir = os.path.abspath(os.path.dirname(__file__))
    doctrees_dir = os.path.join(doc_dir, 'build', 'doctrees')
    source_dir = os.path.join(doc_dir, 'source')
    build_dir = os.path.join(doc_dir, 'build', 'html')

    args = ['-E', '-b', 'html',
            '-d', doctrees_dir,
            source_dir,
            build_dir]
    status = main(args)

    import webbrowser
    webbrowser.open(os.path.join(build_dir, 'index.html'))
