import gurobipy as gp
from gurobipy import GRB
import os
from colour import Color
import time

#own visuliation tools
import visualization.plot_placement as pltp
import visualization.plot_network as pltn

#example file
from examples.ex_01 import tile_set, name, quests


#Modelling tool functions

'''Creates list of all fields on the board.'''
def createBoard(size):
    fields = []
    
    for i in range(0,size):
        for j in range(0, size + i):
            fields.append((i,j))
    for i in range(size, 2 * size - 1):
        for j in range(0,3 * size - 2 - i):
            fields.append((i,j))
    
    return fields

'''Creates list of nodes and edges on the board.'''
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

'''Determines the neighborings fields.'''
def getNeighbours(board, size, row, column):
    neighbours = []
    
    if row < size-1:
        poss = [(row-1,column-1),(row-1,column),(row,column-1),(row,column+1),(row+1,column),(row+1,column+1)]
    elif row == size-1:
        poss = [(row-1,column-1),(row-1,column),(row,column-1),(row,column+1),(row+1,column-1),(row+1,column)]
    else:
        poss = [(row-1,column),(row-1,column+1),(row,column-1),(row,column+1),(row+1,column-1),(row+1,column)]
    
    for f in poss:
        if f in board:
            neighbours.append(f)
    
    return neighbours

'''Distance function on board.
    board - list of all fields
    size - size of the board
    (i,j) - coordinates of a field (start)
    (k,l) - coordinates of a field (end)'''
def dist(board, size, i, j, k, l):
    #start = end
    if i==k and j==l:
        return 0
    
    #prepate loop
    visited = set()
    curr = set([(i,j)])
    d = 1
    
    #2*size as upper bound for distance
    #iterating through distances 1,2,3,4,.. exploring the board through neighbouring fields
    while d < 2 * size:
        #explore board
        new = set()
        for b in curr:
            new = new | (set(getNeighbours(board, size, b[0], b[1])))
        new.difference(curr|visited)
        #check for end field
        if (k,l) in new:
            return d
        
        #prepare next loop
        d += 1
        visited = visited | curr
        curr = new
    
    #if start or end field not on the board
    return -1 

#adjust
def getReachableNodes(board, size, t):
    reachable = []
    
    visited = []
    visiting = [(size-1,size-1)]
    to_visit = []
    
    c = 0
    while c <= t:
        for i,j in visiting:
            if not (i,j) in reachable:
                reachable.append((i,j))
            
            n = getNeighbours(board,size,i,j)
            for k,l in n:
                if not (k,l) in visited + visiting + to_visit:
                    to_visit.append((k,l))
            
            visited.append((i,j))
        visiting = to_visit
        to_visit = []
        
        c += 1
    
    reachable_nodes = []
    for i,j in reachable:
        for k in range(0,7):
            reachable_nodes.append((i,j,k))
    
    return reachable_nodes


'''Determines the nodes that could be connected to a quest location based on the number of tiles.
    board - list of all fields
    size - size of the board
    d - total number of tiles to be placed 
    (i,j) - coordinates of a field (quest location)'''
def connectableNodes(board, size, d, i, j, k):
    #coordinates of center field: (size-1,size-1)
    center = size - 1
    
    #distance from quest location to center field
    q_to_c = dist(board, size, i, j, center, center)
    
    #determines connectable fields based on distances
    conn_fields = []
    for l,m in board:
        c_to_f = dist(board, size, center, center, l, m)
        q_to_f = dist(board, size, l, m, i, j)
        #center -> (l,m) -> quest location
        if c_to_f + q_to_f <= d-1:
            conn_fields.append((l,m))
        #center -> quest location -> (l,m)
        elif q_to_c + q_to_f <= d-1:
            conn_fields.append((l,m))
        #quest location -> center -> (l,m)
        elif q_to_c + c_to_f <= d-1:
            conn_fields.append((l,m))
    
    #from fields to nodes: each field has 7 nodes
    conn_nodes = []
    for l,m in conn_fields:
        for n in range(0,7):
            if not (l == i and m == j and n == k):
                conn_nodes.append((l,m,n))
    '''
    for n in range(0,7):
        if n != k:
            conn_nodes.append((i,j,n))
    '''
    return conn_nodes


