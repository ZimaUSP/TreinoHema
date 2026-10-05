# Entrega de amostras sanguíneas com Webots e ROS 2

## Gabarito e guia do instrutor

> **Uso reservado ao instrutor.** Este documento contém soluções completas, valores de referência, respostas esperadas e observações de aplicação.

---

## 1. Escopo da atividade

A atividade foi deliberadamente limitada a:

- edição básica de um modelo no Webots;
- robô diferencial;
- controlador Python nativo e acesso direto aos motores;
- comparação entre controle direto e comunicação por ROS 2;
- publicação de `geometry_msgs/msg/Twist`;
- controle temporal;
- máquina de estados;
- assinatura opcional de `sensor_msgs/msg/LaserScan`.

Não é necessário introduzir URDF, SLAM, Nav2 ou controle de posição nesta primeira experiência. O controle temporal é usado como recurso didático e sua imprecisão deve fazer parte da discussão final.

---

## 2. Preparação obrigatória

Antes da aula, valide o projeto em uma imagem, VM ou instalação padronizada.

### 2.1 Interfaces esperadas

| Tópico | Tipo | Responsável |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Nó do aluno publica |
| `/scan` | `sensor_msgs/msg/LaserScan` | Webots publica |
| `/clock` | `rosgraph_msgs/msg/Clock` | Webots publica |

Algumas combinações recentes de ROS 2 e `ros2_control` utilizam `TwistStamped`. Para esta atividade, recomenda-se configurar o driver ou fornecer um adaptador que exponha `/cmd_vel` como `geometry_msgs/msg/Twist`. Não deixe essa incompatibilidade para os alunos resolverem.

### 2.2 Dois modos de execução

Valide separadamente:

1. `introduction.wbt` aberto diretamente no Webots, com o controlador interno `straight_line_webots`;
2. os cenários hospitalares iniciados por ROS 2:

```bash
ros2 launch hospital_delivery activity.launch.py world:=hospital_l
ros2 launch hospital_delivery activity.launch.py world:=hospital_l_challenge
```

No mundo introdutório:

- o campo `controller` deve apontar para `straight_line_webots`;
- o controlador deve localizar os dois motores pelos nomes documentados;
- não deve ser necessário executar nenhum nó ROS 2.

No mundo hospitalar, o launch deve:

- abrir o mundo escolhido;
- iniciar o driver do robô;
- publicar `/clock`;
- configurar `use_sim_time` nos nós iniciados pelo próprio launch;
- deixar o robô parado até receber `/cmd_vel`.

### 2.3 Dimensões recomendadas do mundo

| Elemento | Valor de referência |
|---|---:|
| Primeiro trecho | 2,0 m |
| Segundo trecho | 1,5 m |
| Largura livre do corredor | 0,9 a 1,2 m |
| Área de entrega | pelo menos 0,5 × 0,5 m |
| Distância inicial até a primeira parede | pelo menos 2,4 m |

Mantenha margens. Um controle temporal não deve exigir precisão centimétrica.

### 2.4 Modelo recomendado

O `PROTO` deve expor campos simples:

```text
PROTO HospitalRobot [
  field SFVec3f bodySize 0.40 0.28 0.16
  field SFColor bodyColor 0.10 0.45 0.85
]
```

Vincule `bodySize` tanto à geometria visual quanto ao `boundingObject`. O ajuste da posição das rodas e do LiDAR deve ocorrer internamente no `PROTO` ou permanecer válido dentro dos intervalos indicados ao aluno.

Não peça alteração livre do raio das rodas ou da separação entre rodas nesta oficina. Isso acrescentaria variáveis demais à calibração da curva.

---

## 3. Resultados esperados da modelagem

Aceite diferentes dimensões, desde que:

- estejam nos intervalos propostos;
- não causem interpenetração das rodas;
- mantenham o LiDAR acima do chassi;
- preservem o `boundingObject` coerente;
- não façam o robô tocar o chão com o chassi.

Uma resposta possível:

| Campo | Exemplo |
|---|---|
| Comprimento | 0,44 m |
| Largura | 0,30 m |
| Altura | 0,18 m |
| Cor | azul-claro |

O valor exato não deve ser avaliado, apenas a coerência do modelo.

---

## 4. Solução — movimento em linha reta

