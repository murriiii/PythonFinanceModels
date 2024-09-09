# -*- coding: utf-8 -*-
import math
import numpy as np

class Trinomialmodell:
    """
    Eine Klasse zur Bewertung von Derivaten unter Verwendung des Trinomialmodells.

    Das Trinomialmodell ist eine Erweiterung des Binomialmodells und bietet durch die Einführung einer mittleren Bewegung eine genauere
    und flexiblere Bewertung von Derivaten. Diese Klasse unterstützt die Bewertung verschiedener Arten von Derivaten, einschließlich
    europäischer und exotischer Optionen, und ermöglicht die Bestimmung replizierender Handelsstrategien. Benutzer können die Modellparameter,
    einschließlich der Anzahl der Perioden, Volatilität, Zinssätze und Dividenden, anpassen.

    Methods:
        setup_parameters(self):
            Konfiguriert die Parameter für das Trinomialmodell basierend auf der Volatilität des Basiswerts.
        calculate_end_state_probabilities(self):
            Berechnet die Wahrscheinlichkeiten der Endzustände im Trinomialbaum.
        calculate_payoffs(self, option_type):
            Berechnet die finalen Auszahlungen der Option basierend auf dem Optionstyp.
        init_full_tree(self, option_type):
            Initialisiert den vollständigen Baum der Aktienkurse und berechnet daraufhin die Optionspreise.
        price_option(self, option_type):
            Berechnet den Preis einer Option basierend auf dem angegebenen Optionstyp.
    """
    def __init__(self, S0, K, T=1, r=0.05, N=2, sigma=None, div=0, is_put=False, K2=None, pu=None, pd=None, pm=None, u=None, d=None, m=None, is_am=False, exponent=2):
        """
        Initialisiert eine neue Instanz des Trinomialmodells zur Bewertung von Derivaten.

        Dieses Modell erweitert das klassische Binomialmodell um eine mittlere Bewegung, was zu einer genaueren und flexibleren Bewertung führen kann.
        Es unterstützt europäische sowie verschiedene exotische Optionen durch Anpassung der Auszahlungsfunktionen.

        Args:
            S0 (float): Anfänglicher Aktienkurs.
            K (float): Ausübungspreis der Option.
            T (float, optional): Laufzeit der Option in Jahren. Standardwert ist 1.
            r (float, optional): Jährlicher risikofreier Zinssatz. Standardwert ist 0.05.
            N (int, optional): Anzahl der Perioden im Trinomialbaum. Standardwert ist 2.
            sigma (float, optional): Volatilität des Basiswerts. Optional, falls direkt die Bewegungsparameter angegeben werden.
            div (float, optional): Dividendenrendite des Basiswerts. Standardwert ist 0.
            is_put (bool, optional): Gibt an, ob es sich um eine Put-Option handelt. Standardwert ist False.
            K2 (float, optional): Ausübungspreis der zweiten Option für kombinierte Strategien, z.B. Strangles. Optional.
            pu (float, optional): Wahrscheinlichkeit einer Aufwärtsbewegung. Muss angegeben werden, falls `sigma` nicht spezifiziert ist.
            pd (float, optional): Wahrscheinlichkeit einer Abwärtsbewegung. Muss angegeben werden, falls `sigma` nicht spezifiziert ist.
            pm (float, optional): Wahrscheinlichkeit einer mittleren Bewegung. Muss angegeben werden, falls `sigma` nicht spezifiziert ist.
            u (float, optional): Multiplikator für eine Aufwärtsbewegung. Muss angegeben werden, falls `sigma` nicht spezifiziert ist.
            d (float, optional): Multiplikator für eine Abwärtsbewegung. Muss angegeben werden, falls `sigma` nicht spezifiziert ist.
            m (float, optional): Multiplikator für eine mittlere Bewegung. Muss angegeben werden, falls `sigma` nicht spezifiziert ist.
            is_european (bool, optional): Gibt an, ob die Option europäisch ist. Standardwert ist True.
            exponent (int, optional): Exponent für die Auszahlungsfunktion bei Power-Optionen. Standardwert ist 2.
            is_am (bool, optional): Gibt an, ob die Option amerikanisch ist.

        Raises:
            ValueError: Wenn weder `sigma` noch die direkten Bewegungsparameter (`u`, `d`, `m`, `pu`, `pd`, `pm`) angegeben werden.
        """
        self.S0 = S0
        self.K = K
        self.K2 = K2 if K2 is not None else K
        self.r = r
        self.T = T
        self.N = N
        self.div = div
        self.is_put = is_put
        self.is_call = not is_put
        self.is_am = is_am
        self.dt = self.T / self.N
        self.df = math.exp(-self.r * self.dt)
        self.exponent = exponent
        if sigma is not None:
            self.sigma = sigma
            self.setup_parameters()
        elif all(v is not None for v in [u, d, m, pu, pd, pm]):
            self.u = u
            self.d = d
            self.m = m
            self.pu = pu
            self.pd = pd
            self.pm = pm
        else:
            raise ValueError("Entweder sigma oder (u, d, m, pu, pd, pm) müssen angegeben werden.")

    def __repr__(self):
        """
        Gibt eine repräsentative Zeichenkette für eine Instanz des Trinomialmodells zurück. Diese Methode wird aufgerufen, wenn
        `repr(obj)` für eine Instanz der Klasse aufgerufen wird. Die zurückgegebene Zeichenkette enthält wichtige Parameter der
        Modellinstanz, die für die Bewertung von Optionen verwendet werden, einschließlich des Anfangsaktienkurses (S0), des
        Ausübungspreises (K), der Laufzeit (T), des risikofreien Zinssatzes (r), der Anzahl der Perioden im Trinomialbaum (N),
        der Volatilität des Basiswerts (sigma), der Dividendenrendite (div) und ob es sich um eine Put-Option handelt (is_put).

        Returns:
            str: Eine Zeichenkette, die die Instanz des Trinomialmodells repräsentiert, mit Schlüsselparametern in einem
                formatierten Format.

        Beispiel:
            Erstellen einer Instanz des Trinomialmodells und Aufrufen der `__repr__`-Methode:
                >>> modell = Trinomialmodell(S0=100, K=100, T=1, r=0.05, N=50, sigma=0.2, div=0, is_put=False)
                >>> repr(modell)
            Dies gibt eine Zeichenkette zurück, die die Parameter der Modellinstanz darstellt:
                "Trinomialmodell(S0=100, K=100, T=1, r=0.05, N=50, sigma=0.2, div=0, is_put=False)"
        """
        return (f"Trinomialmodell(S0={self.S0}, K={self.K}, T={self.T}, r={self.r}, "
                f"N={self.N}, sigma={self.sigma}, div={self.div}, is_put={self.is_put})")

    def setup_parameters(self):
        """
        Konfiguriert die Parameter für das Trinomialmodell basierend auf der Volatilität des Basiswerts.

        Diese Methode berechnet die Multiplikatoren für Auf-, Abwärts- und mittlere Bewegungen (u, d, m) sowie die zugehörigen Wahrscheinlichkeiten
        (pu, pd, pm) für jede Bewegung. Die Berechnungen basieren auf der angegebenen Volatilität (`sigma`), dem risikofreien Zinssatz (`r`), der
        Dividendenrendite (`div`) und der Zeit pro Periode (`dt`).

        Die Parameter ermöglichen es, den Trinomialbaum für die Bewertung von Derivaten zu konstruieren, wobei die Wahrscheinlichkeiten die
        risikoneutralen Wahrscheinlichkeiten für jede Preisbewegung reflektieren.

        Die Formeln für die Multiplikatoren und Wahrscheinlichkeiten sind speziell auf das Trinomialmodell abgestimmt und berücksichtigen die
        Möglichkeit einer mittleren Bewegung, was dieses Modell von Binomialmodellen unterscheidet.
        """
        self.u = math.exp(self.sigma * math.sqrt(2. * self.dt))  # Berechnet den Multiplikator für eine Aufwärtsbewegung.
        self.d = 1 / self.u  # Setzt den Multiplikator für eine Abwärtsbewegung als Kehrwert des Aufwärtsmultiplikators.
        self.m = 1  # Der Multiplikator für eine mittlere Bewegung bleibt unverändert.

        # Berechnet die Wahrscheinlichkeit einer Aufwärtsbewegung.
        self.pu = ((math.exp((self.r - self.div) * self.dt / 2.) - math.exp(-self.sigma * math.sqrt(self.dt / 2.))) /
                (math.exp(self.sigma * math.sqrt(self.dt / 2.)) - math.exp(-self.sigma * math.sqrt(self.dt / 2.))))**2

        # Berechnet die Wahrscheinlichkeit einer Abwärtsbewegung.
        self.pd = ((math.exp(self.sigma * math.sqrt(self.dt / 2.)) - math.exp((self.r - self.div) * self.dt / 2.)) /
                (math.exp(self.sigma * math.sqrt(self.dt / 2.)) - math.exp(-self.sigma * math.sqrt(self.dt / 2.))))**2

        # Berechnet die Wahrscheinlichkeit einer mittleren Bewegung als Restwahrscheinlichkeit.
        self.pm = 1 - self.pu - self.pd

    def calculate_end_state_probabilities(self):
        """
        Berechnet die Wahrscheinlichkeiten der Endzustände in einem Trinomialbaum.
        """
        # Die Anzahl der Schritte im Baum
        N = self.N

        # Initialisiert ein Dictionary, um die Anzahl der Pfade zu jedem Endzustand zu speichern
        end_state_paths = {}

        # Generiert alle möglichen Pfade
        for i in range(3**N):
            path = format(i, f'0{N}o')
            up_moves = path.count('0')
            mid_moves = path.count('1')
            down_moves = path.count('2')
            # Schlüssel zur Identifizierung des Endzustands
            end_state = (up_moves, mid_moves, down_moves)
            if end_state not in end_state_paths:
                end_state_paths[end_state] = 1
            else:
                end_state_paths[end_state] += 1

        # Berechnet die Wahrscheinlichkeiten für jeden Endzustand
        end_state_probabilities = {}
        for end_state, paths in end_state_paths.items():
            up_moves, mid_moves, down_moves = end_state
            probability = (self.pu**up_moves) * (self.pm**mid_moves) * (self.pd**down_moves)
            probability *= math.factorial(N) / (math.factorial(up_moves) * math.factorial(mid_moves) * math.factorial(down_moves))
            end_state_probabilities[end_state] = probability

        return end_state_probabilities

    def calculate_payoffs(self, option_type):
        """
        Berechnet die finalen Auszahlungen für eine gegebene Option basierend auf dem Optionstyp am Verfallstag.

        Diese Methode bestimmt die Auszahlungen für die Endzustände des Aktienkurses im Trinomialbaum. Abhängig vom Typ der Option
        (europäisch, amerikanisch, Power-Option, digital, Strangle) werden unterschiedliche Berechnungslogiken angewendet.

        Args:
            option_type (str): Der Typ der Option, für die die Auszahlungen berechnet werden sollen. Gültige Werte sind
                            'european', 'american', 'power', 'digital', 'strangle'.

        Returns:
            numpy.ndarray: Ein Array von Auszahlungen für jeden Endzustand im Trinomialbaum.

        Raises:
            ValueError: Wenn ein unbekannter Optionstyp übergeben wird.

        Hinweis:
            Für eine detaillierte Erklärung der Berechnungsmethodik für jeden Optionstyp, siehe die Dokumentation
            des Binomialmodells. Diese Methode folgt einer ähnlichen Logik, jedoch angepasst für das Trinomialmodell.

        Beispiel:
            >>> modell = Trinomialmodell(S0=100, K=100, T=1, r=0.05, N=50, sigma=0.2)
            >>> modell.calculate_payoffs('european')
            Das Beispiel berechnet die Auszahlungen für eine europäische Option basierend auf den Endzuständen des Aktienkurses.

        """
        final_prices = self.stock_price_tree[-1]  # Holt die finalen Aktienkurse aus dem Baum.

        # Differenzierte Auszahlungsberechnungen basierend auf dem Optionstyp
        if option_type in ['european', 'american']:
            # Berechnet Auszahlungen für europäische und amerikanische Optionen (Put und Call)
            if self.is_put:
                payoffs = np.maximum(self.K - final_prices, 0)  # Put-Option Auszahlungen
            else:
                payoffs = np.maximum(final_prices - self.K, 0)  # Call-Option Auszahlungen
        elif option_type == 'power':
            # Berechnet Auszahlungen für Power-Optionen
            if self.is_put:
                payoffs = np.where(final_prices < self.K, (self.K - final_prices)**self.exponent, 0)
            else:
                payoffs = np.where(final_prices > self.K, (final_prices - self.K)**self.exponent, 0)
        elif option_type == 'digital':
            # Berechnet Auszahlungen für digitale Optionen (binäre Optionen)
            if self.is_put:
                payoffs = np.where(final_prices < self.K, 1, 0)
            else:
                payoffs = np.where(final_prices > self.K, 1, 0)
        elif option_type == 'strangle':
            # Berechnet Auszahlungen für Strangle-Strategien
            call_payoffs = np.where(final_prices > self.K, final_prices - self.K, 0)
            put_payoffs = np.where(final_prices < self.K2, self.K2 - final_prices, 0)
            payoffs = call_payoffs + put_payoffs
        else:
            # Ausnahme werfen, wenn ein unbekannter Optionstyp übergeben wird
            raise ValueError("Unbekannter Optionstyp")

        return payoffs


    def init_full_tree(self, option_type):
        """
        Initialisiert den vollständigen Baum der Aktienkurse und berechnet daraufhin die Optionspreise sowie Delta-Werte für jede Periode.

        Diese Methode erstellt zunächst einen Baum der Aktienkurse, der auf den spezifizierten Bewegungsparametern (u für Aufwärtsbewegung, d für
        Abwärtsbewegung, m für mittlere Bewegung) und den zugehörigen Wahrscheinlichkeiten (pu, pm, pd) basiert. Anschließend werden basierend auf
        dem am Verfallstag ermittelten Payoff der Optionen die Optionspreise und Delta-Werte für jede Periode im Baum rückwärts berechnet. Die
        Methode unterstützt verschiedene Optionstypen und passt die Berechnung der finalen Auszahlungen und der rekursiven Preisbestimmung
        entsprechend an.

        Args:
            option_type (str): Der Typ der Option, für die der Baum initialisiert wird. Gültige Werte sind 'european', 'power', 'digital', 'strangle'.
                            Dies bestimmt, wie die finalen Auszahlungen berechnet und wie die Option durch den Baum bewertet wird.

        Raises:
            ValueError: Wird ausgelöst, wenn ein unbekannter Optionstyp spezifiziert wird.
        """
        # Initialisiert den Baum der Aktienkurse. Der mittlere Knoten bei t=0 wird auf den aktuellen Aktienkurs S0 gesetzt.
        self.stock_price_tree = np.zeros((self.N + 1, 2 * self.N + 1))
        self.stock_price_tree[0, self.N] = self.S0

        # Aufbau des Aktienkursbaums durch iterative Berechnung der Kurse für Auf-, Abwärts- und mittlere Bewegungen.
        for i in range(1, self.N + 1):
            for j in range(self.N - i, self.N + i + 1):
                self.stock_price_tree[i, j] = (
                    self.stock_price_tree[i - 1, j - 1] * self.u if j > self.N else (
                        self.stock_price_tree[i - 1, j + 1] * self.d if j < self.N else self.stock_price_tree[i - 1, j]
                    )
                )

        # Initialisierung der Bäume für Optionspreise und Delta-Werte mit Nullen.
        self.option_price_tree = np.zeros_like(self.stock_price_tree)
        self.delta_tree = np.zeros_like(self.stock_price_tree)

        # Berechnung der finalen Auszahlungen am Verfallstag basierend auf dem Optionstyp.
        self.option_price_tree[-1] = self.calculate_payoffs(option_type)

        # Rückwärtsberechnung der Optionspreise und Delta-Werte durch den Baum.
        for i in range(self.N - 1, -1, -1):
            for j in range(self.N - i, self.N + i + 1):
                up = self.option_price_tree[i + 1, j + 1]  # Optionspreis bei Aufwärtsbewegung
                mid = self.option_price_tree[i + 1, j]     # Optionspreis bei mittlerer Bewegung
                down = self.option_price_tree[i + 1, j - 1]  # Optionspreis bei Abwärtsbewegung
                # Berechnet den Optionspreis am aktuellen Knoten durch gewichtete Mittelung und Diskontierung.
                self.option_price_tree[i, j] = (self.pu * up + self.pm * mid + self.pd * down) * self.df

                # Berechnung von Delta, falls benötigt, zur Bestimmung der Hedge-Ratio.
                stock_up = self.stock_price_tree[i + 1, j + 1]   # Aktienkurs bei Aufwärtsbewegung
                stock_down = self.stock_price_tree[i + 1, j - 1]  # Aktienkurs bei Abwärtsbewegung
                # Delta wird berechnet als die Änderung des Optionspreises geteilt durch die Änderung des Aktienkurses.
                self.delta_tree[i, j] = (up - down) / (stock_up - stock_down) if stock_up != stock_down else 0

    def price_option(self, option_type):
        """
        Berechnet den Preis einer Option basierend auf dem angegebenen Optionstyp durch die Verwendung eines Trinomialbaums.

        Diese Methode initialisiert zuerst den vollständigen Trinomialbaum für den spezifizierten Optionstyp mittels der Methode `init_full_tree`.
        Anschließend wird der Preis der Option am Ursprung des Baumes zurückgegeben. Dieser Preis entspricht dem fairen Wert der Option unter den
        gegebenen Marktbedingungen und den Modellannahmen. Die Methode unterstützt verschiedene Optionstypen, darunter europäische, digitale,
        Power-Optionen und Strangles, und passt die Berechnung der Auszahlungen und die Preisbestimmung entsprechend an.

        Args:
            option_type (str): Der Typ der Option, die bewertet werden soll. Unterstützte Typen sind unter anderem 'european', 'digital',
                            'power', und 'strangle'. Die Auswahl bestimmt die Berechnungsmethodik der finalen Auszahlungen und die
                            anschließende Bewertung im Trinomialbaum.

        Returns:
            float: Der berechnete Preis der Option am Ursprung des Baumes. Dieser Wert repräsentiert den gegenwärtigen, fairen Wert der Option.

        Beispiel:
            >>> trinomial_model = Trinomialmodell(S0=100, K=100, T=1, r=0.05, N=50, sigma=0.2)
            >>> print(trinomial_model.price_option('european'))
            Der ausgegebene Wert ist der faire Preis der europäischen Option basierend auf dem Trinomialmodell.

        Hinweis:
            Die Genauigkeit des berechneten Optionspreises hängt von der Anzahl der Perioden im Baum (N) und den spezifizierten Modellparametern ab.
            Eine höhere Anzahl von Perioden kann zu einer genaueren Schätzung des fairen Werts führen, erfordert jedoch mehr Rechenzeit.
        """
        self.init_full_tree(option_type)  # Initialisiert den vollständigen Trinomialbaum für den gegebenen Optionstyp.
        return self.option_price_tree[0, self.N]  # Gibt den Preis der Option am Ursprung des Baumes zurück.
