import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import warnings


#genera grafo casuale e assegna: per ogni nodo, id e numero di interfaccie; per ogni arco, id e peso.
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
    
def ConnettiInterfacce():
    G= nx.read_graphml('rete.graphml')
    H= nx.Graph()
    
    for n,d in G.nodes_iter(data=True): 
        num_int=d['n_interf']
        interf= {}
        
        for x in range(num_int):
            interf[x] = []
        
        H.add_node(n, n_interf=d['n_interf'],interfacce=interf)
        
        i=0
        for a,b,y in G.edges_iter(n, data=True):
            if(i>num_int):
                i=0
            else:
                interf[i].append(y['ID'])
            i+=1        
        
        
    for n,d in H.nodes_iter(data=True):
        print n,d
        


#funzione ausiliaria per i test
def Genera_e_Salva():
    g= GeneraGrafoRandom(15,0.18,True)
    SalvaInGraphml(g)
    
    warnings.filterwarnings("ignore")
    nx.draw(g, with_labels=True)
    plt.show()


#Genera_e_Salva()
ConnettiInterfacce()