Arquivo `controllers/straight_line_webots/straight_line_webots.py`:

```python
from controller import Robot


robot = Robot()
time_step = int(robot.getBasicTimeStep())

left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')

left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

start_time = robot.getTime()

while robot.step(time_step) != -1:
    elapsed = robot.getTime() - start_time

    if elapsed < 1.0:
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
    elif elapsed < 6.0:
        left_motor.setVelocity(4.0)
        right_motor.setVelocity(4.0)
    else:
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
```

### 4.1 Resultados teóricos dos experimentos

Considerando rodas com raio de `0,05 m`:

| Velocidade das rodas | Tempo | Velocidade linear ideal | Distância ideal |
|---:|---:|---:|---:|
| 2,0 rad/s | 5 s | 0,10 m/s | 0,50 m |
| 4,0 rad/s | 5 s | 0,20 m/s | 1,00 m |
| 4,0 rad/s | 8 s | 0,20 m/s | 1,60 m |

Aceite pequenas diferenças na distância observada. Se o erro for grande, verifique:

- se o raio das rodas do modelo é realmente `0,05 m`;
- se os nomes dos motores coincidem com os usados no código;
- se há aceleração limitada no controlador;
- se as rodas deslizam;
- se o aluno reiniciou o mundo antes da tentativa.

### 4.2 Comparação que deve aparecer na discussão

| Controlador nativo | Nó ROS 2 da missão |
|---|---|
| Executado pelo Webots | Executado como processo ROS 2 |
| Obtém dispositivos por nome | Publica em um tópico |
| Define velocidade de cada roda | Define velocidade linear e angular do robô |
| Depende diretamente da API do Webots | Depende da interface ROS 2 acordada |

O aluno não precisa implementar a conversão de `Twist` em velocidade das rodas. Essa responsabilidade deve permanecer no driver fornecido.

---

## 5. Cálculos da missão em L

### 5.1 Primeiro trecho

```text
t = d / v
t = 2,0 / 0,20
t = 10,0 s
```

### 5.2 Curva

```text
90° = π/2 rad
t = θ / ω
t = (π/2) / 0,50
t ≈ 3,1416 s
```

### 5.3 Segundo trecho

```text
t = 1,5 / 0,20
t = 7,5 s
```

Tabela preenchida:

| Movimento | Distância ou ângulo | Velocidade | Tempo calculado |
|---|---:|---:|---:|
| Primeiro trecho | 2,0 m | 0,20 m/s | 10,0 s |
| Curva | π/2 rad | 0,50 rad/s | aproximadamente 3,14 s |
| Segundo trecho | 1,5 m | 0,20 m/s | 7,5 s |

Os tempos ajustados dependem do robô e do mundo. Registre os valores obtidos na validação do ambiente e mantenha-os disponíveis apenas como referência, não como requisito absoluto.

---

## 6. Solução — missão em L

Arquivo `hospital_delivery/delivery_l.py`:

