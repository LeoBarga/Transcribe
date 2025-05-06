from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
import os
from datetime import datetime
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
    )
from django.core.exceptions import ValidationError



def index(request):
    return render(request, "polls/index.html")

def home(request):
    return render(request, "polls/home.html")

def info(request):
    return render(request, "polls/info.html")

def testi(request):
    return HttpResponse("testi")

def correzioni(request):
    if request.method == 'POST':
        print("="*50)
        print("POST richiesta a correzioni:")
        for key, value in request.POST.items():
            print(f"  {key}: {value[:50] if isinstance(value, str) else value}")
        print("="*50)
        
        if 'save_correction' in request.POST:
            correction_type = request.POST.get('correction_type')
            original_id = request.POST.get('original_id')
            
            print(f"Richiesta di correzione ricevuta: tipo={correction_type}, id={original_id}...")
            
            if correction_type and original_id:
                try:
                    if correction_type == 'transcription':
                        print(f"Creazione correzione trascrizione con ID: {original_id}")
                        original = Trascrizioni.objects.get(id=original_id)
                        correction = CorrezioniTrascrizioni.objects.create(
                            trascrizione=original,
                            testo_originale=original.audio_trascritto
                        )
                        correction.correggi_testo()
                        print(f"Correzione trascrizione SALVATA con ID: {correction.id}")
                        
                    elif correction_type == 'translation':
                        print(f"Creazione correzione traduzione con ID: {original_id}")
                        original = Traduzioni.objects.get(id=original_id)
                        correction = CorrezioniTraduzioni.objects.create(
                            traduzione=original,
                            testo_originale=original.testo_tradotto
                        )
                        correction.correggi_testo()
                        print(f"Correzione traduzione SALVATA con ID: {correction.id}")
                        
                    elif correction_type == 'written_text':
                        print(f"Creazione correzione testo scritto con ID: {original_id}")
                        original = TestiScritti.objects.get(id=original_id)
                        correction = CorrezioniTestiScritti.objects.create(
                            testo_scritto=original,
                            testo_originale=original.testo
                        )
                        correction.correggi_testo()
                        print(f"Correzione testo scritto SALVATA con ID: {correction.id}")
                    
                    else:
                        print(f"ERRORE: Tipo correzione non valido: {correction_type}")
                        return JsonResponse({'success': False, 'error': f'Tipo correzione non valido: {correction_type}'})
                    
                    print(f"Correzione salvata con successo: id={correction.id}")
                    return redirect('correzioni')
                
                except Exception as e:
                    import traceback
                    print(f"ERRORE durante il salvataggio della correzione: {str(e)}")
                    traceback.print_exc()
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                missing = []
                if not correction_type: missing.append("correction_type")
                if not original_id: missing.append("original_id")
                error_msg = f"Dati mancanti: {', '.join(missing)}"
                print(f"ERRORE: {error_msg}")
                return JsonResponse({'success': False, 'error': error_msg})
        
        elif 'delete_correction' in request.POST:
            correction_type = request.POST.get('correction_type')
            correction_id = request.POST.get('correction_id')
            
            print(f"Richiesta eliminazione correzione: tipo={correction_type}, id={correction_id}")
            
            if not correction_type:
                return JsonResponse({'success': False, 'error': 'Tipo correzione mancante'})
            if not correction_id:
                return JsonResponse({'success': False, 'error': 'ID correzione mancante'})
            
            try:
                if correction_type == 'transcription':
                    try:
                        correction = CorrezioniTrascrizioni.objects.get(id=correction_id)
                    except CorrezioniTrascrizioni.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Correzione trascrizione con ID {correction_id} non trovata'})
                    
                    correction.delete()
                    print(f"Correzione trascrizione eliminata: id={correction_id}")
                
                elif correction_type == 'translation':
                    try:
                        correction = CorrezioniTraduzioni.objects.get(id=correction_id)
                    except CorrezioniTraduzioni.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Correzione traduzione con ID {correction_id} non trovata'})
                    
                    correction.delete()
                    print(f"Correzione traduzione eliminata: id={correction_id}")
                
                elif correction_type == 'written_text':
                    try:
                        correction = CorrezioniTestiScritti.objects.get(id=correction_id)
                    except CorrezioniTestiScritti.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Correzione testo con ID {correction_id} non trovata'})
                    
                    correction.delete()
                    print(f"Correzione testo scritto eliminata: id={correction_id}")
                
                else:
                    return JsonResponse({'success': False, 'error': f'Tipo correzione non valido: {correction_type}'})
                
                return JsonResponse({'success': True})
            
            except Exception as e:
                import traceback
                print(f"ERRORE eliminazione correzione: {str(e)}")
                traceback.print_exc()
                return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - mostra le correzioni
    transcription_corrections = CorrezioniTrascrizioni.objects.all().order_by('-data_creazione_correzione')
    translation_corrections = CorrezioniTraduzioni.objects.all().order_by('-data_creazione_correzione')
    written_text_corrections = CorrezioniTestiScritti.objects.all().order_by('-data_creazione_correzione')
    
    context = {
        'transcription_corrections': transcription_corrections,
        'translation_corrections': translation_corrections,
        'written_text_corrections': written_text_corrections
    }
    
    return render(request, "polls/correzioni.html", context)

