"""Colours (light pastel theme) and layout constants."""
WIDTH, HEIGHT = 1280, 720
FPS = 60

BG_TOP = (255, 241, 250)
BG_BOTTOM = (222, 240, 255)
TEXT = (72, 58, 112)
TEXT_SOFT = (124, 110, 160)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
CARD_BORDER = (226, 214, 246)
SHADOW = (190, 170, 220)
WRONG = (255, 92, 120)
GOOD = (52, 170, 110)
HINT_GLOW = (255, 214, 10)

# card categories: (main, light, dark)
CAT_COLORS = {
    "red": ((255, 143, 120), (255, 222, 212), (206, 88, 70)),
    "blue": ((116, 160, 255), (220, 230, 255), (70, 104, 206)),
    "green": ((86, 200, 140), (214, 246, 228), (40, 150, 96)),
}
RES_COLORS = {"code": CAT_COLORS["red"], "bytes": CAT_COLORS["blue"], "penguins": CAT_COLORS["green"]}

# player sides
PLAYER_TINT = (255, 170, 200)     # pink ice
AI_TINT = (190, 170, 255)         # lavender ice
SKY_TOP = (214, 236, 255)
SKY_BOTTOM = (252, 240, 255)
SNOW = (250, 252, 255)
SNOW_SHADE = (214, 228, 248)

# button colour pairs (face, shadow/edge)
BTN_PINK = ((255, 143, 171), (214, 92, 128))
BTN_BLUE = ((116, 185, 255), (66, 132, 214))
BTN_MINT = ((107, 214, 160), (52, 160, 110))
BTN_YELLOW = ((255, 209, 102), (222, 160, 40))
BTN_PURPLE = ((178, 145, 255), (128, 96, 214))
BTN_ORANGE = ((255, 170, 110), (222, 120, 60))
BTN_GREY = ((214, 206, 232), (170, 158, 200))

TITLE_COLORS = [(255, 112, 150), (255, 160, 70), (240, 190, 30), (80, 200, 120),
                (70, 160, 255), (150, 110, 255), (255, 110, 200)]
CONFETTI = [(255, 112, 150), (255, 190, 70), (110, 214, 160), (100, 180, 255),
            (180, 140, 255), (255, 230, 90), (120, 230, 230)]
