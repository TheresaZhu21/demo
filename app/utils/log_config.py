import os
import logging

def setup_logging(log_dir: str = "logs", log_file: str = "app.log", level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logging.basicConfig(
        filename=log_path,
        filemode='a', # append mode
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )