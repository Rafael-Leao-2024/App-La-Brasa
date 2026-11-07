# utils.py
import math

# COLOQUE AQUI AS COORDENADAS REAIS DA SUA LANCHONETE
LAT_LOJA = -8.1324223
LNG_LOJA = -34.9349187

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Fórmula de Haversine para calcular distância em KM
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calcular_taxa_entrega(lat_cliente, lng_cliente):
    if not lat_cliente or not lng_cliente:
        return 5.00 # Taxa padrão de segurança se não enviar localização
    
    distancia = calcular_distancia(LAT_LOJA, LNG_LOJA, lat_cliente, lng_cliente)
    print(f"Distância calculada: {distancia} km")  # Debugging line
    
    # Regras de negócio da taxa
    if distancia <= 3.0:
        return 3.00
    elif distancia <= 6.0:
        return 5.00
    elif distancia <= 10.0:
        return 10.00
    else:
        return -1 # Fora da área de entrega