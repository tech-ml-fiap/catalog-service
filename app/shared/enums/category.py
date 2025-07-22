from enum import Enum as PyEnum


class Category(str, PyEnum):
    LUNCH = "Lanche"
    SIDES = "Acompanhamento"
    DRINK = "Bebida"
    DESSERT = "Sobremesa"