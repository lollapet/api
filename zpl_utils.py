def gerar_zpl_ifood(order):
    zpl = """
^XA
^FO50,50^A0N,40,40^FDTeste ZPL^FS
^FO50,100^A0N,30,30^FDSucesso!^FS
^XZ
"""
    return zpl