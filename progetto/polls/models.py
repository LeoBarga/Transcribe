import whisper 
import language_tool_python

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from deep_translator import GoogleTranslator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


def validate_audio_size(file):
    max_size = 30 * 1024 * 1024  # 30 MB
    if file.size > max_size:
        raise ValidationError("Il file audio è troppo grande. La dimensione massima consentita è di 30 MB.")


class AudioDaTrascrivere(models.Model):
    nome_audio = models.CharField(max_length=50, help_text="ATTENZIONE: RIMUOVERE UN AUDIO RIMUOVE TUTTI I TESTI COLLEGATI AD ESSO (trascrizioni, traduzioni, correzioni).")
    pub_date = models.DateTimeField("Data audio")
    file = models.FileField(upload_to='audio_files/', validators=[validate_audio_size])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    MODALITA = [
        ('tiny', 'Veloce'),
        ('small', 'Lenta'),
    ]
    modalita = models.CharField(
        max_length=7,
        choices=MODALITA,
        default='tiny',
        help_text="Modalità di trascrizione  (Veloce è meno precisa, per un audio di circa 10s richiede ~6s. Lenta è più precisa ma per uno stesso audio richiede ~25s)."
    )

    def __str__(self):
        return self.nome_audio

    def generate_transcript(self):
        #Genera la trascrizione dell'audio utilizzando Whisper
        try:
            model = whisper.load_model(self.modalita)
            result = model.transcribe(self.file.path)
            trascrizione = Trascrizioni.objects.create(
                trascrizione_audio=self,
                audio_trascritto=result['text']
            )
            trascrizione.save()
        except Exception as e:
            raise ValidationError(f"Errore durante la trascrizione: {e}")


class AudioDaTradurre(models.Model):
    nome_audio = models.CharField(max_length=50, help_text="ATTENZIONE: RIMUOVERE UN AUDIO RIMUOVE TUTTI I TESTI COLLEGATI AD ESSO (trascrizioni, traduzioni, correzioni).")
    pub_date = models.DateTimeField("Data audio")
    file = models.FileField(upload_to='audio_files/', validators=[validate_audio_size])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    MODALITA = [
        ('tiny', 'Veloce'),
        ('small', 'Lenta'),
    ]
    modalita = models.CharField(
        max_length=7,
        choices=MODALITA,
        default='tiny',
        help_text="Modalità di traduzione  (Veloce è meno precisa, per un audio di circa 10s richiede ~6s. Lenta è più precisa ma per uno stesso audio richiede ~25s)."
    )

    def __str__(self):
        return self.nome_audio

    def generate_translation(self):
        #Genera la traduzione dell'audio utilizzando Whisper e Google Translator
        try:
            model = whisper.load_model(self.modalita)
            result = model.transcribe(self.file.path, language='en')

            testo_tradotto = GoogleTranslator(source='en', target='it').translate(result['text'])
            traduzione = Traduzioni.objects.create(
                traduzione_audio=self,
                testo_tradotto=testo_tradotto
            )
            traduzione.save()
        except Exception as e:
            raise ValidationError(f"Errore durante la traduzione: {e}")


class Trascrizioni(models.Model):
    trascrizione_audio = models.ForeignKey(AudioDaTrascrivere, on_delete=models.CASCADE)
    audio_trascritto = models.TextField(help_text='ATTENZIONE: Modificare manualmente una trascrizione di cui si è già creato la correzione e salvarla con la funzione di correzione automatica attiva non sovrascriverà la correzione originale ma ne creerà un altra')
    time = models.DateTimeField(auto_now_add=True)
    correggi_automaticamente = models.BooleanField(default=False)

    def __str__(self):
        return f"Trascrizione di {self.trascrizione_audio.nome_audio} creata il {self.time}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Salvo la trascrizione

        # Se la correzione automatica è attiva, creo un oggetto di correzione
        if self.correggi_automaticamente:
            correzione = CorrezioniTrascrizioni.objects.create(
                trascrizione=self,
                testo_originale=self.audio_trascritto
            )
            correzione.correggi_testo()


