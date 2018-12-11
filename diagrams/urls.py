from django.conf.urls import url
#from . import views
from diagrams.views import generateSankey,resultProcess

app_name = 'diagrams'
urlpatterns = [
    #url(r'^$', views.home),
    url(r'^$', resultProcess, name='diagramassankey'),
    url(r'^SankeyDiagrams', generateSankey,name='generateSankey'),
]