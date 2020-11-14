"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import logging
import time

import grpc
import pytest

from cloudstate.test.actiondemo.actiondemo2_pb2 import FunctionRequest2
from cloudstate.test.actiondemo.actiondemo2_pb2_grpc import ActionDemo2Stub
from cloudstate.test.actiondemo.actiondemo_pb2 import (
    AddToSum,
    FunctionRequest,
    FunctionResponse,
)
from cloudstate.test.actiondemo.actiondemo_pb2_grpc import ActionDemoStub
from cloudstate.test.run_test_server import run_test_server

logger = logging.getLogger()


def evaluate_ActionDemo_server(host: str, port: int):
    server_hostport = f"{host}:{port}"
    logger.info(f"connecting on {server_hostport}")
    channel = grpc.insecure_channel(server_hostport)

    logger.info("channel established.")
    stub = ActionDemoStub(channel)
    request_oof = FunctionRequest(foo="oof")
    response = stub.ReverseString(request_oof)
    logger.info(f"resp: {response}")
    assert response.bar == "foo"

    stub2 = ActionDemo2Stub(channel)
    response = stub2.ReverseString2(request_oof)
    logger.info(f"resp: {response}")
    assert response.bar == "foo!"

    request_boom2 = FunctionRequest2(foo="boom")
    with pytest.raises(Exception):
        stub2.ReverseString2(request_boom2)
    logger.info("passed.")

    request_boom = FunctionRequest2(foo="boom")
    requests = iter(
        [FunctionRequest(foo=str(i) + ".") for i in range(10)]
        + [request_boom]
        + [FunctionRequest(foo=str(i) + "X") for i in range(10)]
    )
    response = stub.ReverseStrings(requests)
    last_response = None
    with pytest.raises(Exception):
        for r in response:
            last_response = r
            logger.info(f"streamed output: {r}")
    assert last_response.bar == ".9"

    numbers_to_sum = iter([AddToSum(quantity=x) for x in [1, 2, 3, 4, 5, 6, 7, 8, 9]])
    sum = stub.SumStream(numbers_to_sum)
    logger.info(sum)
    assert sum.total == 45

    numbers_to_fail_summing = iter(
        AddToSum(quantity=x) for x in [1, 2, 3, 4, -1, 6, 7, 8, 9]
    )

    with pytest.raises(Exception):
        stub.SumStream(numbers_to_fail_summing)

    resp = list(stub.SillyLetterStream(FunctionRequest(foo="wow")))
    assert resp == [
        FunctionResponse(bar="w!!"),
        FunctionResponse(bar="o!!"),
        FunctionResponse(bar="w!!"),
    ]

    with pytest.raises(Exception):
        resp = stub.SillyLetterStream(FunctionRequest(foo="nope"))
        for i in resp:
            logger.info(i)


def test_ActionDemo():
    server_thread = run_test_server(port=8080)
    import docker

    client = docker.from_env()
    client.images.pull("cloudstateio/cloudstate-proxy-dev-mode:latest")
    container = client.containers.run(
        "cloudstateio/cloudstate-proxy-dev-mode:latest",
        environment={"USER_FUNCTION_HOST": "127.0.0.1", "USER_FUNCTION_PORT": "8080"},
        detach=True,
        ports={"9000/tcp": 9000},
        network="host",
    )
    logger.info(f"status {container.status}")
    try:
        time.sleep(15)
        evaluate_ActionDemo_server("127.0.0.1", 9000)
    except Exception as e:
        raise e
    finally:
        server_thread.stop(None)
        logger.info(container.logs())
        container.stop()
