"""
Implementación clásica del cifrado Trivium en Python.

Este script implementa el algoritmo de cifrado de flujo Trivium, 
siguiendo la especificación original propuesta por 
Christophe De Cannière y Bart Preneel.

Autor: Pablo de la Fuente Rodríguez
Fecha: Junio 2025
Universidad de La Laguna – Escuela Superior de Ingeniería y Tecnología  
Trabajo de Fin de Grado en Ingeniería Informática
Repositorio: https://github.com/PablodlFR/trivium-cipher-tfg.git
"""
from bitstring import BitArray

def key_iv_setup(key, iv):
  """
  Configura el estado inicial del cifrado utilizando la clave y el vector de inicialización.

  Args:
    key (list[int]): lista de 80 bits que representan la clave.
    iv (list[int]): lista de 80 bits que representan el vector de inicialización.

  Returns:
    state (list[int]): lista de 80 bits que representa el estado inicial del cifrado.
  """
  state = [0] * 288

  for i in range(80):
    state[i] = key[i]

  for i in range(80):
    state[93 + i] = iv[i]

  for i in range(3):
    state[285 + i] = 1

  for i in range(4 * 288):
    t1 = state[65] ^ (state[90] & state[91]) ^ state[92] ^ state[170]
    t2 = state[161] ^ (state[174] & state[175]) ^ state[176] ^ state[263]
    t3 = state[242] ^ (state[285] & state[286]) ^ state[287] ^ state[68]

    state = [t3] + state[:92] + [t1] + state[93:176] + [t2] + state[177:287]

  return state

def key_stream_generation(state, N):
  """
  Genera el Keystream usando el estado inicial. Se le pasa N para obtener solo la cantidad necesaria de bits para cifrar.

  Args:
    state (list[int]): lista de 80 bits que representan el estado inicial.
    N (int): número de bits necesarios para cifrar el texto.

  Returns:
    keystream (list[int]): lista de bits que conforman el flujo de clave.
  """
  keystream = [0] * N
  for i in range(N):
    t1 = state[65] ^ state[92]
    t2 = state[161] ^ state[176]
    t3 = state[242] ^ state[287]

    z = t1 ^ t2 ^ t3
    keystream[i] = z

    t1 = t1 ^ (state[90] & state[91]) ^ state[170]
    t2 = t2 ^ (state[174] & state[175]) ^ state[263]
    t3 = t3 ^ (state[285] & state[286]) ^ state[68]

    state = [t3] + state[:92] + [t1] + state[93:176] + [t2] + state[177:287]
  
  return keystream

# -------------------------------------

# Clave e IV
key = BitArray("0x0123456789ABCDEF1234")
iv = BitArray("0x0123456789ABCDEF1234")

n = 256  # Nº de bits del flujo de clave

# Inicializar Trivium
state = key_iv_setup(key, iv)
keystream = BitArray(key_stream_generation(state, n))

print(f"Flujo de clave:", keystream.hex.upper())