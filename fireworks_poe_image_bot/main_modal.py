from fireworks_poe_image_bot.fw_poe_server_bot import FireworksPoeImageServerBot

import fireworks.client

from fastapi_poe import make_app
import os
from modal import Image, Stub, asgi_app
import logging

logging.basicConfig(level=logging.INFO)

bot = FireworksPoeImageServerBot(
    model=os.environ["MODEL"],
    environment=os.environ.get("ENIRONMENT", ""),
    server_version="0.0.1",
    s3_bucket_name=os.environ["S3_BUCKET_NAME"],
)

image = (
    Image.debian_slim()
    .pip_install("fastapi-poe==0.0.23")
    .pip_install("fireworks-ai>=0.6.0")
    .pip_install("boto3")
    .env(
        {
            "FIREWORKS_API_BASE": os.environ.get(
                "FIREWORKS_API_BASE", fireworks.client.base_url
            ),
            "FIREWORKS_API_KEY": os.environ.get(
                "FIREWORKS_API_KEY", fireworks.client.api_key
            ),
            "S3_BUCKET_NAME": os.environ["S3_BUCKET_NAME"],
            "ENVIRONMENT": os.environ.get("ENVIRONMENT", ""),
            "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
            "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
            "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
            "MODEL": os.environ["MODEL"],
        }
    )
)

stub = Stub("fw-poe-image-bot2")


@stub.function(image=image)
@asgi_app()
def fastapi_app():
    app = make_app(bot, allow_without_key=True)
    return app
