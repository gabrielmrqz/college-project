# nota adicionar a função de histórico em um módulo e acoplar a função de envio de email

from django.shortcuts import render,redirect,get_object_or_404
from main.models import Setores,Agendados,Historico,Templates
from django.contrib.auth import authenticate,login,logout
import threading
import datetime
import time
import matplotlib # Inclusão para evitar erro ao encerrar servidor e ao puxar imagem
matplotlib.use('Agg') # Inclusão para evitar erro ao encerrar servidor e ao puxar imagem
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.http import HttpResponse


def verificando_hora(data_hora,target,setores,nome_capanha,template):
    template_nome = str(template[0])
    template_body = Templates.objects.get(nome=template_nome).body
    

    print(template)
    if data_hora:
        data = data_hora.replace("T"," ")
        data_hora = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M")
        Agendados(nome=nome_capanha,emails=";".join(target),setor=";".join(setores),template=template_nome,data_hora=data_hora).save()
        print("Marcando o clock")
        while datetime.datetime.now() < data_hora: # 
            hoje = datetime.datetime.now()
            if hoje.day == data_hora.day and hoje.month == data_hora.month:
                ...
            time.sleep(1)
        print("Phishing enviado com sucesso")
        #enviar.enviar_email(lista_envio,template_body)
    else:
        print("Envio na hora")
        data_hora = datetime.datetime.now()
        #enviar.enviar_email(lista_envio,template_body)
    print("Data e hora alcançadas! Ação final executada.",datetime.datetime.now())
    Historico(nome=nome_capanha, emails=";".join(target), setor=";".join(setores), data_hora=data_hora, emails_enviados=0, falharam=0, passaram=0).save()



# Create your views here.
def index(request):
    return render(request,'main/index.html')

def phising(request):
    if "enviar" in request.POST:
        #capturando dados do post
        nome_capanha = request.POST.get('nome_campanha')
        emails = request.POST.get('emails')
        setores = request.POST.getlist("setores")
        data_hora = request.POST.get('data-hora')
        template = request.POST.getlist("templates")

        if emails or setores:
            print("Deu certo!")
            target = []
            for nome in setores:
                target +=Setores.objects.get(setor=nome).emails.split(';')
            if emails:
                target+=emails.split(";")  
             # corrigir feature sobre autentificação de email
            print(target)
            #envio do email
            threading.Thread(target=verificando_hora, args=(data_hora,target,setores,nome_capanha,template)).start()
        else:
            print("Sem emails para serem enviados!")


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


def agendamentos(request):
    agendamentos = Agendados.objects.all()
    return render(request,'main/agendados.html',{"agendados":agendamentos})

def agendado(request,item_id):
    item = get_object_or_404(Agendados,pk=item_id)
    return render(request,'main/agendado.html',{"item":item})




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
        print(template_content)
    return render(request,'main/template_create.html')





def cancelamento_agendamento(request,item_id):
    print(item_id)
    item = get_object_or_404(Agendados, pk=item_id)
    item.delete()

    return redirect("/agendamentos")

def logout_view(request):
    logout(request)
    return redirect('/login')

def graph_view(request):
    dados = Historico.objects.all()
    emails_enviados = Historico.objects.values_list('emails_enviados', flat=True)
    falharam = Historico.objects.values_list('falharam', flat=True)
    passaram = Historico.objects.values_list('passaram', flat=True)

    x = range(len(emails_enviados))
    width = 0.15

    plt.bar(x, emails_enviados, width=width, color='b', align='center')
    plt.bar([i+width for i in x], falharam, width=width, color='r', align='center')
    plt.bar([i+width*2 for i in x], passaram, width=width, color='g', align='center')

    labels = dados.values_list('nome', flat=True)
    plt.xticks([i + width for i in x], labels)
    plt.ylabel('Quantidade')
    plt.xlabel('Campanha')

    plt.legend(['Enviados', 'Falhados', 'Aprovados'], loc='upper left')

    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')
    plt.close()

    return response