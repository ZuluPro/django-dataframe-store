import pandas as pd

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

import swapper

from dataframe_store import models
from dataframe_store import settings
from dataframe_store import utils

EMPTY = (None, '---')
AXIS = (
    (0, _("Rows")),
    (1, _("Columns")),
)
HOW_DROP_NA = (
    ('any', _("Any")),
    ('all', _("All")),
)
NA_POSITIONS = [
    ('first', _("First")),
    ('last', _("Last")),
]
DROP_DUPLICATES_KEEP = NA_POSITIONS + [
    ('False', _("Drop all")),
]

DATA_FORMATS = [
    (key, value.get('name', key))
    for key, value in settings.DATA_FORMATS.items()
]


class ExportForm(forms.ModelForm):
    filename = forms.CharField(
        required=False,
    )
    format = forms.ChoiceField(
        choices=DATA_FORMATS,
    )

    class Meta:
        model = models.DbDataFrame
        fields = ('filename', 'format',)


class ImportForm(forms.ModelForm):
    format = forms.ChoiceField(
        choices=DATA_FORMATS,
    )
    file = forms.FileField(
    )

    class Meta:
        model = swapper.load_model("dataframe_store", "DbDataFrame")
        exclude = ('obj', 'labels', 'shape_x', 'shape_y', 'parent')

    def clean_file(self):
        tmp_file = self.cleaned_data['file']
        format_id = self.cleaned_data['format']
        format_ = settings.DATA_FORMATS[format_id]
        func = utils.get_func(format_['import_path'])
        dataframe = func(tmp_file.file)
        return dataframe

    def clean(self):
        self.instance.obj = self.cleaned_data['file']


class BaseDataFrameActionForm(forms.ModelForm):
    copy_name = forms.CharField(
        help_text=_("If filled, the output dataframe will be stored with this name."),
        required=False,
    )

    class Meta:
        model = swapper.load_model("dataframe_store", "DbDataFrame")
        exclude = ['parent']

    def save(self, *args, **kwargs):
        if self.cleaned_data['copy_name']:
            self.instance.id = None
            self.instance.name = self.cleaned_data['copy_name']
        return super().save(*args, **kwargs)


class DropLabelForm(BaseDataFrameActionForm):
    x_labels = forms.MultipleChoiceField(
        required=False,
    )
    y_labels = forms.MultipleChoiceField(
        required=False,
    )

    class Meta(BaseDataFrameActionForm.Meta):
        fields = [
            'x_labels',
            'y_labels',
            'copy_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x_labels'].choices = [
            (i, i) for i in self.instance.columns
        ]
        self.fields['y_labels'].choices = [
            (i, i) for i in self.instance.rows
        ]

    def save(self, *args, **kwargs):
        if self.cleaned_data['x_labels']:
            self.instance.obj.drop(labels=self.cleaned_data['x_labels'], axis=1, inplace=True)
        if self.cleaned_data['y_labels']:
            try:
                self.instance.obj.drop(labels=self.cleaned_data['y_labels'], axis=0, inplace=True)
            except KeyError:
                row_ids = [float(i) for i in self.cleaned_data['y_labels']]
                self.instance.obj.drop(labels=row_ids, axis=0, inplace=True)
        return super().save(*args, **kwargs)


class SortValuesForm(BaseDataFrameActionForm):
    x_labels = forms.ChoiceField(
        required=False,
    )
    y_labels = forms.ChoiceField(
        required=False,
    )
    na_position = forms.ChoiceField(
        label=_("N/A position"),
        choices=NA_POSITIONS,
        help_text=_("Puts unknown values at the beginning or the end.")
    )

    class Meta(BaseDataFrameActionForm.Meta):
        fields = [
            'x_labels',
            'y_labels',
            'na_position',
            'copy_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x_labels'].choices = [EMPTY] + [
            ('dsc:'+str(i), 'dsc:'+str(i)) for i in self.instance.columns
        ] + [
            ('asc:'+str(i), 'asc:'+str(i)) for i in self.instance.columns
        ]
        self.fields['y_labels'].choices = [EMPTY] + [
            ('dsc:'+str(i), 'dsc:'+str(i)) for i in self.instance.columns
        ] + [
            ('asc:'+str(i), 'asc:'+str(i)) for i in self.instance.columns
        ]

    def save(self, *args, **kwargs):
        if self.cleaned_data['x_labels']:
            ascending = self.cleaned_data['x_labels'].startswith('asc:')
            by = ':'.join([i for i in self.cleaned_data['x_labels'].split(':')[1:]])
            self.instance.obj.sort_values(by=by, ascending=ascending, axis=0, inplace=True)
        if self.cleaned_data['y_labels']:
            ascending = self.cleaned_data['y_labels'].startswith('asc:')
            by = ':'.join([i for i in self.cleaned_data['y_labels'].split(':')[1:]])
            try:
                self.instance.obj.sort_values(by=by, ascending=ascending, axis=1, inplace=True)
            except KeyError:
                by = int(by)
                self.instance.obj.sort_values(by=by, ascending=ascending, axis=1, inplace=True)
        return super().save(*args, **kwargs)


