# Generated by Django 3.2.12 on 2022-04-26 15:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user', '0002_rename_avatar_image_avatarimage'),
        ('picture', '0002_auto_20220420_2039'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Picture_comment',
            new_name='PictureComment',
        ),
        migrations.RenameModel(
            old_name='Picture_History',
            new_name='PictureHistory',
        ),
        migrations.RenameModel(
            old_name='Repair_step',
            new_name='RepairStep',
        ),
        migrations.AddField(
            model_name='picture',
            name='modify_lock',
            field=models.IntegerField(default=0, verbose_name='信息修改是否在进行'),
        ),
        migrations.AddField(
            model_name='picture',
            name='repair_lock',
            field=models.IntegerField(default=0, verbose_name='修复是否在进行中'),
        ),
        migrations.AlterField(
            model_name='picture',
            name='title',
            field=models.CharField(default='no title', max_length=50, verbose_name='图片标题'),
        ),
    ]
