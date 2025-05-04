from django.urls import path
from student import views

urlpatterns=[
    path('register/',views.StudentAddView.as_view(),name="student-register"),
    path('signin/',views.SigninView.as_view(),name="student-signin"),
    path('index/',views.IndexView.as_view(),name="student-index"),
    path('course/<int:pk>/',views.CourseDetailView.as_view(),name="course-detail"),
    path("course/<int:pk>/add-to-cart/",views.AddCartView.as_view(),name="cart"),
    path('cart/summary/',views.CartSummaryView.as_view(),name='cart-summary'),
    path('cart/<int:pk>/remove',views.CartItemDeleteView.as_view(),name="cart-item-delete"),
    path('checkout/',views.CheckOutView.as_view(),name="checkout"),
    path('mycourses/',views.MyCourseView.as_view(),name="mycourses"),
    path('courses/<int:pk>/watch/',views.LessonDetailView.as_view(),name="lesson-detail"),
    path('payment/verify/',views.PaymentverificationView.as_view(),name="payment-verify"),
    path('signout/',views.LogoutView.as_view(),name="signout"),
    
]  