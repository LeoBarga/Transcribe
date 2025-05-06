from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import (
    AudioDaTrascrivere,
    AudioDaTradurre,
    Trascrizioni,
    Traduzioni,
    TestiScritti,
    CorrezioniTrascrizioni,
    CorrezioniTraduzioni,
    CorrezioniTestiScritti,
    SuggerimentiNuoviStrumenti,
    SuggerimentiNuoveFunzioni,
    SuggerimentiStile,
    AltriSuggerimenti,
    LogAttività,
)

# Segnale per creare automaticamente una trascrizione quando viene creato un AudioDaTrascrivere
@receiver(post_save, sender=AudioDaTrascrivere)
def create_transcription(sender, instance, created, **kwargs):
    if created:
        print(f"Audio da trascrivere creato: {instance.nome_audio}")
        instance.generate_transcript()  


# Segnale per creare automaticamente una traduzione quando viene creato un AudioDaTradurre
@receiver(post_save, sender=AudioDaTradurre)
def create_translation(sender, instance, created, **kwargs):
    if created:
        print(f"Audio da tradurre creato: {instance.nome_audio}")
        instance.generate_translation()  


@receiver(post_save, sender=Trascrizioni)
def correzione_automatica_trascrizione(sender, instance, created, **kwargs):
    if created and instance.correggi_automaticamente:
        # Controlliamo se esiste già una correzione per questa trascrizione
        if not CorrezioniTrascrizioni.objects.filter(trascrizione=instance).exists():
            print(f"Creazione correzione per trascrizione (ID: {instance.id})")
            correzione = CorrezioniTrascrizioni.objects.create(
                trascrizione=instance,
                testo_originale=instance.audio_trascritto
            )
            correzione.correggi_testo()
        else:
            print(f"Correzione già esistente per trascrizione (ID: {instance.id})")


@receiver(post_save, sender=Traduzioni)
def correzione_automatica_traduzione(sender, instance, created, **kwargs):
    if created and instance.correggi_automaticamente:
        # Controlliamo se esiste già una correzione per questa traduzione
        if not CorrezioniTraduzioni.objects.filter(traduzione=instance).exists():
            print(f"Creazione correzione per traduzione (ID: {instance.id})")
            correzione = CorrezioniTraduzioni.objects.create(
                traduzione=instance,
                testo_originale=instance.testo_tradotto
            )
            correzione.correggi_testo()
        else:
            print(f"Correzione già esistente per traduzione (ID: {instance.id})")


@receiver(post_save, sender=TestiScritti)
def correzione_automatica_testi_scritti(sender, instance, created, **kwargs):
    if created and instance.correggi_automaticamente:
        # Controlliamo se esiste già una correzione per questo testo scritto
        if not CorrezioniTestiScritti.objects.filter(testo_scritto=instance).exists():
            print(f"Creazione correzione per testo scritto (ID: {instance.id})")
            correzione = CorrezioniTestiScritti.objects.create(
                testo_scritto=instance,
                testo_originale=instance.testo
            )
            correzione.correggi_testo()
        else:
            print(f"Correzione già esistente per testo scritto (ID: {instance.id})")


def log_activity(instance, action):
    LogAttività.objects.create(
        user=getattr(instance, 'user', None),
        activity_type=action,
        description=f"{action} {instance.__class__.__name__}: {getattr(instance, 'nome_audio', 'ID ' + str(instance.id))}",
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id
    )

@receiver(post_save, sender=AudioDaTrascrivere)
@receiver(post_save, sender=AudioDaTradurre)
@receiver(post_save, sender=Trascrizioni)
@receiver(post_save, sender=Traduzioni)
@receiver(post_save, sender=TestiScritti)
@receiver(post_save, sender=CorrezioniTrascrizioni)
@receiver(post_save, sender=CorrezioniTraduzioni)
@receiver(post_save, sender=CorrezioniTestiScritti)
@receiver(post_save, sender=SuggerimentiNuoviStrumenti)
@receiver(post_save, sender=SuggerimentiNuoveFunzioni)
@receiver(post_save, sender=SuggerimentiStile)
@receiver(post_save, sender=AltriSuggerimenti)
def log_creation_or_update(sender, instance, created, **kwargs):
    action = "Creato" if created else "Modificato"
    log_activity(instance, action)

@receiver(pre_delete, sender=AudioDaTrascrivere)
@receiver(pre_delete, sender=AudioDaTradurre)
@receiver(pre_delete, sender=Trascrizioni)
@receiver(pre_delete, sender=Traduzioni)
@receiver(pre_delete, sender=TestiScritti)
@receiver(pre_delete, sender=CorrezioniTrascrizioni)
@receiver(pre_delete, sender=CorrezioniTraduzioni)
@receiver(pre_delete, sender=CorrezioniTestiScritti)
@receiver(pre_delete, sender=SuggerimentiNuoviStrumenti)
@receiver(pre_delete, sender=SuggerimentiNuoveFunzioni)
@receiver(pre_delete, sender=SuggerimentiStile)
@receiver(pre_delete, sender=AltriSuggerimenti)
def log_deletion(sender, instance, **kwargs):
    log_activity(instance, "Eliminato")
