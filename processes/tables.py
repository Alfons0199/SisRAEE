from django_tables2 import tables

from processes.models import MaterialPrecio


class MaterialPrecioTable(tables.Table):

    class Meta:
        model = MaterialPrecio
        fields=['anio','idmaterial','precioreventa']
        template_name = 'django_tables2/bootstrap.html'

