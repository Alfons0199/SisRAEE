from django.conf.urls import url
#from . import views
from processes.views import newProcess_view, loadEquipoEntrada, getProcesoCalculadoLista_view, getResultadosListView, \
    MaterialCreateView, MaterialListView, MaterialUpdateView, ProcesoCreateView, loadEquipoEntradaFinal, \
    tablaMaterialPrecio

urlpatterns = [
    url(r'^new_Process/$', newProcess_view, name='new_Process'),
    url('ajax/load_EquipoEntrada/', loadEquipoEntrada, name='ajax_load_EquipoEntrada'),
    url('ajax/load_EquipoFinal/', loadEquipoEntradaFinal, name='ajax_load_EquipoFinal'),
    url('ajax/load_TablaPrecio/', tablaMaterialPrecio, name='ajax_load_TablaPrecio'),

    #url('', ProcesoCalculadoListView.as_view(), name='procesoCalculado-list'),
    url(r'^Process_Calculate/$', getProcesoCalculadoLista_view, name='procesoCalculado-list'),
    url(r'^$', getResultadosListView, name='diagramassankey'),
    url('addMaterial/', MaterialCreateView.as_view(), name='material_add'),
    url('listMaterial/', MaterialListView.as_view(), name='material_list'),
    url('<int:pk>/', MaterialUpdateView.as_view(), name='material_update'),
    url('addProceso/', ProcesoCreateView.as_view(), name='proceso_add'),
]