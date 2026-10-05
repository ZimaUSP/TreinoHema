# Entrega de amostras sanguíneas com Webots e ROS 2

## Tutorial do aluno

> **Modalidade:** atividade introdutória, em duplas  
> **Duração estimada:** 3 h 30 min a 4 h  
> **Linguagem adotada neste roteiro:** Python 3  
> **Simulador:** Webots  
> **Middleware:** ROS 2

---

## 1. Contexto

Uma amostra sanguínea foi coletada e precisa ser transportada até o laboratório de análises. Para reduzir deslocamentos repetitivos da equipe do hospital, será utilizado um pequeno robô móvel de duas rodas.

Nesta atividade, você irá:

1. conhecer os elementos básicos do Webots;
2. alterar as dimensões e a aparência de um robô;
3. criar um controlador nativo do Webots para movimentar diretamente as rodas;
4. comparar o controle direto com a comunicação por ROS 2;
5. programar, com ROS 2, uma missão em um corredor em formato de L;
6. opcionalmente, usar o LiDAR para reagir a um carrinho no corredor.

O objetivo não é produzir um sistema hospitalar real. O cenário é uma simulação didática para estudar conceitos iniciais de robótica móvel, ROS 2 e programação.

---

## 2. Objetivos de aprendizagem

Ao concluir a atividade, você deverá ser capaz de:

- identificar o mundo, o robô, o controlador e a árvore de cena do Webots;
- explicar a diferença entre o modelo visual e a geometria de colisão;
- reconhecer um robô com acionamento diferencial;
- usar a API nativa do Webots para acessar motores e executar passos de simulação;
- comparar o controle direto de motores com o envio de comandos por ROS 2;
- identificar nó, tópico, mensagem, publisher e subscriber no ROS 2;
- publicar velocidades lineares e angulares;
- organizar uma missão simples como uma máquina de estados;
- explicar por que um controle baseado apenas em tempo acumula erros;
- usar uma leitura simples de LiDAR para interromper o movimento.

---

## 3. Pré-requisitos e arquivos fornecidos

Você deve receber do professor um workspace já configurado com:

```text
hospital_webots_ws/
└── src/
    └── hospital_delivery/
        ├── controllers/
        │   └── straight_line_webots/
        │       └── straight_line_webots.py
        ├── hospital_delivery/
        │   ├── __init__.py
        │   ├── webots_driver.py
        │   ├── delivery_l.py
        │   └── delivery_challenge.py
        ├── launch/
        │   └── activity.launch.py
        ├── protos/
        │   └── HospitalRobot.proto
        ├── worlds/
        │   ├── introduction.wbt
        │   ├── hospital_l.wbt
        │   └── hospital_l_challenge.wbt
        ├── resource/
        │   └── hospital_robot.urdf
        ├── student_templates/
        ├── package.xml
        └── setup.py
```

O projeto também deve conter:

- um robô diferencial funcional;
- um controlador Python nativo para a primeira etapa;
- um driver que converta `/cmd_vel` em movimento das rodas na etapa hospitalar;
- um LiDAR já instalado, usado somente no desafio;
- os três mundos da atividade;
- os executáveis da missão ROS 2 cadastrados no `setup.py`.

### 3.1 Preparação inicial

Na primeira etapa, não será necessário iniciar o ROS 2. Abra o mundo `introduction.wbt` diretamente no Webots ou pelo atalho indicado pelo professor.

O terminal e a compilação do workspace serão utilizados somente a partir da missão hospitalar:

```bash
cd ~/hospital_webots_ws
colcon build --symlink-install
source install/setup.bash
```

> Execute `source install/setup.bash` em cada novo terminal aberto para a atividade.

---

## 4. Parte A — Primeiros passos no Webots

### 4.1 Abra o mundo introdutório

Abra diretamente no Webots:

```text
hospital_delivery/worlds/introduction.wbt
```

O Webots deve abrir mostrando o robô em um ambiente livre e plano.

Antes de alterar qualquer arquivo, localize:

- os botões para executar, pausar e reiniciar a simulação;
- a janela 3D;
- a árvore de cena;
- o nó `HospitalRobot`;
- as rodas e o LiDAR do robô;
- o campo `controller` do robô.

Nesta primeira parte, o campo `controller` deve estar configurado como:

```text
straight_line_webots
```

