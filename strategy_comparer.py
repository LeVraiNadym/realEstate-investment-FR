import numpy as np
import matplotlib.pyplot as plt
import numpy_financial as npf


class ImmobilierSimulator:
    def __init__(self, duree=20, nb_associes=4, versement_mensuel_par_associe=2500, prix_initial=300000,
                 taux_interet_annuel=0.045, duree_credit_annees=20, rentabilite=0.04, taux_epargne=0.06):
        self.duree = duree
        self.nb_associes = nb_associes
        self.versement_mensuel_par_associe = versement_mensuel_par_associe
        self.versement_mensuel = versement_mensuel_par_associe * nb_associes
        self.prix_initial = prix_initial
        self.taux_interet_annuel = taux_interet_annuel
        self.duree_credit_mois = duree_credit_annees * 12
        self.rentabilite = rentabilite
        self.taux_epargne = taux_epargne

    def evolution_prix(self, prix):
        return prix * np.random.normal(1.02, 0.01)**(1/12)

    def achat_possible(self, tresorerie, prix_bien, credit):
        if credit:
            apport_min = 0.2 * prix_bien
            return tresorerie >= apport_min
        else:
            return tresorerie >= prix_bien

    def simulation(self, regime, credit=True):
        tresorerie = 0
        prix_bien = self.prix_initial
        biens_possedes = []
        valeur_portefeuille, nb_biens, net_valeur = [], [], []
        emprunts_details = []

        for mois in range(self.duree * 12):
            loyers_mensuels = sum(self.rentabilite * p / 12 for p in biens_possedes)
            revenu_total_mensuel = self.versement_mensuel + loyers_mensuels
            tresorerie += revenu_total_mensuel

            mensualites = 0
            nouveaux_emprunts_details = []
            for emprunt in emprunts_details:
                if emprunt['duree_restante'] > 0:
                    mensualite = npf.pmt(rate=self.taux_interet_annuel/12,
                                        nper=self.duree_credit_mois,
                                        pv=-emprunt['capital_initial'])
                    mensualites += mensualite
                    emprunt['capital_restant'] -= (mensualite - emprunt['capital_restant'] * self.taux_interet_annuel/12)
                    emprunt['duree_restante'] -= 1
                    nouveaux_emprunts_details.append(emprunt)
            emprunts_details = nouveaux_emprunts_details
            tresorerie -= mensualites

            while self.achat_possible(tresorerie, prix_bien, credit):
                if credit:
                    apport = 0.2 * prix_bien
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

                if regime == 'SAS':
                    benefice = (self.versement_mensuel * 12 + sum(self.rentabilite * p for p in biens_possedes)) - charges - amortissements - interets
                    impot = 0.15 * benefice if benefice <= 15000 else 0.25 * (benefice - 15000) + 15000 * 0.15
                elif regime == 'SCI_IR':
                    revenu_foncier = (self.versement_mensuel * 12 + sum(self.rentabilite * p for p in biens_possedes)) - charges - interets
                    impot = revenu_foncier * 0.3 if revenu_foncier > 0 else 0

                tresorerie -= impot

            prix_bien = self.evolution_prix(prix_bien)

            portefeuille = tresorerie + sum(biens_possedes)
            dette = sum(e['capital_restant'] for e in emprunts_details)

            valeur_portefeuille.append(portefeuille)
            nb_biens.append(len(biens_possedes))
            net_valeur.append(portefeuille - dette)

        return valeur_portefeuille, nb_biens, net_valeur

    def visualiser_strategies(self):
        regimes = ['SCI_IR', 'SAS']
        linestyles = ['--', '-.']
        markers = ['o', 's']
        annees = np.arange(1, self.duree * 12 + 1) / 12

        fig, axs = plt.subplots(3, 1, figsize=(16, 18))
        labels = ['Valeur du portefeuille (€)', 'Nombre de biens possédés', 'Valeur nette (portefeuille - dette) (€)']

        # Épargne baseline
        epargne = np.cumsum([self.versement_mensuel * (1 + self.taux_epargne/12)**mois for mois in range(self.duree * 12)])

        for idx, ax in enumerate(axs):
            for i, regime in enumerate(regimes):
                for j, credit in enumerate([True, False]):
                    valeurs = self.simulation(regime, credit)[idx]
                    ax.plot(annees, valeurs, label=f'{regime} ({"Crédit" if credit else "Cash"})', linestyle=linestyles[i], marker=markers[j], markevery=12)

            if idx != 1:
                ax.plot(annees, epargne, label='Épargne à '+ str(self.taux_epargne*100) + "%", color='gray', linewidth=2)

            ax.set_title(labels[idx])
            ax.set_xlabel('Années')
            ax.set_ylabel(labels[idx])
            ax.legend()
            ax.grid(True, linestyle='--')

        plt.tight_layout()
        plt.show()

# Example usage
simulator = ImmobilierSimulator()
simulator.visualiser_strategies()
