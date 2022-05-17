from concurrent.futures import ThreadPoolExecutor
import time

def foo():
    time.sleep(3)
    print("this")
def foo2():
    time.sleep(1)
    print("mmm")
    time.sleep(1)
    print("mmmmmm")
    time.sleep(1)
    print("mmmmmmmm")



with ThreadPoolExecutor(max_workers=3) as executor:

    executor.submit(foo)
    executor.submit(foo2)



