from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

#from processes.models import Equipo
from processes.resources import EquipoResource,MaterialResource
from .models import Equipo, Material


@admin.register(Equipo)
class EquipoAdmin(ImportExportModelAdmin):
    resource_class = EquipoResource

@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    resource_class = MaterialResource

# admin.site.register(Parametroseconomicos)
# admin.site.register(CostoEconomico)
#admin.site.register(Equipo)
# admin.site.register(DensidadMaterial)
# admin.site.register(Densidad)
# admin.site.register(Impureza)
# admin.site.register(MasaEntrada)
# admin.site.register(Material)
# admin.site.register(Proceso)
# admin.site.register(ProcesoSeparacion)
# admin.site.register(RendimientoProceso)
# admin.site.register(ProcesoCombinacion)
# admin.site.register(Grupo)
# admin.site.register(Tipo)
# admin.site.register(EquipoEntrada)
# admin.site.register(TipoImpureza)
# admin.site.register(ImpuezaMaterial)
# admin.site.register(ProcesoCalculado)