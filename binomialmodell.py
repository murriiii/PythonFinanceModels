# -*- coding: utf-8 -*-
import math
import numpy as np

class Binomialmodell:
    """
    Das Binomialmodell ist ein weit verbreitetes Werkzeug in der Finanzwirtschaft zur Bewertung von Optionen. Es modelliert die Entwicklung
    des Preises eines Basiswerts über die Zeit durch einen diskreten stochastischen Prozess, bekannt als Binomialbaum. Jeder Knoten im Baum
    repräsentiert einen möglichen Preis des Basiswerts zu einem bestimmten Zeitpunkt in der Zukunft, basierend auf einer Auf- oder Abwärtsbewegung
    in jedem Zeitschritt.

    Dieses Modell ermöglicht die Bewertung einer breiten Palette von Optionstypen, darunter europäische, amerikanische, digitale und exotische
    Optionen wie Power-Optionen und Strangles. Es kann auch angepasst werden, um Dividenden und verschiedene Wahrscheinlichkeiten für Preisbewegungen
    zu berücksichtigen.

    Die Flexibilität und relative Einfachheit des Binomialmodells machen es zu einem nützlichen Werkzeug für das Verständnis der Optionenbewertung
    und der Risikomanagementstrategien. Durch die iterative Rückwärtsberechnung vom Verfallstag bis zum aktuellen Zeitpunkt ermöglicht das Modell
    die Ermittlung des fairen Preises der Option sowie die Analyse der Sensitivität der Option auf verschiedene Marktparameter.

    Merkmale:
    - Unterstützt die Bewertung europäischer und amerikanischer Optionen.
    - Ermöglicht die Bewertung digitaler, Power-Optionen und Strangle-Strategien.
    - Berücksichtigt Dividenden und benutzerdefinierte Wahrscheinlichkeiten für Auf- und Abwärtsbewegungen.
    - Bietet Einblicke in die optimale Ausübungsstrategie für amerikanische Optionen.
    """
    def __init__(self, S0, K, T=1, r=0.05, N=2, sigma=None, div=0, is_put=False, K2=None, exponent=2, pu=None, pd=None, is_am=False, payoff=1):
        """Initialisiert eine neue Instanz zur Bewertung verschiedener Optionstypen mit dem Binomialmodell.

        Args:
            S0 (float): Anfänglicher Aktienkurs.
            K (float): Ausübungspreis der Hauptoption.
            T (float, optional): Laufzeit der Option in Jahren. Standard ist 1.
            r (float, optional): Risikoloser Zinssatz. Standard ist 0.05.
            N (int, optional): Anzahl der Perioden im Binomialbaum. Standard ist 2.
            sigma (float, optional): Volatilität des Basiswerts, erforderlich für die CRR-Parameterkonfiguration. Optional.
            div (float, optional): Dividendenrendite des Basiswerts. Standard ist 0.
            is_put (bool, optional): Gibt an, ob es sich um eine Put-Option handelt. Standard ist False (Call-Option).
            K2 (float, optional): Ausübungspreis der zweiten Option für Strangle-Strategien. Optional.
            payoff (float, optional): Auszahlungsbetrag für digitale Optionen. Standard ist 1.
            exponent (int, optional): Exponent für die Auszahlungsfunktion von Power-Optionen. Standard ist 2.
            pu (float, optional): Benutzerdefinierte Wahrscheinlichkeit einer Aufwärtsbewegung, erforderlich, wenn sigma nicht angegeben ist. Optional.
            pd (float, optional): Benutzerdefinierte Wahrscheinlichkeit einer Abwärtsbewegung, erforderlich, wenn sigma nicht angegeben ist. Optional.
            is_am (bool, optional): Gibt an, ob die Option amerikanisch ist. Standard ist False (europäisch).

        Diese Methode initialisiert die notwendigen Attribute und wählt basierend auf der Verfügbarkeit von `sigma` die entsprechende
        Methode zur Konfiguration der Modellparameter.
        """
        self.S0 = S0
        self.K = K
        self.K2 = K2 if K2 is not None else K
        self.r = r
        self.T = T
        self.N = max(1, N)
        self.div = div
        self.sigma = sigma
        self.is_put = is_put
        self.is_call = not is_put
        self.exponent = exponent
        self.is_am = is_am
        self.payoff = payoff
        # Wählt die Methode zur Konfiguration der Modellparameter basierend auf der Verfügbarkeit von `sigma`
        if sigma is not None:
            self.setup_parameters_with_sigma()
        else:
            self.pu, self.pd = pu, pd
            self.setup_parameters_without_sigma()

    def __repr__(self):
        """
        Gibt eine repräsentative Zeichenkette für eine Instanz des Binomialmodells zurück. Diese Methode wird aufgerufen, wenn
        `repr(obj)` für eine Instanz der Klasse aufgerufen wird. Die zurückgegebene Zeichenkette enthält wichtige Parameter der
        Modellinstanz, die für die Bewertung von Optionen verwendet werden, einschließlich des Anfangsaktienkurses (S0), des
        Ausübungspreises (K), der Laufzeit (T), des risikofreien Zinssatzes (r), der Anzahl der Perioden im Binomialbaum (N),
        der Volatilität des Basiswerts (sigma), der Dividendenrendite (div) und ob es sich um eine Put-Option handelt (is_put).

        Returns:
            str: Eine Zeichenkette, die die Instanz des Binomialmodells repräsentiert, mit Schlüsselparametern in einem
                formatierten Format.

        Beispiel:
            Erstellen einer Instanz des Binomialmodells und Aufrufen der `__repr__`-Methode:
                >>> modell = Binomialmodell(S0=100, K=100, T=1, r=0.05, N=50, sigma=0.2, div=0.03, is_put=False)
                >>> repr(modell)
            Dies gibt eine Zeichenkette zurück, die die Parameter der Modellinstanz darstellt:
                "Binomialmodell(S0=100, K=100, T=1, r=0.05, N=50, sigma=0.2, div=0.03, is_put=False)"
        """
        return (f"Binomialmodell(S0={self.S0}, K={self.K}, T={self.T}, r={self.r}, "
                f"N={self.N}, sigma={self.sigma}, div={self.div}, is_put={self.is_put})")

    def setup_parameters_with_sigma(self):
        """Konfiguriert die Modellparameter basierend auf dem Cox-Ross-Rubinstein (CRR) Ansatz unter Verwendung der Volatilität.

        Diese Methode wird verwendet, wenn die Volatilität (`sigma`) des Basiswerts bekannt ist. Sie berechnet die Zeit pro Periode
        (dt), den Diskontierungsfaktor (df), die Auf- (u) und Abwärtsfaktoren (d) sowie die risikoneutralen Wahrscheinlichkeiten
        (qu und qd) für Auf- und Abwärtsbewegungen basierend auf der CRR-Formel.

        Die CRR-Parameterkonfiguration ermöglicht eine realitätsnahe Modellierung der Aktienkursbewegungen und ist besonders geeignet
        für die Bewertung europäischer Optionen.
        """
        self.dt = self.T / self.N  # Berechnet die Zeit pro Periode.
        self.df = math.exp(-(self.r - self.div) * self.dt)  # Berechnet den Diskontierungsfaktor.
        self.u = math.exp(self.sigma * math.sqrt(self.dt))  # Berechnet den Aufwärtsfaktor basierend auf der Volatilität.
        self.d = 1 / self.u  # Setzt den Abwärtsfaktor als Kehrwert des Aufwärtsfaktors.
        self.qu = (math.exp((self.r - self.div) * self.dt) - self.d) / (self.u - self.d)  # Berechnet die risikoneutrale Wahrscheinlichkeit für eine Aufwärtsbewegung.
        self.qd = 1 - self.qu  # Ergänzt die Wahrscheinlichkeit für eine Abwärtsbewegung.

    def setup_parameters_without_sigma(self):
        """Konfiguriert die Modellparameter mit benutzerdefinierten Wahrscheinlichkeiten für Auf- und Abwärtsbewegungen.

        Diese Methode wird angewendet, wenn die Volatilität (`sigma`) des Basiswerts unbekannt ist. Stattdessen werden
        benutzerdefinierte Werte für die Wahrscheinlichkeiten von Auf- (pu) und Abwärtsbewegungen (pd) verwendet, um die Zeit pro
        Periode (dt), den Diskontierungsfaktor (df), die Auf- (u) und Abwärtsfaktoren (d) sowie die risikoneutralen Wahrscheinlichkeiten
        (qu und qd) zu berechnen.

        Der Ansatz ermöglicht eine flexible Anpassung des Modells an spezifische theoretische Überlegungen oder Marktbedingungen,
        abseits der Standard-CRR-Parameterkonfiguration.
        """
        self.dt = self.T / self.N  # Berechnet die Zeit pro Periode.
        self.df = math.exp(-(self.r - self.div) * self.dt)  # Berechnet den Diskontierungsfaktor.
        self.u = 1 + self.pu  # Setzt den Aufwärtsfaktor basierend auf der benutzerdefinierten Wahrscheinlichkeit.
        self.d = 1 - self.pd  # Setzt den Abwärtsfaktor basierend auf der benutzerdefinierten Wahrscheinlichkeit.
        self.qu = (math.exp((self.r - self.div) * self.dt) - self.d) / (self.u - self.d)  # Berechnet die risikoneutrale Wahrscheinlichkeit für eine Aufwärtsbewegung.
        self.qd = 1 - self.qu  # Ergänzt die Wahrscheinlichkeit für eine Abwärtsbewegung.

    def combos(self, n, i):
        """
        Berechnet die Anzahl der Kombinationen von `n` Elementen, die in `i` Gruppen aufgeteilt werden können,
        ohne Berücksichtigung der Reihenfolge. Diese Methode wird verwendet, um die Anzahl der möglichen Pfade im
        Binomialbaum zu berechnen, was wiederum zur Bestimmung der Endzustandswahrscheinlichkeiten beiträgt.

        Args:
            n (int): Die Gesamtzahl der Elemente.
            i (int): Die Anzahl der Elemente in jeder Gruppe.

        Returns:
            float: Die Anzahl der möglichen Kombinationen von `n` Elementen, die in `i` Gruppen aufgeteilt werden können.

        Beispiel:
            Angenommen, Sie haben einen Binomialbaum mit 3 Perioden und möchten die Anzahl der möglichen Endzustände
            berechnen. Jeder Knoten im Baum repräsentiert eine Periode. In jeder Periode gibt es zwei mögliche Pfade:
            eine Aufwärtsbewegung und eine Abwärtsbewegung. Wenn Sie die Anzahl der Endzustände berechnen möchten, können
            Sie die `combos`-Methode verwenden, um die Anzahl der möglichen Kombinationen von Auf- und Abwärtsbewegungen zu ermitteln:
                >>> modell = Binomialmodell(...)
                >>> modell.combos(3, 2)
            Dies gibt die Anzahl der möglichen Endzustände im Binomialbaum mit 3 Perioden zurück.

        Hinweis:
            Die Berechnung basiert auf der mathematischen Formel C(n, i) = n! / (i! * (n-i)!), wobei `!` das Fakultätssymbol
            darstellt, das das Produkt aller positiven ganzen Zahlen bis zu dieser Zahl einschließlich bezeichnet.
        """
        return math.factorial(n) / (math.factorial(n-i) * math.factorial(i))

    def check_early_exercise(self, payoff, node, level):
        """
        Bewertet die Möglichkeit einer vorzeitigen Ausübung für amerikanische Optionen an einem bestimmten Knoten.

        Args:
            payoff (np.ndarray): Der Payoff der Option, wenn sie bis zum aktuellen Knoten gehalten wird.
            node (int): Der Index des Knotens im Binomialbaum, für den die vorzeitige Ausübung bewertet wird.
            level (int): Die Ebene im Binomialbaum, auf der die Überprüfung stattfindet.

        Returns:
            np.ndarray: Der aktualisierte Payoff unter Berücksichtigung der Möglichkeit einer vorzeitigen Ausübung.
        """
        # Zugriff auf den Aktienkurs am gegebenen Knoten und Ebene
        stock_price_at_node = self.stock_price_tree[level, node]

        if self.is_call:
            # Für Call-Optionen: Vergleicht den Payoff bei Ausübung mit dem Payoff beim Halten.
            return np.maximum(payoff, stock_price_at_node - self.K)
        else:
            # Für Put-Optionen: Vergleicht den Payoff bei Ausübung mit dem Payoff beim Halten.
            return np.maximum(payoff, self.K - stock_price_at_node)

    def calculate_payoffs(self, option_type='european'):
        """
        Berechnet die Payoffs am Verfallstag basierend auf dem Optionstyp.

        Args:
            option_type (str): Der Typ der Option ('european', 'digital', 'power', 'strangle', 'american').

        """
        """
        """
        """ option_type = 'european':
        """
        """Berechnet die Auszahlungen von europäischen Optionen am Verfallstag.

        Europäische Optionen können nur am Verfallstag ausgeübt werden. Diese Methode berechnet die Auszahlung basierend darauf,
        ob es sich um eine Call- oder Put-Option handelt. Für Call-Optionen ist die Auszahlung der Differenz zwischen dem Schlusskurs
        des Basiswerts und dem Ausübungspreis, wenn positiv, sonst null. Für Put-Optionen ist die Auszahlung der Differenz zwischen
        dem Ausübungspreis und dem Schlusskurs, wenn positiv, sonst null.

        Returns:
            np.ndarray: Ein Array der Auszahlungen für jede Endknotenposition im Baum. Für Call-Optionen entspricht dies dem Maximum
                        von null und der Differenz zwischen dem Schlusskurs und dem Ausübungspreis. Für Put-Optionen entspricht dies
                        dem Maximum von null und der Differenz zwischen dem Ausübungspreis und dem Schlusskurs.
        """
        """
        """
        """ option_type = 'american':
        """
        """Berechnet die Auszahlungen von amerikanischen Optionen am Verfallstag und berücksichtigt die Möglichkeit der vorzeitigen Ausübung.

        Amerikanische Optionen können jederzeit vor dem Verfall ausgeübt werden. Diese Flexibilität bietet dem Halter der Option einen potenziellen
        Mehrwert gegenüber europäischen Optionen, die nur am Verfallstag ausgeübt werden können. Die Auszahlung für amerikanische Optionen hängt davon
        ab, ob es sich um eine Call- oder Put-Option handelt. Für Call-Optionen entspricht die Auszahlung dem Maximum von null und der Differenz
        zwischen dem Schlusskurs des Basiswerts und dem Ausübungspreis. Für Put-Optionen ist die Auszahlung das Maximum von null und der Differenz
        zwischen dem Ausübungspreis und dem Schlusskurs. Die Bewertung amerikanischer Optionen im Binomialmodell berücksichtigt die Möglichkeit einer
        optimalen vorzeitigen Ausübung zu jedem Zeitpunkt während der Laufzeit der Option.

        Returns:
            np.ndarray: Ein Array der Auszahlungen für jede Endknotenposition im Baum unter Berücksichtigung der Möglichkeit einer vorzeitigen Ausübung.
                        Für Call-Optionen entspricht dies dem Maximum von null und der Differenz zwischen dem Schlusskurs und dem Ausübungspreis.
                        Für Put-Optionen entspricht dies dem Maximum von null und der Differenz zwischen dem Ausübungspreis und dem Schlusskurs.
        """
        """
        """
        """ option_type = 'digital':
        """
        """ Berechnet die Auszahlungen von digitalen Optionen am Verfallstag im Binomialmodell.

        Digitale oder Binäroptionen zahlen 1 aus, wenn die Option im Geld endet, und 0, wenn sie aus dem Geld endet. Diese Methode
        ermittelt die Auszahlung basierend darauf, ob es sich um eine Call- oder Put-Option handelt und ob der Schlusskurs des
        Basiswerts über oder unter dem Ausübungspreis liegt.

        Returns:
            np.ndarray: Ein Array der Auszahlungen für jede Endknotenposition im Baum. Für jede Position im Baum wird entweder 1
                        oder 0 zurückgegeben, je nachdem, ob die Option im Geld ist oder nicht.
        """
        """
        """
        """ option_type = 'power':
        """
        """ Berechnet die Auszahlungen von Power-Optionen am Verfallstag.

        Power-Optionen sind eine Variante von Optionen, bei denen die Auszahlung eine Potenzfunktion des Unterschieds
        zwischen dem Schlusskurs des Basiswerts und dem Ausübungspreis ist. Diese Methode berechnet die Auszahlung
        basierend darauf, ob es sich um eine Call- oder Put-Option handelt, und auf der Differenz zwischen dem
        Schlusskurs und dem Ausübungspreis, erhoben zur Potenz des angegebenen Exponenten.

        Returns:
            np.ndarray: Ein Array der Auszahlungen für jede Endknotenposition im Baum. Für jede Position wird entweder
                        der Auszahlungsbetrag, basierend auf der Potenzfunktion der Differenz zwischen Schlusskurs und
                        Ausübungspreis, oder 0 zurückgegeben, je nachdem, ob die Option im Geld ist oder nicht.
        """
        """
        """
        """ option_type = 'strangle':
        """
        """ Berechnet die kombinierten Auszahlungen von Strangle-Strategien am Verfallstag.

        Eine Strangle-Strategie besteht aus dem Kauf (oder Verkauf) sowohl einer Call- als auch einer Put-Option mit demselben Verfallsdatum,
        aber unterschiedlichen Ausübungspreisen. Der Käufer eines Strangle profitiert von signifikanten Bewegungen des Basiswerts, unabhängig
        von der Richtung. Diese Strategie ist besonders nützlich in Märkten mit hoher Volatilität, wenn eine starke Preisbewegung erwartet wird,
        aber die Richtung der Bewegung unklar ist. Die Auszahlung für einen Long-Strangle entspricht der Summe der Auszahlungen der Call- und
        Put-Optionen. Die Call-Option zahlt aus, wenn der Schlusskurs über dem Ausübungspreis der Call-Option liegt, während die Put-Option
        auszahlt, wenn der Schlusskurs unter dem Ausübungspreis der Put-Option liegt.

        Returns:
            np.ndarray: Ein Array der kombinierten Auszahlungen für jede Endknotenposition im Baum. Die Auszahlungen reflektieren die Summe der
                        Payoffs der Call- und Put-Optionen, basierend auf ihren spezifischen Ausübungspreisen.
        """

        if option_type == 'european' or option_type == 'american':
            # Europäische Call- oder Put-Optionen
            if self.is_call:
                # Berechnet die Auszahlung für Call-Optionen am Verfallstag.
                return np.maximum(0, self.stock_price_tree[-1] - self.K)
            else:
                # Berechnet die Auszahlung für Put-Optionen am Verfallstag.
                return np.maximum(0, self.K - self.stock_price_tree[-1])

        elif option_type == 'digital':
            # Digitale Optionen
            if self.is_put:
                return np.where(self.stock_price_tree[-1] <= self.K, self.payoff, 0)
            else:
                return np.where(self.stock_price_tree[-1] > self.K, self.payoff, 0)

        elif option_type == 'power':
            # Power-Optionen
            if self.is_put:
                # Für Put-Optionen: Berechnet die Auszahlung basierend auf der Differenz zwischen Ausübungspreis und Schlusskurs,
                # erhoben zur Potenz des Exponenten, wenn die Option im Geld ist.
                return np.where(self.stock_price_tree[-1] < self.K, (self.K - self.stock_price_tree[-1])**self.exponent, 0)
            else:
                # Für Call-Optionen: Berechnet die Auszahlung basierend auf der Differenz zwischen Schlusskurs und Ausübungspreis,
                # erhoben zur Potenz des Exponenten, wenn die Option im Geld ist.
                return np.where(self.stock_price_tree[-1] > self.K, (self.stock_price_tree[-1] - self.K)**self.exponent, 0)

        elif option_type == 'strangle':
            # Strangle-Optionen
            call_payoffs = np.where(self.stock_price_tree[-1] > self.K, self.stock_price_tree[-1] - self.K, 0)
            put_payoffs = np.where(self.stock_price_tree[-1] < self.K2, self.K2 - self.stock_price_tree[-1], 0)
            return call_payoffs + put_payoffs

        else:
            raise ValueError("Unbekannter Optionstyp: " + option_type)

    def init_full_tree(self, option_type='european'):
        """Initialisiert den vollständigen Binomialbaum für die Bewertung von Optionen.

        Diese Methode erstellt zwei Bäume: einen für die Aktienkurse (`stock_price_tree`) und einen für die Optionspreise (`option_price_tree`).
        Sie berechnet auch die Delta-Werte (`delta_tree`) für die Replikationsstrategie. Basierend auf dem Typ der Option (`option_type`) werden
        die entsprechenden Auszahlungen am Verfallstag berechnet. Die Methode unterstützt europäische, amerikanische, digitale, Power- und
        Strangle-Optionen.

        Args:
            option_type (str, optional):    Der Typ der Option, die bewertet werden soll. Unterstützt 'european', 'american', 'digital', 'power',
                                            'strangle'. Standardwert ist 'european'.

        Erstellt:
            self.stock_price_tree (np.ndarray):     Ein 2D-Array, das die Aktienkurse an jedem Knotenpunkt des Binomialbaums enthält. Die Größe des
                                                    Arrays ist (N+1, N+1), wobei N die Anzahl der Perioden ist.
            self.option_price_tree (np.ndarray):    Ein 2D-Array, das die Optionspreise an jedem Knotenpunkt des Binomialbaums enthält.
                                                    Die Größe des Arrays entspricht der des `stock_price_tree`.
            self.delta_tree (np.ndarray):           Ein 2D-Array, das die Delta-Werte an jedem Knotenpunkt des Binomialbaums für die
                                                    Replikationsstrategie enthält. Die Größe des Arrays ist (N, N), da Delta im letzten Schritt nicht
                                                    berechnet wird.

        Hinweise:
            Die Methode passt den `option_price_tree` basierend auf der Optionstyp-spezifischen Auszahlung am Verfallstag an und berechnet Rückwärts
            durch den Baum die Optionspreise an den vorherigen Knotenpunkten. Für amerikanische Optionen berücksichtigt sie zusätzlich die Möglichkeit
            der vorzeitigen Ausübung.
        """
        # Initialisiert den Baum für Aktienkurse mit Nullen
        self.stock_price_tree = np.zeros((self.N + 1, self.N + 1))

        # Füllt den Aktienkursbaum: Für jede Ebene und jeden Knoten berechnet es den Aktienkurs
        for i in range(self.N + 1):
            for j in range(i + 1):
                self.stock_price_tree[i, j] = self.S0 * (self.u ** (i - j)) * (self.d ** j)

        # Berechnet die Auszahlungen am Verfallstag basierend auf dem Optionstyp
        payoffs = self.calculate_payoffs(option_type)

        # Initialisiert den Baum für Optionspreise mit Nullen
        self.option_price_tree = np.zeros_like(self.stock_price_tree)

        # Initialisiert den Baum für Delta-Werte mit Nullen
        self.delta_tree = np.zeros((self.N, self.N))

        # Setzt die Auszahlungen am Verfallstag in den letzten Knoten des Optionspreisbaums
        self.option_price_tree[-1] = payoffs

        # Rückwärtsiteration durch den Baum, um die Optionspreise zu berechnen
        for i in range(self.N - 1, -1, -1):
            for j in range(i + 1):
                if self.is_am:
                    # Überprüft die Möglichkeit einer vorzeitigen Ausübung für amerikanische Optionen
                    in_the_money_payoff = self.check_early_exercise(self.option_price_tree[i + 1, j], j, i + 1) if self.is_call \
                        else self.check_early_exercise(self.option_price_tree[i + 1, j + 1], j + 1, i + 1)
                    self.option_price_tree[i, j] = max((self.qu * self.option_price_tree[i + 1, j] + self.qd * self.option_price_tree[i + 1, j + 1]) * self.df, in_the_money_payoff)
                else:
                    # Berechnet den Optionspreis für den Knoten, ohne vorzeitige Ausübung zu berücksichtigen
                    self.option_price_tree[i, j] = (self.qu * self.option_price_tree[i + 1, j] + self.qd * self.option_price_tree[i + 1, j + 1]) * self.df

                # Berechnet Delta-Werte für die Replikationsstrategie, außer im letzten Schritt
                if i != self.N:
                    self.delta_tree[i, j] = (self.option_price_tree[i + 1, j] - self.option_price_tree[i + 1, j + 1]) / (self.stock_price_tree[i + 1, j] - self.stock_price_tree[i + 1, j + 1])

        # Berechnung der Wahrscheinlichkeiten der Endzustände
        self.end_state_probabilities = np.zeros(self.N + 1)
        for k in range(self.N + 1):
            self.end_state_probabilities[k] = self.combos(self.N, k) * self.qu**k * self.qd**(self.N - k)


    def price_option(self, option_type):
        """Berechnet den Preis einer Option basierend auf dem spezifizierten Optionstyp.

        Diese Methode initialisiert zunächst den vollständigen Binomialbaum für den gegebenen Optionstyp durch den Aufruf der Methode `init_full_tree`.
        Der Baum wird mit allen relevanten Werten für Aktienkurse, Optionspreise und Delta-Werte für die Replikationsstrategie befüllt. Anschließend wird
        der Preis der Option am Ursprung des Baumes (d.h. im heutigen Zeitpunkt) zurückgegeben. Dieser Preis repräsentiert den fairen Wert der Option unter
        Berücksichtigung der gegebenen Marktbedingungen und Modellannahmen.

        Args:
            option_type (str): Der Typ der Option, die bewertet werden soll. Unterstützte Typen sind 'european', 'american', 'digital', 'power' und 'strangle'.

        Returns:
            float: Der berechnete Preis der Option am Ursprung des Baumes.

        Raises:
            ValueError: Wird ausgelöst, wenn ein unbekannter Optionstyp angegeben wird.
        """
        # Initialisiert den vollständigen Binomialbaum basierend auf dem gegebenen Optionstyp.
        self.init_full_tree(option_type)

        # Gibt den Optionspreis am Ursprung des Baumes zurück.
        # Dieser Wert entspricht dem fairen Wert der Option zum heutigen Zeitpunkt.
        return self.option_price_tree[0, 0]
