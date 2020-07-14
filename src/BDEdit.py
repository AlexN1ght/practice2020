import pickle

BD = []

with open("BD.sm", "rb") as FacesBD:
    while True:  
        try:
            face_to_bd = pickle.load(FacesBD)
            name_to_bd = pickle.load(FacesBD)
        except EOFError:
            break
        BD.append((face_to_bd, name_to_bd))


def list_bd():
    num = 0
    for _face_encod, name_to_print in BD:
        print(num, name_to_print)
        num += 1

list_bd()

while True:
    print("Enter del to delete or q to quit")
    command = input()
    if command == "del":
        print("Enter start number to delete")
        num_to_del_start = int(input())
        print("Enter end number to delete")
        num_to_del_end = int(input())
        for i in range(num_to_del_end - num_to_del_start + 1):
            BD.pop(num_to_del_start)
        with open ("BD.sm", "wb") as FacesBD:
            for face_encoding, name in BD:
                pickle.dump(face_encoding, FacesBD)
                pickle.dump(name, FacesBD)
        print("Done\n")
        list_bd()
    if command == "q":
        break