### 4.2 Mundo, robô e controlador

Um projeto Webots possui três elementos importantes:

| Elemento | Função |
|---|---|
| Mundo `.wbt` | Descreve o ambiente, os objetos e os robôs presentes |
| Modelo ou `PROTO` | Define a estrutura reutilizável do robô |
| Controlador | Define o comportamento executado durante a simulação |

Na introdução, o comportamento será executado por um controlador interno do Webots. Na missão hospitalar, o controle passará para um nó ROS 2 externo. A comparação entre essas duas formas de controle é parte da atividade.

### 4.3 Robô diferencial

O robô possui duas rodas motrizes independentes:

```text
mesma velocidade nas rodas       → movimento em linha reta
velocidades diferentes           → trajetória curva
rodas em sentidos opostos        → giro aproximadamente no lugar
velocidade zero nas duas rodas   → parada
```

O driver do projeto recebe uma mensagem ROS 2 contendo:

- `linear.x`: velocidade para frente ou para trás, em m/s;
- `angular.z`: velocidade de rotação, em rad/s.

---

## 5. Parte B — Alteração do modelo

### 5.1 Inspecione o robô

Na árvore de cena, selecione `HospitalRobot`. O modelo preparado para a atividade deve apresentar campos semelhantes a:

```text
bodySize    0.40 0.28 0.16
bodyColor   0.10 0.45 0.85
```

Os três valores de `bodySize` representam, respectivamente:

```text
comprimento, largura e altura
```

### 5.2 Faça as alterações

Altere o modelo respeitando os seguintes intervalos:

| Parâmetro | Intervalo recomendado |
|---|---:|
| Comprimento | 0,36 a 0,48 m |
| Largura | 0,24 a 0,34 m |
| Altura | 0,14 a 0,22 m |

Escolha também uma nova cor para o chassi.

Depois:

1. salve o mundo;
2. reinicie a simulação;
3. observe se o chassi continua apoiado corretamente;
4. verifique se as rodas permanecem nas laterais;
5. verifique se o LiDAR não ficou dentro do chassi.

### 5.3 Visual e colisão

O modelo deve possuir:

- uma forma visual, que determina sua aparência;
- uma forma de colisão, normalmente configurada no campo `boundingObject`.

Se apenas a aparência mudar, o objeto pode parecer maior, mas continuar colidindo como antes. Por isso, o `PROTO` fornecido deve manter as duas dimensões associadas ao campo `bodySize`.

Registre os valores escolhidos:

| Campo | Valor utilizado |
|---|---|
| Comprimento | |
| Largura | |
| Altura | |
| Cor | |

---

## 6. Parte C — Movimento direto no Webots, sem ROS 2

Nesta etapa, o programa controla diretamente os motores simulados. Não há nó, tópico ou mensagem ROS 2.

O fluxo é:

```text
controlador Python do Webots
            │
            ├── motor esquerdo
            └── motor direito
```

### 6.1 Abra o controlador

Abra:

```text
hospital_delivery/controllers/straight_line_webots/straight_line_webots.py
```

Use o seguinte código inicial:

```python
from controller import Robot


robot = Robot()
time_step = int(robot.getBasicTimeStep())

left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')

# Posição infinita coloca os motores em controle de velocidade.
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
        # TODO 1: use a mesma velocidade nas duas rodas.
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
    else:
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
```

### 6.2 Complete o movimento

No `TODO 1`, configure as duas rodas com `4,0 rad/s`.

O comportamento deverá ser:

```text
0 a 1 s  → parado
1 a 6 s  → rodas girando a 4,0 rad/s
após 6 s → parado
```

Como as duas rodas recebem a mesma velocidade, o robô deve seguir aproximadamente em linha reta.

### 6.3 Execute

1. Salve o controlador.
2. Confirme que o campo `controller` do robô contém `straight_line_webots`.
3. Reinicie o mundo.
4. Inicie a simulação.
5. Observe o movimento e a parada.

Controladores Python nativos não precisam ser compilados com `colcon`.

### 6.4 Relacione roda e deslocamento

O valor enviado ao motor está em radianos por segundo. Para uma roda de raio `0,05 m`, a velocidade linear ideal na borda é:

```text
velocidade linear = raio × velocidade angular
velocidade linear = 0,05 × 4,0
velocidade linear = 0,20 m/s
```

