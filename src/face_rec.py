'''This is back-end file that's deals with BDs and picure analizing'''

import pickle
import cv2
import face_recognition


BD = [] #тут из файла BD.sm
PRIVATE_BDS = {} #словарь приватных бд

def bd_init():
    '''Initialize BDs at the start of the bot'''

    with open("PrivateBD.sm", "rb") as faces_bd:
        try:
            global PRIVATE_BDS
            PRIVATE_BDS = pickle.load(faces_bd)
        except EOFError:
            pass

    with open("BD.sm", "rb") as faces_bd:
        while True:    
            try:
                face = pickle.load(faces_bd)
                name = pickle.load(faces_bd)
            except EOFError:
                break
            BD.append((face, name))

def private_bd_add(person_id, image, name):
    '''Function to add a person to private lib of a user'''

    input_photo = face_recognition.load_image_file(image)
    if len(face_recognition.face_encodings(input_photo)) == 0:
        return False
    face_encoding = face_recognition.face_encodings(input_photo)[0]
    if not PRIVATE_BDS.get(person_id, False):
        PRIVATE_BDS[person_id] = []
    PRIVATE_BDS[person_id].append((face_encoding, name))
    with open("PrivateBD.sm", "wb") as faces_bd:
        pickle.dump(PRIVATE_BDS, faces_bd)
    return True

def del_names_from_list(person_id, name):
    '''Support function for private_bd_del'''

    res = False
    out = []
    for pair in PRIVATE_BDS[person_id]:
        if name == pair[1]:
            res = True
        else:
            out.append(pair)
    PRIVATE_BDS[person_id] = out
    return res


def private_bd_del(person_id, name):
    '''Function to del a person from private lib of a user'''

    if not PRIVATE_BDS.get(person_id, False):
        return False
    if not del_names_from_list(person_id, name):
        return False

    #переписываем бд
    with open("PrivateBD.sm", "wb") as faces_bd:
        pickle.dump(PRIVATE_BDS, faces_bd)

    return True


def public_bd_add(image, name):
    '''Function to add a person to public lib'''

    input_photo = face_recognition.load_image_file(image)
    if len(face_recognition.face_encodings(input_photo)) == 0:
        return False
    face_encoding = face_recognition.face_encodings(input_photo)[0]
    BD.append((face_encoding, name))

    #Сохраняем каждый раз в файл BD.sm обновки BD
    with open("BD.sm", "ab") as faces_bd:
        pickle.dump(face_encoding, faces_bd)
        pickle.dump(name, faces_bd)

    return True

def x(input_number):
    '''support instred of a lambda'''
    return input_number * 10

def draw_name(frame, face_location, name):
    '''Adds a name tag to the picture'''
    top, right, bottom, left = map(x, face_location)
    print(top, right, bottom, left)
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 15)
    cv2.rectangle(frame, (left, bottom + int((right - left) / 10)), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, name, (left + 4, bottom + int((right - left) / 10) - 3), font, max(3, int((right - left) / 210)), (255, 255, 255), 5)


def find_faces(inputImage, person_id):
    '''Finds faces at the picture and searchs lib for known persons'''

    frame = cv2.imread(inputImage)
    frame = cv2.resize(frame, (0,0), fx=10, fy=10) 

    #общая плюс приватная

    input_photo = face_recognition.load_image_file(inputImage)
    face_locations = face_recognition.face_locations(input_photo, model="cnn")
    face_encodings = face_recognition.face_encodings(input_photo, face_locations)
    face_names = []    

    for face_encode, face_location in zip(face_encodings, face_locations):
        #проход для общей
        for known_face, known_name in BD:
            match = face_recognition.compare_faces([known_face], face_encode, tolerance=0.5)
            if match[0]:
                face_names.append(known_name)
                BD.append((face_encode, known_name))
                draw_name(frame, face_location, known_name)
                #Сохраняем каждый раз в файл BD.sm обновки BD
                with open ("BD.sm", "ab") as faces_bd:
                    pickle.dump(face_encode, faces_bd)
                    pickle.dump(known_name, faces_bd)
                break

        #проход для частной
        #если нет такого номера в словаре - закругляемся
        if PRIVATE_BDS.get(person_id, False):
            for known_face, known_name in PRIVATE_BDS[person_id]:
                match = face_recognition.compare_faces([known_face], face_encode, tolerance=0.5)
                if match[0]:
                    if not known_name in face_names:
                        face_names.append(known_name)
                        draw_name(frame, face_location, known_name)
                        PRIVATE_BDS[person_id].append((face_encode, known_name))
                        with open ("PrivateBD.sm", "wb") as faces_bd:
                            pickle.dump(PRIVATE_BDS, faces_bd)
                        break
    frame = cv2.resize(frame, (0,0), fx=0.3, fy=0.3) 
    cv2.imwrite('out.png', frame)
    return face_names
