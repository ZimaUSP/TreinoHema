"""Validação estática que não depende de ROS 2 ou Webots instalados."""

import ast
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


PACKAGE_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'package.xml',
    'setup.py',
    'setup.cfg',
    'protos/HospitalRobot.proto',
    'worlds/introduction.wbt',
    'worlds/hospital_l.wbt',
    'worlds/hospital_l_challenge.wbt',
    'resource/hospital_robot.urdf',
    'launch/activity.launch.py',
    'launch/demo.launch.py',
    'hospital_delivery/webots_driver.py',
    'hospital_delivery/delivery_l.py',
    'hospital_delivery/delivery_challenge.py',
    'controllers/straight_line_webots/straight_line_webots.py',
]


def check_required_files(errors):
    for relative_path in REQUIRED_FILES:
        path = PACKAGE_ROOT / relative_path
        if not path.is_file():
            errors.append(f'Arquivo ausente: {relative_path}')


def check_python_syntax(errors):
    for path in PACKAGE_ROOT.rglob('*.py'):
        try:
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        except SyntaxError as exception:
            errors.append(f'Python inválido em {path}: {exception}')


def check_xml(errors):
    for relative_path in ['package.xml', 'resource/hospital_robot.urdf']:
        path = PACKAGE_ROOT / relative_path
        try:
            ET.parse(path)
        except ET.ParseError as exception:
            errors.append(f'XML inválido em {relative_path}: {exception}')


def check_webots_files(errors):
    for path in list(PACKAGE_ROOT.rglob('*.wbt')) + list(
        PACKAGE_ROOT.rglob('*.proto')
    ):
        text = path.read_text(encoding='utf-8')
        if not text.startswith('#VRML_SIM'):
            errors.append(f'Cabeçalho Webots ausente em {path}')
        if text.count('{') != text.count('}'):
            errors.append(f'Chaves desequilibradas em {path}')
        if text.count('[') != text.count(']'):
            errors.append(f'Colchetes desequilibrados em {path}')


def check_cross_references(errors):
    intro = (PACKAGE_ROOT / 'worlds/introduction.wbt').read_text(
        encoding='utf-8'
    )
    hospital = (PACKAGE_ROOT / 'worlds/hospital_l.wbt').read_text(
        encoding='utf-8'
    )
    challenge = (
        PACKAGE_ROOT / 'worlds/hospital_l_challenge.wbt'
    ).read_text(encoding='utf-8')
    urdf = (PACKAGE_ROOT / 'resource/hospital_robot.urdf').read_text(
        encoding='utf-8'
    )

    expected_fragments = [
        (intro, 'controller "straight_line_webots"', 'controlador nativo'),
        (hospital, 'controller "<extern>"', 'controlador externo'),
        (challenge, 'movable hospital cart', 'carrinho do desafio'),
        (urdf, 'hospital_delivery.webots_driver.HospitalRobotDriver', 'plugin'),
        (urdf, '<topicName>/scan</topicName>', 'tópico do LiDAR'),
    ]

    for text, fragment, description in expected_fragments:
        if fragment not in text:
            errors.append(f'Referência ausente: {description}')


def main():
    errors = []
    check_required_files(errors)
    check_python_syntax(errors)
    check_xml(errors)
    check_webots_files(errors)
    check_cross_references(errors)

    if errors:
        print('Falhas encontradas:')
        for error in errors:
            print(f'- {error}')
        return 1

    print('Validação estática concluída sem erros.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
