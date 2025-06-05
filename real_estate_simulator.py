import numpy as np
import matplotlib.pyplot as plt

def lancer_jeu_interactif():
    class ImmobilierGame:
        def __init__(self, duree=20, nb_associes=4, versement_mensuel_par_associe=5000, prix_initial=200000,
             taux_interet_annuel=0.03, duree_credit_annees=20, rendement_annuel=0.035):
            self.duree = duree
            self.nb_associes = nb_associes
            self.versement_mensuel = versement_mensuel_par_associe * nb_associes
            self.prix_initial = prix_initial
            self.taux_interet_annuel = taux_interet_annuel
            self.duree_credit_mois = duree_credit_annees * 12
            self.rendement_annuel = rendement_annuel  # <-- new line
            self.reset()

        def reset(self):
            self.tresorerie = 0
            self.biens_possedes = []
            self.emprunts_details = []
            self.mois = 0
            self.historique = []

        def evolution_prix(self, prix):
            return prix * np.random.normal(1.02, 0.01) ** (1 / 12)

        def payer_mensualites(self):
            mensualites = 0
            nouveaux_emprunts_details = []
            for emprunt in self.emprunts_details:
                if emprunt['duree_restante'] > 0:
                    mensualite = np.pmt(rate=self.taux_interet_annuel / 12,
                                        nper=self.duree_credit_mois,
                                        pv=-emprunt['capital_initial'])
                    mensualites += mensualite
                    interet = emprunt['capital_restant'] * self.taux_interet_annuel / 12
                    principal = mensualite - interet
                    emprunt['capital_restant'] -= principal
                    emprunt['duree_restante'] -= 1
                    nouveaux_emprunts_details.append(emprunt)
            self.emprunts_details = nouveaux_emprunts_details
            self.tresorerie -= mensualites

        def ajouter_loyers(self):
            loyer_total = sum(self.rendement_annuel * bien['prix_initial'] / 12 for bien in self.biens_possedes)
            self.tresorerie += loyer_total

        def calculer_impot_sas(self):
            revenus = sum(self.rendement_annuel * bien['prix_initial'] for bien in self.biens_possedes)
            interets_total = sum(e['capital_restant'] * self.taux_interet_annuel for e in self.emprunts_details)
            resultat_imposable = revenus - interets_total
            if resultat_imposable > 0:
                impot = 0.25 * resultat_imposable
                self.tresorerie -= impot

        def passer_mois(self, nb_mois):
            for _ in range(nb_mois):
                self.tresorerie += self.versement_mensuel
                self.payer_mensualites()
                self.ajouter_loyers()
                if self.mois % 12 == 0 and self.mois != 0:
                    self.calculer_impot_sas()
                self.mois += 1
                self.prix_initial = self.evolution_prix(self.prix_initial)
                for bien in self.biens_possedes:
                    bien['valeur_actuelle'] = self.evolution_prix(bien['valeur_actuelle'])
                self.historique.append(self.etat_actuel())

        def acheter(self, credit=True):
            if credit:
                apport = 0.2 * self.prix_initial
                if self.tresorerie >= apport:
                    montant_emprunte = self.prix_initial - apport
                    self.emprunts_details.append({
                        'capital_initial': montant_emprunte,
                        'capital_restant': montant_emprunte,
                        'duree_restante': self.duree_credit_mois
                    })
                    self.tresorerie -= apport
                    self.biens_possedes.append({'prix_initial': self.prix_initial, 'valeur_actuelle': self.prix_initial})
                    return True
            else:
                if self.tresorerie >= self.prix_initial:
                    self.tresorerie -= self.prix_initial
                    self.biens_possedes.append({'prix_initial': self.prix_initial, 'valeur_actuelle': self.prix_initial})
                    return True
            return False

        def etat_actuel(self):
            dette_totale = sum(e['capital_restant'] for e in self.emprunts_details)
            valeur_biens = sum(b['valeur_actuelle'] for b in self.biens_possedes)
            return {
                'mois': self.mois,
                'tresorerie': round(self.tresorerie, 2),
                'prix_bien': round(self.prix_initial, 2),
                'biens_possedes': len(self.biens_possedes),
                'valeur_biens': round(valeur_biens, 2),
                'emprunts': [{'reste': round(e['capital_restant'], 2), 'mois': e['duree_restante']} for e in self.emprunts_details],
                'patrimoine_net': round(self.tresorerie + valeur_biens - dette_totale, 2),
                'dette_totale': round(dette_totale, 2)
            }

        def afficher_courbe(self):
            mois = [e['mois'] for e in self.historique]
            patrimoine_net = [e['patrimoine_net'] for e in self.historique]
            tresorerie = [e['tresorerie'] for e in self.historique]
            dette = [e['dette_totale'] for e in self.historique]

            plt.plot(mois, patrimoine_net, label='Patrimoine net')
            plt.plot(mois, tresorerie, label='Trésorerie')
            plt.plot(mois, dette, label='Dette totale')
            plt.xlabel('Mois')
            plt.ylabel('Euros')
            plt.title("Évolution financière sur 20 ans")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    def afficher_menu(jeu):
        etat = jeu.etat_actuel()
        revenus_loyers = round(sum(jeu.rendement_annuel * bien['prix_initial'] / 12 for bien in jeu.biens_possedes), 2)
        revenus_associes = jeu.versement_mensuel
        revenu_mensuel_total = round(revenus_loyers + revenus_associes, 2)

        print(f"\n--- MOIS {etat['mois'] + 1} ---")
        print(f"💰 Trésorerie : {etat['tresorerie']} €")
        print(f"🏠 Prix d’un bien : {etat['prix_bien']} €")
        print(f"📊 Patrimoine net : {etat['patrimoine_net']} €")
        print(f"📉 Dette totale : {etat['dette_totale']} €")
        print(f"📈 Revenu mensuel : {revenus_associes} (assoc.) + {revenus_loyers} (loyers) = {revenu_mensuel_total} €")
        print()
        print("1. Passer 1 mois")
        print("6. Passer 2 mois")
        print("7. Passer 3 mois")
        print("8. Passer 6 mois")
        print("9. Passer 12 mois")
        print("2. Acheter un bien avec crédit (si possible)")
        print("3. Acheter un bien sans crédit (si possible)")
        print("4. Afficher l’état actuel détaillé")
        print("5. Terminer la simulation et afficher la courbe")

    # Début de la boucle interactive
    jeu = ImmobilierGame()
    print("Bienvenue dans le simulateur d’investissement immobilier !\n")
    while jeu.mois < jeu.duree * 12:
        afficher_menu(jeu)
        choix = input("Votre choix : ").strip()

        if choix == "1":
            jeu.passer_mois(1)
        elif choix == "6":
            jeu.passer_mois(2)
        elif choix == "7":
            jeu.passer_mois(3)
        elif choix == "8":
            jeu.passer_mois(6)
        elif choix == "9":
            jeu.passer_mois(12)
        elif choix == "2":
            if not jeu.acheter(credit=True):
                print("❌ Achat impossible (fonds insuffisants).")
        elif choix == "3":
            if not jeu.acheter(credit=False):
                print("❌ Achat impossible (fonds insuffisants).")
        elif choix == "4":
            print("\n📋 État détaillé :", jeu.etat_actuel())
        elif choix == "5":
            print("\nFin de la simulation.")
            break
        else:
            print("⛔ Choix invalide. Veuillez réessayer.")

    jeu.afficher_courbe()

lancer_jeu_interactif()
