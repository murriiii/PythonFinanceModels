import numpy as np
import matplotlib.pyplot as plt
from blackscholesmodel import BlackScholesModel
from trinomialmodell import Trinomialmodell
from binomialmodell import Binomialmodell

class FinanzPlot():
    """
    Diese Klasse bietet Werkzeuge zur Visualisierung verschiedener Finanzmodelle,
    einschließlich Binomialbäumen, Trinomialbäumen und dem Black-Scholes-Modell.
    Sie ermöglicht die Erstellung von Plots zur Darstellung von Optionspreisen,
    Payoff-Diagrammen und Konvergenzanalysen.

    Methoden der Klasse bieten Funktionen zum Zeichnen von Preisbäumen, zum
    Vergleichen von Modellpreisen mit dem Black-Scholes-Preis und zur Visualisierung
    von Optionsstrategien wie Strangles.

    Attributes:
        model (object): Ein Finanzmodell-Objekt, das visualisiert werden soll.
                        Unterstützt werden Modelle wie Binomialmodell,
                        Trinomialmodell und BlackScholesModel.
    """

    def __init__(self, model):
        """
        Initialisiert eine neue Instanz der Klasse mit einem spezifischen Finanzmodell.

        :param model: Das Finanzmodell-Objekt, das für Visualisierungen verwendet wird.
        """
        self.model = model

    def get_model_name(self):
        """
        Ermittelt den Namen des Finanzmodells, das derzeit von der Instanz der Klasse verwendet wird.
        Diese Methode unterstützt die Identifizierung des Modelltyps basierend auf der Instanzierung
        innerhalb der Klasse und ermöglicht es, den entsprechenden Namen als Zeichenkette zurückzugeben.

        :return: Eine Zeichenkette, die den Namen des verwendeten Finanzmodells darstellt. Die Methode
        unterstützt spezifisch 'Binomialbaum', 'Trinomialbaum' und 'Black-Scholes-Modell'. Für alle
        anderen Modelltypen wird generisch 'Modell' zurückgegeben.
        :rtype: str
        """
        # Überprüfe den Typ des Modells und gib den entsprechenden Namen zurück
        if isinstance(self.model, Binomialmodell):
            return "Binomialbaum"
        elif isinstance(self.model, Trinomialmodell):
            return "Trinomialbaum"
        elif isinstance(self.model, BlackScholesModel):
            return "Black-Scholes-Modell"
        else:
            return "Modell"

    def plot_option_tree_binomial(self, fig, ax, option_type='european'):
        """
        Visualisiert den Binomialbaum der Aktienkurse sowie die zugehörigen Optionspreise und Deltas
        (und Wahrscheinlichkeiten für die Endzustände) für eine gegebene Option. Die Visualisierung
        erfolgt in einem matplotlib Achsenobjekt.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Wird verwendet, um möglicherweise zusätzliche Plotelemente oder -einstellungen
        außerhalb dieser Methode anzupassen.
        :type fig: matplotlib.figure.Figure

        :param ax: Das Achsenobjekt von matplotlib, in dem der Binomialbaum gezeichnet wird. Dies
        ermöglicht die direkte Manipulation des Plots für Beschriftungen, Titel, Gitterlinien etc.
        :type ax: matplotlib.axes._subplots.AxesSubplot

        :param option_type: Der Typ der Option, die bewertet wird. Standardmäßig auf 'european' gesetzt,
        kann aber auch auf andere Optionstypen gesetzt werden, falls das Modell dies unterstützt.
        :type option_type: str

        :return: Keine Rückgabe. Die Methode modifiziert das übergebene Achsenobjekt `ax` direkt, um
        den Plot zu erstellen.
        :rtype: None
        """
        # Initialisiere den vollständigen Baum basierend auf dem gewählten Optionstyp
        self.model.init_full_tree(option_type=option_type)

        # Iteriere durch jeden Zeitpunkt bis zum letzten Schritt im Baum
        for i in range(self.model.N + 1):
            # Iteriere durch alle möglichen Zustände für jeden Zeitpunkt
            for j in range(i + 1):
                # Zeichne Verbindungslinien für alle Zustände, die nicht der letzte Zeitpunkt sind
                if i < self.model.N:
                    # Zeichne die Linie zum nächsten Zeitpunkt ohne Zustandsänderung
                    ax.plot([i, i + 1], [self.model.stock_price_tree[i, j], self.model.stock_price_tree[i + 1, j]], 'k-', lw=1)
                    # Zeichne die Linie zum nächsten Zeitpunkt mit Zustandsänderung
                    ax.plot([i, i + 1], [self.model.stock_price_tree[i, j], self.model.stock_price_tree[i + 1, j + 1]], 'k-', lw=1)

                # Berechne und formatiere die Anzeige von Optionspreis und Delta für jeden Knotenpunkt
                payoff_or_delta = f'{self.model.option_price_tree[i, j]:.2f}'
                if i < self.model.N:
                    payoff_or_delta += f'\nΔ{self.model.delta_tree[i, j]:.2f}'

                # Für den letzten Zeitpunkt, füge die Wahrscheinlichkeiten der Endzustände hinzu
                if i == self.model.N:
                    payoff_or_delta += f'\np={self.model.end_state_probabilities[j]:.2f}'

                # Füge den Text für Optionspreis, Delta und Wahrscheinlichkeiten zu jedem Knotenpunkt hinzu
                ax.text(i, self.model.stock_price_tree[i, j], payoff_or_delta, ha='center', va='bottom', fontsize=8)

        # Setze die Beschriftungen und Titel für die Achsen und den Plot
        ax.set_xlabel('Zeitschritt')
        ax.set_ylabel('Aktienkurs')
        ax.set_title(f'{self.get_model_name()} für {option_type.capitalize()} Optionen mit Optionspreisen und Deltas')
        # Aktiviere das Gitter für bessere Lesbarkeit
        ax.grid(True)

    def plot_option_tree_trinomial(self, fig, ax, option_type='european'):
        """
        Visualisiert den Trinomialbaum der Aktienkurse sowie die zugehörigen Optionspreise und Deltas
        für eine gegebene Option. Im Gegensatz zum Binomialbaum erlaubt der Trinomialbaum drei mögliche
        Zustände in jedem Schritt: eine Bewegung nach oben, unten oder eine Beibehaltung des aktuellen
        Kursniveaus. Die Visualisierung erfolgt in einem matplotlib Achsenobjekt.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Dies ermöglicht es, die Figur nach Bedarf anzupassen, beispielsweise durch
        Hinzufügen zusätzlicher Plotelemente.
        :type fig: matplotlib.figure.Figure

        :param ax: Das Achsenobjekt von matplotlib, in dem der Trinomialbaum gezeichnet wird. Dies
        ermöglicht die direkte Manipulation des Plots, einschließlich Beschriftungen, Titel und
        Gitterlinien.
        :type ax: matplotlib.axes._subplots.AxesSubplot

        :param option_type: Der Typ der Option, die bewertet wird, standardmäßig auf 'european'
        gesetzt. Dieser Parameter bestimmt, welche Art von Option (europäisch, amerikanisch etc.)
        visualisiert wird.
        :type option_type: str

        :return: Keine Rückgabe. Die Methode modifiziert das übergebene Achsenobjekt `ax` direkt,
        um den Plot zu erstellen.
        :rtype: None
        """
        # Initialisiere den vollständigen Baum für den gewählten Optionstyp
        self.model.init_full_tree(option_type=option_type)

        # Ersetze alle Nullen im Aktienkursbaum durch NaN, um sie in der Visualisierung auszuschließen
        y_positions = np.where(self.model.stock_price_tree != 0, self.model.stock_price_tree, np.nan)

        # Iteriere durch jeden Zeitpunkt bis zum Ende des Baums
        for i in range(self.model.N + 1):
            # Iteriere durch alle möglichen Zustände im Trinomialbaum
            for j in range(2 * self.model.N + 1):
                # Zeichne Verbindungslinien, wenn der aktuelle Zustand gültig ist (nicht NaN)
                if not np.isnan(y_positions[i, j]):
                    # Zeichne Linien zu den drei möglichen nächsten Zuständen, falls diese existieren
                    if i < self.model.N:
                        if j - 1 >= 0 and not np.isnan(y_positions[i + 1, j - 1]):
                            ax.plot([i, i + 1], [y_positions[i, j], y_positions[i + 1, j - 1]], 'k-', lw=1)
                        if not np.isnan(y_positions[i + 1, j]):
                            ax.plot([i, i + 1], [y_positions[i, j], y_positions[i + 1, j]], 'k-', lw=1)
                        if j + 1 <= 2 * self.model.N and not np.isnan(y_positions[i + 1, j + 1]):
                            ax.plot([i, i + 1], [y_positions[i, j], y_positions[i + 1, j + 1]], 'k-', lw=1)

                    # Füge Text für Optionspreise und Deltas an jedem Knotenpunkt hinzu
                    ax.text(i, y_positions[i, j], f'{self.model.option_price_tree[i, j]:.2f}\nΔ{self.model.delta_tree[i, j]:.2f}', ha='center', va='bottom', fontsize=8)

        # Setze die y-Achsenlimits, um sicherzustellen, dass alle Werte sichtbar sind
        ax.set_ylim(np.nanmin(y_positions) * 0.8, np.nanmax(y_positions) * 1.2)

        # Setze Achsenbeschriftungen und Titel
        ax.set_xlabel('Zeitschritt')
        ax.set_ylabel('Aktienkurs')
        ax.set_title(f'{self.get_model_name()} für {option_type.capitalize()} Optionen mit Optionspreisen und Deltas')

        # Aktiviere Gitterlinien für bessere Lesbarkeit
        ax.grid(True)

    def plot_convergence(self, fig, ax, convergence_prices=None):
        """
        Visualisiert die Konvergenz der durch das Baummodell (Binomial- oder Trinomialmodell) berechneten
        Optionspreise zum Black-Scholes-Preis. Die Methode kann entweder eine Liste von bereits
        berechneten Konvergenzpreisen verwenden oder die Preise basierend auf der aktuellen Modellkonfiguration
        neu berechnen.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Erlaubt die Anpassung der Figur, z.B. durch Hinzufügen weiterer Plotelemente.
        :type fig: matplotlib.figure.Figure

        :param ax: Das Achsenobjekt von matplotlib, in dem die Konvergenz visualisiert wird. Ermöglicht
        direkte Manipulation des Plots für Beschriftungen, Titel und Gitterlinien.
        :type ax: matplotlib.axes._subplots.AxesSubplot

        :param convergence_prices: Eine optionale Liste von Optionspreisen, die für die Konvergenzanalyse
        verwendet werden soll. Wenn None, berechnet die Methode die Preise neu basierend auf der
        aktuellen Konfiguration des Baummodells.
        :type convergence_prices: list, optional

        :return: Keine Rückgabe. Die Methode modifiziert das übergebene Achsenobjekt `ax` direkt,
        um den Plot zu erstellen.
        :rtype: None
        """
        # Wenn keine Konvergenzpreise gegeben sind, berechne die Preise neu
        if convergence_prices is None:
            # Definiere den Bereich der Schritte für die Neuberechnung
            max_steps = self.model.N
            steps_range = range(1, max_steps + 1)
            option_prices = []
            # Initialisiere das Black-Scholes-Modell für die Vergleichsberechnung
            bs_model = BlackScholesModel(self.model.S0, self.model.K, self.model.T, self.model.r, self.model.sigma, self.model.div)
            bs_price = bs_model.call_price() if not self.model.is_put else bs_model.put_price()
            original_N = self.model.N
            model_type = type(self.model)
            # Berechne Optionspreise für verschiedene Schrittanzahlen
            for N in steps_range:
                new_model_instance = model_type(self.model.S0, self.model.K, self.model.T, self.model.r, N, self.model.sigma, is_put=self.model.is_put)
                price = new_model_instance.price_option("european")
                option_prices.append(price)
            self.model.N = original_N
        else:
            # Verwende die gegebenen Konvergenzpreise
            option_prices = convergence_prices
            steps_range = range(1, len(convergence_prices) + 1)
            bs_model = BlackScholesModel(self.model.S0, self.model.K, self.model.T, self.model.r, self.model.sigma, self.model.div)
            bs_price = bs_model.call_price() if not self.model.is_put else bs_model.put_price()
            model_type = type(self.model)

        # Visualisiere die Konvergenz der Optionspreise zum Black-Scholes-Preis
        ax.plot(steps_range, option_prices, label='Optionspreis')
        ax.axhline(y=bs_price, color='r', linestyle='-', label='Black-Scholes Preis')
        ax.set_xlabel('Zeitschritte')
        ax.set_ylabel('Optionspreis')
        ax.set_title(f'Konvergenz des {model_type.__name__} Modells zum Black-Scholes-Preis')
        ax.legend()

    def plot_convergence_comparison(self, fig, ax, convergence_bm, convergence_tm, option_type='european'):
        """
        Visualisiert einen Vergleich der Konvergenz von Optionspreisen, berechnet mittels Binomial-
        und Trinomialmodellen, zum Black-Scholes-Preis. Dies ermöglicht die Beurteilung des Konvergenzverhaltens
        beider Modelle im Vergleich zum analytischen Black-Scholes-Modell.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Ermöglicht die Anpassung der Figur, z.B. durch Hinzufügen weiterer Plotelemente.
        :type fig: matplotlib.figure.Figure

        :param ax: Das Achsenobjekt von matplotlib, in dem der Konvergenzvergleich visualisiert wird.
        Ermöglicht direkte Manipulation des Plots für Beschriftungen, Titel und Gitterlinien.
        :type ax: matplotlib.axes._subplots.AxesSubplot

        :param convergence_bm: Eine Liste der Optionspreise, berechnet mit dem Binomialmodell, für
        verschiedene Anzahlen von Zeitschritten. Wenn None, wird eine leere Liste angenommen.
        :type convergence_bm: list, optional

        :param convergence_tm: Eine Liste der Optionspreise, berechnet mit dem Trinomialmodell, für
        verschiedene Anzahlen von Zeitschritten. Wenn None, wird eine leere Liste angenommen.
        :type convergence_tm: list, optional

        :param option_type: Der Typ der Option, die bewertet wird, standardmäßig auf 'european' gesetzt.
        Dieser Parameter bestimmt, welche Art von Option (europäisch, amerikanisch etc.) visualisiert wird.
        :type option_type: str

        :return: Keine Rückgabe. Die Methode modifiziert das übergebene Achsenobjekt `ax` direkt,
        um den Plot zu erstellen.
        :rtype: None
        """
        # Prüfe, ob Konvergenzlisten übergeben wurden, sonst verwende leere Listen
        convergence_bm = convergence_bm if convergence_bm is not None else []
        convergence_tm = convergence_tm if convergence_tm is not None else []

        # Initialisiere das Black-Scholes-Modell für die Vergleichsberechnung
        bs_model = BlackScholesModel(self.model.S0, self.model.K, self.model.T, self.model.r, self.model.sigma, self.model.div)
        bs_price = bs_model.call_price() if not self.model.is_put else bs_model.put_price()

        # Definiere den Bereich der Zeitschritte für die Konvergenzbetrachtung
        max_steps = self.model.N
        steps_range = range(1, max_steps + 1)

        # Visualisiere die Konvergenz der Optionspreise beider Modelle zum Black-Scholes-Preis
        ax.plot(steps_range, convergence_bm, label='Binomialmodell Preis')
        ax.plot(steps_range, convergence_tm, label='Trinomialmodell Preis')
        ax.axhline(y=bs_price, color='r', linestyle='-', label='Black-Scholes Preis')

        # Setze Achsenbeschriftungen und Titel
        ax.set_xlabel('Zeitschritte')
        ax.set_ylabel('Optionspreis')
        ax.set_title(f'Konvergenzvergleich')
        ax.legend()

    def plot_digital_option_prices(self, fig, ax, percentage_range=20, steps=100):
        """
        Visualisiert die Preisentwicklung digitaler Optionen (Call oder Put) in Abhängigkeit vom
        Basiswert S0. Die Preise werden für ein Spektrum von S0-Werten berechnet, das sich um einen
        bestimmten Prozentsatz über und unter dem aktuellen S0-Wert erstreckt.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Ermöglicht die Anpassung der Figur, z.B. durch Hinzufügen weiterer Plotelemente.
        :type fig: matplotlib.figure.Figure

        :param ax: Das Achsenobjekt von matplotlib, in dem die Preisentwicklung visualisiert wird.
        Ermöglicht direkte Manipulation des Plots für Beschriftungen, Titel und Gitterlinien.
        :type ax: matplotlib.axes._subplots.AxesSubplot

        :param percentage_range: Der Prozentsatz, um den der Basiswert S0 nach oben und unten variiert
        wird, um das Spektrum der S0-Werte zu erzeugen. Standardmäßig auf 20% gesetzt.
        :type percentage_range: int, optional

        :param steps: Die Anzahl der Schritte innerhalb des S0-Spektrums, für die der Preis der digitalen
        Option berechnet wird. Bestimmt die Granularität der Visualisierung. Standardmäßig auf 100 gesetzt.
        :type steps: int, optional

        :return: Keine Rückgabe. Die Methode modifiziert das übergebene Achsenobjekt `ax` direkt,
        um den Plot zu erstellen.
        :rtype: None
        """
        # Berechne die Grenzen des S0-Spektrums basierend auf dem angegebenen Prozentsatz
        lower_bound = self.model.S0 * (1 - percentage_range / 100)
        upper_bound = self.model.S0 * (1 + percentage_range / 100)
        S0_range = np.linspace(lower_bound, upper_bound, steps)

        option_prices = []
        original_S0 = self.model.S0  # Speichere den ursprünglichen S0-Wert

        # Berechne die Preise der digitalen Optionen für jedes S0 im Spektrum
        for S0 in S0_range:
            self.model.S0 = S0  # Aktualisiere den Basiswert S0
            self.model.init_full_tree(option_type='digital')  # Initialisiere den Baum für digitale Optionen
            option_prices.append(self.model.price_option('digital'))  # Berechne den Optionspreis und füge ihn zur Liste hinzu

        self.model.S0 = original_S0  # Setze den ursprünglichen S0-Wert zurück

        # Visualisiere die Preisentwicklung
        ax.plot(S0_range, option_prices, label=f'Digitale {"Put" if self.model.is_put else "Call"} Option')
        ax.set_title(f'Preis der digitalen {"Put" if self.model.is_put else "Call"} Option in Abhängigkeit vom Basiswert (S0)')
        ax.set_xlabel('Basiswert (S0)')
        ax.set_ylabel('Optionspreis')
        ax.legend()
        ax.grid(True)

    def plot_power_option_2d_auto_range(self, fig, ax):
        """
        Visualisiert die Preisentwicklung von Power-Optionen in einem 2D-Diagramm, abhängig vom
        Basiswert S0. Die Funktion berechnet Power-Optionspreise für ein Spektrum von S0-Werten,
        die um einen festgelegten Prozentsatz über und unter dem aktuellen S0-Wert des Modells liegen.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Ermöglicht die Anpassung der Figur, z.B. durch Hinzufügen weiterer Plotelemente.
        :type fig: matplotlib.figure.Figure

        :param ax: Das Achsenobjekt von matplotlib, in dem die Preisentwicklung der Power-Optionen
        visualisiert wird. Ermöglicht direkte Manipulation des Plots für Beschriftungen, Titel und
        Gitterlinien.
        :type ax: matplotlib.axes._subplots.AxesSubplot

        :return: Keine Rückgabe. Die Methode modifiziert das übergebene Achsenobjekt `ax` direkt,
        um den Plot zu erstellen.
        :rtype: None
        """
        # Definiere das Spektrum von S0-Werten, basierend auf einem Prozentsatz um den aktuellen S0-Wert
        S0_base = self.model.S0
        S0_range = (S0_base * 0.8, S0_base * 1.2)
        S0_prices = np.linspace(S0_range[0], S0_range[1], 100)

        power_option_prices = []
        # Berechne Power-Optionspreise für das definierte S0-Spektrum
        for S0 in S0_prices:
            self.model.S0 = S0  # Aktualisiere den Basiswert S0
            price = self.model.price_option('power')  # Berechne den Preis der Power-Option
            power_option_prices.append(price)  # Füge den berechneten Preis zur Liste hinzu

        # Visualisiere die Preisentwicklung in Abhängigkeit vom Basiswert S0
        ax.plot(S0_prices, power_option_prices, label='Power-Optionspreis')
        ax.set_xlabel('Basiswert (S0)')
        ax.set_ylabel('Power-Optionspreis')
        ax.set_title('2D-Diagramm des Power-Optionspreises gegenüber dem Basiswert')
        ax.legend()
        ax.grid(True)

    def plot_power_option_3d_auto_range(self, fig, ax):
        """
        Visualisiert die Preisentwicklung von Power-Optionen in einem 3D-Diagramm, abhängig vom
        Basiswert S0 und der Restlaufzeit T. Diese Methode berechnet die Preise von Power-Optionen
        für ein Spektrum von S0- und T-Werten, die um einen festgelegten Prozentsatz bzw. Faktor
        über und unter den aktuellen Werten des Modells liegen.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Erlaubt die Anpassung der Figur, z.B. durch Hinzufügen weiterer Plotelemente
        oder Einstellung der Farbskala.
        :type fig: matplotlib.figure.Figure

        :param ax: Das Achsenobjekt von matplotlib für 3D-Plots, in dem die Preisentwicklung der
        Power-Optionen visualisiert wird. Muss ein Achsenobjekt sein, das für 3D-Visualisierungen
        vorbereitet ist (z.B. erstellt mit `fig.add_subplot(111, projection='3d')`).
        :type ax: matplotlib.axes._subplots.Axes3DSubplot

        :return: Keine Rückgabe. Die Methode modifiziert das übergebene Achsenobjekt `ax` direkt,
        um den Plot zu erstellen.
        :rtype: None
        """
        # Definiere die Bereiche für S0 und T basierend auf den aktuellen Werten
        S0_base = self.model.S0
        T_base = self.model.T
        S0_range = (S0_base * 0.8, S0_base * 1.2)
        T_range = (T_base * 0.5, T_base * 1.5)

        # Erstelle Gitter von S0- und T-Werten für die Visualisierung
        S0_values = np.linspace(S0_range[0], S0_range[1], 50)
        T_values = np.linspace(T_range[0], T_range[1], 50)
        S0_grid, T_grid = np.meshgrid(S0_values, T_values)

        # Initialisiere das Array für die Power-Optionspreise
        power_option_prices = np.zeros(S0_grid.shape)

        # Berechne die Power-Optionspreise für jedes Paar von S0- und T-Werten
        for i in range(S0_grid.shape[0]):
            for j in range(S0_grid.shape[1]):
                self.model.S0 = S0_grid[i, j]
                self.model.T = T_grid[i, j]
                power_option_prices[i, j] = self.model.price_option('power')

        # Visualisiere die Preisentwicklung in einem 3D-Surface-Plot
        surf = ax.plot_surface(S0_grid, T_grid, power_option_prices, cmap='viridis')
        # Füge eine Farblegende hinzu
        fig.colorbar(surf, shrink=0.5, aspect=5)

        # Setze die Achsenbeschriftungen und den Titel
        ax.set_xlabel('Basiswert (S0)')
        ax.set_ylabel('Restlaufzeit (T)')
        ax.set_zlabel('Power-Optionspreis')
        ax.set_title('3D-Diagramm des Power-Optionspreises gegenüber S0 und T')

    def plot_strangle(self, fig, ax_long, ax_short, option_params=None):
        """
        Visualisiert die Payoff-Profile für Long und Short Strangle-Optionsstrategien. Eine Strangle-Strategie
        besteht aus dem Kauf oder Verkauf sowohl einer Call- als auch einer Put-Option mit unterschiedlichen
        Strike-Preisen, aber demselben Verfallsdatum.

        :param fig: Eine Referenz auf das Figure-Objekt von matplotlib, in dem die Visualisierung
        erfolgen soll. Ermöglicht die Anpassung der Figur, z.B. durch Hinzufügen weiterer Plotelemente.
        :type fig: matplotlib.figure.Figure

        :param ax_long: Das Achsenobjekt von matplotlib für die Visualisierung des Long Strangle Payoffs.
        :type ax_long: matplotlib.axes._subplots.AxesSubplot

        :param ax_short: Das Achsenobjekt von matplotlib für die Visualisierung des Short Strangle Payoffs.
        :type ax_short: matplotlib.axes._subplots.AxesSubplot

        :param option_params: Ein optionales Dictionary mit Parametern für die Strangle-Strategie,
        einschließlich der Strike-Preise und Prämien für Call- und Put-Optionen. Wenn None, werden
        Standardwerte basierend auf dem aktuellen Modell verwendet.
        :type option_params: dict, optional

        :return: Keine Rückgabe. Die Methode modifiziert die übergebenen Achsenobjekte `ax_long` und
        `ax_short` direkt, um die Plots zu erstellen.
        :rtype: None
        """
        # Prüfe, ob benutzerdefinierte Optionen-Parameter übergeben wurden, sonst verwende Standardwerte
        if option_params is None:
            model_type = type(self.model)
            call_price = model_type(S0=self.model.S0, K=self.model.K, T=self.model.T, r=self.model.r, N=self.model.N, sigma=self.model.sigma, is_put=False).price_option('european')
            put_price = model_type(S0=self.model.S0, K=self.model.K2, T=self.model.T, r=self.model.r, N=self.model.N, sigma=self.model.sigma, is_put=True).price_option('european')
            option_params = {
                'put_strike': self.model.K2,
                'call_strike': self.model.K,
                'put_premium': put_price,
                'call_premium': call_price
            }

        # Extrahiere die Parameter für die Strangle-Strategie
        S0 = self.model.S0
        K_call = option_params['call_strike']
        K_put = option_params['put_strike']
        P_call = option_params['call_premium']
        P_put = option_params['put_premium']

        # Erstelle ein Array mit möglichen Endpreisen des Basiswerts
        S = np.arange(0.5 * S0, 1.5 * S0, 1)

        # Berechne den Payoff für die Call- und Put-Optionen
        Payoff_call = np.maximum(S - K_call, 0) - P_call
        Payoff_put = np.maximum(K_put - S, 0) - P_put

        # Berechne den Gesamtpayoff für die Long und Short Strangle-Strategien
        Payoff_strangle_long = Payoff_call + Payoff_put
        Payoff_strangle_short = -Payoff_strangle_long

        # Visualisiere die Payoff-Profile für beide Strategien
        for ax, payoff, title, color in zip([ax_long, ax_short],
                                            [Payoff_strangle_long, Payoff_strangle_short],
                                            ['Long Strangle Optionsstrategie Payoff', 'Short Strangle Optionsstrategie Payoff'],
                                            ['black', 'red']):
            ax.plot(S, Payoff_call, '--', label='Call Option Payoff')
            ax.plot(S, Payoff_put, '--', label='Put Option Payoff')
            ax.plot(S, payoff, label=title, linewidth=2, color=color)
            ax.set_xlabel('Basiswert am Verfallstag')
            ax.set_ylabel('Payoff')
            ax.set_title(title)
            ax.legend()
            ax.grid(True)




