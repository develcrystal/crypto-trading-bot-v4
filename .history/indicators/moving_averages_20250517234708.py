import pandas as pd

def simple_moving_average(data, period):
    """
    Berechnet den einfachen gleitenden Durchschnitt.

    :param data: Datenreihe
    :param period: Zeitraum für den gleitenden Durchschnitt
    :return: Einfacher gleitender Durchschnitt
    """
    return data.rolling(window=period).mean()

def exponential_moving_average(data, period):
    """
    Berechnet den exponentiellen gleitenden Durchschnitt.

    :param data: Datenreihe
    :param period: Zeitraum für den gleitenden Durchschnitt
    :return: Exponentieller gleitender Durchschnitt
    """
    return data.ewm(span=period, adjust=False).mean()