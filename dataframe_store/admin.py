from django.contrib import admin
from dataframe_store import models


@admin.register(models.DbDataFrame)
class DbDataFrameAdmin(admin.ModelAdmin):
    pass
