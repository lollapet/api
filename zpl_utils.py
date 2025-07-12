def gerar_zpl_ifood(order):
    order_id = str(order.order_id or "")
    customer_name = str(getattr(order.customer, "name", "") or "")
    order_amount = str(order.order_amount or "")
    zpl = f"""
^XA
^PW800
^LL1200
^FO100,100^A0N,60,60^FDPedido: {order_id}^FS
^FO100,200^A0N,50,50^FDCliente: {customer_name}^FS
^FO100,300^A0N,50,50^FDTotal: R$ {order_amount}^FS
^XZ
"""
    return zpl