from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.generic import FormView
from django.utils.text import slugify
from dataframe_store import settings
from dataframe_store import forms
from dataframe_store import utils


class ExportFormMixin:
    streaming_response_class = StreamingHttpResponse
    form_class = forms.ExportForm

    def _make_filename(self, form, format_):
        if form.cleaned_data['filename']:
            filename = slugify(form.cleaned_data['filename'])
        else:
            filename = slugify(form.instance.name)
        if '.' not in filename and 'extension' in format_:
            filename = '%s.%s' % (filename, format_['extension'])
        return filename

    def form_valid(self, form):
        format_id = form.cleaned_data['format']
        format_ = settings.DATA_FORMATS[format_id]
        export_file = utils.export(form.instance.obj, format_id)
        response_kwargs = {
            'content_type': format_['content_type'],
            'streaming_content': export_file
        }
        response = self.streaming_response_class(**response_kwargs)
        filename = self._make_filename(form, format_)
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response


class ExportFormView(ExportFormMixin, FormView):
    pass


class ImportFormMixin:
    form_class = forms.ImportForm


class ImportFormView(ImportFormMixin, FormView):
    pass
