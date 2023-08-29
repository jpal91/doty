from classes.DotyLogger import DotyLogger

logger = None

def init_dotylogger() -> DotyLogger:
    global logger
    if not logger:
        logger = DotyLogger()
    return logger
