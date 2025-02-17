from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView ,FormView ,CreateView
from student.forms import StudentCreationForm,LoginForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from instructor.models import Course , Cart ,Order, Lesson , Module
from django.db.models import Sum
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from student.decorators import signin_required
from decouple import config


RZP_KEY_ID=config("RZP_KEY_ID")
RZP_KEY_SECRET=config("RZP_KEY_SECRET")


# Create your views here.

# class StudentAddView(View):
#     def get(self,request,*args,**kwargs):
#         form_instance=StudentCreationForm()
#         return render(request,"student_register.html",{"form":form_instance})
    
#     def post(self,request,*args,**kwargs):
#         form_data=request.POST
#         form_instance=StudentCreationForm(form_data)

#         if form_instance.is_valid():
#             form_instance.instance.role="Student"
#             form_instance.save()
#             return redirect("student-register")
#         else:
#             return render(request,"student_register.html",{"form":form_instance})
        #    or

class StudentAddView(CreateView):
    template_name="student_register.html"
    form_class=StudentCreationForm

    success_url=reverse_lazy("student-signin")

    
    
# class SigninView(View):
#     def get(self,request,*args,**kwargs):
#         form_instance=LoginForm()

#         return render(request,"signin.html",{"form":form_instance})
            # or
class SigninView(FormView):
    template_name="signin.html"
    form_class=LoginForm

    def post(self,request,*args,**kwargs):
        form_data=request.POST
        form_instance=self.form_class(form_data)
        if form_instance.is_valid():
            data=form_instance.cleaned_data
            uname=data.get("username")
            pwd=data.get("password")
            user_instance=authenticate(request,username=uname,password=pwd)
        if  user_instance:
            login(request,user_instance)
            print("=================")

            if user_instance.role=="student":
                return redirect("student-index")
            else:
                return render(request,self.template_name,{"form":form_instance})
            

class IndexView(TemplateView):
    template_name="index.html"

@method_decorator(signin_required,name="dispatch")
class IndexView(View):
    def get(self,request,*args,**kwargs):
        all_courses=Course.objects.all()
        purchased_course=Order.objects.filter(student=request.user).values_list("course_objects",flat=True)
        
        return render(request,"index.html",{"courses":all_courses,"purchased_courses":purchased_course})



    
# example        
class MytemplateView(TemplateView): # import TemplateView

    template_name="template_name.html"  # templates can be rendered easily like this way but only template
#  to add form in this method

class FormView(FormView):   # import FormView
    template_name="template_html"     
    form_class=LoginForm

# end example


@method_decorator(signin_required,name="dispatch")
class CourseDetailView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        course_instance=Course.objects.get(id=id)
        return render(request,"course_detail.html",{"course":course_instance})
    
@method_decorator(signin_required,name="dispatch")    
class AddCartView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        course_instance=Course.objects.get(id=id)
        user_instance=request.user
        # Cart.objects.create(course_object=course_instance,user=user_instance) ithil oru preshnam und
        # user same course add to cart koduthalum pinneyum add aakum so
        cart_instance,created=Cart.objects.get_or_create(course_object=course_instance,user=user_instance) 
        # evida course cartil undengi add aakoola , also createdil rand values matre varu True or Fale
        # created=[True|False] 
       
        return redirect("student-index")
    

@method_decorator(signin_required,name="dispatch")
class CartSummaryView(View):
    def get(self,request,*args,**kwargs):

        qs=request.user.basket.all()
        cart_total=qs.values("course_object__price").aggregate(total=Sum("course_object__price")).get("total")
        

        return render(request,"cart-summary.html",{"carts":qs,"basket_total":cart_total})
    
@method_decorator(signin_required,name="dispatch")
class CartItemDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        cart_instance=Cart.objects.get(id=id)

        if cart_instance.user != request.user:
            return redirect("student-index")

        Cart.objects.get(id=id).delete()
        
        return redirect("cart-summary")
    
@method_decorator(signin_required,name="dispatch")   
class CheckOutView(View):
    def get(self,request,*args,**kwargs):
        cart_items=request.user.basket.all()
        order_total=sum([ci.course_object.price for ci in cart_items])

        order_instance=Order.objects.create(student=request.user,total=order_total)

        for ci in cart_items:
            order_instance.course_objects.add(ci.course_object)
            ci.delete()
        
        order_instance.save()

        if order_total>0:

            #authenticate
            client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))
            #create order
            data = { "amount": int(order_total*100), "currency": "INR", "receipt": "order_rcptid_11" }
            payment = client.order.create(data=data)
            rzp_id=payment.get("id")
            order_instance.rzp_order_id=rzp_id
            order_instance.save()
            context={
                "rzp_key_id":RZP_KEY_ID,
                "amount":int(order_total*100),
                "rzp_order_id":rzp_id
            }

            return render(request,"payment.html",context)
        
        elif order_total==0:
            order_instance.is_paid=True
            order_instance.save()

        return redirect("student-index")

@method_decorator(signin_required,name="dispatch")
class MyCourseView(View):
    def get(self,request,*args,**kwargs):
        qs=request.user.purchase.filter(is_paid=True)
        
        return render(request,'mycourse.html',{"order":qs})
    
@method_decorator(signin_required,name="dispatch")
# localhost:8000/student/course/1/watch?module=1&lesson=4
class LessonDetailView(View):
    def get(self,request,*args,**kwargs):
        course_id=kwargs.get("pk")
        course_instance=Course.objects.get(id=course_id)
        purchased_courses=request.user.purchase.filter(is_paid=True).values_list("course_objects",flat=True)
        if course_instance.id not in purchased_courses:
            return redirect("student-index")
        

        # request.GET ={"module":1,"lesson":4}
        if "module" in request.GET:
            module_id=request.GET.get("module")
        else:
            module_id=course_instance.modules.first().id

               

        module_instance=Module.objects.get(id=module_id,course_object=course_instance)
        lesson_id=request.GET.get("lesson") if "lesson" in request.GET else module_instance.lessons.first().id
        lesson_instance=Lesson.objects.get(id=lesson_id,module_object=module_instance)

        return render(request,"lesson_detail.html",{"course":course_instance,"lesson":lesson_instance})


    




@method_decorator([csrf_exempt],name="dispatch")
class PaymentverificationView(View):

    def post(self,request,*args,**kwargs):

        print(request.POST,"+++++++++++++")
        client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

        try:
            client.utility.verify_payment_signature(request.POST)
            print("payment sucsess")
            rzp_order_id=request.POST.get("razorpay_order_id")
            order_instance=Order.objects.get(rzp_order_id=rzp_order_id)
            order_instance.is_paid=True
            order_instance.save()
        except:
            print("payment failed")
        return redirect("student-index")
    
@method_decorator(signin_required,name="dispatch")
class LogoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("student-signin")