from django.contrib import admin
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

class BaseCorrezioniAdmin(admin.ModelAdmin):
    """Admin base per gestire le correzioni in modo simile tra i tre modelli."""
    list_display = ('get_fonte', 'testo_corretto', 'data_creazione_correzione')
    readonly_fields = ('testo_originale', 'testo_corretto', 'data_creazione_correzione')
    fields = ('testo_originale', 'testo_corretto', 'data_creazione_correzione')
    list_filter = ('data_creazione_correzione',)

    def get_fonte(self, obj):
        """Mostra la fonte della correzione (Trascrizione, Traduzione o Testo Scritto)."""
        return obj.__class__.__name__.replace("Correzioni", "")
    get_fonte.short_description = 'Fonte'

    def has_add_permission(self, request, obj=None):
        return False  # Impedisce la creazione manuale di Correzioni


class TrascrizioniAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False  # Impedisce la creazione manuale di Trascrizioni


class TraduzioniAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False  # Impedisce la creazione manuale di Traduzioni
    

class LogAttivitàAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "timestamp", "content_type", "object_id")
    list_filter = ("activity_type", "timestamp", "user")
    search_fields = ("user__username", "activity_type", "description")


# Registrazione dei modelli nel pannello di amministrazione
admin.site.register(AudioDaTrascrivere)
admin.site.register(AudioDaTradurre)
admin.site.register(Trascrizioni, TrascrizioniAdmin)
admin.site.register(Traduzioni, TraduzioniAdmin)
admin.site.register(TestiScritti)
admin.site.register(CorrezioniTrascrizioni, BaseCorrezioniAdmin)
admin.site.register(CorrezioniTraduzioni, BaseCorrezioniAdmin)
admin.site.register(CorrezioniTestiScritti, BaseCorrezioniAdmin)
admin.site.register(SuggerimentiNuoviStrumenti)
admin.site.register(SuggerimentiNuoveFunzioni)
admin.site.register(SuggerimentiStile)
admin.site.register(AltriSuggerimenti)
admin.site.register(LogAttività, LogAttivitàAdmin)
