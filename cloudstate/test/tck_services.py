"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import sys
from logging import getLogger

from cloudstate.test.actiondemo.test_actiondemo import evaluate_ActionDemo_server
from cloudstate.test.run_test_server import run_test_server
from cloudstate.test.shoppingcart.test_shoppingcart import evaluate_shoppingcart_server

logger = getLogger()

if __name__ == "__main__":
    if len(sys.argv) < 1 or sys.argv[1] == "server":
        logger.info("starting server")

        run_test_server(
            "shoppingcart" in sys.argv, "ActionDemo" in sys.argv, port=8080
        ).wait_for_termination()
    elif sys.argv[1] == "client":
        assert "server_host" in sys.argv
        server = sys.argv[sys.argv.index("server_host") + 1]
        if "server_port" in sys.argv:
            server_port = sys.argv[sys.argv.index("server_port") + 1]
        else:
            server_port = 9000

        if "shoppingcart" in sys.argv:
            evaluate_shoppingcart_server(server, server_port)
        if "ActionDemo" in sys.argv:
            evaluate_ActionDemo_server(server, server_port)
    else:
        raise Exception("please specify client or server.")
