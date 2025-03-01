from django.shortcuts import render
from apps.societies.functions import top_societies

def home(request):
    """Display the main page.
    Shows login/signup buttons for anonymous users,
    and user-specific content for authenticated users."""
    disct_soc = top_societies(request.user)
    return render(request, "home.html", {
        "top_societies_per_type": disct_soc['top_societies_per_type'],
        "top_overall_societies": disct_soc['top_overall_societies'],
        'user' : request.user
    })
    # return render(request, 'home.html', {'user': request.user})

from django.shortcuts import render
from django.db.models import Q
from sentence_transformers import SentenceTransformer, util
from symspellpy import SymSpell, Verbosity
import requests
import torch
from apps.societies.models import Society

# Load AI model for meaning-based matching
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load SymSpell for autocorrect
sym_spell = SymSpell(max_dictionary_edit_distance=2)
sym_spell.load_dictionary("frequency_dictionary_en.txt", term_index=0, count_index=1)

# Function to correct spelling using SymSpell
def correct_spelling(query):
    suggestions = sym_spell.lookup(query, Verbosity.CLOSEST, max_edit_distance=2)
    return suggestions[0].term if suggestions else query  # Return corrected word or original

# Function to autocomplete using Datamuse API
def autocomplete(query):
    response = requests.get(f"https://api.datamuse.com/sug?s={query}")
    suggestions = response.json()
    return suggestions[0]["word"] if suggestions else query  # Return best match

def ai_search(request):
    query = request.GET.get('q', '').strip().lower()

    if not query:
        return render(request, 'search_results.html', {'results': [], 'suggestion': None})

    # 🔹 Step 1: Correct Spelling and Autocomplete the Query
    corrected_query = correct_spelling(query)
    completed_query = autocomplete(corrected_query)

    # 🔹 Step 2: Get all society types and names
    society_types = list(Society.objects.values_list("society_type", flat=True))
    all_names = list(Society.objects.values_list("name", flat=True))

    if not society_types:
        return render(request, 'search_results.html', {'results': [], 'suggestion': completed_query})

    # 🔹 Step 3: Use AI to Find Best-Matching `society_type`
    type_embeddings = model.encode(society_types, convert_to_tensor=True)
    query_embedding = model.encode(completed_query, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(query_embedding, type_embeddings)
    best_match_index = torch.argmax(similarity_scores)
    best_match = society_types[best_match_index]

    # 🔹 Step 4: Filter societies strictly by the best-matching `society_type`
    filtered_societies = list(Society.objects.filter(society_type=best_match))

    # If no societies are found, return the corrected suggestion
    if not filtered_societies:
        return render(request, 'search_results.html', {'results': [], 'suggestion': completed_query})

    # 🔹 Step 5: Rank results by how well `description` matches the query
    descriptions = [society.description for society in filtered_societies]
    description_embeddings = model.encode(descriptions, convert_to_tensor=True)

    description_scores = util.pytorch_cos_sim(query_embedding, description_embeddings).squeeze(0)
    ranked_societies = sorted(zip(filtered_societies, description_scores), key=lambda x: x[1], reverse=True)

    sorted_results = [society for society, score in ranked_societies]

    # 🔹 Step 6: ALSO Check Society Names (for name-based searches)
    name_societies = Society.objects.filter(name__icontains=completed_query)

    # 🔹 Step 7: Merge Name Matches + Sorted Description Matches (Avoid Duplicates)
    final_results = list(name_societies) + [society for society in sorted_results if society not in name_societies]

    return render(request, 'search_results.html', {'results': final_results, 'suggestion': completed_query})
