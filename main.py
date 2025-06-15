from Circle import Circle, CircleParams

# Création d'un cercle avec les paramètres par défaut
circle1 = Circle()

# Création d'un cercle rouge qui tourne
params = CircleParams(
    x=100,
    y=100,
    color=(255, 0, 0),
    is_rotating=True,
    rotation_speed=2.0
)
circle2 = Circle(params)

# Création d'un demi-cercle avec gravité
params = CircleParams(
    x=200,
    y=200,
    color=(0, 255, 0),
    arc_length=180,
    has_gravity=True,
    radius=30
)
circle3 = Circle(params)

# Création d'un cercle rebondissant
params = CircleParams(
    x=300,
    y=300,
    velocity_x=100,
    velocity_y=-200,
    bounce_factor=0.9,
    color=(0, 0, 255)
)
circle4 = Circle(params)