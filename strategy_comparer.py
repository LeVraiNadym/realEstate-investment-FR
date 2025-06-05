import numpy as np
import matplotlib.pyplot as plt

class ImmobilierSimulator:
    def __init__(self, duree=20, nb_associes=4, versement_mensuel_par_associe=5000, prix_initial=200000,
                 taux_interet_annuel=0.045, duree_credit_annees=20, rentabilite=0.04):
        self.duree = duree
        self.nb_associes = nb_associes
        self.versement_mensuel_par_associe = versement_mensuel_par_associe
        self.versement_mensuel = versement_mensuel_par_associe * nb_associes
        self.prix_initial = prix_initial
        self.taux_interet_annuel = taux_interet_annuel
        self.duree_credit_mois = duree_credit_annees * 12
        self.rentabilite = rentabilite

    def evolution_prix(self, prix):
        return prix * np.random.normal(1.02, 0.01)**(1/12)

    def achat_possible(self, tresorerie, prix_bien, nb_biens, credit):
        if credit:
            apport_min = min(0.1 * nb_biens, 1.0) * prix_bien
            return tresorerie >= apport_min
        else:
            return tresorerie >= prix_bien

    def simulation(self, regime, credit=True):
        tresorerie = 0
        prix_bien = self.prix_initial
        biens_possedes = []
        valeur_portefeuille = []
        emprunts_details = []

        for mois in range(self.duree * 12):
            loyers_mensuels = sum(self.rentabilite * p / 12 for p in biens_possedes)
            revenu_total_mensuel = self.versement_mensuel + loyers_mensuels
            tresorerie += revenu_total_mensuel

            # Paiement mensuel des crédits
            mensualites = 0
            nouveaux_emprunts_details = []
            for emprunt in emprunts_details:
                if emprunt['duree_restante'] > 0:
                    mensualite = np.pmt(rate=self.taux_interet_annuel/12,
                                        nper=self.duree_credit_mois,
                                        pv=-emprunt['capital_initial'])
                    mensualites += mensualite
                    emprunt['capital_restant'] -= (mensualite - emprunt['capital_restant'] * self.taux_interet_annuel/12)
                    emprunt['duree_restante'] -= 1
                    nouveaux_emprunts_details.append(emprunt)
            emprunts_details = nouveaux_emprunts_details
            tresorerie -= mensualites

            # Achat possible chaque mois
            while self.achat_possible(tresorerie, prix_bien, len(biens_possedes), credit):
                if credit:
                    apport = min(0.1 * len(biens_possedes), 1.0) * prix_bien
                    montant_emprunte = prix_bien - apport
                    emprunts_details.append({'capital_initial': montant_emprunte,
                                             'capital_restant': montant_emprunte,
                                             'duree_restante': self.duree_credit_mois})
                    tresorerie -= apport
                else:
                    tresorerie -= prix_bien
                biens_possedes.append(prix_bien)

            if mois % 12 == 0:
                charges = sum(0.05 * p for p in biens_possedes)
                amortissements = sum(p / 20 for p in biens_possedes)
                interets = sum(e['capital_restant'] * self.taux_interet_annuel for e in emprunts_details)

                if regime == 'SCI_IS' or regime == 'SAS':
                    benefice = (self.versement_mensuel * 12 + sum(self.rentabilite * p for p in biens_possedes)) - charges - amortissements - interets
                    impot = 0.15 * benefice if benefice <= 15000 else 0.25 * (benefice - 15000) + 15000 * 0.15

                elif regime == 'SCI_IR':
                    revenu_foncier = (self.versement_mensuel * 12 + sum(self.rentabilite * p for p in biens_possedes)) - charges - interets
                    impot = revenu_foncier * 0.3 if revenu_foncier > 0 else 0

                tresorerie -= impot

            prix_bien = self.evolution_prix(prix_bien)
            portefeuille = tresorerie + sum(biens_possedes) - sum(e['capital_restant'] for e in emprunts_details)
            valeur_portefeuille.append(portefeuille)

        return valeur_portefeuille

    def visualiser_strategies(self):
        regimes = ['SCI_IS', 'SCI_IR', 'SAS']
        linestyles = ['-', '--', '-.']
        markers = ['o', 's']
        plt.figure(figsize=(12, 8))

        for i, regime in enumerate(regimes):
            for j, credit in enumerate([True, False]):
                valeurs = self.simulation(regime, credit)
                plt.plot(np.arange(1, self.duree * 12 + 1) / 12, valeurs,
                         label=f'{regime} ({"Crédit" if credit else "Cash"})', linewidth=2,
                         linestyle=linestyles[i], marker=markers[j], markevery=12, alpha=0.8)

        plt.xlabel('Années')
        plt.ylabel('Valeur du portefeuille (€)')
        plt.title('Comparaison mensuelle des stratégies SCI IS, SCI IR et SAS avec ou sans crédit')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()

# Exemple d'utilisation
simulator = ImmobilierSimulator()
simulator.visualiser_strategies()
