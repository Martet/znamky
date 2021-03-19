from django.shortcuts import render
from django import forms
from bs4 import BeautifulSoup
import requests
import hashlib
import base64
import datetime


class LoginForm(forms.Form):
    jmeno = forms.CharField(label="Jméno", max_length=100)
    heslo = forms.CharField(label="Heslo", max_length=100)
    skola = forms.CharField(label="Škola", max_length=100)


# Create your views here.
def index(request):
    username = request.session['jmeno']
    password = request.session['heslo']
    skola = request.session['skola']
    with requests.Session() as s:
        poststring = skola + '?gethx=' + username
        p = s.get(poststring)
        bs = BeautifulSoup(p.text, features="html.parser")
        toHash = bs.salt.text + bs.ikod.text + bs.typ.text + password
        passHash = base64.b64encode(hashlib.sha512(toHash.encode('utf-8')).digest()).decode('utf-8')
        toHash = "*login*" + username + "*pwd*" + passHash + "*sgn*ANDR" + datetime.date.today().strftime("%Y%m%d")
        hash = base64.b64encode(hashlib.sha512(toHash.encode('utf-8')).digest()).decode('utf-8').replace('/', '_')\
            .replace('\\', '_').replace('+', '-')
        poststring = skola + '?hx=' + hash + '&pm=znamky'
        p = s.get(poststring)
        bak = p.text
        poststring = skola + '?hx=' + hash + '&pm=login'
        p = s.get(poststring)
        info = p.text
    soup = BeautifulSoup(info, features="html.parser")
    jmeno = soup.jmeno.text
    skola = soup.skola.text
    soup = BeautifulSoup(bak, features="html.parser")
    predmety = []
    znamky = {}
    for predmet in soup.find_all("predmet"):
        predmety.append(predmet.nazev.text)
        znamky_radek = []
        for znamka in predmet.znamky.find_all("znamka", recursive=False):
            mark = znamka.znamka.text
            vaha = znamka.vaha.text
            if vaha == "0" or vaha == "A":
                vaha = "10"
            datum_raw = znamka.datum.text
            datum = datum_raw[-2:] + ". "
            datum += datum_raw[2:-2] + ". "
            datum += "20" + datum_raw[:2]
            nazev = znamka.caption.text
            znamky_radek.append({"znamka": mark, "vaha": vaha, "datum": datum, "nazev": nazev})
        znamky[predmet.nazev.text] = znamky_radek
    return render(request, 'page/index.html', {'predmety': predmety, 'znamky': znamky, 'username': username,
                                               'jmeno': jmeno, 'skola': skola})


def load(request):
    jmeno = request.session.get('jmeno', '')
    heslo = request.session.get('heslo', '')
    skola = request.session.get('skola', '')
    if jmeno == '' or heslo == '' or skola == '':
        form = LoginForm()
        form.jmeno = jmeno
        form.heslo = heslo
        form.skola = skola
        return render(request, 'page/login.html', {'form': form})
    return render(request, 'page/loading.html', {'pololeti': ''})


def get_login(request):
    if request.method == 'GET':
        if request.GET.get('a') == 'logoff':
            request.session['jmeno'] = ''
            request.session['heslo'] = ''
            return render(request, 'page/login.html', {'form': LoginForm(initial={'jmeno': '', 'heslo': '',
                                                                                  'skola': request.session.get('skola',
                                                                                                               '')})})
        else:
            jmeno = request.session.get('jmeno', '')
            heslo = request.session.get('heslo', '')
            skola = request.session.get('skola', '')
            if jmeno == '' or heslo == '' or skola == '':
                uzivatel = False
            else:
                uzivatel = True
            form = LoginForm(initial={'jmeno': '', 'heslo': '', 'skola': skola})
            return render(request, 'page/login.html', {'form': form, 'uzivatel': uzivatel, 'jmeno': jmeno})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['jmeno'] = form.cleaned_data['jmeno']
            request.session['heslo'] = form.cleaned_data['heslo']
            request.session['skola'] = form.cleaned_data['skola']
            return render(request, 'page/loading.html')
        else:
            return render(request, 'page/login.html', {'form': form})
