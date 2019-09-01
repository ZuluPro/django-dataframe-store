import numpy as np

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

import swapper
from picklefield.fields import PickledObjectField
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from dataframe_store import settings


class LabelQuerySet(models.QuerySet):
    def bulk_get_or_create(self, ids):
        instances = []
        for id_ in ids:
            instance, _ = self.get_or_create(id=id_)
            instances.append(instance)
        return instances


class BaseLabel(models.Model):
    id = models.CharField(max_length=255, primary_key=True)

    objects = LabelQuerySet.as_manager()

    class Meta:
        abstract = True
        app_label = "dataframe_store"
        verbose_name = _("label")
        verbose_name_plural = _("labels")

    def __str__(self):
        return self.id


class Label(BaseLabel):
    class Meta(BaseLabel.Meta):
        abstract = False
        swappable = swapper.swappable_setting('dataframe_store', 'Label')


class BaseDbDataFrame(MPTTModel):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=3000, blank=True)
    obj = PickledObjectField()
    tags = TaggableManager(blank=True)

    shape_x = models.IntegerField()
    shape_y = models.IntegerField()

    labels = models.ManyToManyField(swapper.get_model_name('dataframe_store', 'Label'), blank=True)
    parent = TreeForeignKey(swapper.get_model_name('dataframe_store', 'DbDataFrame'), null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
        verbose_name = _("dataframe")
        verbose_name_plural = _("dataframes")
        index_together = [
            ['shape_x', 'shape_y'],
        ]

    def __str__(self):
        return self.name

    @property
    def columns(self):
        return list(self.obj.axes[1])

    @property
    def rows(self):
        return list(self.obj.axes[0])

    @property
    def numeric_columns(self):
        cols = self.obj.select_dtypes(include=[np.number]).columns.values
        return list(cols)


class DbDataFrame(BaseDbDataFrame):
    class Meta(BaseDbDataFrame.Meta):
        swappable = swapper.swappable_setting('dataframe_store', 'DbDataFrame')
        abstract = False


# TODO: Swappable model
@receiver(pre_save)
def pre_set_dataframe_meta(sender, instance, *args, **kwargs):
    if not isinstance(instance, swapper.load_model('dataframe_store', 'DbDataFrame')):
        return
    instance.shape_x = instance.obj.shape[1]
    instance.shape_y = instance.obj.shape[0]


@receiver(post_save)
def post_set_dataframe_meta(sender, instance, *args, **kwargs):
    if not isinstance(instance, DbDataFrame):
        return
    labels = Label.objects.bulk_get_or_create(instance.obj.axes[1])
    instance.labels.add(*labels)
