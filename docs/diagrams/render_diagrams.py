"""Render repository-native SVG UML diagrams without external services.

Run: python3 docs/diagrams/render_diagrams.py
PlantUML files provide equivalent editable notation; layout is defined here.
"""
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

BASE = Path(__file__).parent


def canvas(width, height, title):
    root = Element('svg', xmlns='http://www.w3.org/2000/svg', width=str(width), height=str(height), viewBox=f'0 0 {width} {height}')
    SubElement(root, 'title').text = title
    SubElement(root, 'rect', width='100%', height='100%', fill='#ffffff')
    defs = SubElement(root, 'defs')
    marker = SubElement(defs, 'marker', id='arrow', viewBox='0 0 10 10', refX='9', refY='5', markerWidth='8', markerHeight='8', orient='auto-start-reverse')
    SubElement(marker, 'path', d='M 0 0 L 10 5 L 0 10 z', fill='#334155')
    return root


def text(root, x, y, label, size=18, anchor='middle'):
    el = SubElement(root, 'text', x=str(x), y=str(y), fill='#0f172a', **{'font-family':'DejaVu Sans, sans-serif','font-size':str(size),'text-anchor':anchor})
    for i, line in enumerate(label.split('\n')):
        SubElement(el, 'tspan', x=str(x), dy='0' if i == 0 else str(size+7)).text = line


def rect(root, x, y, w, h, radius=0, fill='#eff6ff'):
    SubElement(root, 'rect', x=str(x), y=str(y), width=str(w), height=str(h), rx=str(radius), fill=fill, stroke='#334155', **{'stroke-width':'2'})


def line(root, path, arrow=True):
    attrs = {'d':path,'fill':'none','stroke':'#334155','stroke-width':'2'}
    if arrow:
        attrs['marker-end']='url(#arrow)'
    SubElement(root, 'path', **attrs)


def actor(root, x, y, label):
    SubElement(root, 'circle', cx=str(x), cy=str(y), r='16', fill='white', stroke='#334155', **{'stroke-width':'2'})
    line(root, f'M{x} {y+16} V{y+68} M{x-30} {y+35} H{x+30} M{x} {y+68} L{x-25} {y+102} M{x} {y+68} L{x+25} {y+102}', False)
    text(root, x, y+132, label)


def save(root, name):
    ElementTree(root).write(BASE / name, encoding='utf-8', xml_declaration=True)


root = canvas(1100, 1060, 'TrafficMaster — UML use case')
text(root, 550, 40, 'TrafficMaster: варианты использования', 25)
rect(root, 340, 75, 710, 940, fill='#ffffff')
text(root, 695, 110, 'Граница системы: REST API', 20)
actor(root, 120, 180, 'Гость')
actor(root, 120, 580, 'Пользователь')
labels = [
    'UR-01 · Зарегистрироваться и войти',
    'UR-02 · Подготовить учебный материал',
    'UR-03 · Изменить / удалить материал',
    'UR-04 · Найти и скопировать колоду',
    'UR-05 · Повторять карточки',
    'UR-06 · Просмотреть / сбросить прогресс',
    'UR-07 · Завершить доступ',
]
for i, label in enumerate(labels):
    y = 180 + i*120
    line(root, f'M150 615 L395 {y}', False) if i else None
    SubElement(root, 'ellipse', cx='700', cy=str(y), rx='305', ry='42', fill='#eff6ff', stroke='#334155', **{'stroke-width':'2'})
    text(root, 700, y+6, label, 18)
line(root, 'M150 215 L395 180', False)
line(root, 'M150 215 L395 540', False)
text(root, 258, 366, 'только каталог', 15)
text(root, 700, 985, 'Копирование и UR-02…UR-07 требуют сессии.', 16)
save(root, 'use-cases.svg')

root = canvas(1280, 1040, 'CardProgress — UML state machine')
text(root, 640, 38, 'CardProgress: жизненный цикл объекта', 25)
rect(root, 65, 80, 1150, 720, 16, '#ffffff')
text(root, 640, 118, 'Прогресс существует', 21)
line(root, 'M65 140 H1215', False)
# nested initial pseudostate
SubElement(root, 'circle', cx='135', cy='290', r='10', fill='#0f172a')
line(root, 'M145 290 H245')
text(root, 190, 252, 'создание', 15)
for x, y, label in [(245,245,'NEW'), (835,245,'LEARNING'), (835,555,'REVIEW'), (245,555,'RELEARNING')]:
    rect(root, x, y, 200, 90, 16)
    text(root, x+100, y+52, label, 22)
line(root, 'M445 290 H835')
text(root, 640, 252, 'T01: AGAIN · T02: HARD', 17)
text(root, 640, 277, 'T03: GOOD [r+1 < n]', 17)
line(root, 'M445 325 L835 565')
text(root, 690, 380, 'T04: EASY или', 17)
text(root, 690, 406, 'GOOD [r+1 ≥ n]', 17)
line(root, 'M935 335 V555')
text(root, 1040, 430, 'T04: EASY /', 17)
text(root, 1040, 456, 'GOOD [r+1 ≥ n]', 17)
line(root, 'M880 245 V190 H990 V245')
text(root, 935, 176, 'T01, T02, T03', 16)
line(root, 'M1035 575 H1160 V680 H1035 V630')
text(root, 1100, 714, 'T05 / HARD, GOOD, EASY', 15)
text(root, 1100, 738, 'T07 / AGAIN [m=0]', 15)
line(root, 'M835 590 H445')
text(root, 640, 570, 'T06: AGAIN [m>0]', 18)
line(root, 'M445 625 H790 V630 H835')
text(root, 640, 663, 'T09: EASY / GOOD [r+1 ≥ m]', 16)
text(root, 640, 690, 'или любая оценка [m=0]', 16)
line(root, 'M245 575 H170 V690 H285 V645')
text(root, 260, 730, 'T08: AGAIN / HARD /', 16)
text(root, 260, 755, 'GOOD [r+1 < m], m>0', 16)
line(root, 'M640 800 V935')
text(root, 660, 846, 'T10: сброс прогресса /', 18, 'start')
text(root, 660, 875, 'удаление карточки / пользователя', 18, 'start')
SubElement(root, 'circle', cx='640', cy='950', r='15', fill='white', stroke='#0f172a', **{'stroke-width':'2'})
SubElement(root, 'circle', cx='640', cy='950', r='10', fill='#0f172a')
text(root, 640, 1007, 'Условия и действия T01…T10 раскрыты в таблице жизненного цикла.', 17)
save(root, 'card-progress.svg')
