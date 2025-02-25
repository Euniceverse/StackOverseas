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
import torch
from apps.societies.models import Society

# Load the AI model
model = SentenceTransformer("all-MiniLM-L6-v2")

def ai_search(request):
    query = request.GET.get('q', '').strip().lower()

    if not query:
        return render(request, 'search_results.html', {'results': []})

    # 🔹 Step 1: Get all society types
    society_types = list(Society.objects.values_list("society_type", flat=True))

    if not society_types:
        return render(request, 'search_results.html', {'results': []})

    # 🔹 Step 2: Find best-matching society type
    type_embeddings = model.encode(society_types, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(query_embedding, type_embeddings)
    best_match_index = torch.argmax(similarity_scores)

    best_match = society_types[best_match_index]

    # 🔹 Step 3: Get societies of the best-matching type
    filtered_societies = list(Society.objects.filter(society_type=best_match))

    if not filtered_societies:
        return render(request, 'search_results.html', {'results': []})

    # 🔹 Step 4: Rank results by description similarity
    descriptions = [society.description for society in filtered_societies]
    description_embeddings = model.encode(descriptions, convert_to_tensor=True)

    description_scores = util.pytorch_cos_sim(query_embedding, description_embeddings).squeeze(0)
    ranked_societies = sorted(zip(filtered_societies, description_scores), key=lambda x: x[1], reverse=True)

    sorted_results = [society for society, score in ranked_societies]

    # 🔹 Step 5: **ALSO check society names (NEW)**
    name_matches = Society.objects.filter(name__icontains=query)

    # Merge name matches + sorted results (avoiding duplicates)
    final_results = list(name_matches) + [society for society in sorted_results if society not in name_matches]

    return render(request, 'search_results.html', {'results': final_results})