class Traduzioni(models.Model):
    traduzione_audio = models.ForeignKey(AudioDaTradurre, on_delete=models.CASCADE)
    testo_tradotto = models.TextField(help_text='ATTENZIONE: Modificare manualmente una traduzione di cui si è già creato la correzione e salvarla con la funzione di correzione automatica attiva non sovrascriverà la correzione originale ma ne creerà un altra')
    time = models.DateTimeField(auto_now_add=True)
    correggi_automaticamente = models.BooleanField(default=False)

    def __str__(self):
        return f"Traduzione di {self.traduzione_audio.nome_audio} creata il {self.time}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Salvo la traduzione

        # Se la correzione automatica è attiva, creo un oggetto di correzione
        if self.correggi_automaticamente:
            correzione = CorrezioniTraduzioni.objects.create(
                traduzione=self,
                testo_originale=self.testo_tradotto
            )
            correzione.correggi_testo()
        

class TestiScritti(models.Model):
    nome = models.CharField(max_length=100)
    testo = models.TextField(help_text='ATTENZIONE: Modificare manualmente un testo scritto di cui si è già creato la correzione e salvarlo con la funzione di correzione automatica attiva non sovrascriverà la correzione originale ma ne creerà un altra')
    time = models.DateTimeField(auto_now_add=True)
    correggi_automaticamente = models.BooleanField(default=False, help_text='Funzionante solo per testi in lingua italiana. ATTENZIONE: Impossibile creare una correzione su un Testo Scritto in creazione. Per creare una correzione salvare il nuovo testo SENZA la funzione di correzione automatica attiva, aprirlo, attivare la funzione e salvare')

    def __str__(self):
        return f"Nuovo testo scritto {self.nome} creato il {self.time}"

    def save(self, *args, **kwargs):
        # Verifica se è un nuovo oggetto e se la correzione automatica è attivata
        if not self.pk and self.correggi_automaticamente:
            raise ValidationError("Impossibile creare una correzione su un Testo Scritto in creazione. Per creare una correzione salvare il nuovo testo SENZA la funzione di correzione automatica attiva, aprirlo, attivare la funzione e salvare")  # Lancia un errore di validazione per la creazione

        # Salva il testo scritto
        super().save(*args, **kwargs)

        # Se la correzione automatica è attiva, crea un oggetto di correzione
        if self.correggi_automaticamente:
            correzione = CorrezioniTestiScritti.objects.create(
                testo_scritto=self,
                testo_originale=self.testo
            )
            correzione.correggi_testo()
        else:
            print(f"Correzione già esistente per testo scritto modificato (ID: {self.id})")



class CorrezioniTrascrizioni(models.Model):
    trascrizione = models.ForeignKey(
        Trascrizioni, on_delete=models.CASCADE, related_name="correzioni"
    )
    testo_originale = models.TextField(editable=False)
    testo_corretto = models.TextField(editable=False, blank=True, null=True)
    data_creazione_correzione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correzione Trascrizione di {self.trascrizione.trascrizione_audio.nome_audio} - {self.data_creazione_correzione}"

    def correggi_testo(self):
        #Corregge automaticamente il testo utilizzando LanguageTool.
        if not self.testo_originale:
            raise ValidationError(_("Nessun testo da correggere."))

        try:
            tool = language_tool_python.LanguageTool("it")
            self.testo_corretto = tool.correct(self.testo_originale)
            self.save(update_fields=['testo_corretto'])
        except Exception as e:
            raise ValidationError(f"Errore durante la correzione AI: {str(e)}")


class CorrezioniTraduzioni(models.Model):
    traduzione = models.ForeignKey(
        Traduzioni, on_delete=models.CASCADE, related_name="correzioni"
    )
    testo_originale = models.TextField(editable=False)
    testo_corretto = models.TextField(editable=False, blank=True, null=True)
    data_creazione_correzione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correzione Traduzione di {self.traduzione.traduzione_audio.nome_audio} - {self.data_creazione_correzione}"

    def correggi_testo(self):
        #Corregge automaticamente il testo utilizzando LanguageTool.
        if not self.testo_originale:
            raise ValidationError(_("Nessun testo da correggere."))

        try:
            tool = language_tool_python.LanguageTool("it")
            self.testo_corretto = tool.correct(self.testo_originale)
            self.save(update_fields=['testo_corretto'])
        except Exception as e:
            raise ValidationError(f"Errore durante la correzione AI: {str(e)}")


