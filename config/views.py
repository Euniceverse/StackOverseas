from django.shortcuts import render
from apps.societies.views import top_societies

def home(request):
    """Display the main page.
    Shows login/signup buttons for anonymous users,
    and user-specific content for authenticated users."""
    disct_soc = top_societies()
    return render(request, "home.html", {
        "top_societies_per_type": disct_soc['top_societies_per_type'],
        "top_overall_societies": disct_soc['top_overall_societies'],
        'user' : request.user
    })
    # return render(request, 'home.html', {'user': request.user})


from django.shortcuts import render
from django.db.models import Q
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import process, fuzz
import torch
from apps.societies.models import Society

# Load AI model for meaning-based matching
model = SentenceTransformer("all-MiniLM-L6-v2")

def ai_search(request):
    query = request.GET.get('q', '').strip().lower()

    if not query:
        return render(request, 'search_results.html', {'results': [], 'suggestions': []})

    # 🔹 Step 1: Get all society types & names
    society_types = list(Society.objects.values_list("society_type", flat=True))
    all_names = list(Society.objects.values_list("name", flat=True))

    if not society_types:
        return render(request, 'search_results.html', {'results': [], 'suggestions': []})

    # 🔹 Step 2: **Fix Typos Using Fuzzy Matching First**
    fuzzy_matches = process.extract(query, society_types, limit=1, scorer=fuzz.ratio)
    fuzzy_match = fuzzy_matches[0][0] if fuzzy_matches and fuzzy_matches[0][1] > 70 else None

    # 🔹 Step 3: Use AI to Find Best-Matching `society_type`
    type_embeddings = model.encode(society_types, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(query_embedding, type_embeddings)
    best_match_index = torch.argmax(similarity_scores)
    ai_match = society_types[best_match_index]

    # **Final Matching Decision: Prefer Fuzzy Match if Found**
    best_match = fuzzy_match if fuzzy_match else ai_match

    # 🔹 Step 4: Filter societies strictly by the best-matching `society_type`
    filtered_societies = list(Society.objects.filter(society_type=best_match))

    # If no societies found in category, return suggestions instead
    if not filtered_societies:
        suggestions = process.extract(query, all_names + society_types, limit=3, scorer=fuzz.ratio)
        suggested_words = [match[0] for match in suggestions if match[1] > 70]
        return render(request, 'search_results.html', {'results': [], 'suggestions': suggested_words})

    # 🔹 Step 5: Rank results by how well `description` matches the query
    descriptions = [society.description for society in filtered_societies]
    description_embeddings = model.encode(descriptions, convert_to_tensor=True)

    description_scores = util.pytorch_cos_sim(query_embedding, description_embeddings).squeeze(0)
    ranked_societies = sorted(zip(filtered_societies, description_scores), key=lambda x: x[1], reverse=True)

    sorted_results = [society for society, score in ranked_societies]

    # 🔹 Step 6: ALSO Check Society Names (Fixes `"Allen"` Issue)
    name_matches = process.extract(query, all_names, limit=5, scorer=fuzz.partial_ratio)
    matched_names = [match[0] for match in name_matches if match[1] > 70]

    name_societies = Society.objects.filter(name__in=matched_names)

    # 🔹 Step 7: Merge Name Matches + Sorted Description Matches (Avoid Duplicates)
    final_results = list(name_societies) + [society for society in sorted_results if society not in name_societies]

    return render(request, 'search_results.html', {'results': final_results, 'suggestions': []})