def suggerimenti(request):
    if request.method == 'POST':
        if 'save_suggestion' in request.POST:
            suggestion_type = request.POST.get('suggestion_type') or request.POST.get('tipo')
            title = request.POST.get('title') or request.POST.get('titolo')
            description = request.POST.get('description') or request.POST.get('descrizione')
            if suggestion_type and title and description:
                try:
                    if suggestion_type == 'function':
                        suggestion = SuggerimentiNuoveFunzioni(
                            nome=title,
                            descrizione=description,
                            data_creazione=datetime.now()
                        )
                    elif suggestion_type == 'tool':
                        suggestion = SuggerimentiNuoviStrumenti(
                            nome=title,
                            descrizione=description,
                            data_creazione=datetime.now()
                        )
                    elif suggestion_type == 'style':
                        suggestion = SuggerimentiStile(
                            nome=title,
                            descrizione=description,
                            data_creazione=datetime.now()
                        )
                    else:
                        suggestion = AltriSuggerimenti(
                            nome=title,
                            descrizione=description,
                            data_creazione=datetime.now()
                        )
                    suggestion.save()
                    return JsonResponse({'success': True, 'id': suggestion.id})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Dati mancanti'})
        elif 'delete_suggestion' in request.POST:
            suggestion_type = request.POST.get('suggestion_type')
            suggestion_id = request.POST.get('suggestion_id')
            if suggestion_type and suggestion_id:
                try:
                    if suggestion_type == 'function':
                        suggestion = SuggerimentiNuoveFunzioni.objects.get(id=suggestion_id)
                    elif suggestion_type == 'tool':
                        suggestion = SuggerimentiNuoviStrumenti.objects.get(id=suggestion_id)
                    elif suggestion_type == 'style':
                        suggestion = SuggerimentiStile.objects.get(id=suggestion_id)
                    else:
                        suggestion = AltriSuggerimenti.objects.get(id=suggestion_id)
                    suggestion.delete()
                    return JsonResponse({'success': True})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Dati mancanti'})
        elif 'update_status' in request.POST:
            suggestion_type = request.POST.get('suggestion_type')
            suggestion_id = request.POST.get('suggestion_id')
            stato = request.POST.get('stato')
            if suggestion_type and suggestion_id and stato:
                try:
                    if suggestion_type == 'function':
                        suggestion = SuggerimentiNuoveFunzioni.objects.get(id=suggestion_id)
                    elif suggestion_type == 'tool':
                        suggestion = SuggerimentiNuoviStrumenti.objects.get(id=suggestion_id)
                    elif suggestion_type == 'style':
                        suggestion = SuggerimentiStile.objects.get(id=suggestion_id)
                    else:
                        suggestion = AltriSuggerimenti.objects.get(id=suggestion_id)
                    suggestion.stato = stato
                    suggestion.save()
                    return JsonResponse({'success': True})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Dati mancanti'})
        
        elif 'approve_suggestion' in request.POST:
            suggestion_type = request.POST.get('suggestion_type')
            suggestion_id = request.POST.get('suggestion_id')
            
            if suggestion_type and suggestion_id:
                try:
                    if suggestion_type == 'function':
                        suggestion = SuggerimentiNuoveFunzioni.objects.get(id=suggestion_id)
                    elif suggestion_type == 'tool':
                        suggestion = SuggerimentiNuoviStrumenti.objects.get(id=suggestion_id)
                    elif suggestion_type == 'style':
                        suggestion = SuggerimentiStile.objects.get(id=suggestion_id)
                    else:  # other
                        suggestion = AltriSuggerimenti.objects.get(id=suggestion_id)
                    
                    suggestion.stato = 'valutazione'
                    suggestion.save()
                    return JsonResponse({'success': True})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Dati mancanti'})
        
        elif 'reject_suggestion' in request.POST:
            suggestion_type = request.POST.get('suggestion_type')
            suggestion_id = request.POST.get('suggestion_id')
            
            if suggestion_type and suggestion_id:
                try:
                    if suggestion_type == 'function':
                        suggestion = SuggerimentiNuoveFunzioni.objects.get(id=suggestion_id)
                    elif suggestion_type == 'tool':
                        suggestion = SuggerimentiNuoviStrumenti.objects.get(id=suggestion_id)
                    elif suggestion_type == 'style':
                        suggestion = SuggerimentiStile.objects.get(id=suggestion_id)
                    else:  # other
                        suggestion = AltriSuggerimenti.objects.get(id=suggestion_id)
                    
                    suggestion.stato = 'respinto'
                    suggestion.save()
                    return JsonResponse({'success': True})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Dati mancanti'})
    
    # GET request - mostra i suggerimenti
    function_suggestions = SuggerimentiNuoveFunzioni.objects.all().order_by('-data_creazione')
    tool_suggestions = SuggerimentiNuoviStrumenti.objects.all().order_by('-data_creazione')
    style_suggestions = SuggerimentiStile.objects.all().order_by('-data_creazione')
    other_suggestions = AltriSuggerimenti.objects.all().order_by('-data_creazione')
    
    context = {
        'function_suggestions': function_suggestions,
        'tool_suggestions': tool_suggestions,
        'style_suggestions': style_suggestions,
        'other_suggestions': other_suggestions
    }
    
    return render(request, "polls/suggerimenti.html", context)

