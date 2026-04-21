# Puzzlebot: trayectoria punto-a-punto respondiendo a un semaforo

Los siguientes programas en conjunto realizan que un robot móvil de dos ruedas realice una trayectoria de un cuadrado con 2m en cada lado, y respete en dicha trayectoria los semáforos, 
de modo que:

*  Si la luz está en verde --- Avanza
*  Si la luz está en amarillo --- Disminuye su velocidad
*  Si la luz está en rojo --- Alto total

Respeta los semáforos hasta que complete toda su trayectoria.

A continuación se enlista una breve descripción de los programas:

## Path_generator
El generador de puntos funciona como el planeador de trayectoria del robot, 
mandando una lista de coordenadas [x,y] que en este caso representan los vértices de las figuras geométricas a implementar (cuadrado, triángulo, trapecio). En este caso un cuadrado de 2m

## Odometry
Se encarga de estimar la pose actual del robot. Se suscribe a los tópicos /VelocityEncR y /VelocityEncL, 
que publican las velocidades angulares medidas por los encoders de cada rueda. A partir de estas lecturas, integra la posición y orientación del robot 
utilizando el modelo cinemático diferencial, calculando la velocidad lineal y angular del robot.



## Closeloop

El controlador aplica la ley de control mediante una **máquina de estados** finitos que separa el movimiento en dos fases, evitando que el robot gire y avance simultáneamente para mejorar la precisión.

**En el primer estado (state1 - orientación)** 
El controlador aplica una ganancia proporcional Kω sobre el error de orientación eθ 
para que el robot gire sobre su propio eje hasta que su encabezado apunte directamente hacia el objetivo. 
Una vez que eθ cae dentro del umbral de tolerancia angular, el sistema transiciona al segundo estado.

**En el segundo estado (state2 - traslación)** 
El controlador utiliza eₚ como error principal para generar la velocidad lineal mediante la ganancia Kv, 
mientras mantiene una corrección angular activa sobre eθ con la ganancia Kω para compensar posibles desviaciones durante el avance. 

Ambas acciones de control se publican en /cmd_vel como un mensaje Twist con las componentes linear.x y angular.z. 
Cuando el robot alcanza el punto deseado dentro del umbral de tolerancia de posición definido, transiciona al estado stop, se detiene y libera el objetivo actual, 
quedando en espera del siguiente punto publicado por el path generator para reiniciar el ciclo.


## colorDetection

Este nodo se encarga de percibir el entorno utilizando la cámara del robot y determinar el estado del semáforo (rojo, amarillo o verde).

**Funcionamiento general**
* Adquisición de imagen
  Se suscribe al tópico /video_source/raw
* Convierte las imágenes de ROS a formato OpenCV usando CvBridge
* Procesamiento de imagen
  Convierte la imagen de RGB/BGR a espacio de color HSV
* Define rangos de color para:
  Rojo
  Amarillo
  Verde
* Segmentación
  Genera máscaras binarias para cada color
  Cada máscara representa dónde aparece ese color en la imagen
*  Detección
  Calcula el área de cada máscara (cantidad de píxeles detectados)
  Compara contra un umbral para evitar ruido


## TrafficDecision

Este nodo actúa como un árbitro de control, modificando las velocidades del robot en función del estado del semáforo.

Lógica de decisión (máquina de estados implícita)

Dependiendo del estado:

🔴 RED
Detiene completamente el robot
linear.x = 0, angular.z = 0

🟡 YELLOW
Reduce la velocidad lineal (ej. 50%)
Mantiene la dirección

🟢 GREEN
Permite el paso normal de comandos
Salida

Publica el comando final en:  */cmd_vel*
