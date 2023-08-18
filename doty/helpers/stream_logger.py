import logging

def init_stream_logger() -> None:
    logger = logging.getLogger('doty')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    logger.addHandler(ch)
    return
