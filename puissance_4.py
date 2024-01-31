""" Petit jeu du puissance 4 a jouer contre l'ordinateur.
"""

# By Piétôt
# Discord : Piétôt#1754
# Start : ~ 01/05/2023
# Time : ~ 1 semaine


import os
import random
import numpy as np
import numpy.typing as npt


class Puissance4:
    """ Object d'un puissance 4. Il aura la forme d'une matrice à 2 dimension de forme 6*7 comme le
        puissance 4. Dans la matrice 0 équivaut à un emplacement vide, 1 aux jetons du joueur 1 et
        2 aux jetons du joueur 2. Un gagnant est désigné quand son chiffre corrspondant est aligné
        4 fois de suite en largeur, en longueur, ou en diagonale.
    """

    def __init__(self) -> None:
        ligne, colonnne = 6, 7
        self.grille = np.zeros((ligne, colonnne), dtype=np.int8)

    def update(self, colonne_index: int, numero_joueur: int) -> tuple[int, int]:
        """ Met à jour la matrice du puissance 4.

        Args:
            colonne_index (int): L'index de la colonne où un joeur veut mettre son jeton
            numero_joueur (int): Si c'est le joueur 1 ou 2

        Raises:
            IndexError: Si on ne peut pas ajouter un jeton a la colonne

        Returns:
            tuple(int, int): Un tuple avec un booléen, si puissance 4 il y a,
            et deux int avec l'index de la ligne et de la colonne où a attérit la pièce
        """
        assert 0 <= colonne_index <= 6
        assert 1 <= numero_joueur <= 2
        assert self.grille.shape == (6, 7)

        for ligne_index, ligne in enumerate(reversed(self.grille), start=-5):
            if np.any(ligne[colonne_index] == 0):  # type: ignore
                ligne[colonne_index] = numero_joueur
                return abs(ligne_index), colonne_index
        raise IndexError('La colonne est remplie')

    def gagnant(self, ligne_index: int, colonne_index: int,
                numero_joueur: int) -> bool:
        """ Vérifie si le joueur qui viens de jouer à fait un puissance 4

        Args:
            ligne_index (int): L'index de la ligne où le jeton est attérit
            colonne_index (int): L'index de la colonne où le joueur à placé son jeton
            numero_joueur (int): Si c'est le joueur 1 ou 2 qui a joué

        Returns:
            bool: Si le jouer à gagné
        """
        assert 0 <= ligne_index <= 5
        assert 0 <= colonne_index <= 6
        assert 1 <= numero_joueur <= 2

        ligne, colonne, diagonale_principale, diagonale_annexe = self.valeurs(
            ligne_index, colonne_index)

        if self.verifie_puissance_4(ligne):
            return True
        if self.verifie_puissance_4(colonne):
            return True
        if (self.verifie_puissance_4(diagonale_principale)
                or self.verifie_puissance_4(diagonale_annexe)):
            return True
        return False

    def valeurs(self, ligne_index: int,
                colonne_index: int) -> tuple[npt.NDArray[np.int8], ...]:
        """ Récupère les valeurs de la ligne, colonne et des diagonnale d'un jeton en fonction
                de sa position dans la matrice

        Args:
            ligne_index (int): L'index de la ligne du jeton
            colonne_index (int): L'index de la colonne du jeton

        Returns:
            tuple[npt.NDArray[np.int8], ...]: Un tuple de 4 tableau numpy contenant toutes 
            les valeurs de leur nom 
            """

        valeurs_ligne = self.grille[ligne_index]
        valeurs_colonne = self.grille[:, colonne_index]
        offset_diagonale_principale = colonne_index - ligne_index
        offset_diagonale_annexe = (6 - colonne_index) - ligne_index

        diagonale_principale = self.grille.diagonal(
            offset_diagonale_principale)
        diagonale_annexe = np.fliplr(self.grille).diagonal(  # type: ignore
            offset_diagonale_annexe)

        return valeurs_ligne, valeurs_colonne, diagonale_principale, diagonale_annexe

    def verifie_puissance_4(self, ligne: npt.NDArray[np.int8]) -> bool:
        """ Fonction récursive qui vérifie si 4 jeton du même joueur sont à la suite

        Args:
            ligne (npt.NDArray[np.int8]): La ligne où la jeton du joueur est attérit

        Returns:
            bool: True si la ligne est gagnante, False dans le cas contraire
        """
        # Cas de base, si la ligne à moins de 4 valeur, impossible d'avoir un puissance 4
        if len(ligne) < 4:
            return False
        # Si les 4 premières valeurs sont identique et que ce ne sont pas des 0 = puissance 4
        if len(set(ligne[:4])) == 1 and list(set(ligne[:4]))[0] != 0:
            return True
        # On recommence sans le premier élément
        return self.verifie_puissance_4(ligne[1:])


