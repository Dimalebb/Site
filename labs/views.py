from django.shortcuts import render

def home(request):
    context = {
        'title': 'Головна сторінка',
        'message': 'Це головна сторінка'
    }
    return render(request, 'labs/template.html', context)


def page1(request):
    context = {
        'title': 'Сторінка 1',
        'message': 'Це перша сторінка'
    }
    return render(request, 'labs/template.html', context)


def page2(request):
    context = {
        'title': 'Сторінка 2',
        'message': 'Це друга сторінка'
    }
    return render(request, 'labs/template.html', context)
