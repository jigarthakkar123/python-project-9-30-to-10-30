from django.shortcuts import render,redirect
from . models import User,Product,Wishlist,Cart
import requests
import random
import stripe
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


YOUR_DOMAIN = 'http://localhost:8000'
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def index(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=="buyer":
            return render(request,'index.html')
        else:
            return render(request,'seller-index.html')
    except:
        return render(request,'index.html')

def signup(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            msg="Email Already Registered"
            return render(request,'login.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    profile_picture=request.FILES['profile_picture'],
                    usertype=request.POST['usertype']
                )
                msg="User Registered Successfully"
                return render(request,'login.html',{'msg':msg})
            else:
                msg="Password & Confirm Password Does Not Matched"
                return render(request,'signup.html',{'msg':msg})
    else:
        return render(request,'signup.html')

def login(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            if user.password==request.POST['password']:
                request.session['email']=user.email
                request.session['fname']=user.fname
                request.session['profile_picture']=user.profile_picture.url
                if user.usertype=="buyer":
                    return render(request,'index.html')
                else:
                    return render(request,'seller-index.html')
            else:
                msg="Incorrect Password"
                return render(request,'login.html',{'msg':msg})
        except:
            msg="Email Not Registered"
            return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        del request.session['profile_picture']
        msg="Logged Out Successfully"
        return render(request,'login.html',{'msg':msg})
    except:
        msg="Logged Out Successfully"
        return render(request,'login.html',{'msg':msg})

def change_password(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                if user.password!=request.POST['new_password']:
                    user.password=request.POST['new_password']
                    user.save()
                    del request.session['email']
                    del request.session['fname']
                    del request.session['profile_picture']
                    msg="Password Changed Successfully"
                    return render(request,'login.html',{'msg':msg})
                else:
                    msg="Your New Password Can't Be From Your Old Password"
                    if user.usertype=="buyer":
                        return render(request,'change-password.html',{'msg':msg})
                    else:
                        return render(request,'seller-change-password.html',{'msg':msg})
            else:
                msg="New Password & Confirm New Password Does Not Matched"
                if user.usertype=="buyer":
                    return render(request,'change-password.html',{'msg':msg})
                else:
                    return render(request,'seller-change-password.html',{'msg':msg})
        else:
            msg="Old Password Does Not Matched"
            if user.usertype=="buyer":
                return render(request,'change-password.html',{'msg':msg})
            else:
                return render(request,'seller-change-password.html',{'msg':msg})

    else:
        if user.usertype=="buyer":
            return render(request,'change-password.html')
        else:
            return render(request,'seller-change-password.html')

def profile(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.mobile=request.POST['mobile']
        user.address=request.POST['address']
        try:
            user.profile_picture=request.FILES['profile_picture']
        except:
            pass
        user.save()
        request.session['profile_picture']=user.profile_picture.url
        msg="Profile Updated Successfully"
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user,'msg':msg})
        else:
            return render(request,'seller-profile.html',{'user':user,'msg':msg})
    else:
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user})
        else:
            return render(request,'seller-profile.html',{'user':user})

def forgot_password(request):
    if request.method=="POST":
        try:
            user=User.objects.get(mobile=request.POST['mobile'])
            otp=random.randint(1000,9999)
            print("Mobile Is : "+user.mobile)
            mobile=str(user.mobile)
            message="Hello, Your OTP For Forgot Password Is "+str(otp)
            params = {
                "message": message,
                "route": "q",
                "numbers": mobile,
                "sms_details": "1"
            }
            headers = {
                "accept": "application/json",
                "Authorization": "k3f1DFcPgZ9DahdaYRK0Yc329i7GKuKnt1Jgcy4mc1oWIiXBrSP36SUoyFV4"
            }
            response = requests.get(
                "https://www.fast2sms.com/dev/bulkV2",
                params=params,
                headers=headers
            )
            print(response.text)
            request.session['mobile']=user.mobile
            request.session['otp']=otp
            return render(request,'otp.html')
        except:
            msg="Mobile Number Not Registered"
            return render(request,'forgot-password.html',{'msg':msg})
        
    else:
        return render(request,'forgot-password.html')

def verify_otp(request):
    otp1=int(request.POST['otp'])
    otp2=int(request.session['otp'])
    if otp1==otp2:
        del request.session['otp']
        msg="Set Your New Password"
        return render(request,'new-password.html',{'msg':msg})
    else:
        msg="Invalid OTP"
        return render(request,'otp.html',{'msg':msg})

def new_password(request):
    if request.POST['new_password']==request.POST['cnew_password']:
        user=User.objects.get(mobile=request.session['mobile'])
        user.password=request.POST['new_password']
        user.save()
        del request.session['mobile']
        msg="Password Updated Successfully"
        return render(request,'login.html',{'msg':msg})
    else:
        msg="New Password & Confirm New Password Does Not Matched"
        return render(request,'new-password.html',{'msg':msg})

def seller_add_product(request):
    if request.method=="POST":
        seller=User.objects.get(email=request.session['email'])
        Product.objects.create(
            seller=seller,
            product_category=request.POST['product_category'],
            product_name=request.POST['product_name'],
            product_price=request.POST['product_price'],
            product_desc=request.POST['product_desc'],
            product_image=request.FILES['product_image'],
        )
        msg="Product Added Successfully"
        return render(request,'seller-add-product.html',{'msg':msg})
    else:
        return render(request,'seller-add-product.html')

def seller_view_product(request,cat):
    seller=User.objects.get(email=request.session['email'])
    products=Product()
    if cat=='all':
        products=Product.objects.filter(seller=seller)
    elif cat=="Men":
        products=Product.objects.filter(seller=seller,product_category='Men')
    elif cat=="Women":
            products=Product.objects.filter(seller=seller,product_category='Women')
    elif cat=="Kids":
                products=Product.objects.filter(seller=seller,product_category='Kids')
    elif cat=="Accessories":
                products=Product.objects.filter(seller=seller,product_category='Accessories')
    elif cat=="Shoes":
                products=Product.objects.filter(seller=seller,product_category='Shoes')    
    return render(request,'seller-view-product.html',{'products':products})

def seller_edit_product(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=="POST":
        product.product_category=request.POST['product_category']
        product.product_name=request.POST['product_name']
        product.product_price=request.POST['product_price']
        product.product_desc=request.POST['product_desc']
        try:
            product.product_image=request.FILES['product_image']
        except:
            pass
        product.save()
        msg="Product Updated Successfully"
        return render(request,'seller-edit-product.html',{'product':product,'msg':msg})
    else:
        return render(request,'seller-edit-product.html',{'product':product})

def seller_delete_product(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    msg="Product Deleted Successfully"
    return render(request,'seller-view-product.html',{'products':products,'msg':msg})

def shop(request,cat):
    products=Product()
    if cat=='all':
        products=Product.objects.all()
    elif cat=="Men":
        products=Product.objects.filter(product_category='Men')
    elif cat=="Women":
            products=Product.objects.filter(product_category='Women')
    elif cat=="Kids":
                products=Product.objects.filter(product_category='Kids')
    elif cat=="Accessories":
                products=Product.objects.filter(product_category='Accessories')
    elif cat=="Shoes":
                products=Product.objects.filter(product_category='Shoes')
    return render(request,'shop.html',{'products':products})

def product_details(request,pk):
    wishlist_flag=False
    cart_flag=False
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    try:
         Wishlist.objects.get(user=user,product=product)
         wishlist_flag=True
    except:
        pass
    try:
        Cart.objects.get(user=user,product=product)
        cart_flag=True
    except:
        pass     
    return render(request,'product-details.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
     product=Product.objects.get(pk=pk)
     user=User.objects.get(email=request.session['email'])
     Wishlist.objects.create(user=user,product=product)
     return redirect('wishlist')

def wishlist(request):
     user=User.objects.get(email=request.session['email'])
     wishlists=Wishlist.objects.filter(user=user)
     return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    wishlist=Wishlist.objects.get(user=user,product=product)
    wishlist.delete() 
    return redirect('wishlist')

def add_to_cart(request,pk):
     product=Product.objects.get(pk=pk)
     user=User.objects.get(email=request.session['email'])
     Cart.objects.create(
          user=user,
          product=product,
          product_price=product.product_price,
          product_qty=1,
          total_price=product.product_price,
          payment_status=False
        )
     return redirect('cart')

def cart(request):
     net_price=0
     user=User.objects.get(email=request.session['email'])
     carts=Cart.objects.filter(user=user,payment_status=False)
     for i in carts:
          net_price=net_price+i.total_price 
     return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    cart=Cart.objects.get(user=user,product=product)
    cart.delete() 
    return redirect('cart')

def change_qty(request,pk):
    cart=Cart.objects.get(pk=pk)
    product_qty=int(request.POST['product_qty'])
    cart.total_price=cart.product_price*product_qty
    cart.product_qty=product_qty
    cart.save()
    return redirect('cart')

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	user=User.objects.get(email=request.session['email'])
	user_name=f"{user.fname} {user.lname}"
	user_address=f"{user.address}"
	user_mobile=f"{user.mobile}"
	session = stripe.checkout.Session.create(
		
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'unit_amount': final_amount,
				'product_data': {
					'name': 'Checkout Session Data',
					'description':f'''Customer:{user_name},\n\n
					Address:{user_address},\n
					Mobile:{user_mobile}''',
				},
			},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',
		customer_email=user.email,
		shipping_address_collection={
			'allowed_countries':['IN'],
		}
		)
	return JsonResponse({'id': session.id})

def success(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
     user=User.objects.get(email=request.session['email'])
     carts=Cart.objects.filter(user=user,payment_status=True)
     return render(request,'myorder.html',{'carts':carts})