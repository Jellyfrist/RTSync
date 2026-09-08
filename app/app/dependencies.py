from collections.abc import Generator


def get_repository() -> Generator[None, None, None]:
    """จุดต่อ dependency สำหรับ repository จริงในอนาคต"""

    yield None
