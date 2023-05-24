import os
import numpy as np
import cv2
import string
import random 
string.ascii_letters
def datetostr(x):
    if len(x) < 2:
        x = '0' + x
    return x

def random_id():
    letters = string.ascii_letters
    num = string.digits
    a = ''.join(random.choice(letters) for i in range(2))
    b = ''.join(random.choice(num) for i in range(2))
    sheet_id = b + a
    return sheet_id

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

main_path = '/home/reyhane/Desktop/oxin_file_manager/HDD'

for year in np.random.randint(2012, 2023, 2):
    year = str(year)
    mkdir(os.path.join(main_path,year))

    for mounth in np.random.randint(1,12, 3):
        mounth = str(mounth)
        mounth = datetostr(mounth)
        mkdir(os.path.join(main_path,year, mounth))

        for day in np.random.randint(1,30,4):
            day = str(day)
            day = datetostr(day)
            

            mkdir(os.path.join(main_path,year, mounth, day))

            for sheet in range(1, np.random.randint(8)):
                sheet_id = random_id()
                mkdir(os.path.join(main_path,year, mounth, day, sheet_id))
                image_num = np.random.randint(1, 9)
                
                for side in ["TOP", "BOTTOM"]:
                    mkdir(os.path.join(main_path,year, mounth, day, sheet_id, side))
                    for cam in range(1, np.random.randint(5,12)):
                        cam = str(cam)

                        mkdir(os.path.join(main_path,year, mounth, day, sheet_id, side, cam))

                        for i in range(1, image_num):
                            
                            file_path = os.path.join(main_path,year, mounth, day, sheet_id, side, cam, str(i)+'.png')
                            img = np.random.randint(0,255, 1920*1200)
                            img = img.reshape((1200,1920))
                            print(img.shape)
                            cv2.imwrite(file_path, img)




