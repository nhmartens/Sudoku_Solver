import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np
import os
import sudokuSolver



def printSolution(img, unsolved, solved, file_name, color_solved = (84,153,2)):
    width = int(img.shape[1]/9)
    height = int(img.shape[0]/9)
    for row_index, row in enumerate(unsolved):
        for col_index, digit in enumerate(row):
            if digit == 0:
                cv2.putText(img, str(solved[row_index][col_index]),
                            (col_index * width + int(width/2) - 42, int((row_index+0.75)*height)),cv2.FONT_HERSHEY_SIMPLEX, 5, color_solved, 6, cv2.LINE_AA)
    cv2.imwrite(f"./Solutions_Sudokus/solution_{os.path.basename(file_name)}", img)


def solveImage(image_path):
    cell_size = 200
    num_cells = 9
    
    # Read image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equalized_image = cv2.equalizeHist(gray)
    mask = np.zeros((gray.shape), np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))

    close = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    div = np.float32(gray) / (close)

    res = np.uint8(cv2.normalize(div, div, 0, 255, cv2.NORM_MINMAX))
    res2 = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)

    # Finding square
    thresh = cv2.adaptiveThreshold(res, 255, 0, 1, 19, 2)
    contour, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    best_cnt = None
    for cnt in contour:
        area = cv2.contourArea(cnt)
        if area > 1000:
            if area > max_area:
                max_area = area
                best_cnt = cnt
    cv2.drawContours(mask, [best_cnt], 0, 255, -1)
    cv2.drawContours(mask, [best_cnt], 0, 0, 2)

    # Find vertical lines
    kernelx = cv2.getStructuringElement(cv2.MORPH_RECT,(2,10))

    dx = cv2.Sobel(equalized_image,cv2.CV_16S,1,0)
    dx = cv2.convertScaleAbs(dx)
    cv2.normalize(dx,dx,0,255,cv2.NORM_MINMAX)
    ret,close = cv2.threshold(dx,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    close = cv2.morphologyEx(close,cv2.MORPH_DILATE,kernelx,iterations = 1)

    contour, hier = cv2.findContours(close,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contour:
        x,y,w,h = cv2.boundingRect(cnt)
        if h/w > 5:
            cv2.drawContours(close,[cnt],0,255,-1)
        else:
            cv2.drawContours(close,[cnt],0,0,-1)
    close = cv2.morphologyEx(close,cv2.MORPH_CLOSE,None,iterations = 2)
    closex = cv2.bitwise_and(close, mask)

    # Finding horizontal lines
    kernely = cv2.getStructuringElement(cv2.MORPH_RECT,(10,2))
    dy = cv2.Sobel(equalized_image,cv2.CV_16S,0,2)
    dy = cv2.convertScaleAbs(dy)
    cv2.normalize(dy,dy,0,255,cv2.NORM_MINMAX)
    ret,close = cv2.threshold(dy,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    close = cv2.morphologyEx(close,cv2.MORPH_DILATE,kernely)

    contour, hier = cv2.findContours(close,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contour:
        x,y,w,h = cv2.boundingRect(cnt)
        if w/h > 5:
            cv2.drawContours(close,[cnt],0,255,-1)
        else:
            cv2.drawContours(close,[cnt],0,0,-1)

    close = cv2.morphologyEx(close,cv2.MORPH_DILATE,None,iterations = 2)
    closey = cv2.bitwise_and(close, mask)

    corner_mask = np.zeros_like(mask, dtype=np.uint8)
    top_left = np.min(np.argwhere(mask), axis=0)
    bottom_right = np.max(np.argwhere(mask), axis=0)
    corner_mask[top_left[0]:top_left[0]+2, top_left[1]:top_left[1]+2] = 255
    corner_mask[top_left[0]:top_left[0]+2, bottom_right[1]-2:bottom_right[1]] = 255
    corner_mask[bottom_right[0]-2:bottom_right[1], top_left[0]:top_left[1]+2] = 255
    corner_mask[bottom_right[0]-2:bottom_right[1], bottom_right[1]-2:bottom_right[1]] = 255

    # Finding grid points
    res = cv2.bitwise_and(closex,closey)
    res = cv2.bitwise_or(res, corner_mask)

    # Correcting defects
    contour, hier = cv2.findContours(res,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    centroids = []
    for cnt in contour:
        mom = cv2.moments(cnt)
        if mom['m00']:
            (x,y) = int(mom['m10']/mom['m00']), int(mom['m01']/mom['m00'])
        else:
            (x,y) = int(mom['m10']), int(mom['m01'])
        cv2.circle(img,(x,y),4,(0,255,0),-1)
        centroids.append((x,y))
    centroids = np.array(centroids,dtype = np.float32)
    c = centroids.reshape((100,2))
    c2 = c[np.argsort(c[:,1])]

    b = np.vstack([c2[i*10:(i+1)*10][np.argsort(c2[i*10:(i+1)*10,0])] for i in range(10)])
    bm = b.reshape((10,10,2))

    output = np.zeros((cell_size * num_cells, cell_size * num_cells,3),np.uint8)
    for i,j in enumerate(b):
        ri = int(i/10)
        ci = i%10
        if ci != 9 and ri!=9:
            src = bm[ri:ri+2, ci:ci+2 , :].reshape((4,2))
            dst = np.array( [ [ci*cell_size,ri*cell_size],[(ci+1)*cell_size-1,ri*cell_size],[ci*cell_size,(ri+1)*cell_size-1],[(ci+1)*cell_size-1,(ri+1)*cell_size-1] ], np.float32)
            retval = cv2.getPerspectiveTransform(src,dst)
            warp = cv2.warpPerspective(res2,retval,(cell_size * num_cells, cell_size * num_cells))
            output[ri*cell_size:(ri+1)*cell_size-1 , ci*cell_size:(ci+1)*cell_size-1] = warp[ri*cell_size:(ri+1)*cell_size-1 , ci*cell_size:(ci+1)*cell_size-1].copy()

    output = cv2.GaussianBlur(output, (5, 5), 0)

    #Text detector
    reader = easyocr.Reader(["en"], gpu = True)

    # Cell boundaries
    coordinates = [(x, y, x + cell_size, y + cell_size) for x in range(0, cell_size * num_cells, cell_size) for y in range(0, cell_size * num_cells, cell_size)]
    matrix = [[0] * num_cells for _ in range(num_cells)]

    for (startX, startY, endX, endY) in coordinates:
        # Extract the region of interest (ROI)
        roi = output[startY:endY, startX:endX]

        # Apply OCR to the ROI
        results = reader.readtext(roi, beamWidth=10)
        
        row = int(startY/cell_size)
        column = int(startX/cell_size)

        # Process OCR results
        if results:
            for a in results:
                matrix[int(startY/cell_size)][int(startX/cell_size)] = int(a[1])
    
    print("Detected Sudoku from Image:")
    for row in matrix:  
        print(row)
    print("")

    solution = sudokuSolver.sudokuSolver(matrix)

    if solution != None:
        printSolution(output, matrix, solution, image_path)

if __name__ == "__main__":
    solveImage("./Unsolved_Sudokus/sudoku_3.png")