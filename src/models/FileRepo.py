import csv


class FileRepo:
    """Enregistre les mesures de pointage au format CSV (séparateur point-virgule)."""

    def __init__(self, nb_file=0):
        self.__nb_file = nb_file

    def default_filename(self):
        return "repo" + str(self.__nb_file) + ".csv"

    def ecrire(self, liste_frame, liste_points, filename=None):
        """Format brut d'origine : numéro d'image et coordonnées en pixels."""
        filename = filename or self.default_filename()
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(("Frame", "x Coordinates", "y Coordinates"))
            for frame, (x, y) in zip(liste_frame, liste_points):
                writer.writerow((frame, x, y))
        return filename

    def ecrire_mesures(self, filename, mesures, unite="m"):
        """Mesures dans le repère : temps (s), position x et position y.

        ``mesures`` est une liste de tuples (t, x, y).
        """
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(("t (s)", f"x ({unite})", f"y ({unite})"))
            for t, x, y in mesures:
                writer.writerow((f"{t:.4f}", f"{x:.4f}", f"{y:.4f}"))
        return filename
