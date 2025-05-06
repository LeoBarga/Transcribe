# Transcribe

Una web application Django per la trascrizione, traduzione e correzione automatica di file audio e testi scritti.

## Funzionalità Principali

- **Trascrizione Audio**: Converte file audio in testo utilizzando il modello OpenAI Whisper
- **Traduzione Audio**: Trascrive file audio in inglese e li traduce automaticamente in italiano
- **Correzione Automatica**: Verifica grammaticale e ortografica dei testi utilizzando Language Tool
- **Gestione Testi**: Creazione e correzione di testi scritti
- **Suggerimenti**: Sistema per proporre miglioramenti alla piattaforma

## Requisiti Tecnici

- Python 3.x
- Django
- OpenAI Whisper
- Language Tool Python
- Deep Translator
- Altre dipendenze elencate nel virtualenv (.venv)

## Caratteristiche Tecniche

### Modelli di Dati Principali

- **AudioDaTrascrivere**: Gestisce file audio per trascrizione
- **AudioDaTradurre**: Gestisce file audio per traduzione
- **Trascrizioni**: Memorizza le trascrizioni generate
- **Traduzioni**: Memorizza le traduzioni generate
- **TestiScritti**: Gestisce testi scritti manualmente
- **CorrezioniTrascrizioni**: Memorizza le correzioni delle trascrizioni
- **CorrezioniTraduzioni**: Memorizza le correzioni delle traduzioni
- **CorrezioniTestiScritti**: Memorizza le correzioni dei testi scritti
- **Suggerimenti**: Vari modelli per la gestione dei feedback

### Modalità di Elaborazione

- **Veloce (tiny)**: Elaborazione rapida ma meno precisa
- **Lenta (small)**: Elaborazione più lenta ma con maggiore precisione

## Come Iniziare

1. Clonare il repository
2. Creare e attivare un ambiente virtuale
3. Installare le dipendenze
4. Configurare il database con `python manage.py migrate`
5. Avviare il server con `python manage.py runserver`

## Limitazioni

- Il file audio deve essere inferiore a 30 MB
- La correzione automatica funziona solo per testi in lingua italiana
- La generazione di correzioni su un nuovo testo scritto richiede due passaggi
- Attualmente vengono utilizzati strumenti gratuiti con capacità minori rispetto a quelli comunemente utilizzati

## Note

Questo progetto utilizza diversi strumenti di IA per l'elaborazione del linguaggio naturale, incluso OpenAI Whisper per la trascrizione audio e Language Tool per la correzione del testo. 