from requests import get
from bs4 import BeautifulSoup
from rdflib import Namespace, Graph, Literal, XSD, RDF
import re, json
import argparse
import os


def RepresentsInt(s):
    if s != None:
        try:
            int(s)
            return True
        except ValueError:
            return False


def makesoup(url):
    html = get(url).text
    soup = BeautifulSoup(html, 'html5lib')
    return(soup)


def getlinks(soup, regex):
    fill = soup.find_all('a', {'href': re.compile(regex)})
    for i in range(len(fill)):
        fill[i] = str(fill[i].get('href'))
    return fill


def getcodes(soup):
    scripts = []
    for script in soup.find_all('script'):
        if re.search('json', str(script)):
            scripts.append(script)

    codes = []
    for script in scripts:
        for line in str(script).splitlines():
            if re.search('categories:', line):
                codes.append(line)


    return codes


def makegraph(codes, vrb_lnk, description):

    base = 'http://data.socialhistory.org/resource/napp/'
    vrb_name = re.sub('.*/', '', vrb_lnk)
    vrb_url_full = base + vrb_name + '/'
    NAPP = Namespace(vrb_url_full)
    SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

    g = Graph()

    g.bind('napp', NAPP)
    g.bind('skos', SKOS)
    g.add((NAPP[vrb_name], RDF.type, SKOS['Scheme']))
    g.add((NAPP[vrb_name], SKOS['definition'], Literal(description)))

    indentlist = []
    codelist = []

    for code in codes:
        cd = code['code']
        lbl = code['label']

        if cd is None:
            cd = re.sub('\s|:', '_', lbl)
            cd = re.sub('/', '_or_', cd)
            cd = re.sub('[(),.''""]', '', cd)

        codelist.append(cd)
        indentlist.append(code['indent'])

        g.add((NAPP[cd], RDF.type, SKOS['Concept']))
        g.add((NAPP[cd], SKOS['prefLabel'], Literal(lbl)))
        g.add((NAPP[cd], SKOS['inScheme'], NAPP[vrb_name]))

        if RepresentsInt(lbl):
            g.add((NAPP[cd], RDF.value, Literal(lbl, datatype=XSD.int)))

        elif RepresentsInt(cd):
            g.add((NAPP[cd], RDF.value, Literal(cd, datatype=XSD.int)))


        if ((len(set(indentlist)) > 1) and (indentlist[i] > 0)):
            parentloc = indentlist[::-1].index(indentlist[i] - 1)
            parent = codelist[::-1][parentloc]

            g.add((NAPP[cd], SKOS['broader'], NAPP[parent]))
            g.add((NAPP[parent], SKOS['narrower'], NAPP[cd]))

    return g

baseurl = 'https://www.nappdata.org/'
soup = makesoup('https://www.nappdata.org/napp-action/variables/group')
groups = getlinks(soup=soup, regex='group\?id')

codelist = []
vrblist = []
desclist = []


parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='?', default="napp/", help='Path to store converted data')
args = parser.parse_args()


path = args.path
if not path.endswith('/'):
    path += '/'


if not os.path.exists(path):
        os.makedirs(path)


for group in groups:
    soup = makesoup(baseurl + group)
    vrbs = getlinks(soup, 'variables/[A-Z]')

    for vrb in vrbs:
        soup = makesoup(baseurl + vrb)
        print(baseurl + vrb)
        codes = getcodes(soup)

        if len(codes) > 0:
            ptrn = re.search('\[.*\]', codes[0])
            codes = json.loads(ptrn.group(0))

        codelist.append(codes)
        vrblist.append(vrb)
        description = soup.find(id='description_section').find('p').getText()
        desclist.append(description)

graphs = {}

for i, codes in enumerate(codelist):
    vrbname = re.sub('/.*/', '', vrblist[i])
    graphs[vrbname] = makegraph(codes, vrblist[i], desclist[i])


# save json as backup
with open('nappcodebook.json', 'w') as out:
    json.dump(codelist, out)

for vrb_name, graph in graphs.items():
    with open(path + vrb_name + '.ttl', 'w') as out:
        graph.serialize(out, format='turtle')