class RenameLabelsForm(BaseDataFrameActionForm):
    x_label = forms.ChoiceField(
        required=False,
    )
    x_name = forms.CharField(
        required=False,
    )
    y_label = forms.ChoiceField(
        required=False,
    )
    y_name = forms.CharField(
        required=False,
    )

    class Meta(BaseDataFrameActionForm.Meta):
        fields = [
            'x_label',
            'x_name',
            'y_label',
            'y_name',
            'copy_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x_label'].choices = [EMPTY] + [
            (i, i) for i in self.instance.columns
        ]
        self.fields['y_label'].choices = [EMPTY] + [
            (i, i) for i in self.instance.rows
        ]

    def save(self, *args, **kwargs):
        if self.cleaned_data['x_label'] and self.cleaned_data['x_name']:
            mapper = {self.cleaned_data['x_label']: self.cleaned_data['x_name']}
            if self.cleaned_data['x_label'].isdigit():
                mapper[int(self.cleaned_data['x_label'])] = self.cleaned_data['x_name']
            self.instance.obj.rename(mapper=mapper, axis=1, inplace=True)
        if self.cleaned_data['y_label'] and self.cleaned_data['y_name']:
            mapper = {self.cleaned_data['y_label']: self.cleaned_data['y_name']}
            if self.cleaned_data['y_label'].isdigit():
                mapper[int(self.cleaned_data['y_label'])] = self.cleaned_data['y_name']
            self.instance.obj.rename(mapper=mapper, axis=0, inplace=True)
        return super().save(*args, **kwargs)


class DropNaForm(BaseDataFrameActionForm):
    axis = forms.MultipleChoiceField(
        choices=AXIS,
        initial=[0],
        required=True,
        help_text=_("Determine if rows or columns which contain missing values are removed."),
    )
    how = forms.ChoiceField(
        choices=HOW_DROP_NA,
        initial='any',
        required=True,
        help_text=_("Determine if row or column is removed when we have at least one NA or all NA."),
    )

    class Meta(BaseDataFrameActionForm.Meta):
        fields = [
            'axis',
            'how',
            'copy_name',
        ]

    def save(self, *args, **kwargs):
        axis = [int(i) for i in self.cleaned_data['axis']]
        self.instance.obj.dropna(
            axis=axis,
            how=self.cleaned_data['how'],
            inplace=True,
        )
        return super().save(*args, **kwargs)


class DropDuplicatesForm(BaseDataFrameActionForm):
    subset = forms.MultipleChoiceField(
        required=True,
        choices=(),
    )
    keep = forms.ChoiceField(
        required=True,
        choices=DROP_DUPLICATES_KEEP,
        initial='first',
    )

    class Meta(BaseDataFrameActionForm.Meta):
        fields = [
            'subset',
            'keep',
            'copy_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subset'].choices = [
            (i, i) for i in self.instance.columns
        ]
        self.fields['subset'].initial = self.instance.columns

    def save(self, *args, **kwargs):
        keep = self.cleaned_data['keep']
        if keep == 'False':
            keep = False
        self.instance.obj.drop_duplicates(
            subset=self.cleaned_data['subset'],
            keep=keep,
            inplace=True
        )
        return super().save(*args, **kwargs)


class GetDummiesForm(BaseDataFrameActionForm):
    columns = forms.MultipleChoiceField(
        required=True,
        choices=(),
        help_text=_("Columns to be encoded"),
    )

    class Meta(BaseDataFrameActionForm.Meta):
        fields = [
            'columns',
            'copy_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['columns'].choices = [
            (i, i) for i in self.instance.columns
        ]

    def save(self, *args, **kwargs):
        self.instance.obj = pd.get_dummies(
            data=self.instance.obj,
            columns=self.cleaned_data['columns'],
        )
        return super().save(*args, **kwargs)


class ClipForm(BaseDataFrameActionForm):
    columns = forms.MultipleChoiceField(
        required=True,
        choices=(),
        help_text=_("Columns to be clipped."),
    )
    lower = forms.FloatField(
        required=False,
        help_text=_("Minimum threshold value."),
        min_value=0,
    )
    upper = forms.FloatField(
        required=False,
        help_text=_("Maximum threshold value."),
        min_value=0,
    )

    class Meta(BaseDataFrameActionForm.Meta):
        fields = [
            'columns',
            'lower',
            'upper',
            'copy_name',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['columns'].choices = [
            (i, i) for i in self.instance.columns
        ]

    def save(self, *args, **kwargs):
        cols = self.cleaned_data['columns']
        self.instance.obj[cols] = self.instance.obj[cols].clip(
            lower=self.cleaned_data['lower'],
            upper=self.cleaned_data['upper'],
        )
        return super().save(*args, **kwargs)
