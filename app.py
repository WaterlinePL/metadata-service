from flask import Flask, request, jsonify
from api import api
import logging
import os
import config


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger()

app = Flask(__name__)

def create_app():
    logger.info(f'Starting app in {config.APP_ENV} environment and host {config.host}')
    app = Flask(__name__)
    app.config.from_object('config')
    api.init_app(app)


    @app.route("/")
    def health():
        logger.log(msg="Health",level=20)
        return 'Ok'

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5001,host=config.host, debug=True)