class CorrezioniTestiScritti(models.Model):
    testo_scritto = models.ForeignKey(TestiScritti, on_delete=models.CASCADE, related_name="correzioni")
    testo_originale = models.TextField(editable=False)
    testo_corretto = models.TextField(editable=False, blank=True, null=True)
    data_creazione_correzione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correzione Testo Scritto di {self.testo_scritto.nome} - {self.data_creazione_correzione}"

    def correggi_testo(self):
        #Corregge automaticamente il testo utilizzando LanguageTool.
        if not self.testo_originale:
            raise ValidationError(_("Nessun testo da correggere."))

        try:
            tool = language_tool_python.LanguageTool("it")
            self.testo_corretto = tool.correct(self.testo_originale)
            self.save(update_fields=['testo_corretto'])
        except Exception as e:
            raise ValidationError(f"Errore durante la correzione AI: {str(e)}")

        
class SuggerimentiNuoviStrumenti(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(help_text="Descrivi il tuo suggerimento.")
    stato = models.CharField(
        max_length=20,
        choices=[
            ('non_visualizzato', 'Non visualizzato'),
            ('valutazione', 'In corso di valutazione'),
            ('respinto', 'Respinto'),
            ('lavorazione', 'In lavorazione'),
            ('attuato', 'Attuato'),
            ('non_valido', 'Non valido'),
        ],
        default='non_visualizzato',
        help_text="Stato del suggerimento."
    )
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        stato_dict = dict(self._meta.get_field('stato').choices)
        return f"{self.nome} - Stato: {stato_dict.get(self.stato)}"


class SuggerimentiNuoveFunzioni(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(help_text="Descrivi il tuo suggerimento.")
    stato = models.CharField(
        max_length=20,
        choices=[
            ('non_visualizzato', 'Non visualizzato'),
            ('valutazione', 'In corso di valutazione'),
            ('respinto', 'Respinto'),
            ('lavorazione', 'In lavorazione'),
            ('attuato', 'Attuato'),
            ('non_valido', 'Non valido'),
        ],
        default='non_visualizzato',
        help_text="Stato del suggerimento."
    )
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        stato_dict = dict(self._meta.get_field('stato').choices)
        return f"{self.nome} - Stato: {stato_dict.get(self.stato)}"


class SuggerimentiStile(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(help_text="Descrivi il tuo suggerimento.")
    stato = models.CharField(
        max_length=20,
        choices=[
            ('non_visualizzato', 'Non visualizzato'),
            ('valutazione', 'In corso di valutazione'),
            ('respinto', 'Respinto'),
            ('lavorazione', 'In lavorazione'),
            ('attuato', 'Attuato'),
            ('non_valido', 'Non valido'),
        ],
        default='non_visualizzato',
        help_text="Stato del suggerimento."
    )
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        stato_dict = dict(self._meta.get_field('stato').choices)
        return f"{self.nome} - Stato: {stato_dict.get(self.stato)}"


class AltriSuggerimenti(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(help_text="Descrivi il tuo suggerimento.")
    stato = models.CharField(
        max_length=20,
        choices=[
            ('non_visualizzato', 'Non visualizzato'),
            ('valutazione', 'In corso di valutazione'),
            ('respinto', 'Respinto'),
            ('lavorazione', 'In lavorazione'),
            ('attuato', 'Attuato'),
            ('non_valido', 'Non valido'),
        ],
        default='non_visualizzato',
        help_text="Stato del suggerimento."
    )
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        stato_dict = dict(self._meta.get_field('stato').choices)
        return f"{self.nome} - Stato: {stato_dict.get(self.stato)}"
    

class LogAttività(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    activity_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user if self.user else 'Sistema'} - {self.activity_type} - {self.timestamp}"
    
