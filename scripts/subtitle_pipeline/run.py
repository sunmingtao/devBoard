from app.main import main
import time
import datetime

if __name__ == "__main__":
    
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    readable_time = str(datetime.timedelta(seconds=int(elapsed_time)))
    print(f"Main 函数耗时: {readable_time}")