def inserisci_file(request):
    if request.method == 'POST':
        if 'transcription' in request.POST:
            # Gestione trascrizione
            file = request.FILES.get('audio_file')
            language = request.POST.get('language')
            mode = request.POST.get('mode')
            
            if file:
                # Salva il file audio
                audio = AudioDaTrascrivere(
                    nome_audio=file.name,
                    pub_date=datetime.now(),
                    file=file,
                    modalita=mode
                )
                try:
                    audio.save()
                except ValidationError as e:
                    # Gestisce l'errore di validazione sollevato dal signal post_save
                    return JsonResponse({'success': False, 'error': f'Errore durante la validazione o trascrizione iniziale: {str(e)}'})
                except Exception as e:
                    # Gestisce altri errori durante il salvataggio
                    return JsonResponse({'success': False, 'error': f'Errore durante il salvataggio del file: {str(e)}'})
                
                # Il signal post_save chiamerà generate_transcript()
                # Recuperiamo la trascrizione creata dal signal
                try:
                    # Recupera la trascrizione appena creata
                    transcription = Trascrizioni.objects.filter(trascrizione_audio=audio).latest('time')
                    
                    return JsonResponse({
                        'success': True,
                        'transcription': transcription.audio_trascritto,
                        'id': transcription.id
                    })
                except Trascrizioni.DoesNotExist:
                     # Questo potrebbe accadere se il signal fallisce silenziosamente o non crea la trascrizione
                     return JsonResponse({'success': False, 'error': 'Trascrizione non trovata dopo il salvataggio.'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'Errore durante il recupero della trascrizione: {str(e)}'})
            else:
                return JsonResponse({'success': False, 'error': 'Nessun file caricato'})
                
        elif 'translation' in request.POST:
            # Gestione traduzione
            file = request.FILES.get('audio_file')
            source_language = request.POST.get('source_language')
            target_language = request.POST.get('target_language')
            
            if file:
                # Salva il file audio
                audio = AudioDaTradurre(
                    nome_audio=file.name,
                    pub_date=datetime.now(),
                    file=file,
                    modalita='tiny'  # Usiamo la modalità veloce per la traduzione
                )
                try:
                    audio.save()
                except ValidationError as e:
                    # Gestisce l'errore di validazione sollevato dal signal post_save
                    return JsonResponse({'success': False, 'error': f'Errore durante la validazione o traduzione iniziale: {str(e)}'})
                except Exception as e:
                    # Gestisce altri errori durante il salvataggio
                    return JsonResponse({'success': False, 'error': f'Errore durante il salvataggio del file: {str(e)}'})
                
                # Il signal post_save chiamerà generate_translation()
                # Recuperiamo la traduzione creata dal signal
                try:
                    # Recupera la traduzione appena creata
                    translation = Traduzioni.objects.filter(traduzione_audio=audio).latest('time')
                    
                    return JsonResponse({
                        'success': True,
                        'translation': translation.testo_tradotto,
                        'id': translation.id
                    })
                except Traduzioni.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Traduzione non trovata dopo il salvataggio.'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'Errore durante il recupero della traduzione: {str(e)}'})
            else:
                return JsonResponse({'success': False, 'error': 'Nessun file caricato'})
    
    # GET request - mostra il form
    return render(request, "polls/inserisci_file.html")

