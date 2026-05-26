from django.shortcuts import render, redirect
from django.db.models import Avg
from .models import Product, Category, Review, NewsletterSubscriber, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
import math


def home(request):

    category_id = request.GET.get('category')
    query = request.GET.get('q')

    cart = request.session.get('cart', {})

    if isinstance(cart, list):
        cart = {}
        request.session['cart'] = cart

    products = Product.objects.all()

    categories = Category.objects.all()

    if category_id:
        products = products.filter(category__id=category_id)

    if query:
        products = products.filter(name__icontains=query)

    cart_data = []

    for item_key, item in cart.items():

        product = Product.objects.get(id=item['product_id'])

        monthly = None

        if item['credit'] and item['months']:
            monthly = math.ceil(product.price / item['months'])

        cart_data.append({
            'key': item_key,
            'product': product,
            'quantity': item['quantity'],
            'credit': item['credit'],
            'months': item['months'],
            'monthly': monthly,
        })

    context = {
        'products': products,
        'categories': categories,
        'cart_products': cart_data
    }

    return render(request, 'labs/home.html', context)


def product_detail(request, id):

    product = Product.objects.get(id=id)

    reviews = product.reviews.all()

    monthly_payment = math.ceil(product.price / 10)

    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    if average_rating:
        average_rating = round(average_rating, 1)
    else:
        average_rating = 0

    recommend_percent = 0

    if reviews.count() > 0:
        recommended = reviews.filter(rating__gte=4).count()
        recommend_percent = int((recommended / reviews.count()) * 100)

    categories = Category.objects.all()

    cart = request.session.get('cart', {})

    if isinstance(cart, list):
        cart = {}
        request.session['cart'] = cart

    cart_data = []

    for item_key, item in cart.items():

        cart_product = Product.objects.get(id=item['product_id'])

        monthly = None

        if item['credit'] and item['months']:
            monthly = math.ceil(cart_product.price / item['months'])

        cart_data.append({
            'key': item_key,
            'product': cart_product,
            'quantity': item['quantity'],
            'credit': item['credit'],
            'months': item['months'],
            'monthly': monthly,
        })

    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'recommend_percent': recommend_percent,
        'cart': cart,
        'cart_products': cart_data,
        'categories': categories,
        'monthly_payment': monthly_payment,
    }

    return render(request, 'labs/product.html', context)


def add_to_cart(request, id):

    cart = request.session.get('cart', {})

    if isinstance(cart, list):
        cart = {}

    months = request.GET.get('months')
    credit = request.GET.get('credit')

    product_id = f"{id}_{credit}_{months}"

    if product_id in cart:

        cart[product_id]['quantity'] += 1

    else:

        cart[product_id] = {
            'product_id': id,
            'quantity': 1,
            'credit': credit == '1',
            'months': int(months) if months else None,
        }

    request.session['cart'] = cart

    return redirect('product', id=id)


def remove_from_cart(request, id):

    cart = request.session.get('cart', {})

    item_key = request.GET.get('item')

    if item_key in cart:
        del cart[item_key]

    request.session['cart'] = cart

    referer = request.META.get('HTTP_REFERER', '/')

    if 'cart=open' not in referer:

        if '?' in referer:
            referer += '&cart=open'
        else:
            referer += '?cart=open'

    return redirect(referer)


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


def register(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.email = request.POST.get('email')

            user.save()

            return redirect('login')

    else:

        form = UserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form
    })


def forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        try:

            user = User.objects.get(email=email)

            code = random.randint(100000, 999999)

            request.session['reset_code'] = str(code)

            request.session['reset_user'] = user.id

            send_mail(
                'Код відновлення пароля',
                f'Ваш код: {code}',
                'admin@test.com',
                [email],
                fail_silently=False,
            )

            return redirect('verify_code')

        except User.DoesNotExist:

            return render(request, 'registration/forgot_password.html', {
                'error': 'Користувача не знайдено'
            })

    return render(request, 'registration/forgot_password.html')


def verify_code(request):

    if request.method == 'POST':

        entered_code = request.POST.get('code')

        session_code = request.session.get('reset_code')

        if entered_code == session_code:

            request.session['verified'] = True

            return redirect('new_password')

        else:

            return render(request, 'registration/verify_code.html', {
                'error': 'Неправильний код'
            })

    return render(request, 'registration/verify_code.html')


def new_password(request):

    if not request.session.get('verified'):
        return redirect('forgot_password')

    if request.method == 'POST':

        password = request.POST.get('password')

        user_id = request.session.get('reset_user')

        user = User.objects.get(id=user_id)

        user.password = make_password(password)

        user.save()

        request.session.flush()

        return redirect('login')

    return render(request, 'registration/new_password.html')


@login_required
def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('home')

    cart_data = []

    for item_key, item in cart.items():

        product = Product.objects.get(id=item['product_id'])

        monthly = None

        if item['credit'] and item['months']:
            monthly = math.ceil(product.price / item['months'])

        cart_data.append({
            'key': item_key,
            'product': product,
            'quantity': item['quantity'],
            'credit': item['credit'],
            'months': item['months'],
            'monthly': monthly,
        })

    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        address = request.POST.get('address', '').strip()
        comment = request.POST.get('comment', '').strip()

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            city=city,
            address=address,
            comment=comment
        )

        for item in cart.values():

            product = Product.objects.get(id=item['product_id'])

            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=item['quantity'],
                credit=item['credit'],
                months=item['months']
            )

        request.session['cart'] = {}

        return redirect('profile')

    return render(request, 'labs/checkout.html', {
        'cart_products': cart_data
    })

@login_required
def profile(request):

    if request.user.is_superuser:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)

    return render(request, 'registration/profile.html', {
        'orders': orders
    })


def logout_view(request):

    logout(request)

    return redirect('home')


def increase_cart(request, id):

    cart = request.session.get('cart', {})

    item_key = request.GET.get('item')

    if item_key in cart:
        cart[item_key]['quantity'] += 1

    request.session['cart'] = cart

    referer = request.META.get('HTTP_REFERER', '/')

    if 'cart=open' not in referer:

        if '?' in referer:
            referer += '&cart=open'
        else:
            referer += '?cart=open'

    return redirect(referer)


def decrease_cart(request, id):

    cart = request.session.get('cart', {})

    item_key = request.GET.get('item')

    if item_key in cart:

        cart[item_key]['quantity'] -= 1

        if cart[item_key]['quantity'] <= 0:
            del cart[item_key]

    request.session['cart'] = cart

    referer = request.META.get('HTTP_REFERER', '/')

    if 'cart=open' not in referer:

        if '?' in referer:
            referer += '&cart=open'
        else:
            referer += '?cart=open'

    return redirect(referer)