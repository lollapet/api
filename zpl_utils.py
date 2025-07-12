def gerar_zpl_ifood(order):
    print(order)
    # Garante que todos os campos são string e não None
    order_id = str(getattr(order, "order_id", "") or "")
    customer_name = str(getattr(getattr(order, "customer", None), "name", "") or "")
    order_amount = str(getattr(order, "order_amount", "") or "")

    zpl = f"""
^XA
^FO50,50^A0N,40,40^FDPedido: {order_id}^FS
^FO50,100^A0N,30,30^FDCliente: {customer_name}^FS
^FO50,150^A0N,30,30^FDTotal: R$ {order_amount}^FS
^XZ
"""
    return zpl