import sys
import os
import logging
import random
from PySide6 import QtSql
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout

# Lokale Ressourcen und GUI-Datei
import resources
from FinanceApp_modern_UI import Ui_MainWindow

# Modellklassen und benutzerdefinierte Widgets
from binomialmodell import Binomialmodell
from trinomialmodell import Trinomialmodell
from finance_plot import FinanzPlot
from plotqtabwidget import PlotQTabWidget
from Custom_Widgets import *

########################################################################################################################
#
# Laden von JSON-Dateien für das Styling sowie Fragenkatalog für die Anwendung
# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
#
########################################################################################################################

def resource_path(relative_path):
    """
    Generiert einen absoluten Pfad zur Ressource, der sowohl in der Entwicklungsumgebung als auch nach der
    Paketierung mit PyInstaller funktioniert.

    Diese Funktion ist besonders nützlich für den Zugriff auf Ressourcen wie Datenbanken, Bilder oder Konfigurationsdateien,
    sowohl während der Entwicklung als auch nach der Kompilierung der Anwendung in eine ausführbare Datei mit PyInstaller.
    PyInstaller extrahiert die Ressourcen in einen temporären Ordner, und dieser Pfad kann mit der Umgebungsvariablen
    '_MEIPASS' abgerufen werden. In der Entwicklungsumgebung, wo '_MEIPASS' nicht definiert ist, wird stattdessen der
    aktuelle Verzeichnispfad verwendet.

    Args:
        relative_path (str): Der relative Pfad zur Ressource ausgehend vom Hauptordner des Projekts oder vom temporären
                             Ordner, der von PyInstaller verwendet wird.

    Returns:
        str: Der absolute Pfad zur angegebenen Ressource.

    Beispiel:
        Angenommen, es gibt eine Konfigurationsdatei im Verzeichnis 'config/settings.json':
            >>> resource_path = resource_path('config/settings.json')
        Dies gibt den absoluten Pfad zur 'settings.json'-Datei zurück, unabhängig davon, ob die Anwendung direkt
        aus dem Quellcode oder als kompilierte Anwendung läuft.
    """
    try:
        # Versucht, den Basispfad aus der Umgebungsvariablen '_MEIPASS' zu erhalten,
        # die von PyInstaller bei der Kompilierung gesetzt wird.
        base_path = sys._MEIPASS
    except Exception:
        # Falls '_MEIPASS' nicht definiert ist (d.h., die Anwendung läuft direkt aus dem Quellcode),
        # wird der aktuelle Verzeichnispfad als Basispfad verwendet.
        base_path = os.path.abspath(".")

    # Verbindet den Basispfad mit dem relativen Pfad zur Ressource und gibt den absoluten Pfad zurück.
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    """
    Hauptfensterklasse der Finanzanwendungs-Benutzeroberfläche.

    Diese Klasse initiiert und verwaltet das Hauptfenster der Anwendung, einschließlich der Benutzeroberfläche für die Bewertung
    von Derivaten mit dem Binomial- und Trinomialmodell, die Darstellung der Ergebnisse, den Zugriff auf einen LearningHub für
    das Üben mathematischer Begriffe, Einstellungen, Informationen zur Anwendung und Hilfeoptionen.

    Die Klasse nutzt das Qt Framework, um die Benutzeroberfläche zu erstellen und Interaktionen zu verwalten. Es integriert
    verschiedene benutzerdefinierte Widgets und Funktionen für die spezifischen Bedürfnisse der Finanzanwendung.

    Attribute:
        ui (Ui_MainWindow): Eine Instanz der Benutzeroberflächenklasse, die mit Qt Designer erstellt wurde.
        radioButtons (list): Eine Liste von RadioButtons, die für Quizantworten im LearningHub verwendet werden.
        dbConnected (bool): Status der Datenbankverbindung für den Fragenkatalog des LearningHubs.

    Methoden:
        __init__: Konstruktor der Klasse, initialisiert die Benutzeroberfläche und setzt den Anfangszustand.
        setupSignals: Verbindet UI-Elemente mit entsprechenden Signalen für Interaktivität.
        setInitialState: Setzt den initialen Zustand der UI-Elemente basierend auf der Anwendungslogik.
        onStrangleToggled, onPowerOptionToggled, onModelToggled, onSigmaUnknownToggled, updateCbIsAMVisibility: Methoden zur Verwaltung der Sichtbarkeit und Zustände von UI-Elementen basierend auf Benutzerinteraktionen.
        calculateOptionPrice: Berechnet den Preis der ausgewählten Option basierend auf Benutzereingaben.
        displayPlotInTab: Zeigt Ergebnisplots in einem Tab-Widget an.
        startQuiz, loadNextQuestion, resetLearningHub: Methoden zur Verwaltung des LearningHubs.
        showMessage: Zeigt Nachrichtenboxen mit Benutzerfeedback an.
        loadNextQuestion: Lädt die nächste Frage im LearningHub und verarbeitet die Benutzerantworten.
        resetRadioButtons: Setzt die RadioButtons im LearningHub zurück.
        updateDatabaseCorrectAnswer: Aktualisiert die Datenbank mit korrekten Antworten im LearningHub.
        setupFragenkatalog: Stellt eine Verbindung zur Datenbank her und lädt Fragen für den LearningHub.
        chooseRandomQuestion: Wählt eine zufällige Frage aus dem Fragenkatalog aus.
        updateUIWithQuestion: Aktualisiert die Benutzeroberfläche mit einer ausgewählten Frage.
        updateCounters: Aktualisiert die Zähler für korrekte und falsche Antworten im LearningHub.
        resetLearningHub: Setzt die Datenbank und die Zähler im LearningHub zurück.
    """
    def __init__(self):
        """
        Konstruktor für das Hauptfenster der Anwendung.

        Initialisiert die Benutzeroberfläche, lädt den JSON-Stil, konfiguriert UI-Signale und setzt den initialen Zustand der Anwendung.
        Stellt zudem die Sichtbarkeit des Fensters ein und prüft die Datenbankverbindung für den LearningHub.
        """
        super(MainWindow, self).__init__()  # Initialisiert das QMainWindow-Objekt.
        self.ui = Ui_MainWindow()  # Erstellt eine Instanz der automatisch generierten UI-Klasse.
        self.ui.setupUi(self)  # Initialisiert die UI-Elemente gemäß der Definition in der UI-Datei.

        # Definiert die RadioButtons, die für die Quizantworten im LearningHub verwendet werden.
        self.radioButtons = [
            self.ui.rb_answer_1,
            self.ui.rb_answer_2,
            self.ui.rb_answer_3,
            self.ui.rb_answer_4
        ]

        # Lädt den JSON-Stil, der das Aussehen der UI-Elemente definiert.
        jsonFilePath = resource_path("C:\\Users\\murat\\OneDrive\\Abschlussarbeit B.Sc\\Python\\QT\\JsonStyle\\style.json")
        loadJsonStyle(self, self.ui, jsonFiles=[jsonFilePath])

        self.setupSignals()  # Konfiguriert die Signale und Slots für UI-Interaktionen.
        self.setInitialState()  # Setzt den initialen Zustand der UI-Elemente.

        self.dbConnected = False  # Initialisiert den Status der Datenbankverbindung als nicht verbunden.

        self.show()  # Macht das Hauptfenster sichtbar.

    def setupSignals(self):
        """
        Konfiguriert Signale und Slots für die Interaktionen der Benutzeroberfläche.

        Diese Methode verbindet die Aktionen des Benutzers, wie Klicks und Auswahländerungen, mit entsprechenden Funktionen
        (sogenannten Slots) in der Anwendung. Dadurch wird die Reaktivität der UI auf Benutzereingaben ermöglicht und die
        Funktionalität hinter den UI-Elementen definiert.
        """
        # Verbindet die Klick-Events der Menübuttons mit der Funktion zur Erweiterung des zentralen Menüs.
        for button in [self.ui.bt_settings, self.ui.bt_info, self.ui.bt_help]:
            button.clicked.connect(lambda _, b=button: self.ui.ct_menu.expandMenu())

        # Verbindet das Klick-Event des Schließbuttons des zentralen Menüs mit der Funktion zum Kollabieren des Menüs.
        self.ui.bt_closeCenterMenu.clicked.connect(self.ui.ct_menu.collapseMenu)

        # Verbindet die Toggle-Events der Radiobuttons für verschiedene Optionstypen mit ihren jeweiligen Funktionen.
        self.ui.rb_strangle.toggled.connect(self.onStrangleToggled)
        self.ui.rb_powcall.toggled.connect(self.onPowerOptionToggled)
        self.ui.rb_powput.toggled.connect(self.onPowerOptionToggled)
        self.ui.rb_binomialmodell.toggled.connect(self.onModelToggled)
        self.ui.rb_trinomialmodell.toggled.connect(self.onModelToggled)
        self.ui.cb_sigma.toggled.connect(self.onSigmaUnknownToggled)
        self.ui.rb_eucall.toggled.connect(self.updateCbIsAMVisibility)
        self.ui.rb_euput.toggled.connect(self.updateCbIsAMVisibility)

        # Verbindet die Klick-Events der Schaltflächen für die Berechnung des Optionspreises, den Start des Quizzes,
        # das Laden der nächsten Frage, das Zurücksetzen des LearningHubs und das Setzen von Standardwerten
        # mit den entsprechenden Funktionen.
        self.ui.bt_check.clicked.connect(self.calculateOptionPrice)
        self.ui.bt_start.clicked.connect(self.startQuiz)
        self.ui.bt_next.clicked.connect(self.loadNextQuestion)
        self.ui.bt_resetLH.clicked.connect(self.resetLearningHub)
        self.ui.cb_default.stateChanged.connect(self.setDefaultValues)
        self.ui.bt_readpdf.clicked.connect(self.open_pdf_in_external_viewer)

    def setInitialState(self):
        """
        Setzt den initialen Zustand der Benutzeroberfläche basierend auf den Standardwerten oder vorausgewählten Optionen.

        Diese Methode wird beim Start der Anwendung aufgerufen, um die UI-Elemente entsprechend der Logik und den 
        Anforderungen der Anwendung zu initialisieren. Sie sorgt dafür, dass bestimmte UI-Elemente sichtbar oder 
        unsichtbar sind, abhängig von den ausgewählten Optionstypen, dem gewählten Modell und anderen Einstellungen.

        Die Methode ruft spezifische Funktionen auf, um den Zustand von UI-Elementen wie RadioButtons und Checkboxen 
        anzupassen, und reflektiert so die Anfangskonfiguration der Benutzeroberfläche für den Benutzer.
        """
        # Überprüft den Zustand des Strangle-Options-RadioButtons und passt die UI entsprechend an.
        self.onStrangleToggled(self.ui.rb_strangle.isChecked())

        # Überprüft den Zustand der Power-Options-RadioButtons und passt die UI entsprechend an.
        self.onPowerOptionToggled(self.ui.rb_powcall.isChecked() or self.ui.rb_powput.isChecked())

        # Überprüft den Zustand der Modell-Auswahl-RadioButtons (Binomial- oder Trinomialmodell) und passt die UI entsprechend an.
        self.onModelToggled(self.ui.rb_binomialmodell.isChecked() or self.ui.rb_trinomialmodell.isChecked())

        # Überprüft den Zustand der Checkbox, die angibt, ob die Sigma-Parameter unbekannt sind, und passt die UI entsprechend an.
        self.onSigmaUnknownToggled(self.ui.cb_sigma.isChecked())

        # Aktualisiert die Sichtbarkeit der Checkbox für die Auswahl zwischen amerikanischen und europäischen Optionen.
        self.updateCbIsAMVisibility()

    def onStrangleToggled(self, checked):
        """
        Passt die Sichtbarkeit der UI-Elemente für die Strangle-Options-Eingabe an, basierend auf dem Zustand des zugehörigen RadioButtons.

        Wird aufgerufen, wenn der Zustand des Strangle-Options-RadioButtons geändert wird. Diese Methode sorgt dafür,
        dass die Eingabefelder und Labels für den zweiten Ausübungspreis (K2) nur dann sichtbar sind, wenn die
        Strangle-Option ausgewählt ist. Dies reflektiert die Notwendigkeit eines zusätzlichen Ausübungspreises für
        die Strukturierung einer Strangle-Option.

        Args:
            checked (bool): Der Zustand des Strangle-Options-RadioButton. `True`, wenn dieser ausgewählt ist, sonst `False`.

        Beispiel:
            Wenn der Benutzer die Strangle-Option auswählt, werden das Eingabefeld und das Label für K2 sichtbar gemacht.
            Wird eine andere Optionstyp ausgewählt, werden diese UI-Elemente ausgeblendet.
        """
        # Setzt die Sichtbarkeit des Eingabefelds und des Labels für den zweiten Ausübungspreis (K2),
        # abhängig vom Zustand des Strangle-Options-RadioButtons.
        self.ui.in_k2.setVisible(checked)
        self.ui.txt_k2.setVisible(checked)

    def onPowerOptionToggled(self, checked):
        """
        Passt die Sichtbarkeit der UI-Elemente für die Eingabe des Exponenten bei Power-Optionen an.

        Diese Methode wird aufgerufen, wenn der Zustand eines der Power-Options-RadioButtons geändert wird.
        Sie kontrolliert die Sichtbarkeit des Eingabefelds und des Labels für den Exponenten, was für die
        Berechnung von Power-Optionen erforderlich ist. Power-Optionen erlauben es dem Benutzer, eine Option
        mit einem Auszahlungsprofil zu bewerten, das von einer Potenzfunktion des Unterschieds zwischen dem
        Endpreis des Basiswerts und dem Ausübungspreis abhängt.

        Args:
            checked (bool): Der Zustand des RadioButton, der diese Methode auslöst. Obwohl dieser Parameter
                            in der Methode nicht direkt verwendet wird, ist er erforderlich, um die Methode
                            als Slot für das Signal `toggled(bool)` zu verwenden.

        Beispiel:
            Wenn der Benutzer eine Power-Call oder Power-Put-Option auswählt, werden das Eingabefeld und das
            Label für den Exponenten sichtbar. Wird eine andere Option ausgewählt, werden diese Elemente
            ausgeblendet.
        """
        # Bestimmt, ob die Power-Options-RadioButtons ausgewählt sind, und setzt `show_exp` entsprechend.
        show_exp = self.ui.rb_powcall.isChecked() or self.ui.rb_powput.isChecked()

        # Setzt die Sichtbarkeit des Eingabefelds und des Labels für den Exponenten basierend auf der Auswahl der Power-Option.
        self.ui.in_exp.setVisible(show_exp)
        self.ui.txt_exp.setVisible(show_exp)

    def onModelToggled(self, checked):
        """
        Passt die Sichtbarkeit der UI-Elemente für spezifische Modellparameter an, basierend auf der Auswahl des Bewertungsmodells.

        Diese Methode wird aufgerufen, wenn der Zustand der RadioButtons für die Modellauswahl (Binomialmodell oder Trinomialmodell)
        geändert wird. Sie steuert die Sichtbarkeit von UI-Elementen, die spezifisch für das Trinomialmodell sind, wie die
        Wahrscheinlichkeit einer mittleren Bewegung (pm) sowie die Faktoren für Aufwärts- (u), Abwärts- (d) und mittlere Bewegungen (m).
        Darüber hinaus wird geprüft, ob die Sigma-Eingabe aktiviert ist, um entsprechende Eingabefelder anzupassen.

        Args:
            checked (bool): Der Zustand des RadioButton, der diese Methode auslöst. Dieser Parameter wird in dieser Methode
                            nicht direkt verwendet, ist aber notwendig, um die Methode als Slot für das Signal `toggled(bool)`
                            zu verwenden.

        Beispiel:
            Wenn der Benutzer das Trinomialmodell auswählt, werden die Eingabefelder und Labels für pm, u, d und m sichtbar.
            Wählt der Benutzer das Binomialmodell, werden diese Elemente ausgeblendet. Zusätzlich wird die Sichtbarkeit
            weiterer UI-Elemente basierend auf dem Zustand der Sigma-Checkbox angepasst.
        """
        # Prüft, ob das Trinomialmodell ausgewählt ist, und passt die Sichtbarkeit der entsprechenden UI-Elemente an.
        is_trinomial = self.ui.rb_trinomialmodell.isChecked()
        self.ui.in_pm.setVisible(is_trinomial)
        self.ui.txt_pm.setVisible(is_trinomial)
        self.ui.in_u.setVisible(is_trinomial)
        self.ui.txt_u.setVisible(is_trinomial)
        self.ui.in_d.setVisible(is_trinomial)
        self.ui.txt_d.setVisible(is_trinomial)
        self.ui.in_m.setVisible(is_trinomial)
        self.ui.txt_m.setVisible(is_trinomial)

        # Ruft `onSigmaUnknownToggled` auf, um die Sichtbarkeit der Sigma-bezogenen UI-Elemente entsprechend anzupassen,
        # basierend auf dem aktuellen Zustand der Sigma-Checkbox.
        self.onSigmaUnknownToggled(self.ui.cb_sigma.isChecked())

    def onSigmaUnknownToggled(self, checked):
        """
        Passt die Sichtbarkeit der UI-Elemente an, basierend auf der Benutzerauswahl, ob die Volatilität (Sigma) bekannt ist.

        Wird aufgerufen, wenn der Zustand der Checkbox für die Unbekanntheit von Sigma geändert wird. Diese Methode steuert die
        Sichtbarkeit von Eingabefeldern für Sigma oder alternativ für die Wahrscheinlichkeiten und Bewegungsfaktoren, falls Sigma
        unbekannt ist. Dies ist relevant für die Flexibilität bei der Modellanwendung, insbesondere wenn Marktdaten unvollständig sind
        oder andere Ansätze zur Bewertung erforderlich sind.

        Args:
            checked (bool): Der Zustand der Checkbox, der angibt, ob Sigma unbekannt ist. Wenn `True`, sind die Eingabefelder
                            für die direkten Modellparameter sichtbar; andernfalls ist das Feld für Sigma sichtbar.

        Beispiel:
            Wenn der Benutzer angibt, dass Sigma unbekannt ist, werden die Eingabefelder für `pu`, `pd` (und im Falle des
            Trinomialmodells zusätzlich `pm`, `u`, `d`, `m`) sichtbar. Wird die Checkbox deaktiviert, werden diese Felder
            ausgeblendet und das Feld für Sigma wird angezeigt.
        """
        # Bestimmt, ob Sigma als unbekannt markiert ist und passt die Sichtbarkeit der UI-Elemente entsprechend an.
        sigma_unknown = checked
        self.ui.in_sigma.setVisible(not sigma_unknown)
        self.ui.txt_sigma.setVisible(not sigma_unknown)
        self.ui.in_pu.setVisible(sigma_unknown)
        self.ui.txt_pu.setVisible(sigma_unknown)
        self.ui.in_pd.setVisible(sigma_unknown)
        self.ui.txt_pd.setVisible(sigma_unknown)

        # Zusätzliche UI-Elemente für das Trinomialmodell werden nur angezeigt, wenn Sigma unbekannt ist
        # und das Trinomialmodell ausgewählt wurde.
        is_trinomial = self.ui.rb_trinomialmodell.isChecked()
        self.ui.in_pm.setVisible(sigma_unknown and is_trinomial)
        self.ui.txt_pm.setVisible(sigma_unknown and is_trinomial)
        self.ui.in_u.setVisible(sigma_unknown and is_trinomial)
        self.ui.txt_u.setVisible(sigma_unknown and is_trinomial)
        self.ui.in_d.setVisible(sigma_unknown and is_trinomial)
        self.ui.txt_d.setVisible(sigma_unknown and is_trinomial)
        self.ui.in_m.setVisible(sigma_unknown and is_trinomial)
        self.ui.txt_m.setVisible(sigma_unknown and is_trinomial)

    def updateCbIsAMVisibility(self):
        """
        Passt die Sichtbarkeit der Checkbox für die Auswahl zwischen amerikanischen und europäischen Optionen an.

        Diese Methode wird aufgerufen, um die Sichtbarkeit der Checkbox zu steuern, die dem Benutzer die Wahl zwischen
        amerikanischen und europäischen Optionen ermöglicht. Die Sichtbarkeit hängt davon ab, ob eine Call- oder Put-Option
        ausgewählt ist, was bedeutet, dass die Wahlmöglichkeit nur für europäische und amerikanische Optionstypen relevant ist.
        Für andere Optionstypen, wie digitale oder Power-Optionen, ist diese Auswahl nicht zutreffend und die Checkbox wird
        dementsprechend ausgeblendet.

        Beispiel:
            Wenn der Benutzer eine europäische Call- oder Put-Option auswählt, wird die Checkbox sichtbar gemacht, um
            die Auswahl zwischen einer amerikanischen und einer europäischen Ausführung zu ermöglichen. Bei der Auswahl
            anderer Optionstypen wird die Checkbox ausgeblendet.
        """
        # Bestimmt, ob die Checkbox für die Auswahl zwischen amerikanischen und europäischen Optionen sichtbar sein soll,
        # basierend auf der Auswahl von europäischen Call- oder Put-Optionen.
        is_visible = self.ui.rb_eucall.isChecked() or self.ui.rb_euput.isChecked()

        # Setzt die Sichtbarkeit der Checkbox entsprechend.
        self.ui.cb_isAM.setVisible(is_visible)

    def setDefaultValues(self, state):
        """
        Setzt die Standardwerte für die Eingabefelder oder löscht sie, abhängig vom Zustand der CheckBox.

        Diese Methode wird aufgerufen, wenn der Zustand der CheckBox für die Verwendung von Standardwerten geändert wird.
        Wenn die CheckBox aktiviert ist, werden die Eingabefelder der Benutzeroberfläche mit vordefinierten Standardwerten
        gefüllt. Dies ist hilfreich, um dem Benutzer einen schnellen Start zu ermöglichen, ohne alle Felder manuell ausfüllen
        zu müssen. Wenn die CheckBox deaktiviert ist, werden alle Eingabefelder geleert, um dem Benutzer zu ermöglichen,
        von vorne zu beginnen.

        Args:
            state (int): Der Zustand der CheckBox (nicht direkt verwendet, da die Überprüfung über `isChecked` erfolgt).

        Beispiel:
            Angenommen, der Benutzer aktiviert die CheckBox für die Verwendung von Standardwerten:
                >>> setDefaultValues(checked)
            Alle Eingabefelder werden daraufhin mit den vordefinierten Werten gefüllt.

            Wenn der Benutzer die CheckBox deaktiviert:
                >>> setDefaultValues(unchecked)
            Alle Eingabefelder werden geleert.
        """
        # Ein Dictionary, das jedes Eingabefeld (Widget) mit seinem Standardwert verknüpft.
        defaultValues = {
            self.ui.in_div: "0.02",
            self.ui.in_exp: "2",
            self.ui.in_k: "52",
            self.ui.in_k2: "55",
            self.ui.in_n: "3",
            self.ui.in_pd: "0.4",
            self.ui.in_pm: "0.2",
            self.ui.in_pu: "0.4",
            self.ui.in_r: "0.05",
            self.ui.in_s0: "50",
            self.ui.in_sigma: "0.2",
            self.ui.in_t: "1",
            self.ui.in_u: "1.1",
            self.ui.in_d: "0.9",
            self.ui.in_m: "1"
        }

        # Überprüft den Zustand der CheckBox und aktualisiert die Eingabefelder entsprechend.
        if self.ui.cb_default.isChecked():
            # Füllt jedes Eingabefeld mit seinem Standardwert, wenn die CheckBox aktiviert ist.
            for widget, value in defaultValues.items():
                widget.setText(value)
        else:
            # Leert alle Eingabefelder, wenn die CheckBox deaktiviert ist.
            for widget in defaultValues.keys():
                widget.clear()

    def show_input_error(self, message, title="Eingabefehler"):
        """
        Zeigt eine Warnmeldungsbox mit einer Fehlermeldung an den Benutzer an.

        Diese Methode wird verwendet, um auf Benutzereingabefehler oder ungültige Daten hinzuweisen. Sie erstellt
        und zeigt eine Warnmeldungsbox mit einer benutzerdefinierten Nachricht und einem optionalen Titel an. Diese
        Funktionalität ist nützlich, um die Benutzererfahrung zu verbessern, indem klare und verständliche Fehlermeldungen
        bereitgestellt werden, die dem Benutzer helfen, Eingabeprobleme zu identifizieren und zu korrigieren.

        Args:
            message (str): Die Nachricht, die in der Warnmeldungsbox angezeigt werden soll. Diese Nachricht sollte
                        das Problem klar beschreiben und idealerweise einen Hinweis darauf geben, wie es behoben
                        werden kann.
            title (str, optional): Der Titel der Warnmeldungsbox. Standardmäßig auf "Eingabefehler" gesetzt, kann
                                aber angepasst werden, um den Kontext des Fehlers besser widerzuspiegeln.

        Beispiel:
            Um einen Fehler anzuzeigen, der darauf hinweist, dass der Ausübungspreis nicht leer sein darf:
                >>> show_input_error("Der Ausübungspreis darf nicht leer sein.", "Ungültige Eingabe")
            Dies würde eine Warnmeldungsbox mit der angegebenen Nachricht und dem Titel anzeigen.
        """
        # Erstellt das QMessageBox-Objekt für die Warnmeldung.
        msg_warning = QMessageBox()
        msg_warning.setIcon(QMessageBox.Warning)  # Setzt das Icon der Meldungsbox auf ein Warnsymbol.
        msg_warning.setText(message)  # Setzt den Text der Meldungsbox auf die übergebene Nachricht.
        msg_warning.setWindowTitle(title)  # Setzt den Titel der Meldungsbox.
        msg_warning.setStandardButtons(QMessageBox.Ok)  # Fügt einen OK-Button hinzu, um die Meldung zu schließen.
        msg_warning.exec_()  # Zeigt die Warnmeldungsbox modal an, d.h., andere Teile der Anwendung sind solange blockiert, bis der Benutzer reagiert.

    def is_valid_float(self, text):
        """
        Überprüft, ob ein gegebener Text in eine Fließkommazahl umgewandelt werden kann.

        Diese Methode versucht, den übergebenen Text in eine Fließkommazahl (float) zu konvertieren. Sie wird
        genutzt, um zu validieren, dass Benutzereingaben, die numerische Werte repräsentieren sollen, tatsächlich
        in solche Werte umgewandelt werden können. Dies ist besonders wichtig, um Eingabefehler zu erkennen und
        die korrekte Verarbeitung numerischer Daten in der Anwendung sicherzustellen.

        Args:
            text (str): Der Text, der auf seine Konvertierbarkeit in eine Fließkommazahl überprüft werden soll.

        Returns:
            bool: True, wenn der Text erfolgreich in eine Fließkommazahl umgewandelt werden kann, andernfalls False.

        Beispiel:
            Um zu überprüfen, ob der Text "123.45" eine gültige Fließkommazahl ist:
                >>> is_valid_float("123.45")
                True
            Um zu überprüfen, ob der Text "abc123" eine gültige Fließkommazahl ist:
                >>> is_valid_float("abc123")
                False
        """
        try:
            # Versucht, den Text in eine Fließkommazahl zu konvertieren.
            float(text)
            return True  # Gibt True zurück, wenn die Konvertierung erfolgreich war.
        except ValueError:
            # Wird ausgelöst, wenn die Konvertierung fehlschlägt, z.B. bei nicht-numerischen Zeichen im Text.
            return False  # Gibt False zurück, wenn der Text nicht in eine Fließkommazahl konvertiert werden kann.

    def is_valid_probability(self, pu, pd, pm=0):
        """
        Überprüft, ob die angegebenen Wahrscheinlichkeiten gültige Werte für ein Binomial- oder Trinomialmodell darstellen.

        Diese Methode validiert die Wahrscheinlichkeiten für Aufwärtsbewegung (pu), Abwärtsbewegung (pd) und, im Falle des
        Trinomialmodells, für die mittlere Bewegung (pm), indem sie sicherstellt, dass die Summe dieser Wahrscheinlichkeiten
        1 ergibt (mit einer geringen Toleranz für Fließkommagenauigkeit) und dass keine der Wahrscheinlichkeiten negativ ist.
        Diese Validierung ist entscheidend für die korrekte Modellierung und Berechnung der Optionspreise.

        Args:
            pu (float): Wahrscheinlichkeit einer Aufwärtsbewegung.
            pd (float): Wahrscheinlichkeit einer Abwärtsbewegung.
            pm (float, optional): Wahrscheinlichkeit einer mittleren Bewegung. Standardwert ist 0, was bedeutet, dass
                                standardmäßig von einem Binomialmodell ausgegangen wird.

        Returns:
            bool: True, wenn die Summe der Wahrscheinlichkeiten 1 ergibt (für das Trinomialmodell mit einer kleinen
                Toleranz) und keine der Wahrscheinlichkeiten negativ ist, andernfalls False.

        Beispiel:
            Für ein Binomialmodell mit pu=0.5 und pd=0.5:
                >>> is_valid_probability(0.5, 0.5)
                True
            Für ein Trinomialmodell mit pu=0.3, pd=0.3, pm=0.4:
                >>> is_valid_probability(0.3, 0.3, 0.4)
                True
            Für ungültige Wahrscheinlichkeiten, z.B. pu=0.5, pd=0.6 (Summe > 1):
                >>> is_valid_probability(0.5, 0.6)
                False
        """
        # Überprüft, ob eine der Wahrscheinlichkeiten negativ ist.
        if pu < 0 or pd < 0 or pm < 0:
            return False  # Gibt False zurück, wenn eine Wahrscheinlichkeit negativ ist.

        # Berechnet die Gesamtwahrscheinlichkeit.
        total_probability = pu + pd + pm

        # Überprüft die Gültigkeit der Wahrscheinlichkeiten basierend auf dem Modell.
        if pm == 0:  # Binomialmodell
            # Für das Binomialmodell muss die Summe von pu und pd kleiner oder gleich 1 sein.
            return total_probability <= 1
        else:  # Trinomialmodell
            # Für das Trinomialmodell muss die Summe von pu, pd und pm nahe 1 sein (Berücksichtigung der Fließkommagenauigkeit).
            return abs(total_probability - 1) < 0.00001


    def calculateOptionPrice(self):
        """
        Berechnet den Preis der ausgewählten Option basierend auf den Benutzereingaben und dem ausgewählten Modell.

        Diese Methode führt die Validierung der Benutzereingaben durch, bestimmt das gewählte Bewertungsmodell (Binomial- oder Trinomialmodell),
        konfiguriert die erforderlichen Modellparameter und ruft die Preisberechnungsfunktion des ausgewählten Modells auf. Bei erfolgreicher
        Berechnung wird der berechnete Optionspreis im UI angezeigt. Im Falle ungültiger Eingaben oder Berechnungsfehler wird eine entsprechende
        Fehlermeldung angezeigt.

        Die Methode loggt außerdem alle Berechnungsaktivitäten und potenzielle Fehler in eine Log-Datei, um die Nachverfolgung und Fehleranalyse zu erleichtern.

        Raises:
            ValueError: Wenn eine oder mehrere Benutzereingaben ungültig sind (z.B. nicht-numerische Werte für numerisch erwartete Felder,
                        ungültige Wahrscheinlichkeiten, etc.).

        Beispiel:
            Der Benutzer gibt alle erforderlichen Daten für eine Option im UI ein und wählt das Binomialmodell für die Berechnung.
            Nach dem Klick auf die Berechnungsschaltfläche zeigt die Anwendung den berechneten Optionspreis oder eine Fehlermeldung an.
        """
        logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

        try:
            # Überprüft jede Eingabe auf gültige Fließkommazahlen und leert das Plot-Layout bei Fehlern.
            for field in [self.ui.in_s0, self.ui.in_k, self.ui.in_r, self.ui.in_t]:
                if not self.is_valid_float(field.text()):
                    clearLayout(self.ui.fr_plot.layout())
                    raise ValueError(f"{field.objectName()} muss ein numerischer Wert sein.")

            # Stellt sicher, dass die Anzahl der Perioden eine ganze Zahl ist.
            if not self.ui.in_n.text().isdigit():
                raise ValueError("N muss eine ganze Zahl sein.")

            # Konvertiert Eingabewerte in ihre entsprechenden Datentypen.
            S0, K, r, T = map(float, [self.ui.in_s0.text(), self.ui.in_k.text(), self.ui.in_r.text(), self.ui.in_t.text()])
            N = int(self.ui.in_n.text())
            sigma = float(self.ui.in_sigma.text()) if not self.ui.cb_sigma.isChecked() else None
            div = float(self.ui.in_div.text()) if self.ui.in_div.text() else 0.0

            # Überprüft, dass sigma und div gültige, positive Werte sind.
            if sigma is not None and (sigma <= 0 or div < 0):
                raise ValueError("sigma und div müssen positive Werte sein.")

            # Stellt die Modellparameter zusammen.
            model_settings = {
                "S0": S0, "K": K, "T": T, "r": r, "N": N, "sigma": sigma, "div": div,
                "is_put": self.ui.rb_euput.isChecked() or self.ui.rb_powput.isChecked() or self.ui.rb_digput.isChecked()
            }

            if self.ui.rb_strangle.isChecked() and self.is_valid_float(self.ui.in_k2.text()):
                K2 = float(self.ui.in_k2.text())
                model_settings["K2"] = K2
            elif self.ui.rb_strangle.isChecked():
                raise ValueError("K2 muss ein numerischer Wert sein für Strangle Optionen.")

            # Fügt die Einstellung für amerikanische Optionen hinzu, falls vorhanden.
            if hasattr(self.ui, 'cb_isAM'):
                model_settings["is_am"] = self.ui.cb_isAM.isChecked()

            # Aktualisiert die Modellparameter für direkte Wahrscheinlichkeiten, wenn Sigma unbekannt ist.
            if self.ui.cb_sigma.isChecked():
                model_settings.update({
                    "pu": float(self.ui.in_pu.text()),
                    "pd": float(self.ui.in_pd.text())
                })

                # Ergänzt Parameter für das Trinomialmodell.
                if self.ui.rb_trinomialmodell.isChecked():
                    model_settings.update({
                        "pm": float(self.ui.in_pm.text()),
                        "u": float(self.ui.in_u.text()),
                        "d": float(self.ui.in_d.text()),
                        "m": float(self.ui.in_m.text())
                    })

            # Wählt das entsprechende Modell basierend auf der Benutzerauswahl.
            model_class = Trinomialmodell if self.ui.rb_trinomialmodell.isChecked() else Binomialmodell
            verfahren = "Trinomialmodell" if self.ui.rb_trinomialmodell.isChecked() else "Binomialmodell"
            option_type = self.determine_option_type()  # Bestimmt den Optionstyp basierend auf der UI-Auswahl.
            option_typ_text = self.get_option_type_text(option_type)  # Holt den Text für den ausgewählten Optionstyp.

            # Erstellt das Modell mit den definierten Einstellungen und berechnet den Optionspreis.
            model = model_class(**model_settings)
            preis = model.price_option(option_type)

            # Berechnet Konvergenzpreise für das europäische Modell ohne bekannte Sigma-Werte.
            convergence_prices_BM = []
            convergence_prices_TM = []
            if option_type == "european" and not self.ui.cb_sigma.isChecked():
                for step in range(1, model.N + 1):
                    temp_model_BM = Binomialmodell(S0=S0, K=K, r=r, T=T, N=step, sigma=sigma, div=div, is_put=model.is_put)
                    temp_model_TM = Trinomialmodell(S0=S0, K=K, r=r, T=T, N=step, sigma=sigma, div=div, is_put=model.is_put)
                    convergence_prices_BM.append(temp_model_BM.price_option(option_type))
                    convergence_prices_TM.append(temp_model_TM.price_option(option_type))

            # Zeigt das Berechnungsergebnis an oder eine Fehlermeldung, falls die Berechnung fehlschlug.
            ausgabe_text = f"Für das ausgewählte Verfahren {verfahren} und der Option \"{option_typ_text}\" beträgt der Optionspreis wie folgt: {preis:.2f}" if preis is not None else "Fehler bei der Berechnung"
            self.ui.txt_preis.setText(ausgabe_text)

            # Zeigt die Ergebnisse in einem Plot-Tab an, inklusive der Konvergenzanalyse.
            sigma_bekannt = not self.ui.cb_sigma.isChecked()
            self.displayPlotInTab(model, verfahren, option_type, sigma_bekannt, convergence_prices_BM, convergence_prices_TM)

        except ValueError as e:
            # Zeigt Fehlermeldungen an und loggt den Fehler.
            self.handleCalculationError(e)

    def handleCalculationError(self, error):
        """
        Behandelt Berechnungsfehler, indem die UI entsprechend aktualisiert und der Fehler geloggt wird.

        Args:
            error (Exception): Die Ausnahme, die während der Berechnung aufgetreten ist.
        """
        clearLayout(self.ui.fr_plot.layout())
        self.ui.txt_preis.setText("Eingabefehler!")
        logging.error("Ein Fehler ist aufgetreten", exc_info=True)
        self.show_input_error(str(error))

    def get_option_type_text(self, option_type):
        """
        Liefert den benutzerfreundlichen Text für einen gegebenen Optionstyp.

        Diese Methode verwendet ein Mapping, um den internen Optionstyp-Schlüssel (wie 'european', 'power', etc.)
        in einen für den Benutzer lesbaren Text umzuwandeln. Dies erleichtert die Anzeige und das Verständnis
        der ausgewählten Optionstypen in der Benutzeroberfläche.

        Args:
            option_type (str): Der Schlüssel des Optionstyps, der in benutzerfreundlichen Text umgewandelt werden soll.

        Returns:
            str: Der benutzerfreundliche Text für den gegebenen Optionstyp. Gibt "Unbekannter Typ" zurück,
                falls der Optionstyp im Mapping nicht gefunden wird.

        Beispiel:
            Um den Text für den 'european' Optionstyp zu erhalten:
                >>> get_option_type_text('european')
                "Europäische Option"
            Um den Text für einen nicht definierten Optionstyp zu erhalten:
                >>> get_option_type_text('exotisch')
                "Unbekannter Typ"
        """
        # Ein Dictionary, das Optionstyp-Schlüssel zu benutzerfreundlichen Texten abbildet.
        option_type_mapping = {
            'european': "Europäische Option",
            'power': "Power Option",
            'digital': "Digitale Option",
            'strangle': "Strangle Option",
            'american': 'Amerikanische Option'
        }

        # Nutzt das Mapping, um den benutzerfreundlichen Text für den gegebenen Optionstyp zu finden, oder gibt einen Standardtext zurück.
        return option_type_mapping.get(option_type, "Unbekannter Typ")

    def show_input_error(self, message):
        """
        Zeigt eine Fehlermeldung im UI-Element für den Optionspreis an.

        Diese Methode aktualisiert das Textfeld, das normalerweise den berechneten Optionspreis anzeigt,
        um stattdessen eine allgemeine Fehlermeldung ("Eingabefehler!") auszugeben. Sie dient als einfache
        Methode, um dem Benutzer Feedback zu geben, falls bei der Eingabe oder Berechnung ein Fehler auftritt.
        Im Gegensatz zu detaillierteren Fehlermeldungen, die möglicherweise in einem Dialogfenster angezeigt werden,
        bietet diese Methode eine schnelle und direkte Art, auf Fehlerzustände hinzuweisen.

        Args:
            message (str): Die Fehlermeldung, die an anderer Stelle geloggt oder verarbeitet werden könnte. In dieser
                        Implementierung wird der Wert von 'message' nicht direkt verwendet, aber er könnte für zukünftige
                        Erweiterungen oder detailliertere Fehlermeldungen nützlich sein.

        Beispiel:
            Wenn ein Fehler bei der Eingabeüberprüfung auftritt, kann diese Methode aufgerufen werden, um den Benutzer
            über das Problem zu informieren:
                >>> show_input_error("Der Ausübungspreis muss größer als 0 sein.")
            Das Ergebnis ist eine allgemeine Fehlermeldung im Preisfeld, unabhängig vom spezifischen Inhalt der 'message'.
        """
        # Setzt den Text des Preis-Anzeigefeldes auf eine allgemeine Fehlermeldung.
        if not ((self.ui.rb_binomialmodell.isChecked() or self.ui.rb_trinomialmodell.isChecked()) and
                (self.ui.rb_eucall.isChecked() or self.ui.rb_euput.isChecked() or
                self.ui.rb_powcall.isChecked() or self.ui.rb_powput.isChecked() or
                self.ui.rb_digcall.isChecked() or self.ui.rb_digput.isChecked() or
                self.ui.rb_strangle.isChecked())):
            # Zeigt eine spezifische Fehlermeldung an, falls kein Verfahren oder Option ausgewählt wurde.
            self.ui.txt_preis.setText("Wählen Sie ein Verfahren oder Option aus!")
        else:
            # Zeigt die allgemeine Fehlermeldung oder eine spezifische Nachricht basierend auf dem 'message'-Parameter an.
            self.ui.txt_preis.setText("Eingabefehler!")

    def determine_option_type(self):
        """
        Ermittelt den Optionstyp basierend auf der Auswahl der RadioButtons im UI.

        Diese Methode überprüft die Zustände der RadioButtons, die verschiedenen Optionstypen entsprechen, und bestimmt,
        welcher Optionstyp ausgewählt wurde. Sie unterstützt die Identifizierung der Hauptoptionstypen, die in der
        Anwendung verfügbar sind: europäische Optionen, Power-Optionen, digitale Optionen und Strangle-Optionen.

        Returns:
            str: Eine Zeichenkette, die den ausgewählten Optionstyp repräsentiert. Mögliche Rückgabewerte sind
                'european', 'power', 'digital', oder 'strangle'.

        Raises:
            ValueError: Wenn kein bekannter Optionstyp ausgewählt wurde. Dies dient als Sicherheitsmaßnahme, um sicherzustellen,
                        dass die Anwendung nur mit definierten und unterstützten Optionstypen arbeitet.

        Beispiel:
            Angenommen, der Benutzer wählt die RadioButton für eine europäische Call-Option:
                >>> self.ui.rb_eucall.setChecked(True)
                >>> determine_option_type()
                'european'
            Diese Rückgabe signalisiert, dass der Benutzer eine europäische Option ausgewählt hat.
        """
        # Überprüft die Zustände der RadioButtons, um den ausgewählten Optionstyp zu bestimmen.
        if self.ui.rb_eucall.isChecked() or self.ui.rb_euput.isChecked():
            return 'european'
        elif self.ui.rb_powcall.isChecked() or self.ui.rb_powput.isChecked():
            return 'power'
        elif self.ui.rb_digcall.isChecked() or self.ui.rb_digput.isChecked():
            return 'digital'
        elif self.ui.rb_strangle.isChecked():
            return 'strangle'
        else:
            # Wirft einen Fehler, wenn kein bekannter Optionstyp ausgewählt wurde.
            raise ValueError("Unbekannter Optionstyp")

    def displayPlotInTab(self, model, verfahren, option_type, sigma_bekannt, convergence_prices_BM, convergence_prices_TM):
        """
        Zeigt die Ergebnisse der Optionspreisberechnung und Konvergenzanalyse in einem Tab-Widget an.

        Diese Methode nimmt die Ergebnisse der Optionspreisberechnung sowie die Konvergenzpreise für das Binomial-
        und Trinomialmodell entgegen und stellt sie graphisch dar. Sie verwendet dazu eine Instanz der FinanzPlot-Klasse,
        um die Plots zu erzeugen, und fügt diese dann einem PlotQTabWidget hinzu, welches im UI angezeigt wird.
        Das Layout des Zielcontainers wird zuerst geleert, um sicherzustellen, dass vorherige Plots entfernt werden,
        bevor der neue Plot hinzugefügt wird.

        Args:
            model (Binomialmodell/Trinomialmodell): Das Modell, das für die Berechnung verwendet wurde.
            verfahren (str): Die Bezeichnung des verwendeten Verfahrens ('Binomialmodell' oder 'Trinomialmodell').
            option_type (str): Der Typ der Option, für die die Berechnung durchgeführt wurde.
            sigma_bekannt (bool): Ein Boolean, der angibt, ob die Volatilität (Sigma) bekannt war.
            convergence_prices_BM (list): Eine Liste von Konvergenzpreisen für das Binomialmodell.
            convergence_prices_TM (list): Eine Liste von Konvergenzpreisen für das Trinomialmodell.

        Beispiel:
            Angenommen, es wurde eine Option mit dem Trinomialmodell bewertet, und die Ergebnisse sowie
            Konvergenzpreise sollen angezeigt werden:
                >>> displayPlotInTab(model, 'Trinomialmodell', 'european', True, convergence_prices_BM, convergence_prices_TM)
            Dies führt dazu, dass die Ergebnisse in einem neuen Tab im UI angezeigt werden.
        """
        # Erstellt den Finanzplot basierend auf dem Modell und den spezifischen Einstellungen.
        plot_finanz = FinanzPlot(model)
        # Erstellt das Tab-Widget, das den Plot enthält, mit zusätzlichen Informationen über den Berechnungstyp und die Konvergenzpreise.
        plotQTabWidget = PlotQTabWidget(plot_finanz, option_type, verfahren, sigma_bekannt, convergence_prices_BM, convergence_prices_TM)

        # Bereinigt das Layout, um sicherzustellen, dass alte Inhalte entfernt werden.
        clearLayout(self.ui.fr_plot.layout())

        # Prüft, ob das Ziel-Layout bereits existiert, und fügt anderenfalls ein neues hinzu.
        if self.ui.fr_plot.layout() is None:
            layout = QVBoxLayout(self.ui.fr_plot)
            self.ui.fr_plot.setLayout(layout)
        else:
            layout = self.ui.fr_plot.layout()

        # Fügt das Plot-Tab-Widget zum Layout hinzu, um es im UI sichtbar zu machen.
        layout.addWidget(plotQTabWidget)

    def startQuiz(self):
        """
        Startet das Quiz im LearningHub der Anwendung.

        Diese Methode wird aufgerufen, um den Quizprozess im LearningHub zu initiieren. Sie überprüft zunächst, ob eine
        Verbindung zur Datenbank besteht, die den Fragenkatalog enthält. Ist dies nicht der Fall, wird versucht, den
        Fragenkatalog durch Aufrufen der `setupFragenkatalog`-Methode zu initialisieren und eine Verbindung zur Datenbank
        herzustellen. Diese Initialisierung umfasst das Laden der Fragen aus der Datenbank und das Vorbereiten der UI für
        das Quiz.

        Die Methode dient als Einstiegspunkt für das Quiz und stellt sicher, dass alle notwendigen Ressourcen geladen und
        verfügbar sind, bevor der Benutzer mit dem Beantworten von Fragen beginnt.

        Beispiel:
            Wenn der Benutzer den Button zum Start des Quizzes anklickt:
                >>> startQuiz()
            Dies prüft die Datenbankverbindung und initialisiert das Quiz, falls erforderlich.
        """
        # Überprüft, ob bereits eine Verbindung zur Datenbank besteht.
        if not self.dbConnected:
            # Initialisiert den Fragenkatalog und stellt eine Datenbankverbindung her, falls noch nicht geschehen.
            self.setupFragenkatalog()

    def showMessage(self, title, text, icon=QMessageBox.Information):
        """
        Zeigt eine Nachrichtenbox mit einem spezifischen Titel, Text und einem Symbol an.

        Diese universelle Methode dient dazu, dem Benutzer Informationen, Warnungen oder Fehler in Form einer
        modalen Dialogbox zu präsentieren. Die Methode ist flexibel einsetzbar, da sie es ermöglicht, den Titel,
        den Text und das Symbol der Nachrichtenbox anzupassen, um den Kontext der Nachricht entsprechend der
        Situation zu reflektieren.

        Args:
            title (str): Der Titel der Nachrichtenbox, der oben in der Box angezeigt wird.
            text (str): Der Textinhalt der Nachrichtenbox, der die eigentliche Nachricht oder Information für den Benutzer darstellt.
            icon (QMessageBox.Icon, optional): Das Symbol, das in der Nachrichtenbox angezeigt wird, um die Art der Nachricht zu kennzeichnen
                                            (z.B. Information, Warnung, Fehler). Standardmäßig wird das Informationssymbol verwendet.

        Beispiel:
            Um eine einfache Informationsnachricht anzuzeigen:
                >>> showMessage("Erfolg", "Die Operation wurde erfolgreich abgeschlossen.")
            Um eine Warnung an den Benutzer auszugeben:
                >>> showMessage("Warnung", "Unzureichende Eingabe.", icon=QMessageBox.Warning)
        """
        # Erstellt das QMessageBox-Objekt.
        msg = QMessageBox()
        msg.setIcon(icon)  # Setzt das Symbol der Nachrichtenbox.
        msg.setText(text)  # Setzt den Text der Nachrichtenbox.
        msg.setWindowTitle(title)  # Setzt den Titel der Nachrichtenbox.
        msg.setStandardButtons(QMessageBox.Ok)  # Fügt einen OK-Button hinzu, um die Nachrichtenbox zu schließen.
        msg.exec_()  # Zeigt die Nachrichtenbox als modalen Dialog an.

    def loadNextQuestion(self):
        """
        Lädt die nächste Frage für das Quiz und verarbeitet die Antwort des Benutzers.

        Diese Methode wird aufgerufen, wenn der Benutzer eine Antwort ausgewählt hat und bereit ist, zur nächsten Frage
        überzugehen. Sie überprüft, ob eine Antwort ausgewählt wurde, bewertet die ausgewählte Antwort, gibt Feedback
        und lädt dann die nächste Frage aus dem Fragenkatalog. Bei einer korrekten Antwort wird der Benutzer gelobt,
        bei einer falschen Antwort erhält er spezifisches Feedback zur richtigen Antwort.

        Raises:
            Eine Warnung, falls keine Antwort ausgewählt wurde, fordert den Benutzer auf, eine Auswahl zu treffen,
            bevor er fortfahren kann.

        Beispiel:
            Der Benutzer wählt eine Antwort und klickt auf 'Nächste Frage'. Diese Methode bewertet die Antwort,
            gibt Feedback und lädt die nächste Frage.
        """
        # Mapping der falschen Antwortoptionen zu ihrem spezifischen Feedback.
        feedback_key_map = {
            'option_2': 'feedback_falsch_1',
            'option_3': 'feedback_falsch_2',
            'option_4': 'feedback_falsch_3'
        }

        # Ermittelt die ID der ausgewählten Antwort.
        selectedAnswerId = next((rb.property("answer_id") for rb in self.radioButtons if rb.isChecked()), None)

        # Zeigt eine Warnung an, wenn keine Antwort ausgewählt wurde.
        if selectedAnswerId is None:
            self.showMessage("Antwort auswählen", "Bitte wählen Sie eine Antwort aus, bevor Sie fortfahren.", QMessageBox.Warning)
            return

        # Überprüft, ob die ausgewählte Antwort korrekt ist.
        if selectedAnswerId == 'option_1':
            self.updateCounters(True)  # Aktualisiert den Zähler für richtige Antworten.
            self.showMessage("Richtig!", "Ihre Antwort ist korrekt.")
            self.updateDatabaseCorrectAnswer()  # Aktualisiert die Datenbank mit der korrekten Antwort.
        else:
            self.updateCounters(False)  # Aktualisiert den Zähler für falsche Antworten.
            # Holt das spezifische Feedback für die falsche Antwort.
            wrong_feedback = self.currentQuestion.get(feedback_key_map.get(selectedAnswerId, 'feedback_falsch_1'))
            correct_option_text = self.currentQuestion['richtige_option']
            # Zeigt eine Nachricht mit dem Feedback und der richtigen Antwort.
            self.showMessage("Falsch!", f"Leider ist Ihre Antwort falsch.\n\nErklärung: {wrong_feedback}\n\nRichtige Antwort: {correct_option_text}", QMessageBox.Warning)

        self.resetRadioButtons()  # Setzt die RadioButtons für die nächste Frage zurück.
        self.setupFragenkatalog()  # Lädt den Fragenkatalog für die nächste Frage.

    def resetRadioButtons(self):
        """
        Setzt die Zustände der RadioButtons für das Quiz zurück.

        Nachdem der Benutzer eine Frage beantwortet hat und zur nächsten Frage übergeht, müssen die RadioButtons
        zurückgesetzt werden, damit keine Auswahl mehr markiert ist. Diese Methode stellt sicher, dass alle
        RadioButtons im Quiz-Bereich für die nächste Frage deselektiert sind. Dies ist notwendig, um zu verhindern,
        dass eine vorherige Auswahl den aktuellen Fragezustand beeinflusst.

        Die Methode setzt kurzzeitig die AutoExclusive-Eigenschaft der RadioButtons auf False, um mehrere RadioButtons
        gleichzeitig deselektieren zu können, und stellt diese Eigenschaft anschließend wieder auf True, damit nur eine
        Option zur Zeit ausgewählt werden kann.

        Beispiel:
            Nachdem der Benutzer eine Frage beantwortet und auf 'Nächste Frage' geklickt hat, werden die RadioButtons
            für die neue Frage zurückgesetzt, sodass keine Auswahl voreingestellt ist.
        """
        # Durchläuft alle RadioButtons, die für Quizantworten verwendet werden.
        for rb in self.radioButtons:
            rb.setAutoExclusive(False)  # Erlaubt vorübergehend, dass kein RadioButton ausgewählt ist.
            rb.setChecked(False)  # Deselektiert den RadioButton.
            rb.setAutoExclusive(True)  # Stellt sicher, dass nach dem Zurücksetzen wieder nur eine Auswahl möglich ist.

    def updateDatabaseCorrectAnswer(self):
        """
        Aktualisiert die Datenbank mit der neuen Anzahl richtiger Antworten für die aktuelle Frage.

        Nachdem der Benutzer eine Frage korrekt beantwortet hat, wird diese Methode aufgerufen, um die Datenbank
        entsprechend zu aktualisieren. Sie erhöht die Anzahl der richtigen Antworten (`richtige_antworten_zahl`)
        für die aktuelle Frage um eins. Dies ist nützlich für die Analyse der Quizleistung und kann dazu beitragen,
        Fragen zu identifizieren, die häufig richtig beantwortet werden, oder um die Schwierigkeit der Fragen
        im Laufe der Zeit anzupassen.

        Die Methode bereitet eine SQL-Update-Anfrage vor, bindet die notwendigen Werte und führt sie aus. Bei
        Fehlern während der Ausführung wird eine Fehlermeldung in der Konsole ausgegeben.

        Beispiel:
            Angenommen, der Benutzer beantwortet eine Frage richtig. Diese Methode wird dann aufgerufen, um
            die Anzahl der richtigen Antworten für diese Frage in der Datenbank zu erhöhen.
        """
        # Extrahiert die ID und die bisherige Anzahl richtiger Antworten der aktuellen Frage.
        frage_id = self.currentQuestion['id']
        richtige_antworten_zahl = self.currentQuestion['richtige_antworten_zahl'] + 1

        # Bereitet die SQL-Update-Anfrage vor.
        update_query = QtSql.QSqlQuery()
        update_query.prepare("UPDATE gt_quiz_fragen SET richtige_antworten_zahl = :richtige_antworten_zahl WHERE id = :id")
        update_query.bindValue(":richtige_antworten_zahl", richtige_antworten_zahl)  # Bindet die neue Anzahl richtiger Antworten.
        update_query.bindValue(":id", frage_id)  # Bindet die ID der aktuellen Frage.

        # Führt die Update-Anfrage aus. Gibt eine Fehlermeldung aus, wenn die Ausführung fehlschlägt.
        if not update_query.exec_():
            print(f"Fehler beim Aktualisieren der Datenbank: {update_query.lastError().text()}")

    def setupFragenkatalog(self):
        """
        Initialisiert den Fragenkatalog für das Quiz, indem eine Verbindung zur Datenbank hergestellt und die Fragen geladen werden.

        Diese Methode überprüft zunächst, ob bereits eine Verbindung zur Quizdatenbank besteht. Ist dies nicht der Fall,
        wird eine neue Verbindung zu einer SQLite-Datenbank hergestellt, die den Fragenkatalog enthält. Anschließend werden
        alle Fragen aus der Datenbank abgefragt und für die Verwendung im Quiz vorbereitet.

        Falls die Datenbankverbindung erfolgreich hergestellt und die Fragen erfolgreich geladen wurden, wird eine zufällige
        Frage für die Anzeige im Quiz ausgewählt. Bei Fehlern in der Datenbankabfrage oder beim Öffnen der Datenbank werden
        entsprechende Fehlermeldungen ausgegeben.

        Returns:
            bool: True, wenn die Datenbank erfolgreich verbunden und die Fragen geladen wurden, False, wenn ein Fehler auftrat.

        Beispiel:
            Beim Start des Quizzes oder beim Laden der nächsten Frage:
                >>> setupFragenkatalog()
            Diese Methode wird aufgerufen, um sicherzustellen, dass die Fragen für das Quiz verfügbar sind.
        """
        # Überprüft, ob bereits eine Verbindung zur Datenbank besteht.
        if not self.dbConnected:
            # Fügt eine SQLite-Datenbank hinzu und setzt den Pfad zur Datenbank.
            QtSql.QSqlDatabase.addDatabase("QSQLITE")
            databasePath = resource_path("C:\\Users\\murat\\OneDrive\\Abschlussarbeit B.Sc\\Python\\QT\\fragenkatalog.sqlite")
            db = QtSql.QSqlDatabase.database()
            db.setDatabaseName(databasePath)

            # Versucht, die Datenbank zu öffnen, und gibt eine Fehlermeldung aus, wenn dies fehlschlägt.
            if not db.open():
                print('Datenbankverbindung konnte nicht hergestellt werden')
                return False
            self.dbConnected = True  # Markiert die Datenbank als verbunden.

        # Bereitet eine SQL-Abfrage vor, um alle Fragen aus der Datenbank zu laden.
        query = QtSql.QSqlQuery()
        if query.exec_("SELECT * FROM gt_quiz_fragen"):
            fragen = []  # Liste, um die geladenen Fragen zu speichern.
            while query.next():
                # Extrahiert jede Frage und ihre Details aus dem Abfrageergebnis.
                frage = {query.record().fieldName(i): query.value(i) for i in range(query.record().count())}
                fragen.append(frage)

            # Wählt eine zufällige Frage aus, wenn Fragen erfolgreich geladen wurden.
            if fragen:
                self.chooseRandomQuestion(fragen)
        else:
            # Gibt eine Fehlermeldung aus, wenn bei der Ausführung der Abfrage ein Fehler auftritt.
            print("Fehler bei der Ausführung der Abfrage:", query.lastError().text())
        return True  # Gibt True zurück, um den Erfolg der Operation anzudeuten.

    def chooseRandomQuestion(self, fragen):
        """
        Wählt eine zufällige Frage aus dem Fragenkatalog für die Anzeige im Quiz.

        Diese Methode wählt basierend auf einer Gewichtung, die invers zur Anzahl der richtigen Antworten pro Frage ist,
        eine zufällige Frage aus. Fragen, die seltener richtig beantwortet wurden, haben somit eine höhere Wahrscheinlichkeit,
        ausgewählt zu werden. Dies fördert eine vielfältigere und ausgewogenere Quiz-Erfahrung, indem es sicherstellt, dass
        Benutzer mit einem breiteren Spektrum an Fragen konfrontiert werden.

        Nach der Auswahl einer Frage wird die UI entsprechend aktualisiert, um die neue Frage und ihre Antwortmöglichkeiten
        anzuzeigen.

        Args:
            fragen (list): Eine Liste von Dictionaries, wobei jedes Dictionary eine Frage mit ihren Details repräsentiert.

        Beispiel:
            Angenommen, der Fragenkatalog wurde geladen und enthält mehrere Fragen:
                >>> fragen = [...]
                >>> chooseRandomQuestion(fragen)
            Diese Methode wählt eine Frage aus und aktualisiert die UI für die Anzeige.
        """
        # Bestimmt das maximale Gewicht basierend auf der Anzahl der richtigen Antworten.
        max_richtige_antworten = max(int(frage["richtige_antworten_zahl"]) for frage in fragen) + 1
        # Berechnet die Gewichte für jede Frage, invers zur Anzahl der richtigen Antworten.
        gewichte = [max_richtige_antworten - int(frage["richtige_antworten_zahl"]) for frage in fragen]

        # Wählt eine Frage basierend auf den berechneten Gewichten zufällig aus.
        self.currentQuestion = random.choices(fragen, weights=gewichte, k=1)[0]

        # Aktualisiert die UI mit der ausgewählten Frage.
        self.updateUIWithQuestion(self.currentQuestion)

    def updateUIWithQuestion(self, frage):
        """
        Aktualisiert die Benutzeroberfläche mit einer neuen Quizfrage und den dazugehörigen Antwortmöglichkeiten.

        Diese Methode nimmt die Daten einer einzelnen Frage und zeigt sie im Quiz-Bereich der Anwendung an. Sie setzt den
        Fragetext und verteilt die Antwortmöglichkeiten auf die entsprechenden RadioButtons. Die Antworten werden zufällig
        sortiert, um Vorhersagbarkeit zu vermeiden und das Quiz herausfordernder zu gestalten. Zudem wird die ID der richtigen
        Antwort für die spätere Überprüfung gespeichert.

        Args:
            frage (dict): Ein Dictionary, das die Details der aktuellen Frage enthält. Es sollte den Fragetext, vier Antwortmöglichkeiten
                        und die ID der richtigen Antwort enthalten.

        Beispiel:
            Angenommen, eine neue Frage soll in der UI dargestellt werden:
                >>> frage = {
                        "frage": "Call-Option",
                        "option_1": "Ein Finanzvertrag, der dem Käufer das Recht gibt, einen Basiswert zu einem festgelegten Preis und Zeitpunkt zu kaufen, ohne eine Kaufpflicht.",
                        "option_2": "Eine Vereinbarung, die den Verkäufer verpflichtet, den Basiswert zu einem bestimmten Preis zu einem festgelegten Zeitpunkt zu verkaufen, unabhängig von den Marktbedingungen.",
                        "option_3": "Ein Finanzinstrument, das dem Inhaber das Recht gibt, den Basiswert zu jedem Zeitpunkt vor der Fälligkeit zu verkaufen, nicht zu kaufen.",
                        "option_4": "Ein Vertrag, der dem Käufer die Pflicht auferlegt, den Basiswert zu einem vorher festgelegten Preis und Zeitpunkt zu kaufen, ohne die Möglichkeit, vom Kauf zurückzutreten.",
                        "richtige_option": "option_1"
                    }
                >>> updateUIWithQuestion(frage)
            Die UI wird dann mit der Frage und den vier zufällig sortierten Antwortmöglichkeiten aktualisiert.
        """
        # Setzt den Fragetext im dafür vorgesehenen Textfeld.
        self.ui.txt_definition_term.setText(frage["frage"])

        # Erstellt eine Liste der Antwortmöglichkeiten und deren IDs.
        answers = [(frage[f"option_{i}"], f'option_{i}') for i in range(1, 5)]
        # Mischelt die Antworten, um sie in zufälliger Reihenfolge anzuzeigen.
        random.shuffle(answers)

        # Weist jeder Antwortoption einen RadioButton zu und setzt den Text entsprechend.
        for rb, (text, answer_id) in zip(self.radioButtons, answers):
            rb.setText(text)
            rb.setProperty("answer_id", answer_id)

        # Speichert die ID der richtigen Antwort, um die Antwort des Benutzers später überprüfen zu können.
        self.correctAnswerId = frage["richtige_option"]

    def updateCounters(self, isCorrect):
        """
        Aktualisiert die Zähler für richtige und falsche Antworten im Quiz.

        Diese Methode wird nach der Beantwortung einer Frage durch den Benutzer aufgerufen, um die Anzahl der
        richtigen und falschen Antworten entsprechend zu aktualisieren. Sie erhöht den jeweiligen Zähler basierend darauf,
        ob die Antwort des Benutzers korrekt war oder nicht. Diese Zähler bieten dem Benutzer ein direktes Feedback
        über seine Leistung im Quiz.

        Args:
            isCorrect (bool): Ein Boolean-Wert, der angibt, ob die Antwort des Benutzers korrekt war. True bedeutet,
                            dass die Antwort korrekt war, False bedeutet, dass sie falsch war.

        Beispiel:
            Angenommen, der Benutzer hat eine Frage richtig beantwortet:
                >>> updateCounters(True)
            Dies erhöht den Zähler der richtigen Antworten um eins.

            Angenommen, der Benutzer hat eine Frage falsch beantwortet:
                >>> updateCounters(False)
            Dies erhöht den Zähler der falschen Antworten um eins.
        """
        if isCorrect:
            # Erhöht den Zähler der richtigen Antworten, wenn die Antwort korrekt war.
            current_count = int(self.ui.txt_true_num.text())  # Holt den aktuellen Stand des Zählers.
            self.ui.txt_true_num.setText(str(current_count + 1))  # Aktualisiert den Zähler.
        else:
            # Erhöht den Zähler der falschen Antworten, wenn die Antwort falsch war.
            current_count = int(self.ui.txt_false_num.text())  # Holt den aktuellen Stand des Zählers.
            self.ui.txt_false_num.setText(str(current_count + 1))  # Aktualisiert den Zähler.

    def resetLearningHub(self):
        """
        Setzt den LearningHub zurück, indem die Zähler für richtige und falsche Antworten
        sowie die Datenbankwerte für die Anzahl der richtigen Antworten aller Fragen auf null gesetzt werden.

        Diese Methode wird typischerweise verwendet, um den LearningHub für einen neuen Durchlauf vorzubereiten,
        indem sie sicherstellt, dass alle Benutzerfortschritte zurückgesetzt und alle Fragen als unbeantwortet markiert werden.
        Das Zurücksetzen der Datenbank beinhaltet das Aktualisieren der 'richtige_antworten_zahl' für jede Frage in der
        Datenbank auf 0, was bedeutet, dass alle statistischen Informationen über vorherige Quizdurchläufe entfernt werden.

        Beispiel:
            Angenommen, der Benutzer möchte das Quiz neu starten oder die Statistiken löschen:
                >>> resetLearningHub()
            Dies führt zum Zurücksetzen der Quizstatistiken und zur Vorbereitung für einen neuen Start.
        """
        # Erstellt eine SQL-Abfrage zum Zurücksetzen der Anzahl der richtigen Antworten in der Datenbank.
        reset_query = QtSql.QSqlQuery()
        if reset_query.exec_("UPDATE gt_quiz_fragen SET richtige_antworten_zahl = 0"):
            # Informiert über den erfolgreichen Reset.
            print("Die Datenbank wurde erfolgreich zurückgesetzt.")
        else:
            # Gibt eine Fehlermeldung aus, falls der Reset nicht erfolgreich war.
            print(f"Fehler beim Zurücksetzen der Datenbank: {reset_query.lastError().text()}")

        # Setzt die Zähler in der UI für richtige und falsche Antworten zurück.
        self.ui.txt_true_num.setText("0")
        self.ui.txt_false_num.setText("0")

    def open_pdf_in_external_viewer(self):
        """
        Öffnet das PDF der Bachelorarbeit in einem externen PDF-Viewer.

        Diese Methode wird aufgerufen, wenn der Benutzer den Button `bt_readpdf` betätigt. Sie nutzt die Fähigkeiten des 
        Betriebssystems, um die Bachelorarbeit in der Standardanwendung für PDF-Dateien zu öffnen. Dadurch wird dem Benutzer 
        eine komfortable Möglichkeit geboten, sich mit der theoretischen Ausarbeitung und der Dokumentation der in der 
        Bachelorarbeit entwickelten App vertraut zu machen. Der externe PDF-Viewer bietet eine umfangreiche 
        Betrachtungsumgebung, die zum Lesen und Navigieren des Dokuments ideal ist.

        Beispiel:
            Der Benutzer klickt auf `bt_readpdf`, woraufhin das Betriebssystem den Standard-PDF-Viewer öffnet und
            das PDF der Bachelorarbeit anzeigt. Dies ermöglicht dem Benutzer eine detaillierte Ansicht der 
            theoretischen Grundlagen und der dokumentierten Implementierung der Baummodelle für die Bewertung von Derivaten.

        Voraussetzungen:
            - Der Pfad zur PDF-Datei muss korrekt sein und auf eine existierende Datei verweisen.
            - Ein PDF-Viewer muss auf dem System des Benutzers installiert sein und korrekt funktionieren.
        """
        # Pfad zum PDF der Bachelorarbeit
        pdf_path = resource_path("C:\\Users\\murat\\OneDrive\\Abschlussarbeit B.Sc\\Python\\QT\\Finanzmathematik.pdf")

        # Umwandlung des Dateipfads in ein QUrl-Objekt
        pdf_url = QUrl.fromLocalFile(pdf_path)

        # Öffnen des PDFs im Standard-PDF-Viewer des Betriebssystems
        QDesktopServices.openUrl(pdf_url)

