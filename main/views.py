# nota adicionar a função de histórico em um módulo e acoplar a função de envio de email

from django.shortcuts import render,redirect,get_object_or_404
from main.models import Setores,Agendados,Historico,Templates,HistoricoIndiv,RastreioPixel,RastreioLink
from django.contrib.auth import authenticate,login,logout
import threading
import datetime
from datetime import timedelta
import uuid
import time
import base64
import matplotlib # Inclusão para evitar erro ao encerrar servidor e ao puxar imagem
matplotlib.use('Agg') # Inclusão para evitar erro ao encerrar servidor e ao puxar imagem
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.urls import reverse
from random import choice
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Q
from random import sample

def verificando_hora(data_hora,target,setores,nome_capanha,template):
    template_nome = str(template[0])
    template_body = Templates.objects.get(nome=template_nome).body
    if data_hora:
        data = data_hora.replace("T"," ")
        data_hora = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M")
        Agendados(nome=nome_capanha,emails=";".join(target),setor=";".join(setores),template=template_nome,data_hora=data_hora).save()
        while datetime.datetime.now() < data_hora: # 
            hoje = datetime.datetime.now()
            if hoje.day == data_hora.day and hoje.month == data_hora.month:
                ...
            time.sleep(1)
        Historico(nome=nome_capanha, emails=";".join(target), setor=";".join(setores), data_hora=data_hora, emails_enviados=0, falharam=0, passaram=0).save()
        enviar_email(target,template_body,nome_capanha)
    else:
        data_hora = datetime.datetime.now()
        Historico(nome=nome_capanha, emails=";".join(target), setor=";".join(setores), data_hora=data_hora, emails_enviados=0, falharam=0, passaram=0).save()
        enviar_email(target,template_body,nome_capanha)


@login_required
# Create your views here.
def index(request):
    hoje = timezone.now()
    ontem = hoje - timedelta(days=1)
    mespassado = hoje - timedelta(days=30)
    sum_emails = Historico.objects.filter(data_hora__gte=ontem).aggregate(Sum('emails_enviados'))
    penviados = sum_emails['emails_enviados__sum'] or 0
    sum_passaram = Historico.objects.filter(data_hora__gte=mespassado).aggregate(Sum('passaram'))
    frejeitaram = sum_passaram['passaram__sum'] or 0
    setor = Setores.objects.all()
    email_count = 0
    emails_total = []
    for item in setor:
        i = item.emails
        if ";" in i:
            emails_total += i.strip(";").split(";")
        else:
            emails_total.append(i)
    email_count = len(set(emails_total))
    return render(request,'main/index.html',{"phishingsenviados":penviados,"funcionariosrejeitaram":frejeitaram,"emails_total":email_count})

def phising(request):
    if "enviar" in request.POST:
        #capturando dados do post
        nome_capanha = request.POST.get('nome_campanha')
        emails = request.POST.get('emails')
        setores = request.POST.getlist("setores")
        data_hora = request.POST.get('data-hora')
        template = request.POST.getlist("templates")
    
        if emails or setores:
            target = []
            for nome in setores:
                target +=Setores.objects.get(setor=nome).emails.split(';')
            if emails:
                target+=emails.split(";")  
             # corrigir feature sobre autentificação de email
            #envio do email
            threading.Thread(target=verificando_hora, args=(data_hora,target,setores,nome_capanha,template)).start()


    templates = Templates.objects.all()
    setores = Setores.objects.all()
    return render(request,'main/envio_phising.html',{"setores":setores,"Templates":templates})





def login_page(request):
    if 'enviar' in request.POST:
        user = request.POST.get('username') # obter o valor do campo "emails"
        passwd = request.POST.get('password') # obter o valor do campo "data-hora"
        user = authenticate(request, username=user, password=passwd)
        if user is not None:
            login(request,user)
            # Usuário autenticado, redireciona para a página principal
            return redirect("/")
    return render(request,'main/login.html')

@login_required

def agendamentos(request):
    agendamentos = Agendados.objects.all()
    return render(request,'main/agendados.html',{"agendados":agendamentos})
@login_required

def agendado(request,item_id):
    item = get_object_or_404(Agendados,pk=item_id)
    return render(request,'main/agendado.html',{"item":item})

def pixelview(request):
    return render(request, 'main/pixel.html')


def template_create(request):
    if "enviar" in request.POST:
        name = request.POST.get("nome")
        template_codigo = request.POST.get("codigo")
        if request.FILES.get("arquivo"):
            template_arquivo  = request.FILES["arquivo"]
            file_contents = template_arquivo.read().decode()
            template_content = file_contents
        else:
            template_content = template_codigo

        Templates(nome=name,body=template_content).save()
    return render(request,'main/template_create.html')





def cancelamento_agendamento(request,item_id):
    item = get_object_or_404(Agendados, pk=item_id)
    item.delete()

    return redirect("/agendamentos")

def logout_view(request):
    logout(request)
    return redirect('/login')