Durante cinco segundos, a distância ideal seria:

```text
distância = velocidade linear × tempo
distância = 0,20 × 5
distância = 1,0 m
```

### 6.5 Experimentos

Reinicie a simulação antes de cada tentativa e preencha:

| Velocidade das rodas | Duração | Velocidade linear ideal | Distância ideal | Distância observada |
|---:|---:|---:|---:|---:|
| 2,0 rad/s | 5 s | | | |
| 4,0 rad/s | 5 s | | | |
| 4,0 rad/s | 8 s | | | |

### 6.6 Perguntas rápidas

1. Por que as duas rodas precisam receber a mesma velocidade para seguir em linha reta?
2. O que acontece se apenas a roda esquerda se mover?
3. Por que a distância observada pode ser diferente da ideal?

> Considere aceleração, contato entre roda e piso, discretização da simulação e possíveis deslizamentos.

---

## 7. Parte D — Da API do Webots para o ROS 2

Na etapa anterior, o programa conhecia diretamente os nomes dos motores. Agora, o programa solicitará o movimento do robô por meio de uma interface ROS 2.

Compare:

```text
Sem ROS 2
controlador Webots → motores → rodas

Com ROS 2
nó do aluno → /cmd_vel → driver → motores → rodas
```

### 7.1 Por que adicionar ROS 2?

O controle direto é simples, mas fica associado à API e aos nomes dos dispositivos do simulador. Com ROS 2, o programa envia mensagens por uma interface definida. Isso permite separar:

- o código da missão;
- a comunicação;
- o driver do robô;
- a simulação.

### 7.2 Inicie a infraestrutura ROS 2

Encerre o mundo introdutório. Abra um terminal e execute:

```bash
cd ~/hospital_webots_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch hospital_delivery activity.launch.py world:=hospital_l
```

O mundo hospitalar deve usar o controlador externo preparado para o `webots_ros2_driver`, e não `straight_line_webots`.

### 7.3 Observe nós e tópicos

Em outro terminal:

```bash
cd ~/hospital_webots_ws
source install/setup.bash
ros2 node list
ros2 topic list
```

Localize `/cmd_vel` e verifique seu tipo:

```bash
ros2 topic type /cmd_vel
```

O resultado esperado neste material é:

```text
geometry_msgs/msg/Twist
```

> Caso apareça `geometry_msgs/msg/TwistStamped`, avise o professor. O projeto precisa expor uma interface compatível com o tutorial.

Veja os campos da mensagem:

```bash
ros2 interface show geometry_msgs/msg/Twist
```

Usaremos:

```text
linear.x  → velocidade do robô para frente ou para trás, em m/s
angular.z → velocidade de giro do robô, em rad/s
```

Observe a mudança de abstração:

| Controle nativo do Webots | Controle por ROS 2 |
|---|---|
| Define a velocidade de cada roda | Define a velocidade do robô |
| Usa nomes dos motores | Usa o tópico `/cmd_vel` |
| Depende diretamente do Webots | A missão fica separada do simulador |
| Não utiliza mensagens ROS 2 | Publica `geometry_msgs/msg/Twist` |

---

## 8. Parte E — Missão hospitalar em L

### 8.1 Abra o cenário hospitalar

Use o mundo hospitalar iniciado na seção anterior. Caso ele não esteja aberto, execute:

```bash
ros2 launch hospital_delivery activity.launch.py world:=hospital_l
```

Identifique:

- a sala de coleta;
- o primeiro trecho do corredor;
- a curva de 90°;
- o segundo trecho;
- a marca de entrega no laboratório.

As dimensões de referência são:

| Trecho | Medida |
|---|---:|
| Primeiro deslocamento | 2,0 m |
| Curva | 90° ou π/2 rad |
| Segundo deslocamento | 1,5 m |

### 8.2 Calcule os tempos

Use:

```text
velocidade linear = 0,20 m/s
velocidade angular = 0,50 rad/s
```

Para os trechos retos:

```text
tempo = distância / velocidade
```

Para a curva:

```text
tempo = ângulo / velocidade angular
```

Complete:

| Movimento | Distância ou ângulo | Velocidade | Tempo calculado |
|---|---:|---:|---:|
| Primeiro trecho | 2,0 m | 0,20 m/s | |
| Curva | π/2 rad | 0,50 rad/s | |
| Segundo trecho | 1,5 m | 0,20 m/s | |

