import threading

def print_something():
    something = input()
    print(something)

def print_something_else(something):
    print(something)

t1 = threading.Thread(target=print_something)
t2 = threading.Thread(target=print_something_else, args=("Hi there!",))

t1.start()
t2.start()
t2.join()
t1.join()