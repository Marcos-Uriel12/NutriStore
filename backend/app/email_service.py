import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

logger = logging.getLogger(__name__)


def _build_order_email(pedido, admin: bool = False) -> tuple[str, str, str]:
    """Build email subject and body for an order notification."""
    items_html = "".join(
        f"<tr><td>{i.producto.nombre if hasattr(i, 'producto') and i.producto else f'#{i.producto_id}'}</td>"
        f"<td>{i.cantidad}{'g' if i.unidad_medida.value == 'KG' else 'u'}</td>"
        f"<td>${float(i.precio_unitario):.2f}</td></tr>"
        for i in pedido.items
    )

    entrega = f"{'Envío' if pedido.tipo_entrega.value == 'ENVIO' else 'Retiro'}"
    if pedido.tipo_entrega.value == 'ENVIO' and pedido.zona_envio:
        entrega += f" - {pedido.zona_envio.value}"

    body = f"""
    <h2>Pedido #{pedido.id}</h2>
    <p><strong>Cliente:</strong> {pedido.cliente_nombre}</p>
    <p><strong>Email:</strong> {pedido.cliente_email}</p>
    <p><strong>Teléfono:</strong> {pedido.cliente_telefono}</p>
    <p><strong>Dirección:</strong> {pedido.cliente_direccion}</p>
    <p><strong>Entrega:</strong> {entrega}</p>
    <p><strong>Pago:</strong> {pedido.pago.metodo.value if pedido.pago else '—'}</p>

    <h3>Productos</h3>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
    <tr><th>Producto</th><th>Cant</th><th>Precio</th></tr>
    {items_html}
    <tr><td colspan="2"><strong>Total</strong></td><td><strong>${float(pedido.total):.2f}</strong></td></tr>
    </table>
    """

    if admin:
        subject = f"[NutriStore] Nuevo pedido #{pedido.id} — {pedido.cliente_nombre}"
        to_email = settings.ADMIN_EMAIL
    else:
        subject = f"Tu pedido #{pedido.id} en NutriStore"
        to_email = pedido.cliente_email
        body = f"<p>Hola {pedido.cliente_nombre},</p><p>Gracias por tu compra. Acá están los detalles de tu pedido:</p>{body}"

    return subject, body, to_email


def send_order_email(pedido):
    """Send order confirmation to client and notification to admin.
    
    If SMTP is not configured, logs the email instead.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning("SMTP not configured. Skipping email for pedido #%s", pedido.id)
        logger.info("Would send email to client: %s", pedido.cliente_email)
        logger.info("Would send email to admin: %s", settings.ADMIN_EMAIL)
        return

    for is_admin in (False, True):
        try:
            subject, body, to_email = _build_order_email(pedido, admin=is_admin)
            if not to_email:
                continue

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_USER
            msg["To"] = to_email
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info("Order email sent to %s", to_email)
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, e)
