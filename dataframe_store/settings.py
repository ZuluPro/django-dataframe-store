from django.conf import settings

PREFIX = 'DATAFRAME_'


def get_setting(name, default=None):
    name = PREFIX + name
    value = getattr(settings, name, default)
    return value


BASE_MODEL = 'dataframe_store.models.BaseDbDataFrame'

DEFAULT_DATA_FORMATS = {
    'csv': {
        'import_path': 'pandas.read_csv',
        'export_path': 'dataframe_store.utils.to_csv',
        'name': 'CSV',
        'content_type': 'text/csv',
        'type': 'text',
        'extension': 'csv',
    },
    'xlsx': {
        'import_path': 'pandas.read_excel',
        'export_path': 'dataframe_store.utils.to_excel',
        'name': 'Excel XLSX',
        'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'type': 'binary',
        'extension': 'xlsx',
    },
}
DATA_FORMATS = get_setting('DATA_FORMATS', DEFAULT_DATA_FORMATS)
