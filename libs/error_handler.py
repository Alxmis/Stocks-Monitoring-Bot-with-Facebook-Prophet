from halo import Halo

def raise_warining(msg: str) -> None:
    echo = Halo()
    echo.warn(
        text=msg
    )

def raise_error(msg: str) -> None:
    echo = Halo()
    echo.fail(
        text=msg
    )
    exit()

def raise_info(msg: str) -> None:
    echo = Halo()
    echo.info(
        text=msg
    )