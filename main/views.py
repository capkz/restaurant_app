from django.shortcuts import render,redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import UpdateUserForm,UpdateProductForm,CreateProductForm, AddReviewForm,ContactForm,DiscountForm,RemoveDiscountForm
#if login required for a method then simply copy this code and put it above the method declaration
#@login_required(login_url='login')
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.db.models import Q


def loginPage(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        user = authenticate(request,username=username, password=password)
        if user is not None :
            login(request,user)
            return redirect('main')
        else:
            messages.info(request,'Username OR password is incorrect !!')
            context={}
            return render(request,'accounts/login.html',context)
    context={}
    return render(request,'accounts/login.html',context)

def logoutPage(request):
    logout(request)
    return redirect('login')

def register(request):
    form = CreateUserForm

    if request.method=='POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            #flashmessage :
            messages.success(request,"Account is created for " + user)
            customer_type= request.POST.getlist('customer')
            rest_type=request.POST.getlist('restaurant')

            #print(customer_type)
            #print(rest_type)

            #print(user)

            if customer_type!=[]:   #the registered user must be a customer object
                Customer.objects.create(user=User.objects.get(username=user), name=(User.objects.get(username=user)).username, email=form.cleaned_data.get('username'))
                #print("I am in custom")
            if rest_type!=[]: #the registered user must be a restaurant owner object
                Restaurant.objects.create(owner=User.objects.get(username=user), name=(User.objects.get(username=user)).username,email=form.cleaned_data.get('username'))
                Customer.objects.create(user=User.objects.get(username=user), name=(User.objects.get(username=user)).username, email=form.cleaned_data.get('username'))
                #print("I am in rest")

            return redirect('login')

    context={'form':form}
    return render(request,'accounts/register.html',context)


def home(request):

    ids=[]
    prods=Product.objects.all()
    for i in range(len(prods)):
        prod_id=prods[i].id
        ids.append(prod_id)

    all_prod_avg=score_of_reviewed_products_list(request)

    all_discounts=Discount_History.objects.all()
    context={"product_id":ids,'all_prod_avg':all_prod_avg,'all_discounts':all_discounts,'nbar':"home"}
    context['cartItems']=getCart(request.user)
    return render(request,'Main_Templates/home.html',context)

def getCart(user):
    if user.is_authenticated:
        customer=Customer.objects.filter(user=user)[0]
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cart = order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cart=order['get_cart_items']
    return cart

def main(request):

    cartItems = getCart(request.user)
    if request.user.is_authenticated:

        #print(request.user)
        #is it a restaurant owner
        restaurant_owner=0
        try:
            if Restaurant.objects.get(name=request.user.username) != []:
                restaurant_owner=1
        except:
            restaurant_owner=0

        #print("Owner ", restaurant_owner)

        customer_group=Group.objects.get(name='Customers')
        customer_group.user_set.add(request.user)

        if restaurant_owner==1 :
            rest_group = Group.objects.get(name='Restaurant Owners') 
            rest_group.user_set.add(request.user)

    else:
        #the user is not authenticated
        items=[]
        order={'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems=order['get_cart_items']

    context={}
    query=""
    if request.method=="POST":
        query=request.POST.get('q')
        context['query']=str(query)

        searched_products=get_product_queryset(query)

        ids=[]
        print(searched_products)
        for i in searched_products:
            ids.append(i.id)

        print(ids)

        return render(request,'Main_Templates/search_results.html',{'searched_products':searched_products,'ids':ids})
    
    products=Product.objects.all()

    all_categories=[]
    all_categories=category_division(request)
    print("ALL CATEGORIES ")
    print(all_categories)

    context = {'products':products, 'cartItems': cartItems,'all_categories':all_categories} # data to pass into the template
    
    return render(request,'Main_Templates/orders.html',context)

def detailedProductView(request):
    cartItems = getCart(request.user)
    str=request.GET['item_id']

    #print(str)
    prod=Product.objects.get(id=int(str))
    #print(prod)
    all_reviews=[]
    try:
        review=Reviews.objects.filter(product=prod)
        for i in review:
            #print(i)
            all_reviews.append(i)
    except:
        print("No review for this product")


    context={'product':prod,'all_reviews':all_reviews,'cartItems':cartItems}
    return render(request,'Main_Templates/detailed_product.html',context)

def addProductReview(request):
    cartItems = getCart(request.user)
    context={}
    str=request.GET['product_id']
    print("PRODUCT : ")
    print(str)
    print("USER : ")
    print(request.user)

    users=request.user
    product=Product.objects.get(name=str)

    if request.method=="POST":
        form=AddReviewForm(request.POST, request.FILES)
        if form.is_valid:
            comm=request.POST.get('comment')
            speed=request.POST.get('speed_rating')
            service=request.POST.get('service_rating')
            quality=request.POST.get('food_quality_rating')
            image = request.FILES.get('image')
            Reviews.objects.create(user=users,product=product,comment=comm,speed_rating=speed,service_rating=service,food_quality_rating=quality,image=image)

    else:
        form=AddReviewForm()
        context={'form':form,'cartItems':cartItems}

    return render(request,"Main_Templates/add_review.html",context)




def cart(request):

    #if user is authenticated ? 
    if request.user.is_authenticated:
        
        customer=Customer.objects.filter(user=request.user)[0]
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        #find or create order then attach items to that order
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        #the user is not authenticated
        items=[]
        order={'get_cart_total':0, 'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']

    context = {'items':items, 'order':order,'cartItems': cartItems} # data to pass into the template
    return render(request,'Main_Templates/cart.html',context)

def checkout(request):

    if request.user.is_authenticated:
        customer=Customer.objects.filter(user=request.user)[0]
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        #find or create order then attach items to that order
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        #the user is not authenticated
        items=[]
        order={'get_cart_total':0, 'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']

    context = {'items':items, 'order':order,'cartItems': cartItems} # data to pass into the template
    return render(request,'Main_Templates/checkout.html',context)

def updateItem(request):
    data=json.loads(request.body)
    productId = data['productId'] #from body section
    action= data['action']

    #print('Action : ', action)
    #print('ProductId : ', productId)

    #logged in customer :
    customer=Customer.objects.filter(user=request.user)[0]
    product=Product.objects.get(id=productId)
    #get or create order
    order,created=Order.objects.get_or_create(customer=customer,complete=False)

    orderItem, created= OrderItem.objects.get_or_create(order=order,product=product)

    #for that item add or subtract:

    if action =='add':
        orderItem.quantity = (orderItem.quantity+1)

    elif action =='remove':
        orderItem.quantity=(orderItem.quantity-1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()


    return JsonResponse('Item was added', safe=False) #to confirm 



def processOrder(request):
    #print('Data : ', request.body)
    transaction_id =datetime.datetime.now().timestamp()
    data =json.loads(request.body)

    if request.user.is_authenticated:
        customer=Customer.objects.filter(user=request.user)[0]
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        total=float(data['form']['total'])
        order.transaction_id= transaction_id

        if total == float(order.get_cart_total):
            order.complete=True

        order.save()
        #print("Shipping information : ", order.shipping)
        if order.shipping == True:
            Shipping.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                date_added=transaction_id,
                
                )
    else:
        print("User is not logged in ")

    return JsonResponse('Payment submitted .. ', safe=False)


def customerProfile(request):
    cartItems = getCart(request.user)
    customer=Customer.objects.filter(user=request.user)[0]
    personal_info=[customer.name,customer.email,customer.phone,customer.date_created]

    orders=Order.objects.filter(customer=customer,complete=True)

    all_orders=[]
    for i in orders:
        orderitems=OrderItem.objects.filter(order=i)
        all_orders.append(orderitems)

    #print(all_orders)

    info=[]
    order_count=[]
    for i in all_orders:
        for j in i :
            item_name=str(j.product)
            order_no=str(j.order)
            order_count.append(int(order_no))
            item_amount=str(j.quantity)
            info.append([item_name,order_no,item_amount])

    #print(info)
    #print(order_count)

    order_status=[]
    for i in order_count:
        orders=Order.objects.filter(customer=customer,id=i)
        order_status.append(orders)
    #print(order_status)
    
    order_status2=[]
    for i in order_status:
        order_status2.append(i[0].order_done)


    a=0
    for i in info:
        i.append(order_status2[a])
        a=a+1
    #print(info)

    context={'personal_info':personal_info,'order_history':info,'cartItems':cartItems}

    #post customer information
    #post order status information

    return render(request,'Main_Templates/customer_profile.html',context)

def customerInfoUpdate(request):
    cartItems = getCart(request.user)
    if request.method=="POST":
        form=UpdateUserForm(request.POST)
        if form.is_valid():
            #for the customer who requested this change make the same changes
            obj = form.save(commit=False)

            request.user.username=obj.username
            request.user.email=obj.email
            request.user.save()
            customer=Customer.objects.filter(user=request.user)[0]
            customer.name=obj.username
            customer.email=obj.email
            customer.phone=request.POST.get('phone_no')
            customer.save()
            try:
                owner=Restaurant.objects.filter(owner=request.user)[0]
                owner.name=obj.username
                owner.email=obj.email
                owner.phone=request.POST.get('phone_no')
                owner.save()
            except:
                print("The user is not a restaurant owner")

            return redirect('customerProfile')

    else : 
        form=UpdateUserForm()

    context={'form':form,'cartItems':cartItems}
    return render(request,"Main_Templates/customer_info_update.html",context)

def customerOrderCancel(request):
    context={}

    #print("This one : " + request.GET['item_id'])
    str=request.GET['item_id']

    lst=str.split(',')
    #print("Form 1 " )
    #print(lst)
    lst2=[]
    for i in lst:
        if ("," in i) or ( "]" in i ) or ( "[" in i ) or ("'" in i) or (" " in i):
            print("hi")
            i1=i.replace(",","")
            i2=i1.replace("]","")
            i3=i2.replace("[","")
            i4=i3.replace("'","")
            

            lst2.append(i4)
        else:
            lst2.append(i)

    #print("List when splitted")
    #print( lst2 )

    prod=Product.objects.filter(name=lst2[0])
    #print(lst2[0])
    #print(prod[0])
    order=OrderItem.objects.filter(product=prod[0],order=lst2[1],quantity=lst2[2])
    
    #print("ORDER")
    #print(order)

    order.delete()
    return redirect('customerProfile')

def restaurantOwnerProfile(request):
    cartItems = getCart(request.user)
    product=Product.objects.filter(restaurant=Restaurant.objects.filter(owner=request.user)[0])  #prodcuts belonging to my restaurant 
    ordered_items=[]
    for j in product:
        orderitems=OrderItem.objects.filter(product=j)   #among the order items select the ones belonging to my restaurant
        ordered_items.append(orderitems)
    str_ordered_items=[]
    for j in ordered_items:
        for k in j:
            str_ordered_items.append(str(k))


    #print(str_ordered_items)
    order_no=[]
    for i in range(len(str_ordered_items)):
        #print(int(str_ordered_items[i][(str_ordered_items[i].find(':')+1 ):]))

        order_no.append(int(str_ordered_items[i][(str_ordered_items[i].find(':')+1 ):]))


    #print(order_no)
    a=0
    lst=[]
    for i in range(len(order_no)) :
        order_status=Order.objects.filter(id=order_no[i])[0].order_done
        lst.append([str_ordered_items[a],order_status])
        a=a+1

    #print(lst)
    #print("NEw : ", ordered_items )
    #print ("Products", product)

    #post received orders information
    context={"products":product,"orderitems":lst,'cartItems':cartItems}

    return render(request,'Main_Templates/restaurant_owner_profile.html',context)

def deleteRestaurantProduct(request):
    context={}

    #print("This one : " + request.GET['item_id'])
    str=request.GET['item_id']

    product=Product.objects.filter(restaurant=Restaurant.objects.filter(owner=request.user)[0],name=str) 


    #print(product[0])
    try:
        orderitems=OrderItem.objects.get(product=product[0])
        #print(orderitems)
        orderitems.delete()
        product.delete()
    except:
        print("No order previously given for this deleted product")

    product.delete()

    return redirect('restaurantOwnerProfile')

def updateRestaurantProduct(request):
    cartItems = getCart(request.user)
    context={}

    #print("This one : " + request.GET['item_id'])
    str=request.GET['item_id']

    product=Product.objects.filter(restaurant=Restaurant.objects.filter(owner=request.user)[0],name=str) 
    #print(product[0])
    obj=product[0]
    #print("I AM HEREEEE ")
    if request.method=="POST":
        #print("I AM IN POST STATEMENT")
        form=UpdateProductForm(request.POST)
        if form.is_valid():
            #for the customer who requested this change make the same changes
            try:
                orderitems=OrderItem.objects.filter(product=obj)
                #print("THE ORDER ITEMS ARE :")
                #print(orderitems)
                #print("FORM INFO :")
                #print(request.POST.get('name'))
                for i in orderitems :
                    #print("INDIVIDUAL ORDER ITEMS ")
                    #print(i)
                    i.name=request.POST.get('name')
                    #print("Object Name")
                    #print(obj.name)
                    #print("new name ")
                    #print(i.name)
                    i.save()
            except:
                print("There is no previous order item related with the updated product")

            obj.name=request.POST.get('name')
            obj.category=request.POST.get('category')
            obj.ingredients=request.POST.get('ingredients')
            
            if request.POST.get('deliverable') =='true':
                var1=True
            if request.POST.get('deliverable')=='false':
                var1=False

            obj.deliverable=var1
            ##print(request.POST.get('deliverable'))
            obj.price=request.POST.get('price')
            obj.image=request.POST.get('image')
            obj.save()
        return redirect('restaurantOwnerProfile')

    else : 
        form=UpdateProductForm()
        context={'form':form,'cartItems':cartItems}
        #print("IAM IN GET STATEMENT")
    return render(request,"Main_Templates/update_product.html",context)


def addRestaurantProduct(request):
    cartItems = getCart(request.user)
    context={}
    if request.method=="POST":
        form=CreateProductForm(request.POST)
        if form.is_valid():
            restaurant=Restaurant.objects.get(owner=request.user)
            name=request.POST.get("name")
            category=request.POST.get("category")
            ingredients=request.POST.get("ingredients")
            if request.POST.get("deliverable")=='true':
                var1=True
            if request.POST.get("deliverable")=='false':
                var1=False

            deliverable= var1
            price=request.POST.get("price")
            image=request.POST.get("image")
        
        
        
        Product.objects.create(name=name,category=category,restaurant=restaurant,ingredients=ingredients,deliverable=deliverable,price=price,image=image)
    
    else:
        form=CreateProductForm()
        context={'form':form,'cartItems':cartItems}
        return render(request,'Main_Templates/create_product.html',context)

    return redirect('restaurantOwnerProfile')

def updateRestaurantOrder(request):
    context={}

    #print("This one : " + request.GET['item_id'])
    str=request.GET['item_id']

    lst=str.split(',')
    #print("Form 1 " )
    #print(lst)
    lst2=[]
    for i in lst:
        if ("," in i) or ( "]" in i ) or ( "[" in i ) or ("'" in i) or (" " in i):
            #print("hi")
            i1=i.replace(",","")
            i2=i1.replace("]","")
            i3=i2.replace("[","")
            i4=i3.replace("'","")
            

            lst2.append(i4)
        else:
            lst2.append(i)


    #print(lst2)
    #print(lst2[0])
    #print(lst2[1])

    #print(lst2[0].find(':'))
    #print(int(lst2[0][int(lst2[0].find(':')+1):]))

    
    obj=Order.objects.get(id=int(lst2[0][int(lst2[0].find(':')+1):]))
    print(obj.order_done)
    
    print(obj)
    if obj.order_done == True:
        print("Section1")
        obj.order_done=False
        obj.save()

    else:
        print("Section2")
        obj.order_done=True
        obj.save()

    print(obj.order_done)
    return redirect('restaurantOwnerProfile')


def get_product_queryset(query=None):
    queryset=[]
    queries = query.split(" ")
    for q in queries:
        product=Product.objects.filter(
            Q(name__icontains=q)
            ).distinct()

        for p in product:
            queryset.append(p)
    return list(set(queryset))


def contactus(request):
    
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ['cmse473project@gmail.com'], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(request,"Your email is sent properly")
            return render(request,'Main_Templates/success.html')
    return render(request, "Main_Templates/contactus.html", {'form': form})


def score_of_reviewed_products_list(request):
    context={}

    all_reviews=Reviews.objects.all()
    #print("ALLL ")
    #print(all_reviews)
    #print("PRINT IND ")
    #print(all_reviews[0])

    reviews=[]
    for i in all_reviews:
        reviews.append(i)

    #print("REVIEWS")
    #print(reviews)

    review_score=[]

    for i in reviews:
        prod=i.product
        #print(prod)

        speed=i.speed_rating
        service=i.service_rating
        quality=i.food_quality_rating

        food_average=(int(speed)+int(service)+int(quality))/3

        review_score.append([prod,food_average])

    #print(review_score)

    all_products=Product.objects.all()
    #print(all_products)



    k=[]
    for i in range(len(review_score)):
        grouping=[i]
        for j in range(len(review_score)):
            if i==j  :
                continue
            if review_score[i][0] == review_score[j][0]:
                grouping.append(j)

        if grouping in k :
            continue
        else:
            k.append(grouping)

    for i in range(len(k)):
        k[i]=list(set(k[i]))
        k[i].sort


    #print("K IS ")
    #print(k)

    uniqe_k = set(map(tuple, k))

    #print(uniqe_k)

    #untill now I grouped reviews for the same product
    #now calculate the average in each group for each product
    #print("Same review indices ")
    #print(list(uniqe_k))
    k=list(uniqe_k)
    sum=0
    prod_avg=0
    all_prod_avgs=[]
    for i in k:
    #   print(i)

        for j in range(len((i))):
        #    print("j",j)
            x=list(review_score[i[j]])
            sum=sum+x[1]
        #   print("X")
        #   print(x[1])
        #   print("REVIEW SCORE ")
        #   print(list(review_score[i[j]]))
        #   print("SUM")
        #   print(sum)
        prod_avg=sum/(j+1)
        #   print("prod_avg")
        #   print(prod_avg)
        all_prod_avgs.append([review_score[i[j]][0],prod_avg])
        sum=0

    print(all_prod_avgs)

    return all_prod_avgs

def makeProductDiscount(request):
    context={}
    if request.method=="POST":
        #print("I AM IN POST STATEMENT")
        form=DiscountForm(data=request.POST)
        if form.is_valid():

            #get selected items product ids
            selected_items=[]
            for i in form.cleaned_data['product_list']:
                selected_items.append(i)

            print("SELECTED ITEMS : ")
            print(selected_items)
            discount_rate=request.POST.get('discount')
            print("DISCOUNT RATE: ")
            print(discount_rate)
        
            prod_lst=[]
            for i in selected_items:
                prod_lst.append(Product.objects.get(id=int(i)))

            print("PRODUCT OBJECTS")
            print(prod_lst)

        #for each product selected calculate discount and save the previus price for deletion of discount

            for i in range(len(prod_lst)):
                previous_price=prod_lst[i].price
                new_price=previous_price-(previous_price*(int(discount_rate)/100))

                prod_lst[i].price=new_price
                prod_lst[i].save()

                obj=Discount_History.objects.create(restaurant=request.user,product=prod_lst[i],discount_rate=discount_rate,previous_price=previous_price)
                obj.save()

        return redirect('restaurantOwnerProfile')

    else : 
        form=DiscountForm()
        #product=Product.objects.filter(restaurant=Restaurant.objects.filter(owner=request.user)[0]) 
        context={'form':form}
        #print("IAM IN GET STATEMENT")
    return render(request,"Main_Templates/discount.html",context)

def removeProductDiscount(request):

    if request.method=="POST" :
        form=RemoveDiscountForm(data=request.POST)
        if form.is_valid():
            selected_items=[]
            for i in form.cleaned_data['discount_list']:
                selected_items.append(i)

        print("SELECTED ITEMS : ")
        print(selected_items)

        discount_lst=[]
        for i in selected_items:
            discount_lst.append(Discount_History.objects.get(id=int(i)))

        #selected discount objects:
        print("DISCOUNT OBJECTS")
        print(discount_lst)

        for i in range(len(discount_lst)):
            restore_price=discount_lst[i].previous_price
            product_id=discount_lst[i].product.id

            prod_obj=Product.objects.get(id=product_id)
            prod_obj.price=restore_price
            prod_obj.save()

            discount_lst[i].delete()


        return redirect('restaurantOwnerProfile')

    else : 
        form=RemoveDiscountForm()
        #product=Product.objects.filter(restaurant=Restaurant.objects.filter(owner=request.user)[0]) 
        context={'form':form}
        #print("IAM IN GET STATEMENT")
        return render(request,"Main_Templates/remove_discount.html",context)


def category_division(request):

    all_prod=Product.objects.all()
    all_categories=[]

    for i in all_prod:
        category=i.category

        if category in all_categories:
            continue
        else:
            all_categories.append(category)

    print(all_categories)
    return all_categories


def category_based_display_items(request):
    context={}

    all_categories=[]
    all_categories=category_division(request)

    category_name=request.GET['category_name']
    print(category_name)

    all_products=Product.objects.filter(category=category_name)

    context['products']=all_products
    context['all_categories']=all_categories
    context['cartItems']=getCart(request.user)

    return render(request,'Main_Templates/category_based_display_items.html',context)

