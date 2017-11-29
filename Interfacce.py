import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json
import warnings


#Genera un grafo casualmente. Ad ogni nodo viene dato un id e numero di interfacce. Ad ogni arco un id e peso.
def GeneraGrafoRandom(num,prob,randWeight=False):
    G = nx.gnp_random_graph(num, prob)
    
    G.remove_nodes_from(nx.isolates(G))
    
    nx.set_node_attributes(G, 'n_interf', 0)
    nx.set_edge_attributes(G, 'ID','')
    
    #non posso creare qui dizionario perche' graphml di base non sopporta  tipi composti
    for n,d in G.nodes_iter(data=True): 
        d['n_interf']= G.degree(n)
    
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
            if(i>num_int):
                i=0
            else:
                interf[i].append(y['ID'])
            i+=1       
            
    return H,archi


#Modifica un grafo generando per ogni nodo una clique di nodi in base al suo numero di interfacce
def ModificaGrafo(G,archi):
    for n,d in G.nodes_iter(data=True):
        print n,d
    
    print json.dumps(archi, indent=4) 
    
    

#funzione ausiliaria per i test
def Genera_e_Salva():
    g= GeneraGrafoRandom(8,0.35,True)
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


'''
graph= nx.read_graphml('rete.graphml')
warnings.filterwarnings("ignore")
nx.draw(graph, with_labels=True)
plt.show()'''


