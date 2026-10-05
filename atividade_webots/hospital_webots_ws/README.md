# Workspace da atividade Webots + ROS 2

Este workspace contém todos os arquivos da atividade **Entrega de amostras
sanguíneas**:

- robô diferencial editável em `PROTO`;
- mundo introdutório executado sem ROS 2;
- controlador Python nativo do Webots;
- corredor hospitalar em L;
- ponte `/cmd_vel` para os motores;
- publicação do LiDAR em `/scan`;
- missão principal;
- desafio com carrinho no corredor;
- templates destinados aos alunos.

## Estrutura

```text
hospital_webots_ws/
├── README.md
└── src/
    └── hospital_delivery/
        ├── controllers/straight_line_webots/
        ├── hospital_delivery/
        ├── launch/
        ├── protos/
        ├── resource/
        ├── student_templates/
        ├── test/
        └── worlds/
```

## Requisitos

- Webots R2023b ou mais recente;
- uma distribuição ROS 2 compatível com a versão instalada de
  `webots_ros2`;
- `colcon` e `rosdep`;
- pacotes ROS 2 `webots_ros2_driver`, `geometry_msgs` e `sensor_msgs`.

No Windows, a documentação oficial recomenda executar ROS 2 em WSL e o Webots
no Windows. Nesse caso, antes de iniciar:

```bash
export WEBOTS_HOME=/mnt/c/Program\ Files/Webots
```

Consulte a documentação oficial de instalação do `webots_ros2` para a sua
distribuição antes da oficina.

## Compilação

```bash
cd ~/hospital_webots_ws
source /opt/ros/$ROS_DISTRO/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Experimento 1 — sem ROS 2

Abra diretamente no Webots:

```text
src/hospital_delivery/worlds/introduction.wbt
```

O mundo carrega automaticamente o controlador:

```text
controllers/straight_line_webots/straight_line_webots.py
```

O robô aguarda um segundo, movimenta as duas rodas a `4 rad/s` durante cinco
segundos e para.

Para entregar o exercício incompleto aos alunos, copie:

```text
student_templates/straight_line_webots.py
```

para a pasta do controlador.

## Experimento 2 — infraestrutura ROS 2

Terminal 1:

```bash
cd ~/hospital_webots_ws
source install/setup.bash
ros2 launch hospital_delivery activity.launch.py world:=hospital_l
```

Confira as interfaces em outro terminal:

```bash
source ~/hospital_webots_ws/install/setup.bash
ros2 topic type /cmd_vel
ros2 topic type /scan
```

Os tipos esperados são:

```text
geometry_msgs/msg/Twist
sensor_msgs/msg/LaserScan
```

## Experimento 3 — entrega em L

Com a simulação do experimento 2 aberta:

```bash
ros2 run hospital_delivery delivery_l --ros-args -p use_sim_time:=true
```

O percurso nominal é:

1. dois metros em linha reta;
2. parada de um segundo;
3. curva anti-horária de 90 graus;
4. um metro e meio em linha reta;
5. espera de cinco segundos na área verde.

## Experimento 4 — desafio com LiDAR

Feche o Webots anterior e carregue o mundo com carrinho:

```bash
ros2 launch hospital_delivery activity.launch.py \
  world:=hospital_l_challenge
```

Em outro terminal:

```bash
ros2 run hospital_delivery delivery_challenge \
  --ros-args -p use_sim_time:=true
```

O nó só aplica a segurança no segundo corredor. Isso evita que a parede em
frente à curva impeça a própria realização da curva. Quando o robô parar,
mova o objeto `movable hospital cart` para fora do corredor pela interface do
Webots; a missão continuará.

## Demonstrações em um comando

Missão comum:

```bash
ros2 launch hospital_delivery demo.launch.py
```

Desafio:

```bash
ros2 launch hospital_delivery demo.launch.py \
  challenge:=true world:=hospital_l_challenge
```

O launch de demonstração aguarda quatro segundos antes de iniciar a missão.
Em computadores lentos, prefira iniciar a simulação e a missão em terminais
separados.

## Arquivos destinados ao aluno e ao instrutor

- `student_templates/`: versões incompletas para distribuição;
- `hospital_delivery/delivery_l.py`: solução funcional da missão;
- `hospital_delivery/delivery_challenge.py`: solução funcional do desafio;
- `controllers/straight_line_webots/`: solução funcional sem ROS 2.

O instrutor deve manter as soluções fora do pacote entregue aos alunos, se a
atividade tiver caráter avaliativo.

## Parâmetros geométricos que devem permanecer coerentes

| Parâmetro | Valor |
|---|---:|
| Raio das rodas | 0,05 m |
| Metade da separação entre rodas | 0,16 m |
| Velocidade máxima das rodas | 12 rad/s |
| Primeiro trecho | 2,0 m |
| Segundo trecho | 1,5 m |

Se o `PROTO` for alterado para mudar o raio ou a posição das rodas, atualize
também `resource/hospital_robot.urdf`.

## Verificações locais

Na raiz do pacote:

```bash
python3 test/validate_project.py
```

O script valida Python, XML, referências dos mundos, delimitadores dos arquivos
Webots e a presença dos arquivos essenciais. Ele não substitui um teste de
execução no Webots.

## Referências técnicas

- [Tutorial oficial de integração Webots–ROS 2](https://docs.ros.org/en/rolling/Tutorials/Advanced/Simulators/Webots/Setting-Up-Simulation-Webots-Basic.html)
- [Pacotes oficiais webots_ros2](https://github.com/cyberbotics/webots_ros2)
