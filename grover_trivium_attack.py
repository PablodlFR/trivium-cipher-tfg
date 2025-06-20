"""
Ataque cuántico al cifrado Trivium usando el algoritmo de Grover.

Este script implementa una simulación de un ataque cuántico al cifrado Trivium mediante
el algoritmo de Grover, con el objetivo de recuperar bits desconocidos de la clave.
La implementación sigue el enfoque descrito en el artículo:
"Quantum Analysis of Trivium" por Sumanta Chakraborty, SK Hafizul Islam y Anubhab Baksi.

Autor: Pablo de la Fuente Rodríguez
Fecha: Junio 2025
Universidad de La Laguna – Escuela Superior de Ingeniería y Tecnología  
Trabajo de Fin de Grado en Ingeniería Informática
Repositorio: https://github.com/PablodlFR/trivium-cipher-tfg.git
"""
import time
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_aer.aerprovider import QasmSimulator
from collections import Counter

backend = QasmSimulator(method='matrix_product_state')

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

def trivium(qc, s, t, rounds, n):
  """
  Implementa el cifrado Trivium en un circuito cuántico.

  Args:
    qc (QuantumCircuit): el circuito cuántico sobre el que se trabaja.
    s (QuantumRegister): registro que representa el estado interno del cifrado (288 qubits).
    t (QuantumRegister): registro temporal (3 qubits) para t₀, t₁ y t₂.
    round (int): número de rondas de inicialización.
    n (int): número de bits del flujo de clave a generar.
  """
  # Inicialización del estado interno
  for _ in range(rounds):
    state_update(qc, s, t, 65, 90, 91, 92, 170, 0)      
    state_update(qc, s, t, 161, 174, 175, 176, 263, 1)  
    state_update(qc, s, t, 242, 285, 286, 287, 68, 2) 

    state_shifting(qc, s, 287, 177, t[1])
    state_shifting(qc, s, 176, 93, t[0])
    state_shifting(qc, s, 92, 0, t[2])

  # Generador del flujo de clave
  for i in range(n):
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

def inv_state_update(qc, s, t, a, b, c, d, e, t_index):
  """
  Versión inversa de la función state_update.
  """
  qc.swap(s[d], t[t_index])          # SWAP(d, tᵢ)
  qc.cx(s[e], s[d])                  # CNOT(e, d)
  qc.ccx(s[b], s[c], s[d])           # TOFFOLI(b, c, d)
  qc.cx(s[a], s[d])                  # CNOT(a, d)

def state_shifting_left(qc, s, a, b, t):
  """
  Igual que state_shifting, pero realiza el desplazamiento hacia la izquierda.
  """
  for j in range(b, a + 1):
    if j == b:
      qc.swap(s[b], t)
    else:
      qc.swap(s[j], s[j - 1])

def inv_update_t(qc, s, t, a, b, t_index):
  """
  Versión inversa de la función update_t.
  """
  qc.swap(s[b], t[t_index])
  qc.cx(s[a], s[b])

def inv_trivium(qc, s, t, rounds, n):
  """
  Versión inversa de la función trivium. 
  """
  # Generador del flujo de clave
  for i in range(n):        
    state_shifting_left(qc, s, 92, 0, t[2])
    state_shifting_left(qc, s, 176, 93, t[0])
    state_shifting_left(qc, s, 287, 177, t[1])        

    qc.cx(s[68], t[2])
    qc.ccx(s[285], s[286], t[2])
    qc.cx(s[263], t[1])
    qc.ccx(s[174], s[175], t[1])
    qc.cx(s[170], t[0])
    qc.ccx(s[90], s[91], t[0])
    
    # Escribe en orden inverso z[2], z[1], z[0]
    qc.cx(t[2],z[n-1-i])
    qc.cx(t[1],z[n-1-i])
    qc.cx(t[0],z[n-1-i])
    
    inv_update_t(qc, s, t, 242, 287, 2)
    inv_update_t(qc, s, t, 161, 176, 1)
    inv_update_t(qc, s, t, 65, 92, 0)            
  
  # Inicialización del estado interno
  for i in range(rounds):         
    state_shifting_left(qc, s, 92, 0, t[2])
    state_shifting_left(qc, s, 176, 93, t[0])
    state_shifting_left(qc, s, 287, 177, t[1])

    inv_state_update(qc, s, t, 242, 285, 286, 287, 68, 2)   
    inv_state_update(qc, s, t, 161, 174, 175, 176, 263, 1)  
    inv_state_update(qc, s, t, 65, 90, 91, 92, 170, 0)  
        
# -----------------

def oracle(qc, r_key, r_ancilla, rev_ks, z, r_output, n, rounds):
  """
  Compara una clave candidata con un flujo de clave conocido. Si la clave es correcta (es decir,
  genera el flujo de clave esperado), invierte la fase del estado cuántico asociado a la clave
  correcta, utilizando r_output como marcador de fase, mediante una puerta MCX.

  Args:
    qc (QuantumCircuit): el circuito cuántico sobre el que se trabaja.
    r_key (QuantumRegister): registro de n qubits que contiene la clave parcial desconocida.
    r_ancilla (QuantumRegister): registro auxiliar para comparar flujos.
    rev_ks (QuantumRegister): registro con el flujo de clave conocido.
    z (QuantumRegister): registro donde se genera el flujo de clave simulado.
    r_output (QuantumRegister): qubit usado para marcar la solución (fase invertida).
    n (int): número de bits del flujo de clave.
    rounds (int): número de rondas de inicialización de Trivium.
  """
  
  # Copia los bits de desconocidos de la clave en el estado interno de Trivium
  for i in range(n): 
    qc.cx(r_key[i], s[51+i])

  # Ejecuta Trivium para generar el flujo de clave
  trivium(qc, s, t, rounds, n)
  
  # Compara el flujo de clave generado con el esperado
  for i in range(n):
    qc.cx(rev_ks[i], r_ancilla[i])  # XOR con el flujo conocido
    qc.cx(z[i], r_ancilla[i])       # XOR con el flujo generado
    qc.x(r_ancilla[i])              # Si coinciden se pone a 1
      
  # Si todos los bits coinciden, activa r_output
  qc.mcx(r_ancilla, r_output)    
  
  # Deshace la comparación (limpiar ancilla)
  for i in range(n):
    qc.x(r_ancilla[i])
    qc.cx(rev_ks[i], r_ancilla[i])
    qc.cx(z[i], r_ancilla[i])
  
  # Deshace Trivium y quitar la clave insertada
  inv_trivium(qc, s, t, rounds, n)
  
  for i in range(n):
    qc.cx(r_key[i], s[51+i])