'''Determines the node that resembles the segment of this noce is facing towards.
    Beware: If no such note exists (board boundary, central segment) it returns the given node!
    TODO: more elegant & quicker implementation?
    '''
def opposingSegment(board, size, row, column, k):
    n = getNeighbours(board,size,row,column)
    
    
    #same row
    if k == 1:
        if (row,column+1) in n:
            return row,column+1,4
    elif k == 4:
        if (row,column-1) in n:
            return row,column-1,1
    
    #cetermine based on different sections of the board: upper half, middle row, lower half
    #upper half
    if row < size-1:
        if k == 0:
            if (row-1,column) in n:
                return row-1,column,3
        elif k == 2:
            if (row+1,column+1) in n:
                return row+1,column+1,5
        elif k == 3:
            if (row+1,column) in n:
                return row+1,column,0
        elif k == 5:
            if (row-1,column-1) in n:
                return row-1,column-1,2
    #middle row
    elif row == size-1:
        if k == 0:
            if (row-1,column) in n:
                return row-1,column,3
        elif k == 2:
            if (row+1,column) in n:
                return row+1,column,5
        elif k == 3:
            if (row+1,column-1) in n:
                return row+1,column-1,0
        elif k == 5:
            if (row-1,column-1) in n:
                return row-1,column-1,2
    #lower half
    elif row > size-1:
        if k == 0:
            if (row-1,column+1) in n:
                return row-1,column+1,3
        elif k == 2:
            if (row+1,column) in n:
                return row+1,column,5
        elif k == 3:
            if (row+1,column-1) in n:
                return row+1,column-1,0
        elif k == 5:
            if (row-1,column) in n:
                return row-1,column,2
    
    return row, column, k

'''Determines adjacent nodes.'''
def adjacentNodes(board,size,i, j, k):
    n = []
    #node is central segment of a field
    if k == 6:
        for l in range(0,6):
            n.append((i,j,l))
    else:
        #central segment
        n.append((i,j,6))
        #neighbouring boundary segments
        n.append((i,j,(k+1)%6))
        n.append((i,j,(k-1)%6))
        #node is a segment that faces another field
        if opposingSegment(board,size,i,j,k) != (i,j,k):
            n.append(opposingSegment(board,size,i,j,k))
        
    return n

'''Determines edges that connect a field to other fields
    TODO: avoid iterating through all edges'''
def getInterTileEdges(row, column, edges):
    inter = []
    
    for i,j,k,l,m,n in edges:
        if i == row and j == column:
            if l != row or m != column:
                inter.append((i,j,k,l,m,n))
    
    return inter


def relevantEdges(edges, rel_nodes):
    rel_edges = []
    for (i,j,k,l,m,n) in edges:
        if (i,j,k) in rel_nodes and (l,m,n) in rel_nodes:
            rel_edges.append((i,j,k,l,m,n))
    
    return rel_edges 
    

#IP modelling and solving functions

'''Modelling and solving of the IP.
    TODO: work around for 'Out of Memory' problem'''
