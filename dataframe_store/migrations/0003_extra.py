# Generated by Django 2.0 on 2019-04-17 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import swapper


class Migration(migrations.Migration):
    dependencies = [
        ('dataframe_store', '0002_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbdataframe',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=swapper.get_model_name('dataframe_store', 'DbDataFrame')),
        ),
        migrations.AddField(
            model_name='dbdataframe',
            name='labels',
            field=models.ManyToManyField(blank=True, to=swapper.get_model_name('dataframe_store', 'Label')),
        ),
        migrations.AlterIndexTogether(
            name='dbdataframe',
            index_together={('shape_x', 'shape_y')},
        ),
    ]