"""
Store pandas dataframes in DB.
"""
VERSION = (0, 1)
__version__ = '.'.join([str(i) for i in VERSION])
__author__ = 'Anthony Monthe (ZuluPro)'
__email__ = 'amonthe@cloudspectator.com'
__url__ = 'https://github.com/cloudspectatordevelopment/django-dataframe-store'
__license__ = 'BSD'

default_app_config = 'dataframe_store.apps.DataframeStoreConfig'