def solveProblem(d, size, tile_set, quests, name, segment_types=['gras','tree','corn','house','rail','water'], dic='output/', fixed_start=True):

    #for output files
    tag = '_' + name + '_' + str(d) + '_' + str(size)

    #create structures
    board = createBoard(size)
    nodes, edges = createNetwork(size)
    
    
    #value edges based on whether it connects two tiles
    edge_points = {}
    for i,j,k,l,m,n in edges:
        if i != l or j != m:
            edge_points[i,j,k,l,m,n] = -0.5
        else:
            edge_points[i,j,k,l,m,n] = 0
    
    
    start = time.time()
    #Gurobi model
    m = gp.Model('romantik' + tag)


    #1. part ------------------------------------
    #tile placement rules
    occ = m.addVars(range(0,d), range(0,6), board, vtype=GRB.BINARY, name='occupies')
    m.addConstrs((occ.sum(t,'*','*','*') == 1 
                    for t in range(0,d)), 
                    name='exactly_once_placed&ori')
    m.addConstrs((occ.sum('*','*',i,j) <= 1 
                    for (i,j) in board), 
                    name='max_one_per_field')
    m.addConstrs((occ.sum(t,'*',i,j) <= gp.quicksum(occ[s,rN,k,l] for s in range(0,t) for rN in range(0,6) for (k,l) in getNeighbours(board,size,i,j)) 
                    for t in range(1,d)
                    for (i,j) in board), 
                    name='connect_to_placed')

    #fixed starting position and rotation (first tile)
    if fixed_start:
        m.addConstr(occ[0,0,size-1,size-1] == 1, name='starting_tile')


    #2. part ------------------------------------
    #segment kind
    kind = m.addVars(nodes, segment_types, vtype=GRB.BINARY, name='kind')
    m.addConstrs(kind.sum(i,j,k,'*') == occ.sum('*','*',i,j) 
                    for (i,j,k) in nodes)
    m.addConstrs((occ[t,r,i,j] == 1) >>  (1 == kind[i,j,k,tile_set[t][(k-r)%6][0]])
                    for t in range(0,d)
                    for r in range(0,6)
                    for (i,j) in board
                    for k in range(0,6))
    m.addConstrs(occ.sum(t,'*',i,j) <= kind[i,j,6,tile_set[t][6][0]]
                    for t in range(0,d)
                    for (i,j) in board)
                    
    #rail placement restrictions
    m.addConstrs((kind[i,j,k,'rail'] + gp.quicksum(kind[l,m,n,s] for l,m,n in [opposingSegment(board,size,i,j,k)] for s in segment_types if s != 'rail') <= 1
                for (i,j) in board
                for k in range(0,6)),
                name='rails')

    #water placement restrictions
    m.addConstrs((kind[i,j,k,'water'] + gp.quicksum(kind[l,m,n,s] for l,m,n in [opposingSegment(board,size,i,j,k)] for s in segment_types if s != 'water') <= 1
                for (i,j) in board
                for k in range(0,6)),
                name='water')
    
    #3. part ------------------------------------
    #number of objects
    #TODO: upper bound
    quant = m.addVars(nodes, vtype=GRB.INTEGER, name='quantity')
    #max number of possible elements on a segment
    z = 6
    m.addConstrs(quant[i,j,k] <= occ.sum('*','*',i,j) * z
                    for (i,j,k) in nodes)
    m.addConstrs(((occ[t,r,i,j] == 1) >> (quant[i,j,k] == tile_set[t][(k-r)%6][1]) 
                    for t in range(0,d) 
                    for r in range(0,6)
                    for (i,j,k) in nodes
                    if k != 6),
                    name='border_quant')
    m.addConstrs((occ[t,r,i,j] == 1) >> (quant[i,j,6] == tile_set[t][6][1])
                    for t in range(0,d) 
                    for r in range(0,6)
                    for (i,j) in board)

    #4.part ------------------------------------
    #connecting tile segments of equal types
    conn = m.addVars(edges, obj=edge_points, vtype=GRB.BINARY, name='conn_by_edge')
    m.addConstrs((conn[i,j,k,l,m,n] == conn[l,m,n,i,j,k] 
                    for (i,j,k,l,m,n) in edges),
                    name='undir_edges')
    m.addConstrs((conn[i,j,k,l,m,n] == gp.quicksum(kind[i,j,k,segt] * kind[l,m,n,segt] for segt in segment_types)
                    for (i,j,k,l,m,n) in edges),
                    name='matching')
    
    #5. part ------------------------------------
    #fields that can be perfectly arranged
    #TODO: can be refined based on number of tiles and board size
    inner_board = []
    for (i,j) in board:
        if len(getNeighbours(board,size,i,j)) == 6:
            inner_board.append((i,j))
    
    #perfect arrangement
    perf = m.addVars(inner_board, obj=-6, vtype=GRB.BINARY, name='perfect')
    m.addConstrs(perf[i,j] <= conn[a,b,k,l,m,n] 
                    for (i,j) in inner_board
                    for a,b,k,l,m,n in getInterTileEdges(i,j,edges))
    
    
    #6. part ------------------------------------
    #TODO: sparse implementation of u, s, ut and quest constraints
    #only quest on tiles which are placed
    quest_tiles = []
    for t in quests.keys():
        if t < d:
            quest_tiles.append(t)
    
    #nodes connected to quest location
    u = m.addVars(quest_tiles, nodes, vtype=GRB.BINARY , name='aux_u')
    
    #size (number of objects) of connected component a quest belongs to
    s = m.addVars(quest_tiles, vtype=GRB.INTEGER , name='s')
    m.addConstrs(s[t] == gp.quicksum(u[t,l,m,n] * quant[l,m,n] for (l,m,n) in nodes)
                    for t in quest_tiles)
    
    #quest completion
    #combine quest with location on the board
    aux_compl = m.addVars(quest_tiles, nodes, obj=-10, vtype=GRB.BINARY, name='aux_completed')
    m.addConstrs(aux_compl[t,i,j,k] == 0
                    for t in quest_tiles
                    for (i,j,k) in nodes
                    if not (i,j,k) in getReachableNodes(board,size,t))
    m.addConstrs(aux_compl[t,i,j,6] == 0
                    for t in quest_tiles
                    for i,j in board)
    m.addConstrs(aux_compl[t,i,j,k] <= occ[t,(k-quests[t][0])%6,i,j]
                    for t in quest_tiles
                    for (i,j,k) in nodes)
    
    #combination of quest, its location and nodes connected to its location
    combo = m.addVars(quest_tiles, nodes, nodes, vtype=GRB.BINARY, name='combo')
    m.addConstrs(combo[t,i,j,k,l,m,n] == aux_compl[t,i,j,k] * u[t,l,m,n]
                    for t in quest_tiles
                    for (i,j,k) in nodes
                    for (l,m,n) in nodes)
    
    #constraints for each quest
    for t in quest_tiles:
        #describing the connected component each quest lies in
    
        #flow values for relevant scenarios. filled while iterating
        flow = {}
        
        
        
        #iterarting through all possible combinations
        #1) possible quest locations (start)
        #TODO: change to reachable field to avoid additional computation 
        for (si,sj,sk) in getReachableNodes(board,size,t):
            #1) nodes that could be connected to quest location (to)
            con_nodes = connectableNodes(board, size, d, si, sj, sk)
            for (ti,tj,tk) in con_nodes:
                
                #generate flow values for path problem
                for (ni,nj,nk) in nodes:
                    if si == ni and sj == nj and sk == nk:
                        flow[si,sj,sk,ti,tj,tk,ni,nj,nk] = 1
                    elif ti == ni and tj == nj and tk == nk:
                        flow[si,sj,sk,ti,tj,tk,ni,nj,nk] = -1
                    else:
                        flow[si,sj,sk,ti,tj,tk,ni,nj,nk] = 0
                
                #formulation of a path problem using flow
                if not (si == ti and sj == tj and sk == tk):
                    
                    rel_edges = relevantEdges(edges, con_nodes + [(si,sj,sk)])
                    
                    #variable to decribe connecting path problem: use or do not use EDGE for path to NODE
                    ut = m.addVars(rel_edges, vtype=GRB.BINARY, name='u_q'+str(t)+'_('+str(ti)+','+str(tj)+','+str(tk)+')')
                
                    #balance of incoming and outgoing flow
                    for (ni,nj,nk) in con_nodes:#nodes:
                        m.addConstr((combo[t,si,sj,sk,ti,tj,tk] == 1) >> (ut.sum(ni,nj,nk,'*','*','*') - ut.sum('*','*','*',ni,nj,nk) == flow[si,sj,sk,ti,tj,tk,ni,nj,nk]))
        
                    #restriction to pick only one edge from quest location
                    m.addConstr((combo[t,si,sj,sk,ti,tj,tk] == 1) >> (ut.sum(si,sj,sk,'*','*','*') <= 1))
                    
                    #edges can only be used if they exist
                    for (ni,nj,nk,nl,nm,nn) in rel_edges:#edges:
                        m.addConstr((combo[t,si,sj,sk,ti,tj,tk] == 1) >> (ut[ni,nj,nk,nl,nm,nn] <= conn[ni,nj,nk,nl,nm,nn]))
                    
                    '''
                    #at least one edge needs to be used
                    m.addConstr((combo[t,si,sj,sk,ti,tj,tk] == 1) >> (1 <= ut.sum('*','*','*','*','*','*')))
                    '''
                    
                    #currently in variable combo 
                    #path does exist
                    m.addConstr((combo[t,si,sj,sk,ti,tj,tk] == 1) >> (ut.sum('*','*','*','*','*','*') <= len(edges) * u[t,ti,tj,tk]))
                    
                    #currently in variable combo 
                    #path does not exist
                    m.addConstr((combo[t,si,sj,sk,ti,tj,tk] == 1) >> (u[t,ti,tj,tk] <= ut.sum(si,sj,sk,'*','*','*')))
                    
        #additional restriction based on the type of the quest
        #larger connected component w.r.t objects
        if quests[t][2] == '>':
            m.addConstrs((aux_compl[t,i,j,k] == 1) >> (quests[t][1] <= quant[i,j,k] + s[t])
                        for (i,j,k) in nodes)
        #exact size of connected component w.r.t. objects
        elif quests[t][2] == '=':
            m.addConstrs((aux_compl[t,i,j,k] == 1) >> (quests[t][1] == quant[i,j,k] + s[t])
                            for (i,j,k) in nodes)
        #closedness of connected component
        if quests[t][3] == 'o':
            m.addConstrs((aux_compl[t,i,j,k]== 1) >> (u[t,l,m,n] <= occ.sum('*',o,p))
                            for (i,j,k) in nodes
                            for (l,m,n) in nodes
                            for (o,p,q) in [opposingSegment(board,d,l,m,n)])
    
    end = time.time()
    print('Modelling duration: ', end - start)
    
    #delete old log file if existing
    if os.path.exists(dic + 'log' + tag + '.txt'):
        os.remove(dic + 'log' + tag + '.txt')

    #create log file when optimizing
    m.Params.LogFile = dic + 'log' + tag + '.txt'
    
    #solving time limit
    m.Params.TimeLimit = 3600
    
    #focus parameter
    #m.Params.MIPFocus = 1 
    
    #start optimization
    m.optimize()
    
    #IIS computation (for examination of unsolvable instances)
    #m.computeIIS()
    #m.write("model.ilp")
    
    #write .lp file
    m.write(dic + 'model' + tag + '.lp')
    
    #save values of the variables
    solAsText(m, dic, tag)

    #show solution in command line
    #print2CMD(m)
    
    #plot tile placement with color coding
    #solAsColBoard(d, size, board, occ, dic, tag)
    
    #plot tile placement
    solAsBoard(d, size, board, occ, dic, tag)

    #plot segments position with connections
    solAsNetwork(nodes, edges, kind, conn, quant, size, dic, tag)