def testi_vari(request):
    if request.method == 'POST':
        print(f"POST richiesta a testi_vari - dati: {request.POST}")
        
        if 'delete_text' in request.POST:
            text_type = request.POST.get('text_type')
            text_id = request.POST.get('text_id')
            
            try:
                if text_type == 'transcription':
                    Trascrizioni.objects.get(id=text_id).delete()
                elif text_type == 'translation':
                    Traduzioni.objects.get(id=text_id).delete()
                elif text_type == 'written':
                    TestiScritti.objects.get(id=text_id).delete()
                
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        elif 'save_correction' in request.POST:
            correction_type = request.POST.get('correction_type')
            original_id = request.POST.get('original_id')
            corrected_text = request.POST.get('corrected_text')
            
            # Log dettagliato dei dati ricevuti
            print(f"RICHIESTA CORREZIONE - Tipo: {correction_type}, ID: {original_id}, Testo: {corrected_text[:50] if corrected_text else None}...")
            
            if not correction_type:
                return JsonResponse({'success': False, 'error': 'Tipo correzione mancante'})
            if not original_id:
                return JsonResponse({'success': False, 'error': 'ID originale mancante'})
            if not corrected_text:
                return JsonResponse({'success': False, 'error': 'Testo corretto mancante'})
            
            try:
                if correction_type == 'transcription':
                    try:
                        original = Trascrizioni.objects.get(id=original_id)
                    except Trascrizioni.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Trascrizione con ID {original_id} non trovata'})
                    
                    # Crea correzione trascrizioni
                    correction = CorrezioniTrascrizioni(
                        trascrizione=original,
                        testo_originale=original.audio_trascritto,
                        testo_corretto=corrected_text,
                        data_creazione_correzione=datetime.now()
                    )
                    correction.save()
                    print(f"Correzione trascrizione creata con ID: {correction.id}")
                
                elif correction_type == 'translation':
                    try:
                        original = Traduzioni.objects.get(id=original_id)
                    except Traduzioni.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Traduzione con ID {original_id} non trovata'})
                    
                    # Crea correzione traduzioni
                    correction = CorrezioniTraduzioni(
                        traduzione=original,
                        testo_originale=original.testo_tradotto,
                        testo_corretto=corrected_text,
                        data_creazione_correzione=datetime.now()
                    )
                    correction.save()
                    print(f"Correzione traduzione creata con ID: {correction.id}")
                
                elif correction_type == 'written_text':
                    try:
                        original = TestiScritti.objects.get(id=original_id)
                    except TestiScritti.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Testo scritto con ID {original_id} non trovato'})
                    
                    # Crea correzione testi scritti con il nome del campo corretto
                    correction = CorrezioniTestiScritti(
                        testo_scritto=original,  # Corretto: testo_scritto invece di testo
                        testo_originale=original.testo,  # Aggiunto testo_originale
                        testo_corretto=corrected_text,
                        data_creazione_correzione=datetime.now()
                    )
                    correction.save()
                    print(f"Correzione testo scritto creata con ID: {correction.id}")
                
                else:
                    return JsonResponse({'success': False, 'error': f'Tipo correzione non valido: {correction_type}'})
                
                # Reindirizza alla pagina delle correzioni
                return JsonResponse({'success': True, 'id': correction.id, 'redirect': 'correzioni'})
            
            except Exception as e:
                import traceback
                print(f"ERRORE creazione correzione: {str(e)}")
                traceback.print_exc()
                return JsonResponse({'success': False, 'error': str(e)})
        
        elif 'save_written_text' in request.POST:
            title = request.POST.get('title')
            text_content = request.POST.get('text')
            
            if title and text_content:
                try:
                    # Crea un nuovo TestiScritti
                    new_text = TestiScritti(
                        nome=title,
                        testo=text_content,
                        time=datetime.now()
                    )
                    new_text.save()
                    
                    return JsonResponse({'success': True, 'id': new_text.id})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Titolo e testo sono richiesti'})
    
    # GET request - mostra la lista dei testi
    transcriptions = Trascrizioni.objects.all().order_by('-time')
    translations = Traduzioni.objects.all().order_by('-time')
    written_texts = TestiScritti.objects.all().order_by('-time')
    
    context = {
        'transcriptions': transcriptions,
        'translations': translations,
        'written_texts': written_texts
    }
    
    return render(request, "polls/testi_vari.html", context)