def diffuser(nqubits):
  """
  Este circuito amplifica la probabilidad del estado marcado por el oráculo invirtiendo las
  amplitudes con respecto a su media, lo que provoca que el estado cuya fase fue invertida
  (la solución) aumente su amplitud relativa y, por tanto, su probabilidad de ser medido.

  Args:
    nqubits (int): número de qubits del registro sobre el que actúa el difusor.

  Returns:
    (Gate): una puerta cuántica que implementa el difusor y puede añadirse al circuito.
  """
  qc = QuantumCircuit(nqubits)    

  for qubit in range(nqubits):
    qc.h(qubit)

  for qubit in range(nqubits):
    qc.x(qubit)

  qc.h(nqubits - 1)
  qc.mcx(list(range(nqubits - 1)), nqubits - 1)
  qc.h(nqubits - 1)

  for qubit in range(nqubits):
    qc.x(qubit)

  for qubit in range(nqubits):
    qc.h(qubit)

  return qc.to_gate()

# ------------------------

n = 3          # Número de qubits de la clave a recuperar
rounds = 200   # Número de rondas que ejecuta Trivium
s = QuantumRegister(288)           # Registro estado de Trivium de 288 qubits
t = QuantumRegister(3, name='t')   # Registros temporales t1, t2, t3
z = QuantumRegister(n, name='z')   # Registro para el flujo de clave
r_key = QuantumRegister(n, name='r_key')         # Registro que representa los qubits de clave desconocidos
r_output = QuantumRegister(1, name='r_output')   # Registro de 1 qubit usado por el oráculo para marcar la clave correcta
rev_ks = QuantumRegister(n, name='rev_ks')       # Registro con el flujo de clave conocido (para comparar en el oráculo)
r_ancilla = QuantumRegister(n, name='r_ancilla') # Registro auxiliar para comparar el flujo de clave generado y el esperado
r_class = ClassicalRegister(n, name='r_class')   # Registro clásico para medir los qubits de la clave (r_key)

qc = QuantumCircuit(s, t, z, r_key, rev_ks, r_ancilla, r_output, r_class)

known_ks = '001' # Flujo de clave conocido utilizado como referencia en el oráculo

# Inicializa el registro rev_ks con los 3 qubits del flujo de clave conocido
for i in range(n):
  if (known_ks[i] == "1"):
    qc.x(rev_ks[i])

qc.h(r_key)

# Inicializar key (los 3 bits desconocidos se omiten)
key_0_50 = '000000010010001101000101011001111000100110101011110' # longitud=51
key_54_79 = '01111011110001001000110100' # longitud=26

for i in range(51): 
  if (key_0_50[i] == "1"):
    qc.x(s[i+0]) 
for i in range(26): 
  if (key_54_79[i] == "1"):
    qc.x(s[i+54])

# Inicializar IV
iv = '00000001001000110100010101100111100010011010101111001101111011110001001000110100'

for i in range(80): 
  if (iv[i] == "1"):
    qc.x(s[i+93]) 

# Bits fijos a 1
qc.x(s[285])
qc.x(s[286])
qc.x(s[287])

# Prepara el qubit de salida (r_output) para el oráculo de Grover
qc.x(r_output)
qc.h(r_output)

time_start = time.process_time()

# 1. Aplicar oráculo de Grover para marcar el estado solución
# 2. Aplicar el difusor (amplifica la probabilidad del estado marcado)
oracle(qc, r_key, r_ancilla, rev_ks, z, r_output, n, rounds)
qc.append(diffuser(n), r_key)

qc.measure(r_key, r_class) 

#---------------------------------------------

# Ejecuta el circuito y obtiene los resultados
result = backend.run(qc.decompose(reps=1), shots=1024).result()
counts = result.get_counts()

# Invierte las cadenas de bits (porque Qiskit usa orden little endian)
inverted_counts = {k[::-1]: v for k, v in counts.items()}
counter = Counter(inverted_counts)

# Extrae la clave más probable
best_key, best_count = counter.most_common(1)[0]

# Imprimir resultados
print("Resultados Ataque Grover sobre Trivium")
print("--------------------------------------")
print("Shots: 1024")
print("Bits desconocidos: K₅₁, K₅₂, K₅₃")
print("Flujo de clave conocida:", known_ks)
print("Resultados:")
for key, count in counter.most_common():
  print(f"  {key} → {count} veces")

print("Clave candidata más probable:", best_key)
print(f"Aparece {best_count} veces ({best_count/1024:.2%} del total)")
print(f"Tiempo de CPU: {time.process_time() - time_start:.2f} segundos")