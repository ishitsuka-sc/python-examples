import argparse
from . import hello

def main():
    """
    CLI エントリポイント
    """
    parser = argparse.ArgumentParser(
        prog="mypkg",
        description="mypackage - A simple greeting tool with YAML config."
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="Name to greet (optional)"
    )

    args = parser.parse_args()

    try:
        message = hello(args.name)
        print(message)
    except Exception as e:
        print(f"ERROR: {e}")
