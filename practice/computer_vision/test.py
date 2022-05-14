import cv2
path_data = "/home/magody/programming/python/data_science/data/images_opencv"
# LOAD AN IMAGE USING 'IMREAD'
img = cv2.imread(f"{path_data}/lena.png")
# DISPLAY
cv2.imshow("Lena Soderberg",img)
cv2.waitKey(0)