def clearLayout(layout):
    """
    Entfernt alle Widgets aus einem gegebenen Layout und löscht sie.

    Diese Funktion durchläuft ein Layout und entfernt jedes darin enthaltene Widget. Es ist eine generische Hilfsfunktion,
    die dazu dient, ein Layout zu leeren, bevor neue Widgets hinzugefügt werden. Dies ist besonders nützlich, um die
    Benutzeroberfläche dynamisch zu aktualisieren, ohne alte Inhalte beizubehalten. Nach dem Entfernen der Widgets aus dem
    Layout werden diese auch aus dem Speicher gelöscht, um Leckagen zu vermeiden.

    Args:
        layout (QLayout): Das Layout-Objekt, aus dem alle Widgets entfernt werden sollen.

    Beispiel:
        Angenommen, es gibt ein Layout mit mehreren Widgets, das geleert werden soll:
            >>> clearLayout(someLayout)
        Nach dem Aufruf dieser Funktion wird `someLayout` keine Widgets mehr enthalten.
    """
    # Überprüft, ob das übergebene Layout nicht None ist.
    if layout is not None:
        # Entfernt jedes Widget aus dem Layout, eins nach dem anderen.
        while layout.count():
            # Nimmt das erste Element aus dem Layout.
            item = layout.takeAt(0)
            # Holt das Widget, falls vorhanden, aus dem Layout-Element.
            widget = item.widget()
            # Falls das Element ein Widget war, löscht es, um Speicher freizugeben.
            if widget is not None:
                widget.deleteLater()