```python
from enum import Enum, auto

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class MissionState(Enum):
    WAITING = auto()
    FIRST_STRAIGHT = auto()
    BEFORE_TURN = auto()
    TURNING = auto()
    SECOND_STRAIGHT = auto()
    DELIVERING = auto()
    FINISHED = auto()


class DeliveryL(Node):
    LINEAR_SPEED = 0.20
    ANGULAR_SPEED = 0.50

    WAIT_TIME = 2.0
    FIRST_STRAIGHT_TIME = 10.0
    BEFORE_TURN_TIME = 1.0
    TURN_TIME = 3.1416
    SECOND_STRAIGHT_TIME = 7.5
    DELIVERY_TIME = 5.0

    def __init__(self):
        super().__init__('delivery_l')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.state = MissionState.WAITING
        self.state_started_at = self.get_clock().now()
        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info('Missão iniciada: aguardando.')

    def elapsed_in_state(self):
        return (
            self.get_clock().now() - self.state_started_at
        ).nanoseconds / 1e9

    def change_state(self, new_state):
        self.state = new_state
        self.state_started_at = self.get_clock().now()
        self.get_logger().info(f'Novo estado: {new_state.name}')

    def control_loop(self):
        elapsed = self.elapsed_in_state()
        command = Twist()

        if self.state == MissionState.WAITING:
            if elapsed >= self.WAIT_TIME:
                self.change_state(MissionState.FIRST_STRAIGHT)

        elif self.state == MissionState.FIRST_STRAIGHT:
            command.linear.x = self.LINEAR_SPEED
            if elapsed >= self.FIRST_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.BEFORE_TURN)

        elif self.state == MissionState.BEFORE_TURN:
            if elapsed >= self.BEFORE_TURN_TIME:
                self.change_state(MissionState.TURNING)

        elif self.state == MissionState.TURNING:
            command.angular.z = self.ANGULAR_SPEED
            if elapsed >= self.TURN_TIME:
                command.angular.z = 0.0
                self.change_state(MissionState.SECOND_STRAIGHT)

        elif self.state == MissionState.SECOND_STRAIGHT:
            command.linear.x = self.LINEAR_SPEED
            if elapsed >= self.SECOND_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.DELIVERING)

        elif self.state == MissionState.DELIVERING:
            if elapsed >= self.DELIVERY_TIME:
                self.change_state(MissionState.FINISHED)

        elif self.state == MissionState.FINISHED:
            pass

        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = DeliveryL()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 6.1 Sentido da curva

Na convenção ROS:

- `angular.z > 0`: giro anti-horário;
- `angular.z < 0`: giro horário.

Se o mundo exigir uma curva à direita, altere:

```python
command.angular.z = -self.ANGULAR_SPEED
```

### 6.2 Observação sobre a transição de estados

Na iteração que atinge o tempo limite, a solução zera o comando antes de alterar o estado. A ação do novo estado começa na próxima chamada do timer, cerca de 50 ms depois. Isso é intencional e didaticamente mais seguro.

---

## 7. Solução — desafio com LiDAR

Esta solução:

- seleciona um setor frontal de ±15°;
- descarta leituras inválidas;
- reduz a velocidade abaixo de 0,80 m;
- para abaixo de 0,50 m;
- pausa o cronômetro do estado enquanto o robô está bloqueado.

Arquivo `hospital_delivery/delivery_challenge.py`:

```python
import math
from enum import Enum, auto

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class MissionState(Enum):
    WAITING = auto()
    FIRST_STRAIGHT = auto()
    BEFORE_TURN = auto()
    TURNING = auto()
    SECOND_STRAIGHT = auto()
    DELIVERING = auto()
    FINISHED = auto()


