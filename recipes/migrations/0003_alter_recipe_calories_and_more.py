# Generated by Django 5.2 on 2025-04-27 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_predefinedcatalogtype_recipeaccess_predefinedcatalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='calories',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='carbohydrate_content',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cholesterol_content',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='fat_content',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='fiber_content',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='instructions',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='protein_content',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='saturated_fat_content',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='sodium_content',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='sugar_content',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
