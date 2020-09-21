"""docutils markdown parser"""

__version__ = '0.2.4'

def setup(app):
    """Initialize Sphinx extension."""
    return {'version': __version__, 'parallel_read_safe': True}
