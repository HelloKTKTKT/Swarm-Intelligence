import numpy as np
import random
import cv2
import sys

def ReadWritePicture():

    img = cv2.imread('lena.jpg', 0)
    # 1 = cv2.IMREAD_COLOR, 0 = cv2.IMREAD_GRAYSCALE, -1 = cv2.IMREAD_UNCHANGED
    # this will return a matrix

    cv2.imshow('MyWindow', img)
    # cv2.imshow('Window name', image_matrix)

    cv2.waitKey(5000)
    # cv2.waitkey(ms), hold the window for x ms. If x=0, the window will hold forever
    # If user presses any key within the delay time, it will return the ASCII of that key. If not, it will return -1
    # PS: ASCII('Esc') = 27

    cv2.destroyAllWindows()
    # close all windows

    cv2.imwrite('lena_copy.png', img)
    # write the image from matrix to a file

def Video_Capture():

    cap = cv2.VideoCapture(0)
    # open the default camera on laptop, or give a file name cv2.VideoCapture('Video_file_Name')

    while True:
        ret, frame = cap.read()


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # convert the frame (frame) to frame (gray)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def Create_Video():

    cap = cv2.VideoCapture(0)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # fourcc is a video data stream format

    out = cv2.VideoWriter('output.avi', fourcc, 60.0, (640, 480))
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            out.write(frame)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def Draw_geo_shape():

    img = cv2.imread('lena.jpg', 1)
    img = cv2.line(img, (0, 0), (255, 255), (0, 0, 255), 2)
    # img_matrix, start_point, end_point, color(blue, green, red), thickness(min 1,
    # -1 will be filled with the specified color)

    img = cv2.rectangle(img, (0, 0), (255, 255), (0, 255, 0), 2)

    img = cv2.circle(img, (255, 255), 60, (0, 255, 255), -1)
    # circle(img, center, radius, color, thickness)

    font = cv2.FONT_HERSHEY_SIMPLEX
    img = cv2.putText(img, 'OpenCV', (10, 500), font, 4, (255, 255, 255), 4, cv2.LINE_AA)
    # PutText(img, name, start_point, font_type, font_size, color, thickness, ???)

    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def Create_img_numpy_zero():

    img = np.zeros([512, 512, 3], np.uint8)
    # Create a black image. If all the elements are 255, it will be a white image
    # [512, 512, 3], 3 means 3 channels: Red, Green, Blue

def Show_real_time_info():

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = 'Width: ' + str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) + ' Height: ' + \
                   str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame = cv2.putText(frame, text, (10, 50), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()

def Mouse_click_event_1(event, x, y, flags, param):
# Click on the window, and show the x,y coordinates on this window

    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, ', ', y)
        font = cv2.FONT_HERSHEY_SIMPLEX
        strXY = str(x) + ', ' + str(y)
        cv2.putText(img, strXY, (x, y), font, 1, (255, 255, 0), 2)
        cv2.imshow('image', img)

# img = np.zeros((512, 512, 3), np.uint8)
# cv2.imshow('image', img)
# cv2.setMouseCallback('image', Mouse_click) #pass the addr of Mouse_click Fucn to this Function.
# cv2.waitKey(0)
# cv2.destroyAllWindows()

def Mouse_click_event_2(event, x, y, flags, param):
# Click on the window, and draw a line between last two clicks

    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)
        cv2.imshow('image', img)
        points.append((x, y))
        if len(points) >= 2:
            cv2.line(img, points[-1], points[-2], (255, 0, 0), 3)
        cv2.imshow('image', img)

# img = np.zeros((512, 512, 3), np.uint8)
# cv2.imshow('image', img)
# points = []
# cv2.setMouseCallback('image', Mouse_click_event_2)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

def Mouse_click_event_3(event, x, y, flags, param):
# Click on the window, and show the color on another window
    if event == cv2.EVENT_LBUTTONDOWN:
        blue = img[x, y, 0]
        green = img[x, y, 1]
        red = img[x, y, 2]
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)
        my_img = np.zeros((512, 512, 3), np.uint8)
        my_img[:] = [blue, green, red]
        cv2.imshow('color', my_img)
# img = cv2.imread('lena.jpg')
# cv2.imshow('image', img)
# cv2.setMouseCallback('image', Mouse_click_event_3)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

def Image_operation():
    img = cv2.imread('lena.jpg')
    print(img.shape)
    print(img.size) # total number of pixels
    b, g, r = cv2.split(img) #split the image into 3 channels
    img = cv2.merge((b,g,r)) #merge 3 channels into the image

def ROI():
# Copy one region to another place
    img = cv2.imread('lena.jpg')
    copy_ROI = img[280:340, 330:390]
    img[10:70, 70:130] = copy_ROI
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def Mytest1():
    img = cv2.imread('lena.jpg')
    print(img[0,0,:])
    # Each img can be viewed as 3D matrix. A 2D coordinate with 2 1*3 array (b,g,r)


def Mytest3():
    dim_x = 1500
    dim_y = 1500
    cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    Map1 = np.zeros((dim_y, dim_x, 3), np.uint8)
    Map2 = np.zeros((dim_y, dim_x, 3), np.uint8)
    cv2.rectangle(Map1, (0, 0), (dim_x + 1, dim_y + 1), (255, 255, 255), -1)
    cv2.rectangle(Map2, (0, 0), (dim_x + 1, dim_y + 1), (255, 255, 255), -1)
    cv2.rectangle(Map1, (800, 800), (1000, 1000), (100, 100, 100), -1)
    cv2.rectangle(Map2, (800, 800), (1000, 1000), (100, 100, 100), -1)
    iteration = 0
    while iteration < 100:
        cv2.circle(Map1, (iteration, 100), 1, (100, 100, 100), -1)
        iteration += 1
        cv2.imshow('test', Map1)
        cv2.waitKey(5)
        Map1[:] = Map2[:]
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def color_test():
    dim_x = 1200
    dim_y = 1200
    cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    map1 = np.zeros((dim_y, dim_x, 3), np.uint8)
    cv2.rectangle(map1, (0, 0), (dim_x + 1, dim_y + 1), (255, 255, 255), -1)
    for i in range(1, 11):
        for j in range(1, 11):
            cv2.circle(map1, (i * 100, j * 100), 20, (i * 25, j * 25, 30), -1)

    cv2.imshow('test', map1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