def graph_view(request):
    dados = Historico.objects.all().order_by('id').reverse()[:5]
    emails_enviados = dados.values_list('emails_enviados', flat=True)
    falharam = dados.values_list('falharam', flat=True)
    passaram = dados.values_list('passaram', flat=True)

    x = range(len(emails_enviados))
    width = 0.15

    fig, ax = plt.subplots()

    ax.bar(x, emails_enviados, width=width, color='b', align='center')
    ax.bar([i + width for i in x], falharam, width=width, color='r', align='center')
    ax.bar([i + width * 2 for i in x], passaram, width=width, color='g', align='center')

    labels = dados.values_list('nome', flat=True)
    ticks = [i + width for i in x]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Quantidade')
    ax.set_xlabel('Campanha')

    ax.legend(['Enviados', 'Falhados', 'Aprovados'], loc='upper left')

    # Set x-axis limits to remove extra space
    ax.set_xlim(ticks[0] - width * 1.5, ticks[-1] + width * 2)

    plt.tight_layout()

    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')
    plt.close()

    return response

import smtplib
from email.message import EmailMessage
from uuid import UUID

def make_tpixel(unique_id: UUID) -> str:
    return reverse('track_pixel', args=[unique_id])

def make_tlink(unique_id: UUID) -> str:
    return reverse('track_link', args=[unique_id])

def enviar_email(target, template_body, nome_capanha):
# configurando o servidor smtp
    smtp_server = "mailserver.no-replyme.com"
    smtp_port = 587
    smtp_username = 'email@no-replyme.com'
    smtp_password = 'p@ssw0rd3x4mpl3'

    # criando o objeto
    msg = EmailMessage()
    msg['Subject'] = 'Assunto do e-mail'
    msg['From'] = 'email@no-replyme.com'

    # envio de e-mail
    with smtplib.SMTP(smtp_server,smtp_port) as server:
        server.starttls()
        server.login(smtp_username,smtp_password)
        func = 1
        for alvo in target:
            idunico = uuid.uuid4()
            pixelurl = make_tpixel(idunico)
            linkurl = make_tlink(idunico)
            linkurl = "http://securitest.com.br" + linkurl
            template_body_with_pixel = template_body + f'<img src="http://securitest.com.br{pixelurl}" width="1" height="1" alt="">'
            if "LINK_URL" in template_body_with_pixel:
                tpcomlink = template_body_with_pixel.replace("LINK_URL",linkurl)
            else:
                tpcomlink = template_body_with_pixel
            if not HistoricoIndiv.objects.filter(email=alvo).exists():
                linhacerta = int(0)
                linhas = Setores.objects.all()
                for linha in linhas:
                    emails = linha.emails.split(';')
                    if alvo in emails:
                        linhacerta = linha
                setoru = linhacerta.setor
                HistoricoIndiv(nome=f'Funcionario {func}',email=alvo,setor=setoru).save()
                func += 1
            RastreioPixel(id_pixel=idunico, nome_campanha=nome_capanha, email=alvo).save()
            RastreioLink(id_link=idunico, nome_campanha=nome_capanha, email=alvo).save()
            msg.set_content(tpcomlink, subtype='html')
            server.sendmail(msg['from'], alvo, msg.as_string())
            historicoindiv = HistoricoIndiv.objects.get(email=alvo)
            historicoindiv.enviados += 1
            historicoindiv.save()
            threading.Thread(target=check_pass, args=([idunico])).start()
        
        historico = Historico.objects.get(nome=nome_capanha)
        historico.emails_enviados = len(target)
        historico.save()

@cache_page(60 * 60 * 24 * 7)  # Cache de 1 semana
# Criação de um pixel branco para "rastreio" caso o usuário abra o e-mail
def track_pixel(request, unique_id: UUID):
    pixel_event = RastreioPixel.objects.get(id_pixel=unique_id)
    linha_pixel = RastreioPixel.objects.filter(id_pixel=unique_id).first()
    pixel_event.aberto = True
    pixel_event.timestamp = datetime.datetime.now()
    pixel_event.save()
    email = linha_pixel.email
    linha_historicoindiv = HistoricoIndiv.objects.filter(email=email).first()
    linha_historicoindiv.abriu += 1
    linha_historicoindiv.save()
    campanha = linha_pixel.nome_campanha
    linha_historico = Historico.objects.filter(nome=campanha).first()
    linha_historico.abriram += 1
    linha_historico.save()
    pixel_gif_data = b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    return HttpResponse(base64.b64decode(pixel_gif_data), content_type="image/gif")