'''Modelling and solving of the IP. STATE: not correct'''
def solveProblemTest(d, size, tile_set, quests, name, segment_types=['gras','tree','corn','house','rail','water'], dic='output/', fixed_start=True):

    #for output files
    tag = '_' + name + '_' + str(d) + '_' + str(size)

    #create structures
    board = createBoard(size)
    nodes, edges = createNetwork(size)
    
    
    #value edges based on whether it connects two tiles
    edge_points = {}
    for i,j,k,l,m,n in edges:
        if i != l or j != m:
            edge_points[i,j,k,l,m,n] = -0.5
        else:
            edge_points[i,j,k,l,m,n] = 0
    
    
    start = time.time()
    #Gurobi model
    m = gp.Model('romantik' + tag)


    #1. part ------------------------------------
    #tile placement rules
    occ = m.addVars(range(0,d), range(0,6), board, vtype=GRB.BINARY, name='occupies')
    m.addConstrs((occ.sum(t,'*','*','*') == 1 
                    for t in range(0,d)), 
                    name='exactly_once_placed&ori')
    m.addConstrs((occ.sum('*','*',i,j) <= 1 
                    for (i,j) in board), 
                    name='max_one_per_field')
    m.addConstrs((occ.sum(t,'*',i,j) <= gp.quicksum(occ[s,rN,k,l] for s in range(0,t) for rN in range(0,6) for (k,l) in getNeighbours(board,size,i,j)) 
                    for t in range(1,d)
                    for (i,j) in board), 
                    name='connect_to_placed')

    #fixed starting position and rotation (first tile)
    if fixed_start:
        m.addConstr(occ[0,0,size-1,size-1] == 1, name='starting_tile')


    #2. part ------------------------------------
    #segment kind
    kind = m.addVars(nodes, segment_types, vtype=GRB.BINARY, name='kind')
    m.addConstrs(kind.sum(i,j,k,'*') == occ.sum('*','*',i,j) 
                    for (i,j,k) in nodes)
    m.addConstrs((occ[t,r,i,j] == 1) >>  (1 == kind[i,j,k,tile_set[t][(k-r)%6][0]])
                    for t in range(0,d)
                    for r in range(0,6)
                    for (i,j) in board
                    for k in range(0,6))
    m.addConstrs(occ.sum(t,'*',i,j) <= kind[i,j,6,tile_set[t][6][0]]
                    for t in range(0,d)
                    for (i,j) in board)
                    
    #rail placement restrictions
    m.addConstrs((kind[i,j,k,'rail'] + gp.quicksum(kind[l,m,n,s] for l,m,n in [opposingSegment(board,size,i,j,k)] for s in segment_types if s != 'rail') <= 1
                for (i,j) in board
                for k in range(0,6)),
                name='rails')

    #water placement restrictions
    m.addConstrs((kind[i,j,k,'water'] + gp.quicksum(kind[l,m,n,s] for l,m,n in [opposingSegment(board,size,i,j,k)] for s in segment_types if s != 'water') <= 1
                for (i,j) in board
                for k in range(0,6)),
                name='water')
    
    #3. part ------------------------------------
    #number of objects
    #TODO: upper bound
    quant = m.addVars(nodes, vtype=GRB.INTEGER, name='quantity')
    #max number of possible elements on a segment
    z = 6
    m.addConstrs(quant[i,j,k] <= occ.sum('*','*',i,j) * z
                    for (i,j,k) in nodes)
    m.addConstrs(((occ[t,r,i,j] == 1) >> (quant[i,j,k] == tile_set[t][(k-r)%6][1]) 
                    for t in range(0,d) 
                    for r in range(0,6)
                    for (i,j,k) in nodes
                    if k != 6),
                    name='border_quant')
    m.addConstrs((occ[t,r,i,j] == 1) >> (quant[i,j,6] == tile_set[t][6][1])
                    for t in range(0,d) 
                    for r in range(0,6)
                    for (i,j) in board)

    #4.part ------------------------------------
    #connecting tile segments of equal types
    conn = m.addVars(edges, obj=edge_points, vtype=GRB.BINARY, name='conn_by_edge')
    m.addConstrs((conn[i,j,k,l,m,n] == conn[l,m,n,i,j,k] 
                    for (i,j,k,l,m,n) in edges),
                    name='undir_edges')
    m.addConstrs((conn[i,j,k,l,m,n] == gp.quicksum(kind[i,j,k,segt] * kind[l,m,n,segt] for segt in segment_types)
                    for (i,j,k,l,m,n) in edges),
                    name='matching')
    
    #5. part ------------------------------------
    #fields that can be perfectly arranged
    #TODO: can be refined based on number of tiles and board size
    inner_board = []
    for (i,j) in board:
        if len(getNeighbours(board,size,i,j)) == 6:
            inner_board.append((i,j))
    
    #perfect arrangement
    perf = m.addVars(inner_board, obj=-6, vtype=GRB.BINARY, name='perfect')
    m.addConstrs(perf[i,j] <= conn[a,b,k,l,m,n] 
                    for (i,j) in inner_board
                    for a,b,k,l,m,n in getInterTileEdges(i,j,edges))
    
    model = m
    #6. part ------------------------------------
    node_combos = []
    for i,j,k in nodes:
        for l,m,n in connectableNodes(board, size, d, i, j, k):
            if not (i,j,k,l,m,n) in node_combos:
                node_combos.append((i,j,k,l,m,n))
    m = model
    
    u = m.addVars(node_combos, vtype=GRB.BINARY, name='u')
    m.addConstrs(u[i,j,k,l,m,n] == conn[i,j,k,l,m,n]
                    for i,j,k,l,m,n in edges
                    if (i,j,k,l,m,n) in node_combos)
    
    m.addConstrs(u[i,j,k,l,m,n] == u[l,m,n,i,j,k]
                    for i,j,k,l,m,n in node_combos)
    
    m.addConstrs(u[i,j,k,l,m,n] * u[i,j,k,o,p,q] == u[i,j,k,l,m,n] * u[l,m,n,o,p,q]
                    for i,j,k,l,m,n in node_combos
                    for o,p,q in nodes
                    if (i,j,k,o,p,q) in node_combos and (l,m,n,o,p,q) in node_combos)
    
    s = m.addVars(nodes, vtype=GRB.INTEGER, name='s')
    m.addConstrs(s[i,j,k] == gp.quicksum(quant[l,m,n] * u[i,j,k,l,m,n] for l,m,n in connectableNodes(board, size, d, i, j, k)) + quant[i,j,k] 
                    for i,j,k in nodes)
    
    #only quest on tiles which are placed
    quest_tiles = []
    for t in quests.keys():
        if t < d:
            quest_tiles.append(t)
    
    
    #quest completion
    #compl = m.addVars(quest_tiles, vtype=GRB.BINARY, name='completed')
    
    #combine quest with location on the board
    aux_compl = m.addVars(quest_tiles, nodes, obj=-10, vtype=GRB.BINARY, name='aux_completed')
    m.addConstrs(aux_compl[t,i,j,k] <= occ[t,(k-quests[t][0])%6,i,j]
                    for t in quest_tiles
                    for (i,j,k) in nodes)
    m.addConstrs(aux_compl[t,i,j,6] == 0
                    for t in quest_tiles
                    for i,j in board)           
    m.addConstrs(aux_compl.sum(t,'*','*','*') <= 1
                    for t in quest_tiles)      
    
    #constraints for each quest
    for t in quest_tiles:        
        #additional restriction based on the type of the quest
        #larger connected component w.r.t objects
        if quests[t][2] == '>':
            m.addConstrs((aux_compl[t,i,j,k] == 1) >> (quests[t][1] <= s[i,j,k])
                        for (i,j,k) in nodes)
        #exact size of connected component w.r.t. objects
        elif quests[t][2] == '=':
            m.addConstrs((aux_compl[t,i,j,k] == 1) >> (quests[t][1] == s[i,j,k])
                            for (i,j,k) in nodes)
        #closedness of connected component
        if quests[t][3] == 'o':
            m.addConstrs((aux_compl[t,i,j,k]== 1) >> (u[t,l,m,n] <= occ.sum('*',o,p))
                            for (i,j,k) in nodes
                            for (l,m,n) in nodes
                            for (o,p,q) in [opposingSegment(board,d,l,m,n)])
    
    end = time.time()
    print('Modelling duration: ', end - start)
    
    #delete old log file if existing
    if os.path.exists(dic + 'log' + tag + '.txt'):
        os.remove(dic + 'log' + tag + '.txt')

    #create log file when optimizing
    m.Params.LogFile = dic + 'log' + tag + '.txt'
    
    #solving time limit
    m.Params.TimeLimit = 3600
    
    #focus parameter
    #m.Params.MIPFocus = 1 
    
    #start optimization
    m.optimize()
    
    #IIS computation (for examination of unsolvable instances)
    #m.computeIIS()
    #m.write("model.ilp")
    
    #write .lp file
    m.write(dic + 'model' + tag + '.lp')
    
    #save values of the variables
    solAsText(m, dic, tag)

    #show solution in command line
    #print2CMD(m)
    
    #plot tile placement with color coding
    #solAsColBoard(d, size, board, occ, dic, tag)
    
    #plot tile placement
    solAsBoard(d, size, board, occ, dic, tag)

    #plot segments position with connections
    solAsNetwork(nodes, edges, kind, conn, quant, size, dic, tag)