class DeliveryChallenge(Node):
    LINEAR_SPEED = 0.20
    ANGULAR_SPEED = 0.50

    WAIT_TIME = 2.0
    FIRST_STRAIGHT_TIME = 10.0
    BEFORE_TURN_TIME = 1.0
    TURN_TIME = 3.1416
    SECOND_STRAIGHT_TIME = 7.5
    DELIVERY_TIME = 5.0

    SLOW_DISTANCE = 0.80
    STOP_DISTANCE = 0.50
    FRONT_HALF_ANGLE = math.radians(15.0)

    def __init__(self):
        super().__init__('delivery_challenge')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10,
        )

        self.state = MissionState.WAITING
        self.state_started_at = self.get_clock().now()
        self.front_distance = math.inf
        self.blocked_since = None

        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info('Missão com segurança iniciada.')

    def scan_callback(self, message):
        valid_front_ranges = []

        for index, distance in enumerate(message.ranges):
            angle = message.angle_min + index * message.angle_increment

            is_front = abs(angle) <= self.FRONT_HALF_ANGLE
            is_valid = (
                math.isfinite(distance)
                and message.range_min <= distance <= message.range_max
            )

            if is_front and is_valid:
                valid_front_ranges.append(distance)

        self.front_distance = (
            min(valid_front_ranges)
            if valid_front_ranges
            else math.inf
        )

    def elapsed_in_state(self):
        return (
            self.get_clock().now() - self.state_started_at
        ).nanoseconds / 1e9

    def change_state(self, new_state):
        self.state = new_state
        self.state_started_at = self.get_clock().now()
        self.blocked_since = None
        self.get_logger().info(f'Novo estado: {new_state.name}')

    def movement_state(self):
        return self.state == MissionState.SECOND_STRAIGHT

    def update_pause(self):
        now = self.get_clock().now()
        blocked = (
            self.movement_state()
            and self.front_distance < self.STOP_DISTANCE
        )

        if blocked and self.blocked_since is None:
            self.blocked_since = now
            self.get_logger().warn('Obstáculo: parada de segurança.')

        if not blocked and self.blocked_since is not None:
            paused_duration = now - self.blocked_since
            self.state_started_at = self.state_started_at + paused_duration
            self.blocked_since = None
            self.get_logger().info('Caminho liberado: retomando missão.')

        return blocked

    def apply_safety(self, command):
        if (
            self.state != MissionState.SECOND_STRAIGHT
            or command.linear.x <= 0.0
        ):
            return command

        if self.front_distance < self.STOP_DISTANCE:
            command.linear.x = 0.0
            command.angular.z = 0.0
        elif self.front_distance < self.SLOW_DISTANCE:
            command.linear.x *= 0.5

        return command

    def control_loop(self):
        blocked = self.update_pause()
        elapsed = self.elapsed_in_state()
        command = Twist()

        if blocked:
            self.publisher.publish(command)
            return

        if self.state == MissionState.WAITING:
            if elapsed >= self.WAIT_TIME:
                self.change_state(MissionState.FIRST_STRAIGHT)

        elif self.state == MissionState.FIRST_STRAIGHT:
            command.linear.x = self.LINEAR_SPEED
            if elapsed >= self.FIRST_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.BEFORE_TURN)

        elif self.state == MissionState.BEFORE_TURN:
            if elapsed >= self.BEFORE_TURN_TIME:
                self.change_state(MissionState.TURNING)

        elif self.state == MissionState.TURNING:
            command.angular.z = self.ANGULAR_SPEED
            if elapsed >= self.TURN_TIME:
                command.angular.z = 0.0
                self.change_state(MissionState.SECOND_STRAIGHT)

        elif self.state == MissionState.SECOND_STRAIGHT:
            command.linear.x = self.LINEAR_SPEED
            if elapsed >= self.SECOND_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.DELIVERING)

        elif self.state == MissionState.DELIVERING:
            if elapsed >= self.DELIVERY_TIME:
                self.change_state(MissionState.FINISHED)

        elif self.state == MissionState.FINISHED:
            pass

        command = self.apply_safety(command)
        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = DeliveryChallenge()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 7.1 Limitação proposital do desafio

A redução para metade da velocidade não compensa o tempo do estado. Portanto, o robô pode percorrer uma distância menor caso permaneça por muito tempo na zona entre 0,50 e 0,80 m.

Para manter o exercício curto, há duas opções:

1. posicionar o carrinho de modo que o robô entre rapidamente na zona de parada; ou
2. aceitar que os alunos calibrem o segundo trecho após testar o desafio.

Uma versão mais rigorosa deveria integrar a velocidade ao longo do tempo, utilizar odometria ou pausar também o relógio proporcionalmente à redução. Isso pode ser apresentado como discussão, sem exigir implementação.

### 7.2 LiDAR com zero em outra direção

O código pressupõe que o ângulo zero do `/scan` aponta para a frente do robô. Verifique isso previamente. Se o sensor estiver rotacionado ou o driver reorganizar os dados, adapte o cálculo do setor frontal no gabarito e no template.

---

## 8. Respostas esperadas

### 8.1 Como o controlador nativo acessa os motores?

Ele usa `robot.getDevice(...)` com os nomes definidos no modelo do Webots. Depois configura os motores em controle de velocidade e chama `setVelocity(...)` diretamente em cada dispositivo.

### 8.2 Diferença entre o controlador nativo e o nó ROS 2

O controlador nativo é executado pelo Webots e depende diretamente da API e dos dispositivos do simulador. O nó ROS 2 é um processo separado que publica mensagens em uma interface; o driver recebe essas mensagens e controla os motores.

### 8.3 O que representa `/cmd_vel`?

É o tópico pelo qual o controlador envia a velocidade desejada do robô. Neste exercício, a mensagem contém velocidade linear e angular, que o driver converte em comandos para as rodas.

### 8.4 Diferença entre `linear.x` e `angular.z`

`linear.x` representa a velocidade para frente ou para trás, em metros por segundo. `angular.z` representa a velocidade de rotação em torno do eixo vertical, em radianos por segundo.

### 8.5 O que caracteriza um robô diferencial?

