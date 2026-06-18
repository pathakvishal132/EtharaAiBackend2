from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from products.models import Product
from customers.models import Customer
from orders.models import Order


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_products = Product.objects.count()
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        low_stock_products = Product.objects.filter(quantity_in_stock__lt=10).count()

        data = {
            'total_products': total_products,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'low_stock_products': low_stock_products,
        }
        return Response(data)
