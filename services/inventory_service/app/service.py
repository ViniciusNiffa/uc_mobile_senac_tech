from .database import get_connection

# O inventory cuida só de saldo de estoque, e essas operações são curtas o
# bastante pra viverem direto no routes.py. Consulta de produto é com o catalog.