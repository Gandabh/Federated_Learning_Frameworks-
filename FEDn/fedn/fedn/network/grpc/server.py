from concurrent import futures

import grpc

import fedn.network.grpc.fedn_pb2_grpc as rpc
from fedn.common.log_config import (logger, set_log_level_from_string,
                                    set_log_stream)


class Server:
    """ Class for configuring and launching the gRPC server."""

    def __init__(self, servicer, modelservicer, config):

        set_log_level_from_string(config.get('verbosity', "INFO"))
        set_log_stream(config.get('logfile', None))

        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=350))
        self.certificate = None

        if isinstance(servicer, rpc.CombinerServicer):
            rpc.add_CombinerServicer_to_server(servicer, self.server)
        if isinstance(servicer, rpc.ConnectorServicer):
            rpc.add_ConnectorServicer_to_server(servicer, self.server)
        if isinstance(servicer, rpc.ReducerServicer):
            rpc.add_ReducerServicer_to_server(servicer, self.server)
        if isinstance(modelservicer, rpc.ModelServiceServicer):
            rpc.add_ModelServiceServicer_to_server(modelservicer, self.server)
        if isinstance(servicer, rpc.CombinerServicer):
            rpc.add_ControlServicer_to_server(servicer, self.server)

        if config['secure']:
            logger.info(f'Creating secure gRPCS server using certificate: {config["certificate"]}')
            server_credentials = grpc.ssl_server_credentials(
                ((config['key'], config['certificate'],),))
            self.server.add_secure_port(
                '[::]:' + str(config['port']), server_credentials)
        else:
            logger.info("Creating insecure gRPC server")
            self.server.add_insecure_port('[::]:' + str(config['port']))

    def start(self):
        """ Start the gRPC server."""
        logger.info("gRPC Server started")
        self.server.start()

    def stop(self):
        """ Stop the gRPC server."""
        logger.info("gRPC Server stopped")
        self.server.stop(0)