@cache_page(60 * 60 * 24 * 7)  # Cache de 1 semana
# Criação de rastreio no link a ser clicado no e-mail
def track_link(request, unique_id: UUID):
    link_event = RastreioLink.objects.get(id_link=unique_id)
    linha_link = RastreioLink.objects.filter(id_link=unique_id).first()
    link_event.aberto = True
    link_event.timestamp = datetime.datetime.now()
    link_event.save()
    email = linha_link.email
    linha_historicoindiv = HistoricoIndiv.objects.filter(email=email).first()
    linha_historicoindiv.falhou += 1
    linha_historicoindiv.save()
    campanha = linha_link.nome_campanha
    linha_historico = Historico.objects.filter(nome=campanha).first()
    linha_historico.falharam += 1
    linha_historico.save()
    destino = choice(['https://form.jotform.com/230834110022033','https://form.jotform.com/231114702333643','https://form.jotform.com/231117180647654','https://www.jotform.com/build/231218379017657'])
    return redirect(destino)

# Verificação se o usuário clicou no link ou abriu o e-mail
def check_pass(unique_id: UUID):
    data_hora = datetime.datetime.now() + datetime.timedelta(minutes=2160)
    idunico = unique_id
    while datetime.datetime.now() < data_hora:
        link_event = RastreioLink.objects.get(id_link=idunico)
        pixel_event = RastreioPixel.objects.get(id_pixel=idunico)
        linha_pixel = RastreioPixel.objects.filter(id_pixel=idunico).first()
        email = linha_pixel.email
        linha_historicoindiv = HistoricoIndiv.objects.filter(email=email).first()
        time.sleep(3600)
        if link_event.aberto:
            break
        if pixel_event.aberto:
            break
    if datetime.datetime.now() >= data_hora:
        if not link_event.aberto:
            if not pixel_event.aberto:
                linha_historicoindiv.passou += 1
                linha_historicoindiv.save()
                campanha = linha_pixel.nome_campanha
                linha_historico = Historico.objects.filter(nome=campanha).first()
                linha_historico.passaram += 1
                linha_historico.save()


def login_page(request):
    if 'enviar' in request.POST:
        user = request.POST.get('username') # obter o valor do campo "emails"
        passwd = request.POST.get('password') # obter o valor do campo "data-hora"
        user = authenticate(request, username=user, password=passwd)
        if user is not None:
            login(request,user)
            # Usuário autenticado, redireciona para a página principal
            return redirect("/")
    return render(request,'main/login.html')

def logout_view(request):
    logout(request)
    return redirect('/login')

def relatorio(request):
    return render(request,'main/relatorio.html')

def relatoriocsv(request):
    campanhas = Historico.objects.all()
    return render(request,'main/relatoriocsv.html',{"campanhas":campanhas})

import csv
from django.http import HttpResponse
from .models import Historico

def export_csv_campanha(request, nome_campanha):
    # recupera os dados da campanha
    campanha = Historico.objects.filter(nome=nome_campanha).first()

    # define o nome do arquivo CSV
    nome_arquivo = f"{nome_campanha}.csv"

    # abre o arquivo CSV para escrita
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    writer = csv.writer(response)

    # escreve os cabeçalhos das colunas
    writer.writerow(["Nome da Campanha", "Data", "Setores", "Usuarios que abriram e-mail", "Usuarios que falharam (clicaram)", "Usuarios que passaram"])

    # escreve os dados da campanha
    writer.writerow([campanha.nome, campanha.data_hora, campanha.setor, campanha.abriram, campanha.falharam, campanha.passaram])

    return response

def template_create(request):
    if request.method == 'POST':
        name = request.POST.get("setorName")
        template_arquivo  = request.FILES["csvFile"]
        file_contents = template_arquivo.read().decode()
        Templates(nome=name,body=file_contents).save()
    return render(request,'main/template_create.html')

def gerenciador_setor(request):
    setores_itens = Setores.objects.all()
    return render(request,"main/gerenciador_setor.html",{"setor":setores_itens})

def setorunico(request,setor_id):
    emails = Setores.objects.get(id=setor_id).emails.split(';')
    setor = Setores.objects.get(id=setor_id)
    if  "enviar" in request.POST:
        email_add = request.POST.get('email_add')
        if email_add:
            setor.emails += ';' + email_add
            setor.save()
            return render(request,"main/setor.html",{"emails":emails,"setorid":setor_id})
        # emails_add  = request.FILES["file"]
        # emails_add = emails_add.read().decode()
        # emails_add = emails_add.strip(";")
    elif "excluir" in request.POST:
        setor.delete()
        return redirect("gerenciador_setor")
    return render(request,"main/setor.html",{"emails":emails,"setorid":setor_id})
    
def remover_item(request,setor_id, item_id):
    setor = get_object_or_404(Setores, pk=setor_id)
    setor.emails =setor.emails.replace(";"+item_id,"")
    setor.emails =setor.emails.replace(item_id,"")
    setor.save()
    return redirect('setorunico', setor_id=setor_id)

def addsetor(request):
    if request.method == 'POST':
        setor_name = request.POST['setorName']
        csv_file = request.FILES['csvFile']
        Setores(setor=setor_name,emails = csv_file.read().decode()).save()
    return render(request,'main/addsetor.html')