if __name__ == "__main__":
    """
    Haupt-Einstiegspunkt der Anwendung.

    Dieser Abschnitt des Codes wird ausgeführt, wenn die Datei als Hauptprogramm gestartet wird, und nicht,
    wenn sie als Modul in einem anderen Skript importiert wird. Es initialisiert die QApplication, welche
    für alle Qt-Anwendungen benötigt wird, erstellt ein Fenster der MainWindow-Klasse und startet die
    Ereignisverarbeitungsschleife (Event Loop). Die Ereignisverarbeitungsschleife hält die Anwendung am Laufen,
    indem sie auf Benutzerinteraktionen wie Klicks oder Tastatureingaben reagiert und entsprechende Ereignisse
    verarbeitet.

    Args:
        sys.argv: Eine Liste von Befehlszeilenargumenten, die an das QApplication-Objekt übergeben wird. Qt kann
                  diese Argumente nutzen, um bestimmte Initialisierungsoptionen zu konfigurieren.

    Beispiel:
        Wenn dieses Skript direkt ausgeführt wird, initialisiert es die grafische Benutzeroberfläche und zeigt das
        Hauptfenster an. Der Benutzer kann dann mit der Anwendung interagieren, bis sie explizit geschlossen wird,
        woraufhin die Ereignisverarbeitungsschleife beendet wird und das Programm ordnungsgemäß schließt.
    """
    # Initialisiert die QApplication mit den übergebenen Befehlszeilenargumenten.
    app = QApplication(sys.argv)
    # Erstellt eine Instanz des Hauptfensters.
    window = MainWindow()
    # Zeigt das Hauptfenster an.
    window.show()
    # Startet die Ereignisverarbeitungsschleife und wartet, bis die Anwendung beendet wird.
    # Der Aufruf von `sys.exit` stellt sicher, dass das Programm mit dem richtigen Status beendet wird.
    sys.exit(app.exec_())