### 8.3 Máquina de estados

A missão será dividida nestes estados:

```text
WAITING
   ↓
FIRST_STRAIGHT
   ↓
BEFORE_TURN
   ↓
TURNING
   ↓
SECOND_STRAIGHT
   ↓
DELIVERING
   ↓
FINISHED
```

Cada estado possui:

- uma ação;
- uma duração;
- uma condição para passar ao próximo estado.

Abra:

```text
hospital_delivery/hospital_delivery/delivery_l.py
```

Use o seguinte esqueleto:

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
    FIRST_STRAIGHT_TIME = 0.0       # TODO 1
    BEFORE_TURN_TIME = 1.0
    TURN_TIME = 0.0                 # TODO 2
    SECOND_STRAIGHT_TIME = 0.0      # TODO 3
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
            command.linear.x = 0.0  # TODO 4
            if elapsed >= self.FIRST_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.BEFORE_TURN)

        elif self.state == MissionState.BEFORE_TURN:
            if elapsed >= self.BEFORE_TURN_TIME:
                self.change_state(MissionState.TURNING)

        elif self.state == MissionState.TURNING:
            command.angular.z = 0.0  # TODO 5
            if elapsed >= self.TURN_TIME:
                command.angular.z = 0.0
                self.change_state(MissionState.SECOND_STRAIGHT)

        elif self.state == MissionState.SECOND_STRAIGHT:
            command.linear.x = 0.0  # TODO 6
            if elapsed >= self.SECOND_STRAIGHT_TIME:
                command.linear.x = 0.0
                self.change_state(MissionState.DELIVERING)

        elif self.state == MissionState.DELIVERING:
            if elapsed >= self.DELIVERY_TIME:
                self.change_state(MissionState.FINISHED)

        elif self.state == MissionState.FINISHED:
            # O comando permanece zerado.
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

### 8.4 Complete os `TODO`s

- `TODO 1`: duração calculada para o primeiro trecho;
- `TODO 2`: duração calculada para a curva;
- `TODO 3`: duração calculada para o segundo trecho;
- `TODO 4`: velocidade linear do primeiro trecho;
- `TODO 5`: velocidade angular da curva;
- `TODO 6`: velocidade linear do segundo trecho.

> O sinal de `angular.z` depende da orientação inicial e do sentido da curva. Use valor positivo para giro anti-horário e negativo para giro horário.

### 8.5 Execute a missão

Reinicie o mundo e execute:

```bash
ros2 run hospital_delivery delivery_l --ros-args -p use_sim_time:=true
```

Observe no terminal as mudanças de estado.

### 8.6 Ajuste experimental

Os tempos calculados são o ponto de partida. Caso o robô não termine dentro da marca de entrega:

1. altere apenas um parâmetro por vez;
2. reinicie a simulação;
3. execute novamente;
4. registre o ajuste.

| Parâmetro | Calculado | Ajustado | Motivo |
|---|---:|---:|---|
| Primeiro trecho | | | |
| Curva | | | |
| Segundo trecho | | | |

### 8.7 Critérios de conclusão

A missão principal está concluída quando:

- o robô permanece dentro do corredor;
- realiza a curva no sentido correto;
- não colide com paredes;
- alcança a marca do laboratório;
- permanece parado durante a entrega;
- continua parado no estado `FINISHED`.

---

## 9. Desafio adicional — carrinho no corredor

Um carrinho hospitalar será colocado no segundo trecho. O robô deve parar quando o caminho estiver bloqueado e continuar quando o carrinho for retirado.

### 9.1 Novo conceito: subscriber

Até agora, seu nó apenas publicou comandos. No desafio, ele também receberá leituras:

```text
Webots ── /scan ──► nó da missão
                         │
                         │ decisão
                         ▼
Webots ◄─ /cmd_vel ──────┘
```

Verifique o tipo do tópico:

```bash
ros2 topic type /scan
```

O resultado esperado é:

```text
sensor_msgs/msg/LaserScan
```

Inspecione a interface:

```bash
ros2 interface show sensor_msgs/msg/LaserScan
```

### 9.2 Requisitos do desafio

Crie ou complete `delivery_challenge.py` para:

