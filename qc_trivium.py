"""
Implementación cuántica del cifrado Trivium utilizando Qiskit.

Este script implementa el algoritmo de cifrado de flujo Trivium
como un circuito cuántico, siguiendo la descripción presentada
en el artículo:
"Quantum Analysis of Trivium" por Sumanta Chakraborty, SK Hafizul Islam y Anubhab Baksi.

Autor: Pablo de la Fuente Rodríguez
Fecha: Junio 2025
Universidad de La Laguna – Escuela Superior de Ingeniería y Tecnología  
Trabajo de Fin de Grado en Ingeniería Informática
Repositorio: https://github.com/PablodlFR/trivium-cipher-tfg.git
"""
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator
from bitstring import BitArray

def state_update(qc, s, t, a, b, c, d, e, t_index):
  """
  Actualiza los qubits correspondientes a t₀, t₁ y t₂ utilizando ciertos qubits específicos del estado s.

  Args:
    qc (QuantumCircuit): el circuito cuántico sobre el que se trabaja.
    s (QuantumRegister): registro que representa el estado interno del cifrado (288 qubits).
    t (QuantumRegister): registro temporal (3 qubits) para t₀, t₁ y t₂.
    a, b, c, d, e (int): índice de qubits en el registro s.
    t_index (int): índice del registro t donde se guarda el resultado.
  """
  qc.cx(s[a], s[d])                  # CNOT(a, d)
  qc.ccx(s[b], s[c], s[d])           # TOFFOLI(b, c, d)
  qc.cx(s[e], s[d])                  # CNOT(e, d)
  qc.swap(s[d], t[t_index])          # SWAP(d, tᵢ)

def state_shifting(qc, s, a, b, t):
  """
  Realiza un desplazamiento a la derecha sobre una sección del registro s, trasladando todos los qubits entre
  las posiciones a y b una posición a la derecha y copiando el valor del registro t en la posición s[b].

  Args:
    qc (QuantumCircuit): el circuito cuántico sobre el que se trabaja.
    s (QuantumRegister): registro que representa el estado interno del cifrado (288 qubits).
    a (int): índice del último qubit del segmento a desplazar.
    b (int): índice del primer qubit del segmento a desplazar (posición final del nuevo valor).
    t (qubit): qubit temporal (tᵢ) que se insertará en s[b].
  """
  j = a
  while j >= b:
    if j == b:
      qc.swap(s[b], t)
    else:
      qc.swap(s[j], s[j-1])      
    j = j - 1
    
def update_t(qc, s, t, a, b, t_index):
  """
  Calcula tᵢ como la suma XOR entre dos qubits específicos del estado s y guarda el resultado en t[t_index].

  Args:
    qc (QuantumCircuit): el circuito cuántico sobre el que se trabaja.
    s (QuantumRegister): registro que representa el estado interno del cifrado (288 qubits).
    t (QuantumRegister): registro temporal (3 qubits) para t₀, t₁ y t₂.
    a (int): primer índice del qubit involucrado en la operación XOR.
    b (int): segúndo índice del qubit involucrado en la operación XOR.
    t_index (int): índice del registro t donde se guarda el resultado.
  """
  qc.cx(s[a], s[b])
  qc.swap(s[b], t[t_index])

# -------------------------------------

r = 256                             # Número de qubits del flujo de clave
s = QuantumRegister(288, name='s')  # Registro estado de Trivium de 288 qubits
t = QuantumRegister(3, name='t')    # Registros temporales t1, t2, t3
z = QuantumRegister(r, name='z')    # Registro cuántico para el flujo de clave
c = ClassicalRegister(r, name='c')  # Registro clásico para medir el flujo de clave

qc = QuantumCircuit(s, t, z, c)

key = BitArray(hex="0x0123456789abcdef1234")
iv = BitArray(hex="0x0123456789abcdef1234")

# Inicializar key
for i in range(80):
  if key[i]:
    qc.x(s[i])

# Inicializar IV
for i in range(80):
  if iv[i]:
    qc.x(s[i + 93])

# Bits fijos a 1
qc.x(s[285])
qc.x(s[286])
qc.x(s[287])

# Inicialización del estado interno. 4 ciclos (4 * 288 = 1152 rondas)
for _ in range(1152):
  state_update(qc, s, t, 65, 90, 91, 92, 170, 0) 
  state_update(qc, s, t, 161, 174, 175, 176, 263, 1) 
  state_update(qc, s, t, 242, 285, 286, 287, 68, 2) 

  state_shifting(qc, s, 287, 177, t[1])
  state_shifting(qc, s, 176, 93, t[0])
  state_shifting(qc, s, 92, 0, t[2])

# Generador del flujo de clave
for i in range(r):
  update_t(qc, s, t, 65, 92, 0)
  update_t(qc, s, t, 161, 176, 1)
  update_t(qc, s, t, 242, 287, 2)

  qc.cx(t[0], z[i])
  qc.cx(t[1], z[i])
  qc.cx(t[2], z[i])

  qc.ccx(s[90], s[91], t[0])
  qc.cx(s[170], t[0])
  qc.ccx(s[174], s[175], t[1])
  qc.cx(s[263], t[1])
  qc.ccx(s[285], s[286], t[2])
  qc.cx(s[68], t[2])
  
  state_shifting(qc, s, 287, 177, t[1])
  state_shifting(qc, s, 176, 93, t[0])
  state_shifting(qc, s, 92, 0, t[2])

qc.measure(z, c)

# Simulación
simulator = QasmSimulator(method='matrix_product_state')
job = simulator.run(qc, shots=1, memory = True)
result = job.result()
memory = result.get_memory()

# Invertir porque en qiskit, cuando haces una medición, el qubit con índice más bajo aparece a la derecha.
bin_str = memory[0][::-1]
ba = BitArray(bin=bin_str)
hex_str = ba.tobytes().hex().upper()

print("Flujo de clave:", hex_str)