import ctypes
import sys

# Verifica se o sistema operacional é macOS
if sys.platform != 'darwin':
    print("Este exemplo é específico para macOS.")
    exit()

libc = ctypes.CDLL(None)
libc.getpid.restype = ctypes.c_int

# Obtém o PID do processo atual usando a função getpid()
pid = libc.getpid()

print("ID do processo atual:", pid)
