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

# Load a pre-trained AI model for contextual search
model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and efficient

def ai_search(request):
    query = request.GET.get('q', '').strip().lower()

    if not query:
        return render(request, 'search_results.html', {'results': []})

    # 🔹 Step 1: Get all unique society categories
    society_types = list(Society.objects.values_list("society_type", flat=True))

    if not society_types:
        return render(request, 'search_results.html', {'results': []})

    # 🔹 Step 2: Convert categories + query into AI embeddings
    type_embeddings = model.encode(society_types, convert_to_tensor=True)  # Society category embeddings
    query_embedding = model.encode(query, convert_to_tensor=True)  # Query embedding

    # 🔹 Step 3: Find the most similar category based on meaning
    similarity_scores = util.pytorch_cos_sim(query_embedding, type_embeddings)
    best_match_index = torch.argmax(similarity_scores)  # Find best category match

    best_match = society_types[best_match_index]  # Get best-matching category

    # 🔹 Step 4: Filter societies strictly by the best-matching category
    filtered_societies = list(Society.objects.filter(society_type=best_match))

    if not filtered_societies:
        return render(request, 'search_results.html', {'results': []})

    # 🔹 Step 5: Rank results by how well their descriptions match the query
    descriptions = [society.description for society in filtered_societies]
    description_embeddings = model.encode(descriptions, convert_to_tensor=True)

    description_scores = util.pytorch_cos_sim(query_embedding, description_embeddings).squeeze(0)

    # Sort societies by description relevance
    ranked_societies = sorted(zip(filtered_societies, description_scores), key=lambda x: x[1], reverse=True)
    sorted_results = [society for society, score in ranked_societies]  # Extract sorted societies

    return render(request, 'search_results.html', {'results': sorted_results})
