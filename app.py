from quantumlab.database import initialize_database
from quantumlab.ui.layout import render_app


def main() -> None:
    initialize_database()
    render_app()


if __name__ == "__main__":
    main()
