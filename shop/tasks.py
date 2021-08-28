from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Order


@shared_task
def send_invoice(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    order = Order.objects.get(id=order_id)

    # create invoice e-mail
    subject = f'Ecommerce - EE Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject,
                         message,
                         settings.EMAIL_HOST_USER,
                         [order.orderdetails.email])
    # generate PDF
    html = render_to_string('shop/invoice.html', {'order': order})
    out = BytesIO()
    weasyprint.HTML(string=html).write_pdf(
        out,
        stylesheets=[
            weasyprint.CSS(
                settings.BASE_DIR / 'static/mystatic/css/invoice.css'
            )
        ]
    )
    # attach PDF file
    email.attach(f'order_{order.id}.pdf',
                 out.getvalue(),
                 'application/pdf')
    # send e-mail
    email.send()