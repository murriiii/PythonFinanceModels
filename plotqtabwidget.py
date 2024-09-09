import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QTabWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from finance_plot import FinanzPlot
from binomialmodell import Binomialmodell
from mpl_toolkits.mplot3d import Axes3D

class PlotCanvas(FigureCanvas):
    """
    Eine spezialisierte Canvas-Klasse für die Darstellung von Finanzmodell-Plots innerhalb
    einer PyQt6-Anwendung. Diese Klasse erbt von FigureCanvasQTAgg und integriert Matplotlib-Figuren
    in die Qt-Anwendung, um verschiedene Finanzplots darzustellen. Sie unterstützt die Visualisierung
    von Binomial- und Trinomialbäumen, Konvergenzanalysen, sowie spezifische Optionsstrategien
    wie Strangles in einem Qt-Widget.

    Attributes:
        fig (matplotlib.figure.Figure): Die Figur, die für die Plot-Darstellung verwendet wird.
        ax (matplotlib.axes._subplots.AxesSubplot/Axes3DSubplot): Die Achse oder Achsen, auf denen
            die Plots gezeichnet werden.
    """
    def __init__(self, plot_finanz, plot_method, plot_args=None, convergence_prices=None, parent=None, width=5, height=4, dpi=100):
        """
        Initialisiert die PlotCanvas-Instanz mit einer Figur und Achsen für die Darstellung und
        ruft die spezifizierte Plot-Methode des FinanzPlot-Objekts auf.

        :param plot_finanz: Eine Instanz der FinanzPlot-Klasse, die die Plot-Methoden enthält.
        :param plot_method: Der Name der Methode als Zeichenkette, die aus plot_finanz aufgerufen
            werden soll, um den Plot zu erstellen.
        :param plot_args: Eine Liste von Argumenten, die an die Plot-Methode übergeben werden.
            Standardmäßig None.
        :param convergence_prices: Spezifische Preise für Konvergenzplots, falls erforderlich.
            Standardmäßig None.
        :param parent: Das Eltern-QWidget, zu dem diese Canvas gehört. Standardmäßig None.
        :param width: Die Breite der Figur in Zoll. Standardmäßig 5.
        :param height: Die Höhe der Figur in Zoll. Standardmäßig 4.
        :param dpi: Die Auflösung der Figur in Punkten pro Zoll. Standardmäßig 100.
        """
        self.init_figure(width, height, dpi)
        self.setParent(parent)

        self.handle_plot(plot_finanz, plot_method, plot_args, convergence_prices)
        self.draw()

    def init_figure(self, width, height, dpi):
        """
        Initialisiert eine Matplotlib-Figur und eine zugehörige Achse (oder Achsen) für die 
        Darstellung von Plots. Diese Methode erstellt eine Figur mit den spezifizierten 
        Dimensionen und Auflösung und fügt ihr eine Achse hinzu. Anschließend wird die Figur 
        in die FigureCanvasQTAgg-Instanz integriert, um die Darstellung innerhalb einer PyQt-Anwendung 
        zu ermöglichen.

        :param width: Die Breite der zu erstellenden Figur in Zoll.
        :type width: float

        :param height: Die Höhe der zu erstellenden Figur in Zoll.
        :type height: float

        :param dpi: Die Auflösung der Figur in Punkten pro Zoll (Dots Per Inch).
        :type dpi: float
        """
        # Erstelle eine neue Figur mit den gegebenen Dimensionen und Auflösung
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        # Füge der Figur eine Achse hinzu
        self.ax = self.fig.add_subplot(111)

        # Initialisiere das FigureCanvasQTAgg-Objekt mit der erstellten Figur
        FigureCanvas.__init__(self, self.fig)

    def handle_plot(self, plot_finanz, plot_method, plot_args, convergence_prices):
        """
        Ruft die angegebene Plot-Methode des FinanzPlot-Objekts auf, um einen spezifischen 
        Finanzplot zu erstellen. Diese Methode ermöglicht die dynamische Auswahl und Ausführung 
        von Plot-Methoden basierend auf dem übergebenen Methodennamen und optionalen Argumenten. 
        Sie behandelt auch spezielle Fälle, wie die Visualisierung von Konvergenzplots oder die 
        Erstellung von 3D-Plots, durch Anpassung der Achsenkonfiguration.

        :param plot_finanz: Eine Instanz der FinanzPlot-Klasse, die die zu verwendenden 
            Plot-Methoden enthält.
        :type plot_finanz: FinanzPlot

        :param plot_method: Der Name der Plot-Methode als Zeichenkette, die aus `plot_finanz` 
            aufgerufen werden soll.
        :type plot_method: str

        :param plot_args: Eine Liste von Argumenten, die an die Plot-Methode übergeben werden. 
            Standardmäßig eine leere Liste, wenn `None` übergeben wird.
        :type plot_args: list

        :param convergence_prices: Spezifische Preise für Konvergenzplots, falls erforderlich. 
            Wird nur verwendet, wenn `plot_method` "plot_convergence" ist.
        :type convergence_prices: list

        """
        # Stelle sicher, dass plot_args eine Liste ist, falls None übergeben wurde
        plot_args = plot_args if plot_args is not None else []

        # Behandle spezielle Plot-Methoden und passe die Plot-Umgebung entsprechend an
        if plot_method == "plot_convergence" and convergence_prices:
            # Rufe die Konvergenzplot-Methode auf, wenn spezifische Konvergenzpreise übergeben wurden
            plot_finanz.plot_convergence(self.fig, self.ax, convergence_prices)
        elif plot_method == "plot_strangle":
            # Für Strangle-Plots, rufe die spezielle Methode plot_strangle auf
            self.plot_strangle(plot_finanz)
        elif plot_method == "plot_power_option_3d_auto_range":
            # Für 3D-Power-Option-Plots, passe die Achsenkonfiguration an und rufe die Methode auf
            self.ax.remove()
            self.ax = self.fig.add_subplot(111, projection='3d')
            getattr(plot_finanz, plot_method)(self.fig, self.ax, *plot_args)
        else:
            # Für alle anderen Methoden, rufe die angegebene Methode mit den übergebenen Argumenten auf
            getattr(plot_finanz, plot_method)(self.fig, self.ax, *plot_args)

    def plot_strangle(self, plot_finanz):
        """
        Spezialisierte Methode zur Visualisierung der Payoff-Diagramme einer Strangle-Optionsstrategie
        für Long und Short Positionen. Diese Methode passt die aktuelle Figurenkonfiguration an, um
        zwei separate Subplots für die Long- und Short-Strangle-Strategien zu erstellen. Es wird
        die entsprechende Plot-Methode des übergebenen FinanzPlot-Objekts aufgerufen, um die
        Payoff-Diagramme zu zeichnen.

        :param plot_finanz: Eine Instanz der FinanzPlot-Klasse, die die Methode zur Erstellung
            der Strangle-Plot-Diagramme enthält.
        :type plot_finanz: FinanzPlot
        """
        # Entferne die aktuelle Achse, um die Figure für neue Subplots vorzubereiten
        self.ax.remove()

        # Erstelle zwei Subplots in der Figur für die Long- und Short-Strangle-Diagramme
        ax_long = self.fig.add_subplot(121)  # Subplot für die Long-Strangle-Strategie
        ax_short = self.fig.add_subplot(122)  # Subplot für die Short-Strangle-Strategie

        # Rufe die Plot-Methode für Strangle auf dem FinanzPlot-Objekt auf, übergebe die neuen Achsen
        plot_finanz.plot_strangle(self.fig, ax_long, ax_short)

