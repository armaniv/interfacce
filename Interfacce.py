import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json
import warnings
import itertools
from netdiff.utils import _netjson_networkgraph as to_netjson
import random


def PrintGrafoInJson(G,njproto='OLSR',njversion='0.1',njrevision='a09z',njmetric='ETX'):
    js= to_netjson(njproto,
                    njversion,
                    njrevision,
                    njmetric,
                    G.nodes(data=True),
                    G.edges(data=True), dict=True)
    f1=open('./topology.json', 'w+')
    f1.write(json.dumps(js, indent=4))
    f1.close()


#Genera un grafo casualmente. Ad ogni nodo viene dato un id e numero di interfacce. Ad ogni arco un id e peso.
def GeneraGrafoRandom(num,prob,randWeight=False,MenoInterf=False):
    G = nx.gnp_random_graph(num, prob)
    
    G.remove_nodes_from(nx.isolates(G))
    
    nx.set_node_attributes(G, 'n_interf', 0)
    nx.set_edge_attributes(G, 'ID','')
    
    #non posso creare qui dizionario perche' graphml di base non sopporta  tipi composti
    for n,d in G.nodes_iter(data=True):
        if(MenoInterf==False): 
            d['n_interf']= G.degree(n)
        else:
            d['n_interf']= random.randint(1, G.degree(n))
            
    i=0
    for u,v,d in G.edges(data=True):
        d['ID']='e'+str(i)
        if(randWeight==False):
            d['weight']=1
        else:
            d['weight']=float (np.random.uniform(1.0,1.1))
        i+=1
        
    return G


def SalvaInGraphml(G):
    nx.write_graphml(G, "rete.graphml")
    
    
#Connetti gli edge di un nodo alle sue interfacce.
#return: @H grafo contente per ogni nodo le informazioni sulle proprie intefacce e senza nessun arco tra i nodi
#return: @archi un dizionario contentente tutti gli archi del grafo
def ConnettiInterfacce():
    G= nx.read_graphml('rete.graphml')
    H= nx.Graph()
    archi={}
    
    for n,d in G.nodes_iter(data=True): 
        num_int=d['n_interf']
        interf= {}
        
        for x in range(num_int):
            interf[x] = []
        
        H.add_node(n, n_interf=d['n_interf'],interfacce=interf)
        
        i=0
        for a,b,y in G.edges_iter(n, data=True):
            archi[y['ID']]= []
            archi[y['ID']].append(a)
            archi[y['ID']].append(b)
            archi[y['ID']].append(y['weight'])
            if(i>=num_int):
                i=0
                interf[i].append(y['ID'])
            else:
                interf[i].append(y['ID'])
            i+=1       
            
    return H,archi


#funzione ausiliaria per modificare grafo
def CercaNodoCorrispondente(origine,destinazione,nome_arco,grafo):
    ret=float(destinazione)+0.1 
    interf = grafo.node[destinazione]['interfacce']
    for key, value in interf.iteritems():
        for q in value:
            if(q==nome_arco):
                if(key!=0):
                    ret+=float(key)/10
    return ret
                    

#Modifica un grafo generando per ogni nodo una clique di nodi in base al suo numero di interfacce
def ModificaGrafo(G,archi):
    for n,d in G.nodes_iter(data=True):
        print n,d
         
    rimuovi=[]    
    for n in G.nodes():
        rimuovi.append(n)
        num_int = G.node[n]['n_interf']
        elem=[]
        for i in range(num_int):
            if(i!=0):
                z=(float(n)+0.1 + float(i)/10)
            else:
                z=float(n)+0.1
            G.add_node(z)  
            elem.append(z)
            
        for x, y in itertools.combinations(elem, 2):
            G.add_edge(x,y,weight=0.00001) 
        
        interf = G.node[n]['interfacce']
        
        for key, value in interf.iteritems():
            w=elem[key]
            for q in value:         #ad un interfaccia possono essere attacatti piu edge
                if(archi[q][0]!=n):
                    to= CercaNodoCorrispondente(n,(archi[q][0]),q,G)
                    G.add_edge(w,to,weight=archi[q][2]) #non hanno nome i nuovi archi
                else:
                    to=CercaNodoCorrispondente(n,(archi[q][1]),q,G)
                    G.add_edge(w,to,weight=archi[q][2])
    
    G.remove_nodes_from(rimuovi)
    
    #PrintGrafoInJson(G)
    
    BC = nx.betweenness_centrality(G, weight='weight',endpoints=True,normalized=False)
    print '------------'
    print json.dumps(BC, indent=4)
                         
    warnings.filterwarnings("ignore")
    nx.draw(G, with_labels=True)
    plt.show()

   

#funzione ausiliaria per i test
def Genera_e_Salva():
    g= GeneraGrafoRandom(5,0.4,randWeight=True,MenoInterf=True)
    SalvaInGraphml(g)
    
    warnings.filterwarnings("ignore")
    nx.draw(g, with_labels=True)
    plt.show()

#funzione ausiliaria per i test
def Run_Test():
    g,archi = ConnettiInterfacce()
    ModificaGrafo(g,archi)



#Genera_e_Salva()
Run_Test()