Ele possui duas rodas motrizes controladas independentemente. A combinação das velocidades das rodas determina se o robô avança, curva ou gira.

### 8.6 Função do publisher

Criar e enviar mensagens para um tópico ROS 2.

### 8.7 Função do subscriber

Receber mensagens publicadas em um tópico e executar uma função de tratamento quando novos dados chegam.

### 8.8 Por que o controle temporal acumula erro?

Porque pressupõe que a velocidade comandada é atingida imediatamente e permanece exata. Aceleração, deslizamento, colisões, atrasos e discretização podem fazer a distância real divergir da estimativa.

### 8.9 Por que pausar o cronômetro durante o obstáculo?

Sem a pausa, o estado continua consumindo sua duração mesmo com o robô imóvel. Ao liberar o caminho, o programa pode avançar para o próximo estado antes de percorrer o trecho.

### 8.10 Forma mais precisa de identificar chegada

Aceitar respostas como:

- usar odometria e realimentação;
- comparar a pose atual com a pose objetivo;
- usar localização em um mapa;
- utilizar um controlador de navegação, como Nav2.

---

## 9. Rubrica detalhada

| Critério | Pontos | Evidência |
|---|---:|---|
| Modelo | 15 | Dimensões alteradas, modelo consistente e sem interpenetrações |
| Controlador nativo | 20 | Acessa motores, executa passos, avança e para sem intervenção |
| Transição para ROS 2 | 10 | Explica `/cmd_vel` e a separação entre missão e driver |
| Cálculos | 10 | Tempos calculados e unidades identificadas |
| Estados | 15 | Estados claros, transições e parada entre segmentos |
| Trajeto em L | 20 | Completa o caminho sem colisão e chega à área final |
| Qualidade | 10 | Parada final, nomes claros e código legível |
| **Total** | **100** | |

### Desafio: até 15 pontos adicionais

| Item | Pontos adicionais |
|---|---:|
| Assinatura e leitura válida do LiDAR | 4 |
| Redução de velocidade | 3 |
| Parada antes do obstáculo | 4 |
| Retomada com compensação do tempo parado | 4 |

---

## 10. Erros comuns e intervenções

| Sintoma | Causa provável | Orientação |
|---|---|---|
| Robô não se move na introdução | Controlador ou nomes dos motores incorretos | Verificar o campo `controller`, o console do Webots e `getDevice(...)` |
| Robô não se move na missão | Nó não executado ou tópico incorreto | Verificar `ros2 node list` e `ros2 topic info /cmd_vel` |
| Mensagem não conecta ao driver | `Twist` versus `TwistStamped` | Corrigir o adaptador fornecido pelo professor |
| Robô move antes do início | Outro nó publicando | Usar `ros2 topic info /cmd_vel --verbose` |
| Curva para o lado errado | Sinal de `angular.z` | Inverter o sinal |
| Curva passa de 90° | Tempo ou velocidade angular excessivos | Ajustar um parâmetro por vez |
| Nó fica parado no início | `/clock` ausente com `use_sim_time` | Confirmar publicação de `/clock` |
| Robô atravessa visualmente uma parede | `boundingObject` inconsistente | Revisar o `PROTO` |
| LiDAR sempre informa infinito | Setor frontal incorreto ou nenhuma leitura válida | Verificar orientação, `angle_min` e `angle_increment` |
| Missão termina após esperar no obstáculo | Cronômetro não foi compensado | Implementar `blocked_since` |

---

## 11. Critérios de aplicação

Para manter o caráter introdutório:

- forme duplas;
- forneça a infraestrutura funcional;
- limite a edição aos `TODO`s;
- demonstre a missão completa antes de iniciar;
- não avalie instalação de dependências;
- não exija precisão centimétrica;
- trate ajustes experimentais como parte da atividade;
- destaque a troca do controle direto de motores pela interface `/cmd_vel`;
- encerre relacionando as limitações observadas à odometria e à realimentação.

O resultado desejado é o aluno perceber primeiro como o Webots executa comandos diretamente nos motores e, depois, como o ROS 2 separa a lógica da missão do driver. Sensores podem então alterar a decisão do programa sem mudar a estrutura do simulador. A atividade não deve se transformar em uma avaliação de configuração do Webots ou do ROS 2.
