import cv2
import face_recognition
import pickle

BD = [] #тут из файла BD.sm

with open("BD.sm", "rb") as file:
    while True:    
        try:
            face = pickle.load(file)
            name = pickle.load(file)
        except EOFError:
            break

        BD.append((face, name))


def BDAdd(image, name):

    face_encoding = face_recognition.face_encodings(image)[0]
    BD.append((face_encoding, name))

    #Сохраняем каждый раз в файл BD.sm обновки BD
    with open ("BD.sm", "wb") as file:
        for face, name in BD:
            pickle.dump(face, file)
            pickle.dump(name, file)
    
    return True

def FindFaces(inputImage):
#на вход картинку?????

    face_locations = face_recognition.face_locations(inputImage, model="cnn")
    face_encodings = face_recognition.face_encodings(inputImage, face_locations)
    face_names = []    

    for face_encode in face_encodings:
        count = 0
        for knownFace, knownName in BD:
            match = face_recognition.compare_faces([knownFace], face_encode, tolerance=0.5)
            if match[0]:
                face_names.append(knownName)
                break

    return face_names
