from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from .models import Equipo, Material


class EquipoResource(resources.ModelResource):
    #materiales = fields.Field(widget=ManyToManyWidget(Material))
    materiales = fields.Field(widget=ManyToManyWidget(Material,field='idmaterial'))
    class Meta:
        model = Equipo
        skip_unchanged = False
        report_skipped = True
        exclude = ('id',)
        import_id_fields = ('nombre',)


class MaterialResource(resources.ModelResource):
    class Meta:
        model = Material
        skip_unchanged = True
        report_skipped = True
        exclude = ('id',)
        import_id_fields = ('idmaterial', 'nombre')
