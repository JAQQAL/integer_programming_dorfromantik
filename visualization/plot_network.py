import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.pyplot import figure


tile_dist = 10
dist = 3

def positionAddRow(pos, row_y, row_x, number_tiles, row_index):
    clock_x = (tile_dist - dist / np.sqrt(2)) / 4
    clock_y = (tile_dist - dist) / 2
    z = (tile_dist - 2 * clock_x) / 2
    center_x = row_x
    
    for i in range(0,number_tiles):
        pos[row_index,i,6] = (center_x,row_y)
        
        pos[row_index,i,0] = (center_x + clock_x, row_y + clock_y)
        pos[row_index,i,1] = (center_x + z, row_y)
        pos[row_index,i,2] = (center_x + clock_x, row_y - clock_y)
        pos[row_index,i,3] = (center_x - clock_x, row_y - clock_y)
        pos[row_index,i,4] = (center_x - z, row_y)
        pos[row_index,i,5] = (center_x - clock_x, row_y + clock_y)
        
        center_x += tile_dist


def describeGraph(tiles):
    pos = {}
    
    row_x = 0 
    row_y = 0 
    for i in range(0,tiles):
        number_tiles = tiles + i
        
        positionAddRow(pos, row_y, row_x, number_tiles, i)
        
        row_x -= tile_dist / 2
        row_y -= tile_dist
    
    row_x += tile_dist
    for i in range(tiles, 2*tiles-1):
        number_tiles = 3 * tiles -2 - i
        
        positionAddRow(pos, row_y,row_x,number_tiles,i)
        
        row_x += tile_dist / 2
        row_y -= tile_dist
    
    return pos


def drawNetwork(d, nodes, edges, n_colors, e_width, filename, node_labels):
    figure(figsize=(15, 12), dpi=80)
    
    pos = describeGraph(d)
    
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    widths = [e_width[i,j,k,l,m,n] for ((i,j,k),(l,m,n)) in G.edges]
        
    
    nx.draw(G, pos=pos, with_labels=False, arrows=False, node_color=n_colors, width=widths)
    
    nx.draw_networkx_labels(G,pos,node_labels,font_size=12)
    
    plt.savefig(filename+'.jpeg', dpi=1000)
    
    plt.close()




'''
#tool to create board network; a copy from solver.py
def createNetwork(size):
    nodes = []
    edges = []
    
    #upper half
    for i in range(0,size):
        for j in range(0, size + i):
            #center node
            nodes.append((i,j,6))
            for k in range(0,6):
                nodes.append((i,j,k))
                
                #tile intern edges
                edges.append((i,j,k,i,j,6))
                edges.append((i,j,k,i,j,(k+1)%6))
            
            #inter tile edges
            if i < size - 1:
                edges.append((i,j,2,i+1,j+1,5))
                edges.append((i,j,3,i+1,j,0))
            if j < size + i - 1:
                edges.append((i,j,1,i,j+1,4))
    
    #lower half
    for i in range(size, 2 * size - 1):
        for j in range(0,3 * size - 2 - i):
            #center node
            nodes.append((i,j,6))
            for k in range(0,6):
                nodes.append((i,j,k))
                
                #tile intern edges
                edges.append((i,j,k,i,j,6))
                edges.append((i,j,k,i,j,(k+1)%6))
                
            #inter tile edges
            edges.append((i,j,0,i-1,j+1,3))
            edges.append((i,j,5,i-1,j,2))
            if j < 3 * size - 3 - i:
                edges.append((i,j,1,i,j+1,4))
    
    rev_edges = []
    for (i,j,k,l,m,n) in edges:
        rev_edges.append((l,m,n,i,j,k))
    edges += rev_edges
    
    return nodes, edges
'''

'''
#whole graph
nodes, edges = createNetwork(1)

real_edges = []
for (i,j,k,l,m,n) in edges:
    real_edges.append(((i,j,k),(l,m,n)))

n_color = []
for n in nodes:
    n_color.append('w')

e_width = {}
for e in edges:
    e_width[e] = 1

#n_label ={(0,0,0):0, (0,0,1):1, (0,0,2): 2, (0,0,3):3, (0,0,4):4, (0,0,5):5, (0,0,6):6}

drawNetwork(1, nodes, real_edges, n_color, e_width, 'tile_graph', {})
'''

'''
#tile
nodes, edges = createNetwork(1)

real_edges = [((0,0,6),(0,0,2)),
              ((0,0,6),(0,0,3)),
              ((0,0,6),(0,0,5)),
              ((0,0,2),(0,0,3))]

n_color = ['#f2d21d','#da0707','#0d691e','#f2d21d','#f2d21d','#0d691e','#f2d21d']


e_width = {}
for e in edges:
    e_width[e] = 1

n_label ={(0,0,0):1, (0,0,1):4, (0,0,2): 1, (0,0,3):0, (0,0,4):4, (0,0,5):1, (0,0,6):0}
#n_label ={(0,0,0):0, (0,0,1):1, (0,0,2): 2, (0,0,3):3, (0,0,4):4, (0,0,5):5, (0,0,6):6}

drawNetwork(1, nodes, real_edges, n_color, e_width, 'tile_graph_ex', n_label)
'''