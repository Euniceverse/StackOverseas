from django.shortcuts import render

def eventspage(request):
    """이벤트 페이지를 렌더링"""
    return render(request, "events/events.html")  # ✅ 올바른 경로인지 확인
