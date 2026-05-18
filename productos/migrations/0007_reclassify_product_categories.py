"""Reclassify products from generic 'otros' to correct categories.

Based on inventory review: all 27 active products were stored as
categoria='otros'. This migration assigns each product to its proper
category per the veterinary clinic's product classification.
"""

from django.db import migrations


def reclassify_products(apps, schema_editor):
    """Assign correct categories to all products."""
    Producto = apps.get_model('productos', 'Producto')

    # Map: product PK -> correct category
    # Based on detailed inventory review by the clinic team
    category_map = {
        # ── Alimentos (4) ──
        2: 'alimentos',    # Concentrado premium para perros
        7: 'alimentos',    # Snacks dentales para perros
        14: 'alimentos',   # Comida húmeda para cachorros
        28: 'alimentos',   # Concentrado para gatos esterilizados

        # ── Medicamentos (2) ──
        18: 'medicamentos',  # Gotas para los oídos
        22: 'medicamentos',  # Spray repelente de insectos

        # ── Insumos médicos (3) ──
        1: 'insumos',    # Jeringa Desechable de 35 ml con Aguja
        23: 'insumos',   # Termómetro digital uso rectal
        31: 'insumos',   # Kit de primeros auxilios para mascotas

        # ── Higiene y cuidado (9) ──
        5: 'higiene',    # Shampoo antipulgas para perros
        8: 'higiene',    # Cepillo para pelo de gato
        13: 'higiene',   # Guantes de látex desechables
        16: 'higiene',   # Champú hipoalergénico
        20: 'higiene',   # Bolsas sanitarias para perros
        21: 'higiene',   # Venda elástica autoadherente
        24: 'higiene',   # Cortaúñas para mascotas
        27: 'higiene',   # Limpiador de lágrimas para perros
        29: 'higiene',   # Cepillo de dientes de dedo

        # ── Otros / Accesorios (9) ──
        3: 'otros',   # Juguete interactivo para gatos
        6: 'otros',   # Collar isabelino talla M
        9: 'otros',   # Cama ortopédica para perros grandes
        10: 'otros',  # Transportadora para gatos
        15: 'otros',  # Arenero autolimpiable
        17: 'otros',  # Juguete dispensador de comida
        19: 'otros',  # Plato doble de acero inoxidable
        25: 'otros',  # Jaula plegable para perros
        30: 'otros',  # Correa retráctil para perros
    }

    for pk, categoria in category_map.items():
        Producto.objects.filter(pk=pk).update(categoria=categoria)


def reverse_reclassify(apps, schema_editor):
    """Revert all products to 'otros' (original state)."""
    Producto = apps.get_model('productos', 'Producto')
    for pk in range(1, 32):
        Producto.objects.filter(pk=pk).update(categoria='otros')


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0006_alter_producto_options_alter_producto_managers'),
    ]

    operations = [
        migrations.RunPython(reclassify_products, reverse_reclassify),
    ]