FROM python:3.8.0-slim

COPY . /app
WORKDIR /app
RUN pip install --user -r requirements.txt && \
    pip install wheel && \
    python setup.py bdist_wheel && \
    pip install dist/cloudstate-0.5.0-py3-none-any.whl

ENTRYPOINT python shopping_cart.py