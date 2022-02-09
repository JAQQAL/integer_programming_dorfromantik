import random as rn


'''Generate  tiles and quests
    All segment types are treated equally w.r.t. object numbers and quests
    TODO: check format for up-to-dateness
'''
def genInst(d, q, allowed_types=['gras','tree','corn','house','rail','water']):
    #create sequence of segment types for all tiles
    type_seq = []
    for s in range(0,d*7):
        type_seq.append(rn.choice(allowed_types))
    
    #quest candidates, only used if some tiles/segments should be excluded
    q_cand = []
    
    #create tiles
    tile_set = []
    for t in range(0,d):
        tile = []
        for s in range(0,7):
            tile.append((type_seq[t*6 + s],rn.randint(1,4)))
            q_cand.append((t,s))
        
        tile_set.append(tile)
    
    #create quests
    quests = {'>': [],
              '=': [],
              '>,o': [],
              '=,o': []
              }
    for i in range(0,q):
        t,s = rn.choice(q_cand)
        q_cand.remove((t,s))
        
        q_type = rn.choice(['>','=','>,o','=,o'])
        value = rn.randint(5,30)
        quests[q_type].append((t,s,value))
    
    return tile_set, quests

#TODO: finish/expand genGameInst()
'''Generate  tiles and quests that mimic the tiles and quests from the videogame
TODO: check tiles after creation and adjust segment types and number of elements
'''
def genGameInst(d, q, allowed_types=['gras','tree','corn','house','rail','water']):
    #create sequence of segment types for all tiles
    type_seq = []
    for s in range(0,d*7):
        type_seq.append(rn.choice(allowed_types))
    
    #quest candidates, used to exclude gras segments
    q_cand = []
    
    #create tiles
    tile_set = []
    for t in range(0,d):
        tile = []
        for s in range(0,7):
            s_type = type_seq[t*6 + s]
            tile.append((s_type,createAmount(s_type, s)))
            if s_type != 'gras' and s != 6:
                q_cand.append((t,s))
        
        tile_set.append(tile)
    
    #create quests
    quests = {'>': [],
              '=': [],
              '>,o': [],
              '=,o': []
              }
    for i in range(0,q):
        t,s = rn.choice(q_cand)
        q_cand.remove((t,s))
        
        s_type = tile_set[t][s][0]
        print(s_type)
        #TODO 
        q_type, value = createQuest(s_type)
        
        quests[q_type].append((t,s,value))
    
    return tile_set, quests

'''Create number of elements for a segment depending on its type'''
def createAmount(segment_type, s):
    match segment_type:
        case 'gras': return 0
        case 'tree': return rn.choice([4] + 4*[5] + [6])
        case 'corn': return rn.choice([0,1])
        case 'house': return rn.choice(6*[1] + [2])
        case 'rail': 
            if s == 6: return 1
            else: return 0
        case 'water': 
            if s == 6: return 1
            else: return 0

'''Create a quest depending on a given segment type'''
def createQuest(segment_type):
    match segment_type:
        case 'tree': return rn.choice([('>','u'),('>,o')]), rn.randint(29,55)
        case 'corn': return rn.choice([('>','u'),('=','o')]), rn.randint(6,14)
        case 'house': return rn.choice([('>','u'),('=','o')]), rn.randint(7,19)
        case 'rail': return rn.choice([('>','u'),('=','u')]), rn.randint(4,8)
        case 'water': return rn.choice([('>','u'),('=','u')]), rn.randint(4,8)

'''Save instance as .py file in 'example' directory'''
def export(name, tiles, quests, direc='examples/'):
    
    with open(direc + name + '.py','w')  as file:
        #write name
        file.write("name = '" + name + "'\n")
        file.write('\n')
        
        #write tiles
        file.write('tile_set = [\n')
        for t in tiles:
            file.write('\t\t\t'+str(t)+',\n')
        file.write('\t\t\t]\n')
        
        #wirte quests
        file.write('quests = {\n')
        for q in quests.keys():
            file.write("\t\t\t'" + q + "': " + str(quests[q]) + ',\n')
        file.write('\t\t}')