- assinar `/scan`;
- selecionar leituras em aproximadamente 15° para cada lado da frente;
- ignorar valores não finitos ou fora do intervalo do sensor;
- encontrar a menor distância frontal válida;
- reduzir a velocidade abaixo de 0,80 m;
- parar abaixo de 0,50 m;
- retomar o estado anterior quando o caminho for liberado.

Tabela de comportamento:

| Distância frontal | Comando |
|---:|---|
| Acima de 0,80 m | Velocidade normal |
| Entre 0,50 e 0,80 m | Metade da velocidade |
| Abaixo de 0,50 m | Parar |

### 9.3 Atenção ao tempo da missão

Se o cronômetro do estado continuar avançando enquanto o robô está parado, o estado pode terminar sem que o robô percorra a distância esperada.

Sua solução deve, portanto:

1. registrar o instante em que a parada começou;
2. manter o comando zerado;
3. quando o caminho for liberado, acrescentar o tempo parado ao início do estado.

Pseudocódigo:

```text
se obstáculo muito próximo:
    se esta é a primeira iteração bloqueada:
        guardar o instante da parada
    publicar velocidade zero

se caminho foi liberado:
    calcular quanto tempo o robô ficou parado
    deslocar o início do estado pelo mesmo intervalo
    continuar a missão
```

### 9.4 Execução

Encerre o mundo hospitalar sem obstáculo. Em um terminal, abra o cenário com o carrinho:

```bash
ros2 launch hospital_delivery activity.launch.py world:=hospital_l_challenge
```

Em outro terminal, execute:

```bash
ros2 run hospital_delivery delivery_challenge --ros-args -p use_sim_time:=true
```

O professor retirará o objeto `movable hospital cart` após a parada, ou fornecerá um mecanismo para movê-lo.

O desafio está concluído quando:

- o robô para antes do carrinho;
- não ocorre colisão;
- a missão não avança indevidamente durante a espera;
- o robô continua quando o caminho fica livre;
- a entrega é concluída.

---

## 10. Entregas

Entregue:

1. `HospitalRobot.proto` ou o mundo com as dimensões modificadas;
2. `controllers/straight_line_webots/straight_line_webots.py`;
3. `delivery_l.py`;
4. `delivery_challenge.py`, caso tenha realizado o desafio;
5. uma captura de tela ou vídeo curto da entrega;
6. a tabela de tempos calculados e ajustados;
7. as respostas da seção seguinte.

---

## 11. Questões finais

Responda com suas próprias palavras:

1. Como o controlador nativo do Webots acessa os motores?
2. Qual é a principal diferença entre o controlador nativo e o nó ROS 2?
3. O que representa o tópico `/cmd_vel`?
4. Qual é a diferença entre `linear.x` e `angular.z`?
5. O que caracteriza um robô diferencial?
6. Qual é a função de um publisher?
7. Qual é a função de um subscriber?
8. Por que o controle baseado somente em tempo pode acumular erro?
9. Por que o cronômetro do estado precisa ser pausado durante uma parada por obstáculo?
10. Qual seria uma maneira mais precisa de determinar se o robô chegou ao destino?

---

## 12. Critérios de avaliação

| Critério | Pontos |
|---|---:|
| Alteração coerente do modelo | 15 |
| Controlador nativo e movimento em linha reta | 20 |
| Compreensão da transição para ROS 2 e `/cmd_vel` | 10 |
| Cálculo dos tempos | 10 |
| Organização em estados | 15 |
| Trajeto hospitalar em L | 20 |
| Parada final e organização do código | 10 |
| **Total** | **100** |

O desafio do LiDAR pode valer até 15 pontos adicionais, conforme orientação do professor.

---

## 13. Encerramento

Nesta atividade, você controlou primeiro os motores diretamente pela API do Webots. Depois, passou a enviar velocidades por uma interface ROS 2, deixando o driver cuidar dos motores. Nos dois casos, a trajetória foi executada principalmente com velocidades e tempos.

Essa estratégia é chamada de controle em malha aberta: o programa envia comandos, mas não verifica continuamente a posição real do robô.

Em atividades futuras, o controle pode ser melhorado com:

- odometria;
- controladores com realimentação;
- mapeamento;
- localização;
- planejamento de trajetórias;
- Nav2.

O importante é reconhecer as duas camadas: o Webots simula os dispositivos e a física; o ROS 2 permite que o programa da missão se comunique com o robô sem controlar diretamente cada motor.
