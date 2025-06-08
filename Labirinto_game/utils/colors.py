import constants


def to_gray(r, g, b):
    gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
    return (gray, gray, gray)


def cor_com_escala_cinza(r, g, b):
    if not constants.ESCALA_CINZA:
        return (r, g, b)
    else:
        return to_gray(r, g, b)