#Output functions

'''Save solution as .txt file'''
def solAsText(model, dic, tag):
    with open(dic + 'sol' + tag + '.txt','w')  as file:
        file.write('Runtime: ' + str(model.RUNTIME) + ' s\n\n')
        for v in model.getVars():
            file.write('%s = %g\n' % (v.VarName, v.X))
        
        file.write('Obj: %g' % model.ObjVal)

'''Save resulting board of the solution with segments'''
def solAsNetwork(nodes, edges, segment, conn, quant, size, dic, tag):
    #color nodes by their type
    node_color = []
    node_label = {}
    for (i,j,k) in nodes:
        if round(segment[i,j,k,'gras'].X) == 1:
            node_color.append('#679219')
        elif round(segment[i,j,k,'tree'].X) == 1:
            node_color.append('#0d691e')
        elif round(segment[i,j,k,'corn'].X) == 1:
            node_color.append('#f2d21d')
        elif round(segment[i,j,k,'house'].X) == 1:  
            node_color.append('#da0707')
        elif round(segment[i,j,k,'rail'].X) == 1:
            node_color.append('#7f6336')
        elif round(segment[i,j,k,'water'].X) == 1:
            node_color.append('#3bbbeb')
        else:
            node_color.append('#eae7d9')
        node_label[i,j,k] = round(quant[i,j,k].X)

    #highlight edges between different tiles 
    conn_edges = []
    e_width = {}
    for (i,j,k,l,p,q) in edges:
        if round(conn[i,j,k,l,p,q].X) == 1:
            fr = (i,j,k)
            to = (l,p,q)
            conn_edges.append((fr,to))
            
            if i != l or j != p:
                e_width[i,j,k,l,p,q] = 4
            else:
                e_width[i,j,k,l,p,q] = 1


    pltn.drawNetwork(size, nodes, conn_edges, node_color, e_width, dic + 'netw' + tag, node_label)

