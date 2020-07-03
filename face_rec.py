import cv2
import face_recognition
import pickle

BD = [] #тут из файла BD.sm

def BDInit():
    with open("BD.sm", "rb") as FacesBD:
        while True:    
            try:
                face = pickle.load(FacesBD)
                name = pickle.load(FacesBD)
            except EOFError:
                break
            BD.append((face, name))

def BDAdd(image, name):

    input_photo = face_recognition.load_image_file(image)
    if len(face_recognition.face_encodings(input_photo)) == 0:
        return False
    face_encoding = face_recognition.face_encodings(input_photo)[0]
    BD.append((face_encoding, name))

    #Сохраняем каждый раз в файл BD.sm обновки BD
    with open ("BD.sm", "ab") as FacesBD:
        pickle.dump(face_encoding, FacesBD)
        pickle.dump(name, FacesBD)
    
    return True

def FindFaces(inputImage):

    input_photo = face_recognition.load_image_file(inputImage)
    face_locations = face_recognition.face_locations(input_photo, model="cnn")
    face_encodings = face_recognition.face_encodings(input_photo, face_locations)
    face_names = []    

    for face_encode in face_encodings:
        for knownFace, knownName in BD:
            match = face_recognition.compare_faces([knownFace], face_encode, tolerance=0.5)
            if match[0]:
                face_names.append(knownName)
                break

    return face_names