class IntelligenceArtificielle:
    """ Classe IA qui simule des décision qu'un humain pourrais prendre pour jouer en solo
    """

    def coup_a_jouer(self) -> tuple[int, int]:
        """ Trouve le meilleur en fonction de cette algoritme:
        Le bot simule chaque coup possible en mettant un jeton dans une colonne de gauche à droite.
        Ensuite il vérifie à chaque fois s'il peut faire un puissance 4. Si oui il joue ce coup,
        sinon il vérifie si son adversaire peut faire un puissance 4. Si oui, il le pare sinon il
        refait la même chose mais avec 3 jeton au lieu de 4, puis 2. S'il à trouvé aucun coup pour
        aligner 2 jetons, il choisi un coup au hasard parmis les coups restants.

        Returns:
            int | Literal[True]: int pour la colonne ou faut jouer (pour l'animation tkinter),
            True si ya un puissance 4 et qu'il faut arrêter le jeu
            """
        if np.all(jeu.grille == np.zeros((6, 7), dtype=np.int8)):
            return jeu.update(3, 1)

        colonne_index = self.cherche_puissance_4() or self.cherche_puissance_4(
            adversaire=True)

        if colonne_index is not None:
            return colonne_index

        for nb_jeton in reversed(range(2, 4)):
            colonne_index = (self.cherche_jeton_aligne(nb_jeton)
                             or self.cherche_jeton_aligne(nb_jeton, adversaire=True))
            if colonne_index is not None:
                return colonne_index

        zero_index = [index for index, valeur in enumerate(
            jeu.grille[0]) if valeur == 0]
        return jeu.update(random.choice(zero_index), 1)

    def cherche_puissance_4(self,
                            adversaire: bool = False) -> tuple[int, int] | None:
        """ Cherche si ya un puissance 4

        Args:
            adversaire (bool, optional): Si on cherche un puissance 4 pour gagner ou à parer.
            Defaults to False.

        Returns:
            tuple[int, int] | None: tuple si on a trouver un puissance 4
                                    (avec les coordonnées du jeton a placer), None si non
        """
        numero_joueur = 2 if adversaire else 1
        for colonne_index in range(7):
            try:
                ligne_index, _ = jeu.update(colonne_index, numero_joueur)
            except IndexError:
                continue

            gagnant = jeu.gagnant(ligne_index, colonne_index, numero_joueur)

            if gagnant:
                if adversaire:
                    jeu.grille[ligne_index, colonne_index] = 1
                return ligne_index, colonne_index

            jeu.grille[ligne_index, colonne_index] = 0
        return None

    def cherche_jeton_aligne(self,
                             nb_jeton_aligne: int,
                             adversaire: bool = False) -> tuple[int, int] | None:
        """ Cherche si 3 puis 2 jeton sont alignés

        Args:
            nb_jeton_aligne (int): Le nombre de jeton qu'on souhaite aligner
            adversaire (bool, optional): Si c'est le bot qui joue ou son adversaire.
            Defaults to False.

        Returns:
            tuple[int, int] | None: Les coordonées du jeton
            """
        numero_joueur = 2 if adversaire else 1
        for col_index in range(7):
            try:
                ligne_index, _ = jeu.update(col_index, numero_joueur)
            except IndexError:
                continue

            coordonees = self.trouve_jeton_aligne(ligne_index, col_index,
                                                  nb_jeton_aligne, numero_joueur)
            if coordonees is not None:
                return coordonees[0], coordonees[1]
        return None

    def trouve_jeton_aligne(self, ligne_index: int, colonne_index: int,
                            nb_jeton_aligne: int,
                            numero_joueur: int) -> tuple[int, int] | None:
        """ Regarde si x jeton d'un même joueur sont aligné en ligne, colonne ou diagonnale

        Args:
            ligne_index (int): L'index de la ligne où le jeton est attérit
            colonne_index (int): L'index de la colonne où le jeton est attérit
            nb_jeton_aligne (int): Le nombre de jeton qu'on souhaite aligner
            numero_joueur (int): Le numéro du joueur

        Returns:
            tuple[int, int] | None: Les coordonées du jeton. None si il n'y a pas d'alignement
        """
        ligne, colonne, diag_principale, diag_annexe = jeu.valeurs(
            ligne_index, colonne_index)

        stop_colonne = colonne_index + nb_jeton_aligne
        stop_ligne = ligne_index + nb_jeton_aligne
        target = [numero_joueur] * nb_jeton_aligne

        col_index = (
            list(ligne[colonne_index:stop_colonne]) == target or
            list(colonne[ligne_index:stop_ligne]) == target or
            list(diag_principale[colonne_index:stop_colonne]) == target or
            list(diag_annexe[colonne_index:stop_colonne]) == target)

        if col_index:
            if numero_joueur == 2:
                jeu.grille[ligne_index, colonne_index] = 1
            return ligne_index, colonne_index

        jeu.grille[ligne_index, colonne_index] = 0
        return None


jeu = Puissance4()
bot = IntelligenceArtificielle()

while True:
    col_bot, ligne_bot = bot.coup_a_jouer()
    os.system('cls')
    print(jeu.grille)
    if jeu.gagnant(col_bot, ligne_bot, 1):
        print("ORDI WIN")
        break
    col_user = int(input('colonne:\n'))-1
    ligne_user, colone_user = jeu.update(col_user, 2)
    if jeu.gagnant(ligne_user, col_user, 2):
        print("HUMAIN WIN")
        break
input()
