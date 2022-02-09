import os
import solver
import generator


#implemenation for large tests using different instances
#only partly relevant since the size of one problem limits the usability strongly

test_name = 'NO_QUEST_01'
test_dir = 'test_results/' + test_name 

#number of instances
numb_inst = 2

#number of quests
numb_quests = 0

if not os.path.exists(test_dir):
    #create directory for results
    os.mkdir(test_dir)
    
    
    for d in range(7,8):
        #number of tiles
        max_tiles = d
        board_size = d
        
        size_dir = test_dir + '/' + str(max_tiles) + '_tile_' + str(board_size) + '_board'
        os.mkdir(size_dir)
        
        c = 1
        for i in range(0,numb_inst):
            inst_name = 'inst_' + str(c)
            
            inst_dir = size_dir + '/' + inst_name +'/'
            os.mkdir(inst_dir)
            
            tile_set, quests = generator.genInst(max_tiles, numb_quests)
            
            generator.export(inst_name, tile_set, quests, direc=inst_dir)
            
            solver.solveProblem(max_tiles, board_size, tile_set, inst_name, dic=inst_dir)
            
            c += 1
    
    
else:
    print('No test started b/c of existing directory')