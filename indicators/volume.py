def get_volume_signal(volume_series):

    latest_volume = volume_series.iloc[-1]

    avg_volume = volume_series.tail(20).mean()

    if latest_volume > avg_volume * 1.2:
        return "high"

    elif latest_volume < avg_volume * 0.8:
        return "low"

    return "normal"