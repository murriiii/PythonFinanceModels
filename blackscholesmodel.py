import numpy as np
from scipy.stats import norm

class BlackScholesModel:
    """
    Das Black-Scholes-Modell ist ein fundamentales Konzept in der Finanzmathematik und wird zur Bewertung der Preise
    europäischer Call- und Put-Optionen verwendet. Das Modell basiert auf der Annahme, dass die Preise des Basiswerts
    einer log-normalen Verteilung folgen und nimmt kontinuierliches Trading sowie keine Arbitragemöglichkeiten an.
    Es ermöglicht die Bewertung von Optionen unter Berücksichtigung verschiedener Faktoren wie dem aktuellen Preis des
    Basiswerts, dem Ausübungspreis der Option, der Restlaufzeit bis zur Ausübung, dem risikofreien Zinssatz und der
    Volatilität des Basiswerts. Zusätzlich kann eine kontinuierliche Dividendenrate berücksichtigt werden.

    Das Modell liefert geschlossene Lösungen für die Preise von europäischen Call- und Put-Optionen, die es zu einem
    unverzichtbaren Werkzeug für Trader und Analysten macht. Es dient auch als Grundlage für die Entwicklung
    komplexerer Optionspreismodelle und -strategien.

    Hinweis: Das Black-Scholes-Modell ist auf europäische Optionen beschränkt, die nur am Verfallstag ausgeübt
    werden können. Es berücksichtigt keine amerikanischen Optionen, die jederzeit vor dem Verfall ausgeübt
    werden können.
    """
    def __init__(self, S, K, T, r, sigma, div=0):
        """
        Initialisiert eine neue Instanz des Black-Scholes-Modells zur Bewertung von Optionen.

        Args:
            S (float): Der aktuelle Preis des Basiswerts (z.B. Aktienkurs).
            K (float): Der Ausübungspreis der Option.
            T (float): Die Restlaufzeit der Option in Jahren (z.B. 0,5 für sechs Monate).
            r (float): Der risikofreie Zinssatz, ausgedrückt als kontinuierliche Rate.
            sigma (float): Die Volatilität des Basiswerts, ausgedrückt als Standardabweichung der logarithmierten Renditen.
            div (float, optional): Die kontinuierliche Dividendenrate des Basiswerts. Standardwert ist 0, was bedeutet, dass keine
                                Dividenden berücksichtigt werden.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2)
            Dies initialisiert ein Black-Scholes-Modell für eine Option mit einem Basispreis von 100, einer Restlaufzeit von einem Jahr,
            einem risikofreien Zinssatz von 5% und einer Volatilität von 20%.

        Hinweis:
            Dieses Modell berücksichtigt keine amerikanischen Optionen, da es von einer europäischen Ausübungsart ausgeht, bei der Optionen
            nur am Verfallstag ausgeübt werden können.
        """
        self.S = S
        self.T = T
        self.r = r
        self.sigma = sigma
        self.K = K  # Standard-Ausübungspreis
        self.div = div  # Kontinuierliche Dividendenrate, standardmäßig auf 0 gesetzt, falls nicht anders angegeben.

    def d1(self, K):
        """
        Berechnet den Wert von d1, eine Schlüsselkomponente in den Black-Scholes-Formeln für die Bewertung von Optionen.

        Der Wert von d1 ist ein Faktor in den Formeln zur Berechnung des Preises europäischer Call- und Put-Optionen sowie in den
        Formeln für die Delta-Werte dieser Optionen. d1 berücksichtigt den aktuellen Preis des Basiswerts, den Ausübungspreis der Option,
        die Restlaufzeit bis zur Fälligkeit, den risikofreien Zinssatz, die Volatilität des Basiswerts und die Dividendenrate.

        Args:
            K (float): Der Ausübungspreis der Option, für die d1 berechnet wird. Dies ermöglicht die Berechnung von d1 für verschiedene
                    Ausübungspreise innerhalb des gleichen Modells, ohne das Modell neu initialisieren zu müssen.

        Returns:
            float: Der berechnete Wert von d1, der in weiteren Berechnungen innerhalb des Black-Scholes-Modells verwendet wird.

        Beispiel:
            >>> model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0)
            >>> print(model.d1(K=100))
            Dies gibt den Wert von d1 zurück, basierend auf den gegebenen Parametern des Modells und einem Ausübungspreis von 100.

        Hinweis:
            Der Wert von d1 ist direkt abhängig von den Modellparametern und dem spezifizierten Ausübungspreis. Änderungen an den
            Parametern des Modells oder am Ausübungspreis führen zu unterschiedlichen Werten von d1.
        """
        return (np.log(self.S / K) + (self.r - self.div + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))

    def d2(self, K):
        """
        Berechnet den Wert von d2, der für die Bestimmung der Optionspreise im Black-Scholes-Modell benötigt wird.

        d2 ist ein entscheidender Faktor in den Black-Scholes-Formeln zur Bewertung der Preise von europäischen Call- und Put-Optionen.
        Es wird zusammen mit d1 verwendet, um die Wahrscheinlichkeiten zu bestimmen, dass die Option im Geld endet, was wiederum zur
        Berechnung des erwarteten Payoffs benötigt wird. d2 berücksichtigt den aktuellen Basispreis, den Ausübungspreis, die Zeit bis
        zur Fälligkeit, den risikofreien Zinssatz, die Volatilität des Basiswerts und die Dividendenrate.

        Args:
            K (float): Der Ausübungspreis der Option. Dies ermöglicht es, d2 für verschiedene Ausübungspreise innerhalb des gleichen
                    Modells zu berechnen.

        Returns:
            float: Der berechnete Wert von d2. Dieser Wert wird in der Black-Scholes-Formel verwendet, um den Preis der Option zu
                bestimmen.

        Beispiel:
            >>> model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0)
            >>> print(model.d2(K=100))
            Dies gibt den Wert von d2 zurück, basierend auf den gegebenen Parametern des Modells und einem Ausübungspreis von 100.

        Hinweis:
            Der Wert von d2 ist eng mit d1 verbunden und wird durch Subtraktion eines volatilitäts- und zeitabhängigen Terms von d1
            berechnet. Änderungen in den Modellparametern oder im Ausübungspreis beeinflussen somit sowohl d1 als auch d2.
        """
        return self.d1(K) - self.sigma * np.sqrt(self.T)

    def call_price(self, K=None):
        """
        Berechnet den Preis einer europäischen Call-Option unter Verwendung des Black-Scholes-Modells.

        Diese Methode verwendet die Black-Scholes-Formel, um den theoretischen Preis einer europäischen Call-Option zu bestimmen. Die
        Berechnung berücksichtigt den aktuellen Preis des Basiswerts, den Ausübungspreis, die Zeit bis zur Fälligkeit, den risikofreien
        Zinssatz, die Volatilität des Basiswerts und die Dividendenrate. Die Methode ermöglicht die Bewertung der Option mit einem
        alternativen Ausübungspreis, falls gewünscht.

        Args:
            K (float, optional): Der Ausübungspreis der Option. Wenn kein Wert angegeben wird, verwendet die Methode den Ausübungspreis,
                                der bei der Initialisierung des Modells festgelegt wurde.

        Returns:
            float: Der berechnete Preis der Call-Option. Dieser Wert repräsentiert den fairen Wert der Option zum aktuellen Zeitpunkt
                unter den gegebenen Marktbedingungen und Modellannahmen.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0.02)
            >>> print(black_scholes_model.call_price())
            Dies gibt den Preis einer europäischen Call-Option zurück, basierend auf den spezifizierten Modellparametern und einem
            Ausübungspreis von 100.

        Hinweis:
            Der berechnete Optionspreis basiert auf der Annahme, dass die Aktienkursrenditen log-normal verteilt sind und der Markt keine
            Arbitragemöglichkeiten bietet. Änderungen in den Modellparametern können den berechneten Preis signifikant beeinflussen.
        """
        if K is None:
            K = self.K  # Verwende den Standard-Ausübungspreis, falls keiner angegeben ist.
        d1 = self.d1(K)  # Berechnet d1 unter Berücksichtigung des Ausübungspreises.
        d2 = self.d2(K)  # Berechnet d2 unter Berücksichtigung des Ausübungspreises.
        # Berechnet den Call-Optionspreis unter Berücksichtigung von Dividenden.
        return self.S * np.exp(-self.div * self.T) * norm.cdf(d1) - K * np.exp(-self.r * self.T) * norm.cdf(d2)

    def put_price(self, K=None):
        """
        Berechnet den Preis einer europäischen Put-Option unter Verwendung des Black-Scholes-Modells.

        Diese Methode nutzt die Black-Scholes-Formel zur Bestimmung des theoretischen Preises einer europäischen Put-Option. Dabei
        werden der aktuelle Preis des Basiswerts, der Ausübungspreis, die Zeit bis zum Verfall der Option, der risikofreie Zinssatz,
        die Volatilität des Basiswerts und die Dividendenrate berücksichtigt. Optional kann ein alternativer Ausübungspreis für die
        Berechnung angegeben werden.

        Args:
            K (float, optional): Der Ausübungspreis der Option. Wenn kein spezifischer Wert angegeben wird, verwendet die Methode den
                                bei der Initialisierung festgelegten Ausübungspreis.

        Returns:
            float: Der berechnete Preis der Put-Option. Der Wert spiegelt den fairen Wert der Option zum aktuellen Zeitpunkt wider, basierend
                auf den gegebenen Marktbedingungen und den Annahmen des Modells.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0.02)
            >>> print(black_scholes_model.put_price())
            Gibt den Preis einer europäischen Put-Option zurück, basierend auf den Modellparametern und einem Ausübungspreis von 100.

        Hinweis:
            Das Black-Scholes-Modell geht von einer log-normalen Verteilung der Aktienkursrenditen aus und setzt einen friktionslosen Markt
            ohne Arbitragemöglichkeiten voraus. Die Modellparameter, einschließlich des Ausübungspreises, beeinflussen den berechneten
            Optionspreis erheblich.
        """
        if K is None:
            K = self.K  # Standard-Ausübungspreis verwenden, wenn kein spezifischer Wert angegeben ist.
        d1 = self.d1(K)  # Berechnung von d1 für den gegebenen oder standardmäßigen Ausübungspreis.
        d2 = self.d2(K)  # Berechnung von d2 für den gegebenen oder standardmäßigen Ausübungspreis.
        # Berechnet den Put-Optionspreis unter Berücksichtigung von Dividenden.
        return K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * np.exp(-self.div * self.T) * norm.cdf(-d1)

    def digital_call_price(self):
        """
        Berechnet den Preis einer digitalen Call-Option unter Verwendung des Black-Scholes-Modells.

        Digitale Call-Optionen zahlen einen festgelegten Betrag aus, wenn der Basiswert bei Verfall über dem Ausübungspreis liegt,
        und nichts, wenn dies nicht der Fall ist. Diese Methode verwendet die Black-Scholes-Formel zur Bewertung digitaler Call-Optionen,
        wobei die Wahrscheinlichkeit, dass der Basiswert über dem Ausübungspreis liegt, durch den Term 'norm.cdf(d2)' repräsentiert wird.

        Returns:
            float: Der berechnete Preis der digitalen Call-Option. Dieser Preis gibt den gegenwärtigen fairen Wert der Option an,
                basierend auf den aktuellen Marktbedingungen und den Annahmen des Black-Scholes-Modells.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0)
            >>> print(black_scholes_model.digital_call_price())
            Gibt den Preis einer digitalen Call-Option zurück, basierend auf den gegebenen Modellparametern.

        Hinweis:
            Die Berechnung des Preises einer digitalen Call-Option hängt maßgeblich von der Wahrscheinlichkeit ab, dass der Basiswert bei Verfall
            über dem Ausübungspreis liegt. Diese Wahrscheinlichkeit wird durch den Term 'norm.cdf(d2)' ausgedrückt, der die kumulative
            Normalverteilungsfunktion von d2 darstellt. Die Formel berücksichtigt den risikofreien Zinssatz und die Zeit bis zum Verfall, um
            den erwarteten Auszahlungsbetrag zu diskontieren.
        """
        d2 = self.d2(self.K)  # Berechnet d2 unter Verwendung des standardmäßigen Ausübungspreises.
        # Berechnet den Preis der digitalen Call-Option durch Diskontierung der erwarteten Auszahlung.
        return np.exp(-self.r * self.T) * norm.cdf(d2)

    def digital_put_price(self):
        """
        Berechnet den Preis einer digitalen Put-Option unter Verwendung des Black-Scholes-Modells.

        Digitale Put-Optionen zahlen einen festgelegten Betrag aus, wenn der Basiswert bei Verfall unter dem Ausübungspreis liegt,
        und nichts, wenn dies nicht der Fall ist. Diese Methode verwendet die Black-Scholes-Formel zur Bewertung digitaler Put-Optionen,
        wobei die Wahrscheinlichkeit, dass der Basiswert unter dem Ausübungspreis liegt, durch den Term 'norm.cdf(-d2)' repräsentiert wird.

        Returns:
            float: Der berechnete Preis der digitalen Put-Option. Dieser Wert gibt den gegenwärtigen fairen Wert der Option an,
                basierend auf den aktuellen Marktbedingungen und den Annahmen des Black-Scholes-Modells.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0)
            >>> print(black_scholes_model.digital_put_price())
            Gibt den Preis einer digitalen Put-Option zurück, basierend auf den gegebenen Modellparametern.

        Hinweis:
            Die Berechnung des Preises einer digitalen Put-Option hängt maßgeblich von der Wahrscheinlichkeit ab, dass der Basiswert bei Verfall
            unter dem Ausübungspreis liegt. Diese Wahrscheinlichkeit wird durch den Term 'norm.cdf(-d2)' ausgedrückt, der die kumulative
            Normalverteilungsfunktion von -d2 darstellt. Die Formel berücksichtigt den risikofreien Zinssatz und die Zeit bis zum Verfall, um
            den erwarteten Auszahlungsbetrag zu diskontieren.
        """
        d2 = self.d2(self.K)  # Berechnet d2 unter Verwendung des standardmäßigen Ausübungspreises.
        # Berechnet den Preis der digitalen Put-Option durch Diskontierung der erwarteten Auszahlung.
        return np.exp(-self.r * self.T) * norm.cdf(-d2)


    def strangle_price(self, K_call, K_put):
        """
        Berechnet den Gesamtpreis einer Strangle-Optionsstrategie unter Verwendung des Black-Scholes-Modells.

        Eine Strangle-Strategie besteht aus dem Kauf einer Call-Option und einer Put-Option auf denselben Basiswert mit unterschiedlichen
        Ausübungspreisen und derselben Verfallzeit. Die Strategie zielt darauf ab, von signifikanten Preisbewegungen des Basiswerts zu profitieren,
        unabhängig von der Richtung dieser Bewegungen. Der Gesamtpreis der Strangle-Strategie ist die Summe der Preise der Call- und Put-Option.

        Args:
            K_call (float): Der Ausübungspreis der Call-Option.
            K_put (float): Der Ausübungspreis der Put-Option.

        Returns:
            float: Der kombinierte Preis der Call- und Put-Option, der den Gesamtpreis der Strangle-Strategie darstellt.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0)
            >>> strangle_price = black_scholes_model.strangle_price(K_call=105, K_put=95)
            >>> print(strangle_price)
            Gibt den Gesamtpreis der Strangle-Strategie zurück, basierend auf den angegebenen Ausübungspreisen für die Call- und Put-Option.

        Hinweis:
            Die Effektivität einer Strangle-Strategie hängt von der Volatilität des Basiswerts und der Differenz zwischen den Ausübungspreisen
            der Call- und Put-Optionen ab. Eine größere Bewegung des Basiswerts ist erforderlich, damit die Strategie profitabel ist, da beide
            Optionsprämien berücksichtigt werden müssen.
        """
        call_price = self.call_price(K=K_call)  # Berechnet den Preis der Call-Option mit dem gegebenen Ausübungspreis.
        put_price = self.put_price(K=K_put)  # Berechnet den Preis der Put-Option mit dem gegebenen Ausübungspreis.
        # Gibt die Summe der Preise der Call- und Put-Option zurück, was dem Gesamtpreis der Strangle-Strategie entspricht.
        return call_price + put_price


    def call_delta(self, K=None):
        """
        Berechnet das Delta für eine Call-Option unter Verwendung des Black-Scholes-Modells.

        Das Delta einer Option gibt an, um wie viel sich der Preis der Option voraussichtlich ändert, wenn sich der Preis des Basiswerts
        um eine Einheit ändert. Für eine Call-Option liegt das Delta zwischen 0 und 1, wobei ein höheres Delta auf eine höhere Sensitivität
        des Optionspreises bezüglich Veränderungen im Preis des Basiswerts hinweist. Diese Methode berechnet das Delta unter Berücksichtigung
        der Dividendenrate des Basiswerts.

        Args:
            K (float, optional): Der Ausübungspreis der Call-Option. Wenn kein Wert angegeben wird, verwendet die Methode den Ausübungspreis,
                                der bei der Initialisierung des Modells festgelegt wurde.

        Returns:
            float: Das Delta der Call-Option, das die Preisänderung der Option relativ zur Preisänderung des Basiswerts darstellt.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0.02)
            >>> print(black_scholes_model.call_delta())
            Gibt das Delta einer Call-Option zurück, basierend auf den gegebenen Modellparametern und einem Ausübungspreis von 100.

        Hinweis:
            Das Delta ist besonders nützlich für das Risikomanagement und die Portfoliooptimierung, da es Händlern ermöglicht, die
            Sensitivität ihrer Optionspositionen gegenüber Preisbewegungen des Basiswerts zu bewerten und entsprechende Hedging-Strategien
            zu implementieren.
        """
        if K is None:
            K = self.K  # Verwendet den Standard-Ausübungspreis, wenn kein spezifischer Wert angegeben ist.
        d1 = self.d1(K)  # Berechnet d1, was eine Schlüsselrolle bei der Bestimmung von Delta spielt.
        # Berechnet das Delta der Call-Option.
        return np.exp(-self.div * self.T) * norm.cdf(d1)


    def put_delta(self, K=None):
        """
        Berechnet das Delta für eine Put-Option unter Verwendung des Black-Scholes-Modells.

        Das Delta einer Put-Option gibt an, um wie viel sich der Preis der Option voraussichtlich ändert, wenn sich der Preis des Basiswerts
        um eine Einheit ändert. Im Gegensatz zu Call-Optionen, für die das Delta positiv ist, weisen Put-Optionen ein negatives Delta auf, was
        darauf hindeutet, dass der Preis der Put-Option tendenziell sinkt, wenn der Preis des Basiswerts steigt. Diese Methode berechnet das
        Delta unter Berücksichtigung der Dividendenrate des Basiswerts.

        Args:
            K (float, optional): Der Ausübungspreis der Put-Option. Wenn kein Wert angegeben wird, verwendet die Methode den Ausübungspreis,
                                der bei der Initialisierung des Modells festgelegt wurde.

        Returns:
            float: Das Delta der Put-Option. Dieser Wert repräsentiert die erwartete Preisänderung der Option in Relation zur Preisänderung
                des Basiswerts, angepasst um die Dividendenrate.

        Beispiel:
            >>> black_scholes_model = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2, div=0.02)
            >>> print(black_scholes_model.put_delta())
            Gibt das Delta einer Put-Option zurück, basierend auf den gegebenen Modellparametern und einem Ausübungspreis von 100.

        Hinweis:
            Das Delta für Put-Optionen ist negativ, da der Preis der Option mit steigendem Basiswert tendenziell sinkt. Das Verständnis von
            Delta ist entscheidend für das Risikomanagement und die Implementierung von Hedging-Strategien in einem Optionsportfolio.
        """
        if K is None:
            K = self.K  # Verwendet den Standard-Ausübungspreis, falls keiner spezifisch angegeben wurde.
        d1 = self.d1(K)  # Berechnet d1, eine Schlüsselgröße für die Delta-Berechnung.
        # Berechnet das Delta der Put-Option, angepasst um die Dividendenrate.
        return np.exp(-self.div * self.T) * (norm.cdf(d1) - 1)
