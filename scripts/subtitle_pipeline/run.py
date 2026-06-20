import argparse
import datetime
import time

from app.main_v2 import main as main_v2

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-mode",
        "--mode",
        choices=("single", "batch"),
        default="batch",
        help="Translation mode to use.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    start_time = time.perf_counter()
    main_v2(translation_mode=args.mode)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    readable_time = str(datetime.timedelta(seconds=int(elapsed_time)))
    print(f"Main 函数耗时: {readable_time}")
