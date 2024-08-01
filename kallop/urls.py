"""
URL configuration for kallop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from main.views import template_create,index,phising,agendamentos,agendado,cancelamento_agendamento, relatoriocsv, addsetor
from main.views import graph_view,track_pixel,track_link,login_page,logout_view, relatorio, export_csv_campanha, gerenciador_setor,setorunico,remover_item

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index,name='index'),
    path('phising/',phising,name='phising'),
    path('agendamentos/',agendamentos,name='agendamentos'),
    path('agendado/<int:item_id>',agendado,name='agendado'),
    path('cancelamento_agendamento/<int:item_id>',cancelamento_agendamento,name='cancelamento_agendamento'),
    path("template_create",template_create,name ="template_create"),
    path('graph/', graph_view, name='graph'),
    path('track_pixel/<uuid:unique_id>', track_pixel, name='track_pixel'),
    path('track_link/<uuid:unique_id>', track_link, name='track_link'),
    path('login/',login_page,name="login"),
    path("logout/",logout_view,name="logout_view"),
    path("relatorio/", relatorio, name='relatorio'),
    path("relatoriocsv/<str:nome_campanha>", export_csv_campanha, name="relatoriocsv1"),
    path("relatoriocsv/", relatoriocsv, name="relatoriocsv"),
    path("gerenciador-setores",gerenciador_setor,name="gerenciador_setor"),
    path("setor/<int:setor_id>",setorunico,name="setorunico"),
    path('setor/<int:setor_id>/remover-item/<str:item_id>/', remover_item, name='remover_item'),
    path('addsetor', addsetor, name='addsetor')
]