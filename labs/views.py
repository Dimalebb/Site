from django.shortcuts import render, redirect
from django.db.models import Avg
from .models import Product, Category, Review, NewsletterSubscriber

def home(request):
    category_id = request.GET.get('category')
    query = request.GET.get('q')
    cart = request.session.get('cart', [])
    cart_products = Product.objects.filter(id__in=cart)
    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories,
        'cart_products': cart_products
    }

    return render(request, 'labs/home.html', context)

def product_detail(request, id):
    product = Product.objects.get(id=id)
    reviews = product.reviews.all()

    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    if average_rating:
        average_rating = round(average_rating, 1)
    else:
        average_rating = 0

    recommend_percent = 0

    if reviews.count() > 0:
        recommended = reviews.filter(rating__gte=4).count()
        recommend_percent = int((recommended / reviews.count()) * 100)

    cart = request.session.get('cart', [])

    cart_products = Product.objects.filter(id__in=cart)

    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'recommend_percent': recommend_percent,
        'cart': cart,
        'cart_products': cart_products
    }

    return render(request, 'labs/product.html', context)

def add_to_cart(request, id):

    cart = request.session.get('cart', [])

    if id not in cart:
        cart.append(id)

    request.session['cart'] = cart

    return redirect('product', id=id)

def remove_from_cart(request, id):

    cart = request.session.get('cart', [])

    if id in cart:
        cart.remove(id)

    request.session['cart'] = cart

    referer = request.META.get('HTTP_REFERER', '/')

    if '?' in referer:
        return redirect(referer + '&cart=open')

    return redirect(referer + '?cart=open')

def add_review(request, id):

    if request.method == 'POST':

        product = Product.objects.get(id=id)

        name = request.POST.get('name')
        text = request.POST.get('text')
        rating = request.POST.get('rating')

        Review.objects.create(
            product=product,
            name=name,
            text=text,
            rating=rating
        )

    return redirect('product', id=id)


def subscribe(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        name = request.POST.get('name')
        agreed = request.POST.get('agreed')

        if email and agreed:

            NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'agreed': True
                }
            )

    return redirect('home')