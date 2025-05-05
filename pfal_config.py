# Parámetros óptimos para cada cultivo (empezamos con lechuga)
CULTIVOS = {
    "lechuga": {
        "nombre": "Lactuca sativa",
        "fotoperiodo": (12, 16),       # Horas de luz
        "temperatura_optima": (16, 18), # °C
        "humedad_optima": (50, 70),     # %
        "co2_optimo": (1200, 1500),     # ppm
        "ph_optimo": (6.5, 7.0),        # pH
        "espectro_optimo": {
            "alta_intensidad": {"B435": 1.25, "R663": 1.0},
            "baja_intensidad": {"B435": 1.0, "R663": 1.0, "G520": 0.1}
        }
    }
}