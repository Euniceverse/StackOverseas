'''this file is for functions to be reused in other files'''
from sentence_transformers import SentenceTransformer, util
from symspellpy import SymSpell, Verbosity
import requests
import torch
from apps.societies.models import Society
from apps.events.models import Event

# Load AI model for meaning-based matching
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load SymSpell for autocorrect
sym_spell = SymSpell(max_dictionary_edit_distance=2)
sym_spell.load_dictionary("frequency_dictionary_en.txt", term_index=0, count_index=1)

def correct_spelling(query):
    """Correct spelling using SymSpell."""
    suggestions = sym_spell.lookup(query, Verbosity.CLOSEST, max_edit_distance=2)
    return suggestions[0].term if suggestions else query

def autocomplete(query):
    """Autocomplete using Datamuse API."""
    response = requests.get(f"https://api.datamuse.com/sug?s={query}")
    suggestions = response.json()
    return suggestions[0]["word"] if suggestions else query

def search_events(query):
    """Search events with AI-powered matching, spell checking, and suggestions."""
    if not query:
        return [], None

    # Step 1: Correct Spelling and Autocomplete the Query
    corrected_query = correct_spelling(query.strip().lower())
    completed_query = autocomplete(corrected_query)

    # Step 2: Get all event categories/types
    event_types = list(Event.objects.values_list("event_type", flat=True).distinct())

    if not event_types:
        return [], completed_query

    # Step 3: Use AI to Find Best-Matching event_type
    type_embeddings = model.encode(event_types, convert_to_tensor=True)
    query_embedding = model.encode(completed_query, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(query_embedding, type_embeddings)
    best_match_index = torch.argmax(similarity_scores)
    best_match = event_types[best_match_index]

    # Step 4: Filter events by the best-matching event_type
    filtered_events = list(Event.objects.filter(event_type=best_match))

    if not filtered_events:
        # If no events found by type, try name-based search
        name_events = Event.objects.filter(name__icontains=completed_query)
        if name_events:
            return list(name_events), completed_query
        return [], completed_query

    # Step 5: Rank results by how well description matches the query
    descriptions = [event.description for event in filtered_events]
    description_embeddings = model.encode(descriptions, convert_to_tensor=True)

    description_scores = util.pytorch_cos_sim(query_embedding, description_embeddings).squeeze(0)
    ranked_events = sorted(zip(filtered_events, description_scores), key=lambda x: x[1], reverse=True)

    sorted_results = [event for event, score in ranked_events]

    # Step 6: Check Event Names (for name-based searches)
    name_events = Event.objects.filter(name__icontains=completed_query)

    # Step 7: Merge Name Matches + Sorted Description Matches (Avoid Duplicates)
    final_results = list(name_events) + [event for event in sorted_results if event not in name_events]

    return final_results, completed_query

def search_societies(query):
    """Main search function that handles all the AI-powered society search logic."""
    if not query:
        return [], None

    # Step 1: Correct Spelling and Autocomplete the Query
    corrected_query = correct_spelling(query.strip().lower())
    completed_query = autocomplete(corrected_query)

    # Step 2: Get all society types and names
    society_types = list(Society.objects.values_list("society_type", flat=True))

    if not society_types:
        return [], completed_query

    # Step 3: Use AI to Find Best-Matching `society_type`
    type_embeddings = model.encode(society_types, convert_to_tensor=True)
    query_embedding = model.encode(completed_query, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(query_embedding, type_embeddings)
    best_match_index = torch.argmax(similarity_scores)
    best_match = society_types[best_match_index]

    # Step 4: Filter societies strictly by the best-matching `society_type`
    filtered_societies = list(Society.objects.filter(society_type=best_match))

    if not filtered_societies:
        return [], completed_query

    # Step 5: Rank results by how well `description` matches the query
    descriptions = [society.description for society in filtered_societies]
    description_embeddings = model.encode(descriptions, convert_to_tensor=True)

    description_scores = util.pytorch_cos_sim(query_embedding, description_embeddings).squeeze(0)
    ranked_societies = sorted(zip(filtered_societies, description_scores), key=lambda x: x[1], reverse=True)

    sorted_results = [society for society, score in ranked_societies]

    # Step 6: Check Society Names (for name-based searches)
    name_societies = Society.objects.filter(name__icontains=completed_query)

    # Step 7: Merge Name Matches + Sorted Description Matches (Avoid Duplicates)
    final_results = list(name_societies) + [society for society in sorted_results if society not in name_societies]

    return final_results, completed_query
