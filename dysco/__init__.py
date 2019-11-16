from dysco.dysco import Dysco

__version__ = '0.0.8'
__author__ = 'Evan Sangaline <evan@intoli.com>'
__description__ = 'Dysco provides configurable dynamic scoping behavior in Python.'
__all__ = ['Dysco', 'g']

g = Dysco()
