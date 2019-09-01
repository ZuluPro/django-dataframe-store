import io
import importlib
from dataframe_store import settings


def to_csv(fileobj, df, **kwargs):
    return df.to_csv(fileobj, **kwargs)


def to_excel(fileobj, df, **kwargs):
    return df.to_excel(fileobj, **kwargs)


def get_func(func_path=None):
    module_path = '.'.join(func_path.split('.')[:-1])
    func_name = func_path.split('.')[-1]
    module = importlib.import_module(module_path)
    func_class = getattr(module, func_name)
    return func_class


def export(df, format_id, func_kwargs=None, fileobj=None):
    func_kwargs = func_kwargs or {}
    format_ = settings.DATA_FORMATS[format_id]
    fileobj = io.StringIO() if format_['type'] == 'text' else io.BytesIO()
    func = get_func(format_['export_path'])
    func(fileobj, df, **func_kwargs)
    fileobj.seek(0)
    return fileobj
