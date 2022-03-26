from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', null=True, blank=True)
    name=models.CharField(max_length=200,null=True)
    email=models.EmailField(max_length=200,null=True)
    phone= models.CharField(max_length=200, null=True)
    date_created=models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name 


class Restaurant(models.Model):

    CITIES=[ 
            ('F','Famagusta'),
            ('N','Nicosia'),
            ('K','Kyrenia'),
            ('L','Lefke'),
            ('G','Guzelyurt')
            ]

    owner = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    name=models.CharField(max_length=200,null=True)
    email=models.EmailField(max_length=200,null=True)
    phone=models.CharField(max_length=200,null=True)
    location=models.CharField(max_length=200,choices=CITIES)


    def __str__(self):
        return self.name
class Product(models.Model):
    CATEGORY= [
                ('Breakfast','Breakfast'),
                ('Pastry','Pastry'),
                ('Toasts','Toasts'),
                ('Chicken Meals','Chicken Meals'),
                ('Burgers','Burgers'),
                ('Meat Meals','Meat Meals'),
                ('Lunch','Lunch'),
                ('Dinner','Dinner'),
                ('Pastas','Pastas'),
                ('Salads','Salads'),
                ('Desserts','Desserts'),
                ('Cold Drinks','Cold Drinks'),
                ('Hot Drinks','Hot Drinks'),
                ('Side Dishes','Side Dishes'),
                ]

    name=models.CharField(max_length=200,null=True)
    category=models.CharField(max_length=200,choices=CATEGORY)
    restaurant=models.ForeignKey(Restaurant,on_delete=models.SET_NULL,null=True,blank=True)
    ingredients=models.TextField()
    deliverable=models.BooleanField(default=True,null=True,blank=True)
    price=models.FloatField()
    image=models.ImageField(null=True,blank=True)

    @property #helps to access as attribute rather than a method
    def imageURL(self):
        #if image does not exist it may give error so we write this func.
        try: 
            url = self.image.url
        except:
            url= ''

        return url

    def __str__(self):
        return self.name


class Reviews(models.Model):

    DIGITS=[
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
    ('9','9'),
    ('10','10'),
        ]

    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    comment=models.TextField()
    speed_rating=models.CharField(max_length=200,choices=DIGITS)
    service_rating=models.CharField(max_length=200,choices=DIGITS)
    food_quality_rating=models.CharField(max_length=200,choices=DIGITS)
    image=models.ImageField(null=True,blank=True)

class Order(models.Model):  #when all orders are selected
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True,blank=True)
    order_date=models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(default=False,null=True,blank=True) #if false= we can add new items to cart, if true add items to another cart
    transaction_id=models.CharField(max_length=200,null=True)
    order_done=models.BooleanField(default=False,null=True,blank=True)
    @property
    def get_cart_total(self):
        orderitems= self.orderitem_set.all() #finds this classes child
        total= sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems= self.orderitem_set.all() #finds this classes child
        total = sum([item.quantity for item in orderitems])
        return total
    
    
    @property
    def shipping(self): #can we deliver the selected product ?
        shipping=False
        orderitems=self.orderitem_set.all() #its child objects
        for i in orderitems:
            if i.product.deliverable == True:
                shipping =True
        return shipping
    


    def __str__(self):
        return str(self.id)

#single order may have multiple order items

class OrderItem(models.Model): #individual order items
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    quantity=models.IntegerField(default=0,null=True,blank=True)
    date_added=models.DateTimeField(auto_now_add=True)


    @property
    def get_total(self):
       total = self.product.price * self.quantity
       return total
    

    def __str__(self):
        return self.product.name + ' for Order : ' + str(self.order)

class Shipping(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    address=models.CharField(max_length=200,null=False)
    city=models.CharField(max_length=200,null=False)
    state=models.CharField(max_length=200,null=False)
    zipcode=models.CharField(max_length=200,null=False)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Discount_History(models.Model):
    restaurant = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    date_created=models.DateTimeField(auto_now_add=True)
    discount_rate=models.IntegerField()
    previous_price=models.IntegerField(null=True,blank=True)
