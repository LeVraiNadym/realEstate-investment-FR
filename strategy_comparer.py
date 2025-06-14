import numpy as np
import matplotlib.pyplot as plt
import numpy_financial as npf

class ImmobilierSimulator:
    def __init__(self, duree=23, nb_associes=4, versement_mensuel_par_associe=2500, prix_initial=300000,
                 taux_interet_annuel=0.045, duree_credit_annees=20, rentabilite=0.05,
                 taux_epargne_fonction=None, taux_amortissement=0.025):
        self.duree = duree
        self.nb_associes = nb_associes
        self.versement_mensuel_par_associe = versement_mensuel_par_associe
        self.versement_mensuel = versement_mensuel_par_associe * nb_associes
        self.prix_initial = prix_initial
        self.taux_interet_annuel = taux_interet_annuel
        self.duree_credit_mois = duree_credit_annees * 12
        self.rentabilite = rentabilite
        self.taux_amortissement = taux_amortissement

        if taux_epargne_fonction is None:
            self.mean_annuel = 0.04
            self.sigma_annuel = 0.02
            self.taux_epargne_fonction = lambda mois: np.random.normal(self.mean_annuel, self.sigma_annuel) / 12
        else:
            self.taux_epargne_fonction = taux_epargne_fonction
            self.mean_annuel = None
            self.sigma_annuel = None

    def evolution_prix(self, prix):
        return prix * np.random.normal(1.03, 0.01)**(1/12)
        

    def achat_possible(self, tresorerie, prix_bien, credit):
        return tresorerie >= (0.2 * prix_bien if credit else prix_bien)

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
                    mensualite = npf.pmt(rate=self.taux_interet_annuel / 12,
                                         nper=self.duree_credit_mois,
                                         pv=-emprunt['capital_initial'])
                    mensualites += mensualite
                    emprunt['capital_restant'] -= (mensualite - emprunt['capital_restant'] * self.taux_interet_annuel / 12)
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
                amortissements = sum(self.taux_amortissement * prix_achat for prix_achat in biens_possedes)
                interets = sum(e['capital_restant'] * self.taux_interet_annuel for e in emprunts_details)

                if regime == 'SAS':
                    benefice = (self.versement_mensuel * 12 + sum(self.rentabilite * p for p in biens_possedes)) - charges - amortissements - interets
                    if benefice > 0:
                        impot = 0.15 * benefice if benefice <= 15000 else 0.25 * (benefice - 15000) + 15000 * 0.15
                    else:
                        impot = 0
                elif regime == 'SCI_IR':
                    revenu_foncier = (self.versement_mensuel * 12 + sum(self.rentabilite * p for p in biens_possedes)) - charges - interets - amortissements
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

        taux_epargne_par_mois = np.array([max(self.taux_epargne_fonction(mois), 0) for mois in range(self.duree * 12)])
        epargne = np.zeros(self.duree * 12)
        capital = 0
        for mois in range(self.duree * 12):
            capital += self.versement_mensuel
            capital *= (1 + taux_epargne_par_mois[mois])
            epargne[mois] = capital

        cash = np.cumsum([self.versement_mensuel for _ in range(self.duree * 12)])

        break_even_points = []
        for i, regime in enumerate(regimes):
            for j, credit in enumerate([True, False]):
                valeurs = self.simulation(regime, credit)[2]
                for mois in range(len(valeurs)):
                    if valeurs[mois] >= cash[mois]:
                        break_even_points.append((annees[mois], valeurs[mois], f'{regime} ({"Crédit" if credit else "Cash"})'))
                        break

        break_even_points.sort()

        for idx, ax in enumerate(axs):
            for i, regime in enumerate(regimes):
                for j, credit in enumerate([True, False]):
                    valeurs = self.simulation(regime, credit)[idx]
                    label = f'{regime} ({"Crédit" if credit else "Cash"})'
                    ax.plot(annees, valeurs, label=label, linestyle=linestyles[i], marker=markers[j], markevery=12)

            if idx == 2:
                ylim_top = ax.get_ylim()[1]
                for x, y, label in break_even_points:
                    if y < ylim_top / 2:
                        ypos = y + 0.3 * ylim_top
                        va = 'bottom'
                    else:
                        ypos = y - 0.3 * ylim_top
                        va = 'top'

                    ax.annotate(f'{label}\n{int(x)} ans\nrattrape la somme cumulative\ndes investissements',
                                xy=(x, y),
                                xytext=(x, ypos),
                                arrowprops=dict(arrowstyle='->', color='red'),
                                fontsize=9, color='red', ha='center', va=va)

            if idx != 1:
                mu_sigma_label = f'Épargne simulée (μ={self.mean_annuel*100:.1f}%, σ={self.sigma_annuel*100:.1f}%)'
                ax.plot(annees, epargne, label=mu_sigma_label, color='gray', linewidth=2)
                ax.plot(annees, cash, label='Cash non investi', color='black', linewidth=2)

            ax.set_title(labels[idx])
            ax.set_xlabel('Années')
            ax.set_ylabel(labels[idx])
            ax.legend()
            ax.grid(True, linestyle='--')

        plt.tight_layout()
        plt.show()


# Run the simulator with the updated legend for the savings line
simulator = ImmobilierSimulator()
simulator.visualiser_strategies()