"""Minimal .env file loader for MicroPython."""


def load_dotenv(path=".env"):
    """Read a .env file and return a dict of key=value pairs.

    Supports:
      - Lines with KEY = VALUE or KEY=VALUE
      - Optional double or single quotes around values
      - Comments (lines starting with #) and blank lines
    """
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Strip matching quotes
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                env[key] = value
    except OSError:
        pass  # .env file not found — use defaults
    return env