class PlotQTabWidget(QWidget):
    """
    Ein Widget für die Anzeige verschiedener Finanzplots in einem tabbasierten Layout innerhalb
    einer PyQt-Anwendung. Diese Klasse erstellt ein QTabWidget und fügt Tabs für die Visualisierung
    verschiedener Arten von Finanzanalysen hinzu, darunter Optionenbaum-Darstellungen,
    Konvergenzanalysen, sowie spezifische Optionsstrategien.

    Die Klasse ermöglicht die dynamische Erstellung von Tabs basierend auf dem übergebenen
    Optionstyp und anderen Parametern. Jeder Tab enthält eine PlotCanvas-Instanz für die
    Visualisierung des entsprechenden Finanzplots.

    Attributes:
        plot_finanz (FinanzPlot): Eine Instanz der FinanzPlot-Klasse, die für die Erstellung
                                  der Finanzplots verwendet wird.
        option_type (str): Der Typ der Option, die visualisiert wird (z.B. "european", "digital").
        verfahren (str): Gibt an, welches Modell verwendet wird ("Binomialmodell" oder "Trinomialmodell").
        sigma_bekannt (bool): Ein Flag, das angibt, ob die Volatilität bekannt ist. Standardmäßig True.
        convergence_prices_BM (list): Eine Liste mit Konvergenzpreisen für das Binomialmodell.
        convergence_prices_TM (list): Eine Liste mit Konvergenzpreisen für das Trinomialmodell.
    """
    def __init__(self, plot_finanz, option_type, verfahren, sigma_bekannt=True, convergence_prices_BM=None, convergence_prices_TM=None):
        """
        Initialisiert das PlotQTabWidget mit den notwendigen Parametern für die Darstellung
        der Finanzplots und ruft die Methode zur UI-Initialisierung auf.

        :param plot_finanz: Eine Instanz der FinanzPlot-Klasse.
        :param option_type: Der Typ der zu visualisierenden Option ("european", "digital", etc.).
        :param verfahren: Das zu verwendende Finanzmodell ("Binomialmodell" oder "Trinomialmodell").
        :param sigma_bekannt: Gibt an, ob die Volatilität bekannt ist. Standardmäßig True.
        :param convergence_prices_BM: Konvergenzpreise für das Binomialmodell, falls vorhanden.
        :param convergence_prices_TM: Konvergenzpreise für das Trinomialmodell, falls vorhanden.
        """
        super().__init__()
        self.initUI(plot_finanz, option_type, verfahren, sigma_bekannt, convergence_prices_BM, convergence_prices_TM)

    def initUI(self, plot_finanz, option_type, verfahren, sigma_bekannt=True, convergence_prices_BM=None, convergence_prices_TM=None):
        """
        Initialisiert die Benutzeroberfläche des Widgets, indem es verschiedene Tabs für die
        Visualisierung von Finanzplots basierend auf dem spezifizierten Optionstyp und Modellverfahren
        hinzufügt. Die Methode konfiguriert das Layout und fügt entsprechende Tabs zum QTabWidget hinzu,
        je nachdem, welche Finanzanalysen und -strategien visualisiert werden sollen.

        :param plot_finanz: Eine Instanz der FinanzPlot-Klasse zur Nutzung der Plot-Methoden.
        :param option_type: Der Typ der zu visualisierenden Option (z.B. "european", "digital").
        :param verfahren: Das verwendete Finanzmodellverfahren ("Binomialmodell" oder "Trinomialmodell").
        :param sigma_bekannt: Flag, das angibt, ob die Volatilität bekannt ist (default ist True).
        :param convergence_prices_BM: Eine Liste mit Konvergenzpreisen für das Binomialmodell.
        :param convergence_prices_TM: Eine Liste mit Konvergenzpreisen für das Trinomialmodell.
        """
        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        # Wähle die passende Plot-Methode basierend auf dem spezifizierten Verfahren
        plot_method = "plot_option_tree_binomial" if verfahren == "Binomialmodell" else "plot_option_tree_trinomial"
        self.add_tab(tab_widget, plot_finanz, plot_method, [option_type], "Plot Baum")

        # Füge Tabs für spezifische Analysen und Optionstypen hinzu
        if option_type == "european" and sigma_bekannt:
            self.add_tab(tab_widget, plot_finanz, "plot_convergence",
                        convergence_prices=convergence_prices_BM if verfahren == "Binomialmodell" else convergence_prices_TM,
                        title="Konvergenz-Analyse (1/2)")
            self.add_tab(tab_widget, plot_finanz, "plot_convergence_comparison",
                        plot_args=[convergence_prices_BM, convergence_prices_TM],
                        title="Konvergenz-Analyse (2/2)")
        elif option_type == "digital":
            self.add_tab(tab_widget, plot_finanz, "plot_digital_option_prices", title="Plot Other")
        elif option_type == "power":
            self.add_tab(tab_widget, plot_finanz, "plot_power_option_2d_auto_range", title="Other 1/2")
            self.add_tab(tab_widget, plot_finanz, "plot_power_option_3d_auto_range", title="Other 2/2")
        elif option_type == "strangle" and sigma_bekannt:
            self.add_tab(tab_widget, plot_finanz, "plot_strangle", title="Other")

        layout.addWidget(tab_widget)
        self.setLayout(layout)
        self.setWindowTitle('Matplotlib in Qt Tabs')
        self.setGeometry(100, 100, 800, 600)

    def add_tab(self, tab_widget, plot_finanz, plot_method, plot_args=[], title="Tab", **kwargs):
        """
        Fügt dem übergebenen QTabWidget einen neuen Tab hinzu, der eine PlotCanvas-Instanz für
        die Darstellung eines spezifischen Finanzplots enthält. Diese Methode erlaubt es,
        dynamisch Tabs basierend auf den gewünschten Finanzanalysen und -strategien zu erstellen.

        :param tab_widget: Das QTabWidget-Objekt, zu dem der neue Tab hinzugefügt werden soll.
        :type tab_widget: QTabWidget

        :param plot_finanz: Eine Instanz der FinanzPlot-Klasse, die für die Erstellung der
            Finanzplots verwendet wird.
        :type plot_finanz: FinanzPlot

        :param plot_method: Der Name der Plot-Methode als Zeichenkette, die auf `plot_finanz`
            aufgerufen werden soll, um den Plot zu erstellen.
        :type plot_method: str

        :param plot_args: Eine Liste von Argumenten, die an die Plot-Methode übergeben werden.
            Standardmäßig eine leere Liste.
        :type plot_args: list, optional

        :param title: Der Titel des Tabs. Standardmäßig "Tab".
        :type title: str

        :param kwargs: Zusätzliche Schlüsselwortargumente, die an die PlotCanvas-Instanz
            übergeben werden, wie z.B. die Dimensionen und Auflösung der Figur.
        """
        tab = QWidget()  # Erstelle ein neues QWidget für den Tab
        tab_layout = QVBoxLayout()  # Erstelle ein vertikales Layout für den Tab-Inhalt

        # Erstelle eine PlotCanvas-Instanz mit den übergebenen Parametern
        plotCanvas = PlotCanvas(plot_finanz, plot_method, plot_args, **kwargs)

        # Füge die PlotCanvas-Instanz dem Tab-Layout hinzu
        tab_layout.addWidget(plotCanvas)

        # Setze das Layout für den Tab
        tab.setLayout(tab_layout)

        # Füge den Tab mit dem spezifizierten Titel zum Tab-Widget hinzu
        tab_widget.addTab(tab, title)
