# Script che genera un grafo casuale dove ogni nodo conosce quante interfacce ha
# ed espande in una clique di nodi un nodo scelto

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json
import warnings
import itertools
from netdiff.utils import _netjson_networkgraph as to_netjson
import random
from lib_brandes.brandes import betweenness_centrality as BC_salta_nodi

warnings.filterwarnings("ignore")

aggiunti = []


def PrintGrafoInJson(G, njproto='OLSR', njversion='0.1', njrevision='a09z',
                     njmetric='ETX'):
    js = to_netjson(njproto,
                    njversion,
                    njrevision,
                    njmetric,
                    G.nodes(data=True),
                    G.edges(data=True), dict=True)
    f1 = open('./topology.json', 'w+')
    f1.write(json.dumps(js, indent=4))
    f1.close()


# Genera un grafo casualmente. Ad ogni nodo viene dato un id e numero di
# interfacce. Ad ogni arco un id e peso.
def GeneraGrafoRandom(num, prob, randWeight=False, MenoInterf=False):
    G = nx.gnp_random_graph(num, prob)

    G.remove_nodes_from(nx.isolates(G))

    nx.set_node_attributes(G, 'n_interf', 0)
    nx.set_edge_attributes(G, 'ID', '')

    # non posso creare qui dizionario perche' graphml non sopporta tipi composti
    for n, d in G.nodes_iter(data=True):
        if(MenoInterf == False):
            d['n_interf'] = G.degree(n)
        else:
            d['n_interf'] = random.randint(1, G.degree(n))

    i = 0
    for u, v, d in G.edges(data=True):
        d['ID'] = 'e' + str(i)
        if(randWeight == False):
            d['weight'] = 1
        else:
            d['weight'] = float(np.random.uniform(1.0, 1.1))
        i += 1

    return G


def SalvaInGraphml(G):
    nx.write_graphml(G, "rete.graphml")


# Connetti gli edge di un nodo alle sue interfacce.
# return: @H grafo contente per ogni nodo le informazioni sulle proprie
#          intefacce e senza nessun arco tra i nodi
# return: @archi un dizionario contentente tutti gli archi del grafo
def ConnettiInterfacce():
    G = nx.read_graphml('rete.graphml')
    H = nx.Graph()
    archi = {}

    for n, d in G.nodes_iter(data=True):
        num_int = d['n_interf']
        interf = {}

        for x in range(num_int):
            interf[x] = []

        H.add_node(n, n_interf=d['n_interf'], interfacce=interf)

        i = 0
        for a, b, y in G.edges_iter(n, data=True):
            archi[y['ID']] = []
            archi[y['ID']].append(a)
            archi[y['ID']].append(b)
            archi[y['ID']].append(y['weight'])
            if(i >= num_int):
                i = 0
                interf[i].append(y['ID'])
            else:
                interf[i].append(y['ID'])
            i += 1

    return H, archi


def ConnettiNodiStandard(G, archi, UnicoNodoDaEspandere):
    for n in G.nodes():
        if(n in set(aggiunti)):
            continue

        num_int = G.node[n]['n_interf']
        interf = G.node[n]['interfacce']

        for key, value in interf.iteritems():
            for q in value:
                to = archi[q][0]
                da = archi[q][1]
                G.add_edge(da, to, weight=archi[q][2])

        G.remove_nodes_from([UnicoNodoDaEspandere])


# Modifica un grafo generando per ogni nodo una clique di nodi in base al suo
# numero di interfacce
def ModificaGrafo(G, archi, UnicoNodoDaEspandere):
    numnodiorginale = len(G.nodes())

    rimuovi = []
    for n in G.nodes():
        if (n != UnicoNodoDaEspandere):
            continue

        rimuovi.append(n)
        num_int = G.node[n]['n_interf']
        elem = []  # i nuovi nodi
        for i in range(num_int):
            if(i != 0):
                z = round((float(n) + 0.1 + float(i) / 10), 2)
            else:
                z = float(n) + 0.1
            G.add_node(z)  # !!! id nodi aggiunti int, es 4.1    NON '4.1'
            elem.append(z)

        for x, y in itertools.combinations(elem, 2):
            G.add_edge(x, y, weight=0.00001)

        interf = G.node[n]['interfacce']

        for key, value in interf.iteritems():
            w = elem[key]
            for q in value:  # ad un interfaccia possono essere attacatti + edge
                if(archi[q][0] != n):
                    to = archi[q][0]
                    G.add_edge(w, to, weight=archi[q][2])  # no nome i nuovi archi
                else:
                    to = archi[q][1]
                    G.add_edge(w, to, weight=archi[q][2])
                aggiunti.append(w)

    G.remove_nodes_from(rimuovi)

    ConnettiNodiStandard(G, archi, UnicoNodoDaEspandere)

    # PrintGrafoInJson(G)

    CalcolaCentralitaGrafoEspanso(G, numnodiorginale)


def CalcolaCentralitaGrafoEspanso(G, numnodiorginale):
    BCprimo = BC_salta_nodi(G, aggiunti, weight='weight', endpoints=False,
                            normalized=False)

    nodi = G.nodes()
    for i in set(aggiunti):
        nodi.remove(i)

    BCsecondo = BC_salta_nodi(G, nodi, weight='weight',
                              endpoints=False, normalized=False)

    BCClique = {}

    for key, value in BCprimo.items():
        BCClique[key] = value - BCsecondo[key]

    print '------------'
    print 'BC grafo dopo espansione nodo:'
    print json.dumps(BCClique, indent=4)
    ''''
    nx.draw(G, with_labels=True)
    plt.show()'''


# funzione ausiliaria per i test
def Genera_e_Salva():
    g = GeneraGrafoRandom(5, 0.4, randWeight=True, MenoInterf=True)
    SalvaInGraphml(g)
    #nx.draw(g, with_labels=True)
    # plt.show()


# funzione ausiliaria per i test
def Run_Test():
    grafo = nx.read_graphml('rete.graphml')

    BC_origin = nx.betweenness_centrality(grafo, weight='weight',
                                          endpoints=False, normalized=False)
    print "BC grafo originale:"
    print json.dumps(BC_origin, indent=4)
    #nx.draw(grafo, with_labels=True)
    # plt.show()

    g, archi = ConnettiInterfacce()
    ModificaGrafo(g, archi, '4')  # ad esempio '4' e non 4!



# Genera_e_Salva()
Run_Test()
