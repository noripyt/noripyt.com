# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-22 10:06
from __future__ import unicode_literals

from django.db import migrations
from wagtail.wagtailcore.blocks import CharBlock, StreamBlock, RichTextBlock
from noripyt.blocks import CardBlock, ShowcaseBlock


HEIGHT_ATTRIBUTES = ('height_xs', 'height_sm', 'height_md', 'height_lg')
COL_ATTRIBUTES = ('width_xs', 'width_sm', 'width_md', 'width_lg',
                  'offset_xs', 'offset_sm', 'offset_md', 'offset_lg')


def migrate_streamfield(model):
    for obj in model.objects.all():
        for stream_child in obj.body:
            block = stream_child.block
            if block.name == 'row':
                height_data = {k: stream_child.value[k]
                               for k in HEIGHT_ATTRIBUTES}
                col_data = None
                row_content = []
                for col in stream_child.value['columns']:
                    for col_content in col['body']:
                        row_content.append(col_content)
                        if col_content.block.name == 'card':
                            col_content.block.child_blocks.update(
                                {k: CharBlock(required=False)
                                 for k in HEIGHT_ATTRIBUTES})
                            col_content.value.update(height_data)
                    if col_data is None:
                        col_data = {k: col[k] for k in COL_ATTRIBUTES}
                block.child_blocks.update({k: CharBlock()
                                           for k in COL_ATTRIBUTES})
                stream_child.value.update(col_data)
                block.child_blocks['body'] = StreamBlock([
                    ('card', CardBlock()),
                    ('showcase', ShowcaseBlock()),
                    ('text', RichTextBlock()),
                ], required=True)
                stream_child.value['body'] = row_content
        obj.save()


def migrate_streamfields(apps, schema_editor):
    Home = apps.get_model('noripyt', 'Home')
    Article = apps.get_model('noripyt', 'Article')
    for model in (Home, Article):
        migrate_streamfield(model)


class Migration(migrations.Migration):

    dependencies = [
        ('noripyt', '0003_auto_20160825_2005'),
    ]

    operations = [
        migrations.RunPython(migrate_streamfields),
    ]