'''Print variables with value 1 on command line '''
def print2CMD(model):
    for v in model.getVars():
        if round(v.X) == 1:
            print('%s %g' % (v.VarName, v.X))

    print('Obj: %g' % model.ObjVal)

'''Save resulting board of the solution using colors. without segment'''
def solAsColBoard(d, size, board, occ, dic, tag):
    #mark the tile through a color gradient relating their order
    red = Color("#ff0000")
    colors = list(red.range_to(Color("#8b008b"),d))

    #translate solution to coloring
    hex_colors = {}
    for (i,j) in board:
        color = '#ababab'
        for t in range(0,d):
            for r in range(0,6):
                if round(occ[t,r,i,j].X) == 1:
                    color = str(colors[t])
        hex_colors[i,j] = color
    
    pltp.drawColoredBoard(size, hex_colors, dic + 'board_color' + tag)

'''Save resulting board of the solution using numbers. without segment'''
def solAsBoard(d, size, board, occ, dic, tag):
    numbering = {}
    for t in range(0,d):
        for (i,j) in board:
            for r in range(0,6):
                if round(occ[t,r,i,j].X) == 1:
                    numbering[t] = (i,j)
    
    pltp.drawNumberedBoard(size, numbering, dic + 'board' + tag)



#number of tiles to consider
d = 3

#board size
size = 3

#start ILP modelling and solving
solveProblem(d, size, tile_set, quests, name)
