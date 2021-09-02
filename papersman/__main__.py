#-X strict
from . import papersman


# Preload template for strict mode.
papersman.tmpl_loader.load("index.tpl")


def __main__():
    papersman.__main__()


if __name__ == "__main__":
    __main__()
