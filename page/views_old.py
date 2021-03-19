from django.shortcuts import render
from django import forms
from bs4 import BeautifulSoup
import json
import requests


class LoginForm(forms.Form):
    jmeno = forms.CharField(label="jmeno", max_length=100)
    heslo = forms.CharField(label="heslo", max_length=100)


payload = {

    '__LASTFOCUS': '',
    '__EVENTTARGET': 'loginButton',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': '/wEPDwUKMTg2MTExMjY5MWQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgIFCnBvcHVwaW50cm8FDXBvcHVwUXVlc3Rpb27oo3Y4JNJZS84F+IKubPEeB867mdpXqNSohPKnFEd/1g==',
    '__VIEWSTATEGENERATOR': 'BA8EC58D',
    '__EVENTVALIDATION': '/wEdAAY+KVVdE36UC/QCBK6UnnEzKhoCyVdJtLIis5AgYZ/RYe4sciJO3Hoc68xTFtZGQEjOzLf+PULXAx0siEaqrIWO3UZn4M6n3GSDUe8CZ9gwLqLv0gmrAtlduolG6OPHbK/kocjnNGi5zHlpcilLzjEiHmnibXBnLo5ZZvmoIrp4rQ==',
    'username': 'zak010116dywi',
    'password': '531pn36b',

}


# Create your views here.
def index(request):
    payload['username'] = request.session['jmeno']
    payload['password'] = request.session['heslo']
    with requests.Session() as s:
        poststring = 'https://bakalari.gymfrydl.cz/bakaweb/next/login.aspx?ReturnUrl=%2fbakaweb%2fnext%2fprubzna.aspx'
        if request.method == 'GET' and request.GET.get('pololeti'):
            pololeti = request.GET['pololeti']
            if pololeti == '1':
                poststring = 'https://bakalari.gymfrydl.cz/bakaweb/next/login.aspx?ReturnUrl=%2fbakaweb%2fnext%2fprubzna.aspx%3fdfrom%3d1909010000%26dto%3d2001310000%26subt%3d1pololeti'
            elif pololeti == '2':
                poststring = 'https://bakalari.gymfrydl.cz/bakaweb/next/login.aspx?ReturnUrl=%2fbakaweb%2fnext%2fprubzna.aspx%3fdfrom%3d2002010000%26dto%3d2006300000%26subt%3d2pololeti'
        p = s.post(poststring, data=payload)
        bak = p.text
    # with open("page/bak.html", encoding="utf-8") as bak:
        soup = BeautifulSoup(bak, features="html.parser")
    jmeno = soup.find(id='lusername').string
    predmety = []
    znamky = {}
    for radek in soup.find_all(class_="predmet-radek"):
        detail = radek.find_all(class_="_subject_detail")
        predmety.append(detail[0].h3.string)
        znamky_radek = []
        for znamka in radek.find_all(class_="znamka-v"):
            d = json.loads(znamka["data-clasif"])
            znamka = d["MarkText"]
            vaha = d["oznaceni"][-1:]
            if vaha == "0" or vaha == "A":
                vaha = "10"
            datum = d["strdatum"]
            nazev = d["caption"]
            znamky_radek.append({"znamka": znamka, "vaha": vaha, "datum": datum, "nazev": nazev})
        znamky[detail[0].h3.string] = znamky_radek
    pololeti = soup.find(id="cphmain_obdobiLabel").get_text()
    return render(request, 'page/index.html', {'predmety': predmety, 'znamky': znamky, 'username': payload['username'],
                                               'jmeno': jmeno, 'pololeti': pololeti})


def load(request):
    jmeno = request.session.get('jmeno', '')
    heslo = request.session.get('heslo', '')
    if jmeno == '' or heslo == '':
        form = LoginForm()
        form.jmeno = jmeno
        form.heslo = heslo
        return render(request, 'page/login.html', {'form': form})
    if request.method == 'GET' and request.GET.get('pololeti'):
        pololeti = request.GET['pololeti']
        return render(request, 'page/loading.html', {'pololeti': pololeti})
    return render(request, 'page/loading.html', {'pololeti': ''})


def get_login(request):
    if request.method == 'GET':
        if request.GET.get('a') == 'logoff':
            request.session['jmeno'] = ''
            request.session['heslo'] = ''
            return render(request, 'page/login.html', {'form': LoginForm(initial={'jmeno': '', 'heslo': ''})})
        else:
            jmeno = request.session.get('jmeno', '')
            heslo = request.session.get('heslo', '')
            if jmeno == '' or heslo == '':
                uzivatel = False
            else:
                uzivatel = True
            form = LoginForm(initial={'jmeno': '', 'heslo': ''})
            return render(request, 'page/login.html', {'form': form, 'uzivatel': uzivatel, 'jmeno': jmeno})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['jmeno'] = form.cleaned_data['jmeno']
            request.session['heslo'] = form.cleaned_data['heslo']
            return render(request, 'page/loading.html')
        else:
            return render(request, 'page/login.html', {'form': form})
