from requests import get
from bs4 import BeautifulSoup
import rdflib as rdf
import re, os, json


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

    base = 'http://data.socialhistory.org/vocab/napp/'
    vrb_name = re.sub('.*/', '', vrb_lnk)
    vrb_url_full = base + vrb_name + '/'
    NAPP = rdf.Namespace(vrb_url_full)
    SKOS = rdf.Namespace('http://www.w3.org/2004/02/skos/core#')

    g = rdf.Graph()

    g.bind('napp', NAPP)
    g.bind('skos', SKOS)
    g.add((NAPP[vrb_name], rdf.RDF.type, SKOS['Scheme']))
    g.add((NAPP[vrb_name], SKOS['definition'], rdf.Literal(description)))

    indentlist = []
    codelist = []

    for i in range(len(codes)):
        code = codes[i]
        cd = code['code']
        lbl = code['label']
        if cd is None:
            cd = re.sub('\s|:', '_', lbl)
            cd = re.sub('/', '_or_', cd)
            cd = re.sub('[(),.''""]', '', cd)
        codelist.append(cd)
        indentlist.append(code['indent'])

        g.add((NAPP[cd], rdf.RDF.type, SKOS['Concept']))
        g.add((NAPP[cd], SKOS['prefLabel'], rdf.Literal(lbl)))
        g.add((NAPP[cd], SKOS['inScheme'], NAPP[vrb_name]))

        if len(set(indentlist)) > 1:
            if indentlist[i] > 0:
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


basepath = '/users/auke/dropbox/files attached directly to project/rdf/napp/'

# with open(basepath + 'nappcodebook.json', 'w') as out:
#     json.dump(codelist, out)

for vrb_name, graph in graphs.items():
    with open(basepath + vrb_name + '.ttl', 'w') as out:
        graph.serialize(out, format='turtle')
