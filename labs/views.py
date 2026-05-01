from django.shortcuts import render
from .models import Product, Category

def home(request):
    category_id = request.GET.get('category')
    query = request.GET.get('q')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories
    }

    return render(request, 'labs/home.html', context)