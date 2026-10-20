class Espositore:
    def __init__(self, codice_esp, nome_esp, cognome_esp):
        """Inizializza gli attributi dell'espositore"""
        self.__codice = codice_esp
        self.__nome = nome_esp
        self.__cognome = cognome_esp

    @property
    def codice_esp(self):
        return self.__codice

    def __str__(self):
        """Rappresentazione testuale dell'espositore"""
        return f"{self.__codice}: {self.__cognome} {self.__nome}"

    def __eq__(self, other):
        """Confronta due espositori in base al codice"""
        if isinstance(other, Espositore):
            return self.__codice == other.__codice
        return False


class Stand:
    def __init__(self, codice_stand, superficie_stand, padiglione_stand, prezzo_base_stand):
        """Inizializza gli attributi comuni di uno stand"""
        self._codice = codice_stand
        self._superficie = float(superficie_stand)
        self._padiglione = int(padiglione_stand)
        self._prezzo_base = float(prezzo_base_stand)
        self.disponibile = True
        self.espositore = None

    @property
    def codice_stand(self):
        return self._codice

    def calcola_prezzo(self):
        """Restituisce il prezzo base per lo stand Standard"""
        return self._prezzo_base

    def __lt__(self, other):
        """Permette l'ordinamento degli stand confrontando il prezzo calcolato"""
        return self.calcola_prezzo() < other.calcola_prezzo()

    def __str__(self):
        """Rappresentazione testuale dello stand Standard"""
        stato = "Disponibile" if self.disponibile else f"Occupato da {self.espositore.codice_esp}" if self.espositore else "Occupato"
        return f"{self._codice}: Standard | {self._superficie} mq - Padiglione {self._padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - {stato}"


class StandPreseExtra(Stand):
    def __init__(self, codice_stand, superficie_stand, padiglione_stand, prezzo_base_stand, numero_prese):
        """Inizializza lo stand con prese elettriche aggiuntive"""
        super().__init__(codice_stand, superficie_stand, padiglione_stand, prezzo_base_stand)
        self._numero_prese = int(numero_prese)

    def calcola_prezzo(self):
        """Calcola il prezzo applicando il sovrapprezzo del 7% per ogni presa extra"""
        return self._prezzo_base * (1 + 0.07 * self._numero_prese)

    def __str__(self):
        """Rappresentazione testuale dello stand con prese extra"""
        stato = "Disponibile" if self.disponibile else f"Occupato da {self.espositore.codice_esp}" if self.espositore else "Occupato"
        return f"{self._codice}: Prese Extra | {self._superficie} mq - Padiglione {self._padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - Prese aggiuntive: {self._numero_prese} - {stato}"


class StandPremium(Stand):
    def __init__(self, codice_stand, superficie_stand, padiglione_stand, prezzo_base_stand, posizione):
        """Inizializza lo stand di tipo Premium"""
        super().__init__(codice_stand, superficie_stand, padiglione_stand, prezzo_base_stand)
        self._posizione = posizione

    def calcola_prezzo(self):
        """Calcola il prezzo applicando il sovrapprezzo fisso del 30%"""
        return self._prezzo_base * 1.30

    def __str__(self):
        """Rappresentazione testuale dello stand Premium"""
        stato = "Disponibile" if self.disponibile else f"Occupato da {self.espositore.codice_esp}" if self.espositore else "Occupato"
        return f"{self._codice}: Premium ({self._posizione}) | {self._superficie} mq - Padiglione {self._padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - {stato}"


class LingottoFiere:
    def __init__(self, nome):
        """Inizializza il centro fieristico e i dizionari per stand ed espositori"""
        self.__nome = nome
        self.stand = {}
        self.espositori = {}

    # Getter e Setter per il nome
    def get_nome(self):
        return self.__nome

    def set_nome(self, nuovo_nome):
        self.__nome = nuovo_nome

    def carica_file_dati(self, file_path):
        """Legge il file CSV e popola le strutture dati creando i relativi oggetti"""
        with open(file_path, "r", encoding="utf-8") as file:
            for riga in file:
                riga_pulita = riga.rstrip()
                if not riga_pulita:
                    continue
                campi = riga_pulita.split(",")

                codice = campi[0]

                # Se è un espositore (inizia con ES)
                if codice.startswith("ES"):
                    if len(campi) >= 3:
                        espositore = Espositore(codice, campi[1], campi[2])
                        self.espositori[codice] = espositore

                # Se è uno stand (inizia con ST)
                elif codice.startswith("ST"):
                    if len(campi) == 4:
                        # Stand Standard
                        s = Stand(codice, campi[1], campi[2], campi[3])
                        self.stand[codice] = s
                    elif len(campi) == 5:
                        ultimo_campo = campi[4]
                        # Controllo se l'ultimo campo è un numero (Prese Extra) o una stringa (Premium)
                        if ultimo_campo.isdigit() or (ultimo_campo.startswith("-") and ultimo_campo[1:].isdigit()):
                            s = StandPreseExtra(codice, campi[1], campi[2], campi[3], ultimo_campo)
                        else:
                            s = StandPremium(codice, campi[1], campi[2], campi[3], ultimo_campo)
                        self.stand[codice] = s

    def assegna_stand_a_espositore(self, codice_stand, codice_espositore):
        """Associa uno stand a un espositore eseguendo tutti i controlli necessari"""
        if codice_stand not in self.stand:
            raise ValueError(reale_err := f"Lo stand '{codice_stand}' non esiste nel sistema.")

        if codice_espositore not in self.espositori:
            raise ValueError(f"L'espositore '{codice_espositore}' non esiste nel sistema.")

        stand_obj = self.stand[codice_stand]
        espositore_obj = self.espositori[codice_espositore]

        if not stand_obj.disponibile:
            raise ValueError(f"Lo stand '{codice_stand}' risulta già occupato.")

        # Verifica se l'espositore ha già uno stand assegnato
        for s in self.stand.values():
            if s.espositore == espositore_obj:
                raise ValueError(f"L'espositore '{codice_espositore}' è già associato a un altro stand.")

        # Effettua l'assegnazione
        stand_obj.disponibile = False
        stand_obj.espositore = espositore_obj

    def elenca_espositori(self):
        """Stampa l'elenco degli espositori mostrando l'eventuale stand associato"""
        if not self.espositori:
            print("Nessun espositore registrato.")
            return

        for espositore in self.espositori.values():
            # Cerca se questo espositore ha uno stand associato
            stand_trovato = None
            for s in self.stand.values():
                if s.espositore == espositore:
                    stand_trovato = s
                    break

            if stand_trovato:
                print(f"{espositore} -> Assegnato allo stand {stand_trovato.codice_stand}")
            else:
                print(f"{espositore} -> Nessuno stand assegnato")

    def stand_ordinati_per_prezzo(self):
        """Restituisce la lista degli stand ordinati per prezzo crescente"""
        return sorted(self.stand.values())
