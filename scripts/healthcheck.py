import http.client
import sys
from argparse import ArgumentParser


def health_check(
    host: str = "localhost", port: int = 8080, use_https: bool = True
) -> None:
    """Health check for the application."""
    conn_class = (
        http.client.HTTPSConnection if use_https else http.client.HTTPConnection
    )
    conn = conn_class(host=host, port=port)
    try:
        conn.request("GET", "/api/v1/health")
        response = conn.getresponse()
        print(f"Received status code: {response.status} from {host}:{port}")
        if response.status == 200:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--host", type=str, default="localhost")
    argparser.add_argument("--port", type=int, default=8080)
    argparser.add_argument(
        "--https", action="store_true", help="Use HTTPS for health check"
    )
    args = argparser.parse_args()

    health_check(host=args.host, port=args.port, use_https=args.https)
