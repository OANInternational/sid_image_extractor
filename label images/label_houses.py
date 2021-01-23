import cv2
import numpy as np
import sqlite3
import pandas as pd
import os

# Create a function based on a CV2 Event (Left button click)
drawing = False # True if mouse is pressed
points = []
all_points_metal = []
all_points_round = []
all_points = []
mouse = [0,0]
mouse_in = [0,0]
show='all'

# mouse callback function
def save_xy(event,x,y,flags,param):
    global points,drawing,mode,mouse,mouse_in
    mouse = [x+mouse_in[0],y+mouse_in[1]]
    #elif event == cv2.EVENT_LBUTTONUP:
    if event == cv2.EVENT_LBUTTONDOWN:
        # When you click DOWN with left mouse button drawing is set to True
        drawing = True
        # Then we take note of where that mouse was located
        points = points + [[x+mouse_in[0],y+mouse_in[1]]]
        
print("select file to work")
images = [f for f in os.listdir() if 'png' in f]
for im in images:
    print(im)
    y_n = input("es esta [y] o [n]")
    if y_n == 'y':
        file = im
        break 
vil = file.split('_')[0]
# Create a black image
img = cv2.imread(file)

y_n = input("upload results [y] o [n]?")
if y_n == 'y':
    file = im
    conn = sqlite3.connect("casas.sqlite")
    df = pd.read_sql('SELECT * FROM `{}`'.format(vil),conn)
    df['houses'] = df['houses'].apply(eval)
    houses = df.T.to_dict()
    for i in houses:
        row = houses[i]
        house = row['houses']
        ttype = row['type']
        all_points = all_points + [house]
        if ttype == 'metal':
            all_points_metal = all_points_metal + [house]
            vertices = np.array(house,dtype=np.int32)
            pts = vertices.reshape((-1,1,2))
            cv2.polylines(img,[pts],isClosed=True,color=(255,0,0),thickness=5)
        if ttype == 'round':
            all_points_round = all_points_round + [house]
            vertices = np.array(house,dtype=np.int32)
            pts = vertices.reshape((-1,1,2))
            cv2.polylines(img,[pts],isClosed=True,color=(0,255,0),thickness=5)

# This names the window so we can reference it 
cv2.namedWindow('my_drawing',cv2.WINDOW_NORMAL)
# Connects the mouse button to our callback function
cv2.setMouseCallback('my_drawing',save_xy)

while True: #Runs forever until we break with Esc key on keyboard
    
    if show=='all':
        # Shows the image window
        cv2.imshow('my_drawing',img)
        
    elif show == 'in':
        cv2.imshow("my_drawing", img[mouse_in[1]:mouse_in[1]+300,mouse_in[0]:mouse_in[0]+300]) 
        
    # EXPLANATION FOR THIS LINE OF CODE:
    # https://stackoverflow.com/questions/35372700/whats-0xff-for-in-cv2-waitkey1/39201163
        
    # CHECK TO SEE IF ESC WAS PRESSED ON KEYBOARD
    k = cv2.waitKey(1) & 0xFF
    if k == ord('m'):
        img_1 = img.copy()
        drawing = False
        vertices = np.array(points,dtype=np.int32)
        pts = vertices.reshape((-1,1,2))
        cv2.polylines(img,[pts],isClosed=True,color=(255,0,0),thickness=5)
        all_points_metal = all_points_metal +[points]
        all_points = all_points +[points]
        print('house {}: {}'.format(len(all_points),points))
        points = []
    if k == ord('r'):
        img_1 = img.copy()
        drawing = False
        vertices = np.array(points,dtype=np.int32)
        pts = vertices.reshape((-1,1,2))
        cv2.polylines(img,[pts],isClosed=True,color=(0,255,0),thickness=5)
        all_points_round = all_points_round +[points]
        all_points = all_points +[points]
        print('house {}: {}'.format(len(all_points),points))
        points = []
        
    elif k == ord('i'):
        show='in'
        mouse_in=[mouse[0]-100,mouse[1]-100]
    elif k == ord('o'):
        show='all'
        mouse_in=[0,0]
    elif k == ord('b'):
        points = []
    elif k == ord('d'):
        print('want to delete metal house')
        y_n = input('[y_n]')
        if y_n == 'y':
            all_points_metal = all_points_metal[:-1]
            all_points = all_points[:-1]
            img = img_1.copy()
            
        print('want to delete round house')
        y_n = input('[y_n]')
        if y_n == 'y':
            img = img_1.copy()
            all_points_round = all_points_round[:-1]
            all_points = all_points[:-1]
        
        
    elif k == 27:
        break
# Once script is done, its usually good practice to call this line
# It closes all windows (just in case you have multiple windows called)
cv2.destroyAllWindows()

y_n = input("¿save results? [y] o [n]")
if y_n == 'y':
    
    df = pd.DataFrame()
    df[['houses','type']]=[pd.Series([str(d),'metal']) for d in all_points_metal
                          ]+[pd.Series([str(d),'round']) for d in all_points_round]
    df['village']=vil
    df['size']=file.split('_')[1].split('.')[0]
    conn = sqlite3.connect("casas.sqlite")
    conn.execute('DROP TABLE IF EXISTS `'+vil+'`')
    df.to_sql(vil,conn)
    print('saved sqlite table {}'.format(file.split('_')[0]))
print('end')