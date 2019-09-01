# Generated by Django 2.0 on 2019-04-17 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import picklefield.fields
import taggit.managers
import swapper


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='DbDataFrame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, max_length=3000)),
                ('obj', picklefield.fields.PickledObjectField(editable=False)),
                ('shape_x', models.IntegerField()),
                ('shape_y', models.IntegerField()),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'verbose_name_plural': 'dataframes',
                'verbose_name': 'dataframe',
                'abstract': False,
                'swappable': swapper.swappable_setting('dataframe_store', 'DbDataFrame')
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'labels',
                'verbose_name': 'label',
                'abstract': False,
                'swappable': swapper.swappable_setting('dataframe_store', 'Label')
            },
        ),
        migrations.AddField(
            model_name='dbdataframe',
            name='labels',
            field=models.ManyToManyField(blank=True, to=swapper.get_model_name('dataframe_store', 'Label')),
        ),
        migrations.AddField(
            model_name='dbdataframe',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterIndexTogether(
            name='dbdataframe',
            index_together={('shape_x', 'shape_y')},
        ),
    ]
