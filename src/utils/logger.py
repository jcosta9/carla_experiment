import datetime
import logging
import os


def setup_logger(process):
    if not os.path.exists("../files/log/"):
        os.makedirs("../files/log")

    filename="../files/log/log_" + process + "_{:%d%m%Y_%H%M}.log".format(datetime.datetime.now())

    logging.basicConfig(
        format="[%(asctime)s][%(levelname)s] %(message)s",
        level=logging.DEBUG,
        datefmt="%m/%d/%Y %H:%M:%S",
        filename=filename,
    )

    return filename