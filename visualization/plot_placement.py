import tkinter
import turtle
import numpy as np


#for size
edge_length = 20

'''Draws a row of the board with prescribed colors'''
def drawColoredRow(myT, start_x, start_y, num_hexagons, hex_colors, index):
    #starting position
    myT.penup()
    myT.setposition(start_x,start_y)
    myT.pendown()
    
    for i in range(0,num_hexagons):
        myT.setheading(90)
        myT.pencolor(hex_colors[index,i])
        for j in range(6):
            #draw edge
            myT.forward(edge_length)
            #change angle by 60° (inwards)
            myT.right(60)
        
        #next hexagon
        x,y = myT.position()
        shift = np.round(2 * np.sin(np.pi/3) * edge_length) + myT.pensize()
        myT.penup()
        myT.setposition(x+shift,y)
        myT.pendown()        

'''Draw the board with prescribed colors for every field'''
def drawColoredBoard(tiles, hex_colors, filename):
    ws = turtle.Screen()
    myT = turtle.Turtle()
    
    #windows size
    ws.setup(800,1000)
    
    #Less frequent screen updates and faster creation
    ws.tracer(2, 0)
    myT.speed(0)
    
    #thicken lines
    myT.pensize(2)
    
    #shifts to calculate row starting positions from previous row
    x_shift = np.round(np.sin(np.pi/3) * edge_length)
    y_shift = np.round(edge_length + np.cos(np.pi/3) * edge_length)

    #starting reference position
    row_x = -200
    row_y = 400
    
    #upper half and central row of the board
    for i in range(0,tiles):
        #new row start position
        row_y -= y_shift + myT.pensize() / 2
        row_x -= x_shift + myT.pensize() / 2
        
        #hexagons in this row
        num_hex = tiles + i
        
        drawColoredRow(myT, row_x, row_y, num_hex, hex_colors, i)
    
    #lower half of the board
    for i in range(0,tiles-1):
        #new row start position
        row_y -= y_shift + myT.pensize() / 2
        row_x += x_shift + myT.pensize() / 2
        
        #hexagons in this row
        num_hex = 2 * tiles - 2 - i
        
        drawColoredRow(myT, row_x, row_y, num_hex, hex_colors, tiles+i)
    

    myT.hideturtle()
    
    #save drawing as file
    ws.getcanvas().postscript(file=filename+'.eps')
    
    #close window
    #turtle.bye()
    
    return myT


'''Draws a row of the board with optional numbers'''
def drawNumberedRow(myT, start_x, start_y, num_hexagons, numbering):
    #starting position
    myT.penup()
    myT.setposition(start_x,start_y)
    myT.pendown()
    
    for i in range(0,num_hexagons):
        myT.setheading(90)
        for j in range(6):
            #draw edge
            myT.forward(edge_length)
            #change angle by 60° (inwards)
            myT.right(60)
        
        #next hexagon
        x,y = myT.position()
        shift = np.round(2 * np.sin(np.pi/3) * edge_length) #+ myT.pensize()/2
        myT.penup()
        
        if i in numbering:
            myT.setposition(x + shift/2 - 3, y + edge_length/2 - 8)
            myT.write(str(numbering[i]))
        
        myT.setposition(x+shift,y)
        myT.pendown()        

'''Draws the board with optional numbers on fields'''
def drawNumberedBoard(tiles, numbering, filename):
    ws = turtle.Screen()
    myT = turtle.Turtle()
    turtle.TurtleScreen._RUNNING=True
    #windows size
    ws.setup(800,1000)
    
    #Less frequent screen updates and faster creation
    ws.tracer(2, 0)
    myT.speed(0)
    
    #thicken lines
    myT.pensize(2)
    
    #shifts to calculate row starting positions from previous row
    x_shift = np.round(np.sin(np.pi/3) * edge_length)
    y_shift = np.round(edge_length + np.cos(np.pi/3) * edge_length)

    #starting reference position
    row_x = -200
    row_y = 400
    
    #upper half and central row of the board
    for i in range(0,tiles):
        #new row start position
        row_y -= y_shift #+ myT.pensize() / 2
        row_x -= x_shift #+ myT.pensize() / 2
        
        #hexagons in this row
        num_hex = tiles + i
        
        numb = {}
        for t in numbering.keys():
            k,l = numbering[t]
            if k == i:
                numb[l] = t
        
        drawNumberedRow(myT, row_x, row_y, num_hex, numb)
    
    #lower half of the board
    for i in range(0,tiles-1):
        #new row start position
        row_y -= y_shift #+ myT.pensize() / 2
        row_x += x_shift #+ myT.pensize() / 2
        
        #hexagons in this row
        num_hex = 2 * tiles - 2 - i
        
        numb = {}
        for t in numbering.keys():
            k,l = numbering[t]
            if k - tiles == i:
                numb[l] = t
        
        drawNumberedRow(myT, row_x, row_y, num_hex, numb)
    

    myT.hideturtle()

    #save drawing as file
    ws.getcanvas().postscript(file=filename+'.eps')
    
    #close window
    #turtle.bye()
    
    myT.clear()
    
    return myT







#drawNumberedBoard(3, {}, 'board')