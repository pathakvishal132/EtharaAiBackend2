from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from customers.models import Customer
from products.models import Product


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(customer_id, items_data):
        customer = get_object_or_404(Customer, id=customer_id)

        order = Order.objects.create(
            customer=customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal('0.00')
        )

        total = Decimal('0.00')
        order_items = []

        for item in items_data:
            product_id = item['product_id']
            quantity = item['quantity']

            product = get_object_or_404(Product, id=product_id)

            if product.quantity_in_stock < quantity:
                raise ValueError(
                    f"Insufficient stock for product '{product.name}'. "
                    f"Available: {product.quantity_in_stock}, Requested: {quantity}"
                )

            unit_price = product.price
            line_total = unit_price * quantity
            total += line_total

            product.quantity_in_stock -= quantity
            product.save()

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )
            )

        OrderItem.objects.bulk_create(order_items)
        order.total_amount = total
        order.status = Order.StatusChoices.COMPLETED
        order.save()

        return order
