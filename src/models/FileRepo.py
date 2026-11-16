import csv
class FileRepo:
    def __init__(self, nb_file=0):
        self.__nb_file = nb_file
    
    def ecrire(self, liste_frame, liste_points):
        filename = "repo" + str(self.__nb_file) + ".csv"
        with open(filename, "w+", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            head = ("Frame", "x Coordinates", "y Coordinates")
            writer.writerow(head)
            
            for y in range(len(liste_frame)):
                data = (liste_frame[y], liste_points[y][0], liste_points[y][1])
                writer.writerow(data)
        
        print("Data Saved Successfully in", filename)