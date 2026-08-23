###########
# Multitasking:
'''
- Multitasking is a facility to execute multiple jobs
concurrently(by using the concept of time sharing).
'''

# Advantages of Multitasking:
'''
- a) It improves the efficiency of application.
- b) Here the jobs run independently without affecting
others jobs.
'''

# Types of Multitasking:
'''
- 1) Process Based Multitasking (Multiprocessing)
- 2) Thread based Multitasking (Multithreading)
'''

# Process and Multiprocessing:
'''
- Program in execution is called process.
- Ex.
    - Running a browser is a process
    - Running a video game is a process
- Any process has 3 basic components:
    - An executable program.
    - Associated data needed by the program (variables,
    work space, buffers, etc.)
    - Execution context of the program(state of process)
- For each process resources are allocated independently.

- Concurrent execution of multiple process is called
multiprocessing.
- Multiprocessing is OS level concept.
- Ex. of multiprocessing is simultaneously operating
vlc,ms-word, bowser.
'''

# Thread and Multithreading:
'''
- Independent part of a process is called a thread.
- Threads allows the program to run tasks in parallel.
- - Ex. While playing a video game, system has to handle
multiple tasks 
    - handle graphics
    - handle user interface
    - handle networking (when playing multiplayer)

- All these tasks are performed simultaneously in parallel
and also remaning responsive all the times using
multithreading.
- The thread provide sequence of control flow.
- The thread exist entirely inside process and share
it's(process) resources.
- Every process has at least one thread, i.e, the process
itself.

- Concurrent execution of multiple threads is called
multithreading i.e, a process can start multiple threads.
- The operating system executes these threads like
parallel "processes". 
- On a single processor machine, this parallelism is
achieved by thread scheduling or timeslicing.
- Multithreading is a program level concept.
- Ex. multiple tabs opened in browser is example of
multithreading.

- Fig.
- A single process may have multiple threads of execution
to perform multiple concurrent individual task on a
shared data.
    - Here this process is having three threads and
    inside each threads we have code(independent of each
    other). 
    - Also we have global variable, each thread will be
    able to share those global variables and in addition
    each thread can have its own local variables and its
    own control flow to work with those local and global
    variables.
'''

#############
# Types of Thread:
'''
- 1.Kernel thread: These threads are the part of operating
system.
- 2.User thread: User space threads are not implemented
in kernel. The user space thread can be seen as an
extension of function concepts in programming languages. 
    - i.e, user-space thread is similar to a function call,
    but there are differences to regular functions,
    especially the return behaviour.
'''

###########
# Independent task in a process:
'''
from time import time_ns
print('Check for even-odd',time_ns())
num = int(input("Enter no.: "))
if(num % 2 == 0):
    print(num,"is Even")
else:
    print(num,"is Odd")
print('Check for even-odd Done',time_ns())

print('Open a file to write',time_ns())
f1 = open('File2Save/msg.txt', 'w')
f1.write('Hello\n')
print('Writing done',time_ns())
f1.close()

print('Open a file to read',time_ns())
f2 = open('File2Save/msg.txt')
data= f2.read()
print('Reading done',time_ns())
f2.close()

print(data)
print('File handling done',time_ns())
'''

###########
# Multithreading in python:
'''
- Modules which support the usage of threads in Python
is threading.
- In Python, the functionality of a thread is represented
by Thread class. 

- In python, object of Thread or thread,
    - thread share the memory and the state of the process
    - i.e, thread share the code or instructions and the
    values of its variables.
    - During it's lifetime, a thread can be in various
    state.
'''

##########
# __main__ process executed as MainThread
'''
from threading import current_thread, activeCount
print("Hello")
print('Current thread:', current_thread())
print('Current thread name:', current_thread().getName())
print('Total thread in program: ', activeCount())
'''

##########
# Implement multithreading
'''
from time import time_ns
from threading import Thread, current_thread, activeCount
def even_odd(num):
    print('Check for even-odd',time_ns())
    if(num % 2 == 0):
        print(num,"is Even")
    else:
        print(num,"is Odd")
    print('Check for even-odd Done',time_ns())
        
def file_handling():
    print('Open a file to write',time_ns())
    f1 = open('File2Save/msg.txt', 'w')
    f1.write('Hello\n')
    print('Writing done',time_ns())
    f1.close()

    print('Open a file to read',time_ns())
    f2 = open('File2Save/msg.txt')
    data= f2.read()
    print('Reading done',time_ns())
    f2.close()

    print(data)
    print('File handling done',time_ns())

if __name__=='__main__':
    print('Main thread start',time_ns())
    num=int(input("Enter a no.: "))
    t1=Thread(target=even_odd, args=(num,), name='Th1')
    t2=Thread(target=file_handling, name='Th2')

    print('Even-odd thread triggered',time_ns())
    t1.start()
    print('File-Handling thread triggered',time_ns())
    t2.start()
    print('Total thread in program:', activeCount())
    print('Main thread completed',time_ns())
'''

# Detailed Threads tracing
'''
from time import time_ns
from threading import Thread, current_thread, activeCount
def even_odd(num):
    print('Check for even-odd',time_ns(), current_thread().getName())
    if(num % 2 == 0):
        print(num,"is Even")
    else:
        print(num,"is Odd")
    print('Check for even-odd Done',time_ns(), current_thread().getName())
        
def file_handling():
    print('Open a file to write',time_ns(), current_thread().getName())
    f1 = open('File2Save/msg.txt', 'w')
    f1.write('Hello\n')
    print('Writing done',time_ns(), current_thread().getName())
    f1.close()

    print('Open a file to read',time_ns(), current_thread().getName())
    f2 = open('File2Save/msg.txt')
    data= f2.read()
    print('Reading done',time_ns(), current_thread().getName())
    f2.close()

    print(data)
    print('File handling done',time_ns(), current_thread().getName())

if __name__=='__main__':
    print('Main thread start',time_ns(), current_thread().getName())
    num=int(input("Enter a no.: "))
    t1=Thread(target=even_odd, args=(num,), name='Th1')
    t2=Thread(target=file_handling, name='Th2')

    print('Even-odd thread triggered',time_ns(), current_thread().getName())
    t1.start()
    print('File-Handling thread triggered',time_ns(), current_thread().getName())
    t2.start()
    
    print('Total thread in program:', activeCount())
    print('Main thread completed',time_ns(), current_thread().getName())
'''
