import cv2
import face_recognition
from sys import argv

#подгружаем входное фото 
input_photo = face_recognition.load_image_file(argv[1])

#наша БД
known_faces = []
image = face_recognition.load_image_file("2020-06-30-150640.jpg")
face_encoding = face_recognition.face_encodings(image)[0] 
known_faces.append(face_encoding)
#image = face_recognition.load_image_file("mom.jpg")
#face_encoding = face_recognition.face_encodings(image)[0]
#known_faces.append(face_encoding)
known_names = ["Gennadii", "Irina"]



face_locations = []
face_encodings = []
frame_number = 0
 	
# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	
rgb_frame = input_photo[:, :, ::-1]
 
# Find all the faces and face encodings in the current frame of video
	
face_locations = face_recognition.face_locations(rgb_frame, model="cnn")
face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
face_names = []
	
for face_encoding in face_encodings:
    	
    # See if the face is a match for the known face(s)
    #токо нам нужно понять теперь с каким именно совпало
	a = 0
	for base_face in known_faces:
		match = face_recognition.compare_faces([base_face], face_encoding, tolerance=0.7)	
		name = None
		if match[0]:
            # нэйм из  known_names который совпал 	
			name = known_names[a]
			print("OKK")
			face_names.append(name)
			break
		else:
 			print("not in base")

		a = a + 1
#печатаем че нашли
for name in face_names:
	print(name)