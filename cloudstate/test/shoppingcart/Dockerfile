FROM python:3.8.0-slim

COPY ./dist /dist
RUN pip install /dist/cloudstate-0.1.2-py3-none-any.whl

WORKDIR /app
COPY ./shoppingcart ./shoppingcart
ENV PYTHONPATH=/app
ENTRYPOINT python ./shoppingcart/shopping_cart.py