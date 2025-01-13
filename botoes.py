from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior


class ImageButton(ButtonBehavior, Image): #botao de imagem
    pass


class LabelButton(ButtonBehavior, Label): #botao de texto
    pass