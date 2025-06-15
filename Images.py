import os


class GestionnaireImages:
    def __init__(self, dossier_images):
        self.dossier = dossier_images
        self.images = {}
        self.charger_images()

    def charger_images(self):
        for nom_fichier in os.listdir(self.dossier):
            if nom_fichier.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                nom_sans_ext = os.path.splitext(nom_fichier)[0]
                chemin_complet = os.path.join(self.dossier, nom_fichier)
                self.images[nom_sans_ext] = chemin_complet

    def get_image(self, nom):
        return self.images.get(nom)
