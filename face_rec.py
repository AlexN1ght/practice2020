import cv2
import face_recognition
import pickle

BD = [] #тут из файла BD.sm
private_bds = {} #словарь приватных бд

def bd_init():
    #добавить инициализацию приватной БД
    with open("PrivateBD.sm", "rb") as FacesBD:
        try:
            private_bds = pickle.load(FacesBD)
        except EOFError:
            pass

    with open("BD.sm", "rb") as FacesBD:
        while True:    
            try:
                face = pickle.load(FacesBD)
                name = pickle.load(FacesBD)
            except EOFError:
                break
            BD.append((face, name))

def private_bd_add(id, image, name):

    input_photo = face_recognition.load_image_file(image)
    if len(face_recognition.face_encodings(input_photo)) == 0:
        return False
    face_encoding = face_recognition.face_encodings(input_photo)[0]
    if not private_bds.get(id, False):
        private_bds[id] = [] 
    private_bds[id].append((face_encoding, name))

    with open ("PrivateBD.sm", "wb") as FacesBD:
        pickle.dump(private_bds, FacesBD)
    
    return True

def private_bd_del(id, name):
    if not private_bds.get(id, False):
        return False
    try:
        private_bds[id].remove((face,name))
    except ValueError:
        return False

    #переписываем бд
    with open ("PrivateBD.sm", "wb") as FacesBD:
        pickle.dump(private_bds, FacesBD)
    
    return True


def public_bd_add(image, name):

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

def find_faces(inputImage, id):
    #общая плюс приватная

    input_photo = face_recognition.load_image_file(inputImage)
    face_locations = face_recognition.face_locations(input_photo, model="cnn")
    face_encodings = face_recognition.face_encodings(input_photo, face_locations)
    face_names = []    

    for face_encode in face_encodings:
        #проход для общей
        for knownFace, knownName in BD:
            match = face_recognition.compare_faces([knownFace], face_encode, tolerance=0.5)
            if match[0]:
                face_names.append(knownName)
                break

        #проход для частной
        #если нет такого номера в словаре - закругляемся
        if not private_bds.get(id, False):
            return face_names

        for knownFace, knownName in private_bds[id]:
            match = face_recognition.compare_faces([knownFace], face_encode, tolerance=0.5)
            if match[0]:
                if not knownName in face_names:
                    face_names.append(knownName)
                    break

    return face_names