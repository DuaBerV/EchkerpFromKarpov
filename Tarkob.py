import pygame as pg
import math
import random
import time
import sys
import os
import main
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import sqlite3


class Boss:
    def __init__(self, size, hp):
        self.size_x = 200
        self.size_y = 200
        self.pos_x = size[0] // 2 - self.size_x // 2
        self.pos_y = size[1] // 2 - self.size_y // 2
        self.hp = hp

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(79, 0, 20), (self.pos_x, self.pos_y, self.size_x, self.size_y))

    def health(self, attack, screen):
        self.hp -= attack
        pg.draw.rect(screen, pg.Color(100, 21, 43), (self.pos_x, self.pos_y, self.size_x, self.size_y))

    def get_pos_for_attack(self):
        return self.pos_x, self.pos_y, self.size_x, self.size_y

    def get_health(self):
        return self.hp


class Enemy:
    def __init__(self, x, y, to_x, to_y, time_attack, all_sprites):
        self.x = x
        self.y = y
        self.height = 30
        self.weight = 30
        self.speed = 3
        self.hp = 100
        self.time_attack = time_attack
        self.time_to_attack = 0

        self.to_x = to_x
        self.to_y = to_y

        self.enemy_sprite = pg.sprite.Sprite()
        self.enemy_sprite.image = load_image("Enemy.png")
        self.enemy_sprite.rect = self.enemy_sprite.image.get_rect()
        self.enemy_sprite.rect.x, self.enemy_sprite.rect.y = self.x, self.y
        all_sprites.add(self.enemy_sprite)

    def spawn(self, size):
        if self.y < 0:
            self.y += self.speed

        if self.y > size[1]:
            self.y -= self.speed

    def render(self, screen):
        # pg.draw.rect(screen, pg.Color(79,0,20), (self.x, self.y, self.weight, self.height))
        pass

    def get_pos_for_attack(self):
        return self.x, self.y, self.weight, self.height

    def get_health(self):
        return self.hp

    def health(self, attack, screen):
        self.hp -= attack

    def move(self, size):
        dx, dy = self.to_x - self.x, self.to_y - self.y
        lenth = math.hypot(dx, dy)
        vector_x = dx / lenth
        vector_y = dy / lenth
        self.x += self.speed * vector_x
        self.y += self.speed * vector_y
        self.time_to_attack += 1
        if self.time_to_attack >= self.time_attack:
            self.time_to_attack = 0

        if self.x - 2 <= self.to_x <= self.x + 2 and self.y - 2 <= self.to_y <= self.y + 2:
            self.to_x = random.randint(0, size[0])
            self.to_y = random.randint(0, size[1])

    def get_attack(self):
        return self.time_to_attack

    def get_sprite(self):
        return self.enemy_sprite


class Bullet:
    def __init__(self, player_pos, screen):
        self.x = player_pos[0]
        self.y = player_pos[1]
        self.vector_x = 0
        self.vector_y = 0
        self.speed = 7
        self.screen = screen

    def spawn(self, x, y):
        dx, dy = x - self.x, y - self.y
        lenth = math.hypot(dx, dy)
        self.vector_x = dx / lenth
        self.vector_y = dy / lenth

    def render(self, screen):
        self.x += self.speed * self.vector_x
        self.y += self.speed * self.vector_y
        pg.draw.circle(screen, pg.Color(255, 0, 0), (self.x, self.y), 3)

    def attack(self, unit):
        unit_pos = unit.get_pos_for_attack()
        unit_x1 = unit_pos[0]
        unit_x2 = unit_pos[2]
        unit_y1 = unit_pos[1]
        unit_y2 = unit_pos[3]
        if unit_x1 <= self.x <= unit_x1 + unit_x2 and unit_y1 <= self.y <= unit_y1 + unit_y2:
            unit.health(50, self.screen)
            return 1

    def get_pos(self):
        return self.x, self.y


class Player:
    def __init__(self, weight, height, size):
        self.start_time = 0
        self.ost_time = 1

        self.height = height
        self.weight = weight
        self.pos_x = 5
        self.pos_y = size[1] // 2
        self.speed = 3
        self.ammo = 20
        self.hp = 1000
        self.stamina = 1000

    def render(self, screen):
        # pg.draw.rect(screen, pg.Color(0, 0, 0), (self.pos_x, self.pos_y, self.weight, self.height))
        pass

    def move(self, keys, size, endgame):
        if keys[pg.K_LSHIFT] and self.stamina > 10:
            self.speed = 5
            self.stamina -= 2
        else:
            self.speed = 3
            if self.stamina < 1000:
                self.stamina += 1

        if keys[pg.K_w]:
            self.pos_y -= self.speed
        if keys[pg.K_s]:
            self.pos_y += self.speed
        if keys[pg.K_d]:
            self.pos_x += self.speed
        if keys[pg.K_a]:
            self.pos_x -= self.speed

        if self.pos_x < 0:
            self.pos_x = 0
        if self.pos_y < 0:
            self.pos_y = 0
        if self.pos_x + self.weight + 2 > size[0] and endgame:
            self.pos_x = size[0] - self.weight + 2
        if self.pos_x + self.weight + 2 > size[0] and not endgame:
            self.pos_x = size[0] - self.weight
        if self.pos_y + self.height > size[1]:
            self.pos_y = size[1] - self.height

    def open_case(self, case):
        if len(case) > 0:
            for xy in case:
                x = xy[0]
                y = xy[1]
                if (self.pos_x - 30 <= x <= self.pos_x + 60) and (self.pos_y - 30 <= y <= self.pos_y + 30):
                    self.set_ammo(20)
                    case.remove(xy)

    def get_stamina(self):
        return self.stamina

    def get_health(self):
        return self.hp

    def health(self, attack, screen):
        self.hp -= attack

    def get_pos(self):
        return self.pos_x, self.pos_y

    def get_pos_for_attack(self):
        return self.pos_x, self.pos_y, self.weight, self.height

    def get_ammo(self):
        return self.ammo

    def set_ammo(self, ammo):
        self.ammo += ammo

    def go_out(self, size, screen, level, name):
        if not (size[0] - size[0] // 65 <= self.pos_x <= size[0] - size[0] // 65 + size[0] // 65 and
                size[1] // 4 <= self.pos_y <= size[1] // 4 + size[1] // 2):
            self.start_time = time.time()

        if size[0] - size[0] // 65 <= self.pos_x <= size[0] - size[0] // 65 + size[0] // 65 and \
                size[1] // 4 <= self.pos_y <= size[1] // 4 + size[1] // 2:
            f = pg.font.Font(None, 100)
            self.ost_time = round(10 - (time.time() - self.start_time), 1)
            if self.ost_time < 0.1:
                self.ost_time = 0
            text = f.render(f'{self.ost_time} Выход с локации', True, (0, 200, 0))
            screen.blit(text, (size[0] // 3, size[1] // 2))
            if self.ost_time <= 0:
                f.render(f'{self.ost_time} Выход с локации', True, (0, 200, 0))
                main(level + 1, name)


class Field:
    def __init__(self, size):
        self.height = size[1]
        self.weight = size[0]
        self.size = size
        self.plates = [(random.randint(0, size[0]), random.randint(0, size[1]),
                        random.randint(1, 100), random.randint(1, 100)) for _ in range(100)]
        self.cases = [
            (random.randint(0, size[0]), random.randint(0, size[1]), 30, 30) for _ in range(random.randint(5, 15))]

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(90, 90, 90), (0, 0, self.weight, self.height))
        for plate in self.plates:
            pg.draw.rect(screen, pg.Color(100, 100, 100), plate)
        for case in self.cases:
            pg.draw.rect(screen, pg.Color(121, 85, 61), case)

        if len(self.cases) == 0:
            self.cases.append((random.randint(0, self.size[0]), random.randint(0, self.size[1]), 30, 30))

    def send_cases(self):
        return self.cases


class EndGame:
    def __init__(self, size):
        self.x = size[0] - size[0] // 65
        self.y = size[1] // 4
        self.size_x = size[0] - self.x
        self.size_y = size[1] // 2

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(38, 171, 29), (self.x, self.y, self.size_x, self.size_y))


class UI:
    def __init__(self, player, boss):
        self.player_hp = player.get_health()
        self.player_stamina = player.get_stamina()
        self.boss_hp = boss.get_health()
        self.player_ammo = None

    def render(self, player, boss, screen, size):
        self.player_hp = player.get_health()
        self.player_stamina = player.get_stamina()
        self.player_ammo = player.get_ammo()
        if boss == 0:
            self.boss_hp = 0
        else:
            self.boss_hp = boss.get_health()

        f = pg.font.Font(None, 30)
        text = f.render(f'Осталось здоровья: {self.player_hp}', True, (0, 200, 0))
        pg.draw.rect(screen, pg.Color(0, 255, 0), (size[0] // 100, size[1] // 10, self.player_hp // 3, size[1] // 100))
        #screen.blit(text, (size[0] // 100, size[1] // 10))

        text = f.render(f'Осталось выносливости: {self.player_stamina}', True, (0, 200, 0))
        pg.draw.rect(screen, pg.Color(219, 197, 0), (size[0] // 100, size[1] // 10 + size[1] // 25,
                                                   self.player_stamina // 3, size[1] // 100))
        #screen.blit(text, (size[0] // 100, size[1] // 10 + size[1] // 15))

        text = f.render(f'Осталось патрон: {self.player_ammo}', True, (0, 200, 0))
        screen.blit(text, (size[0] // 100, size[1] // 10 + (size[1] // 25) * 2))

        text = f.render(f'Осталось здоровья босса: {self.boss_hp}', True, (0, 200, 0))
        screen.blit(text, (size[0] - size[0] // 5, size[1] // 10))


def load_image(name):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image


def main(level, name):
    pg.init()
    clock = pg.time.Clock()
    FPS = 100
    size = (1920, 1080)
    screen = pg.display.set_mode(size)
    pg.display.set_caption("Эщкерп пром Карков")
    field = Field(size)
    level = level
    name = name
    end = False

    all_sprites = pg.sprite.Group()
    player_sprite = pg.sprite.Sprite()
    player_sprite.image = load_image("Player.png")
    player_sprite.rect = player_sprite.image.get_rect()
    all_sprites.add(player_sprite)

    boss_sprite = pg.sprite.Sprite()
    boss_sprite.image = load_image("Boss.png")
    boss_sprite.rect = boss_sprite.image.get_rect()
    all_sprites.add(boss_sprite)

    player = Player(30, 30, size)
    players = [player]
    boss = Boss(size, 1000 + 100 * (level - 1))
    bosses = [boss]
    enemies = []

    key = []
    bullets = []
    enemy_bullets = []
    running = True
    ui = UI(player, boss)

    while running:
        if player.get_health() <= 0:
            players = []
        if len(players) > 0:
            player_sprite.rect.x, player_sprite.rect.y = player.get_pos()[0], player.get_pos()[1]
            keys = pg.key.get_pressed()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        running = False
                        end = True

                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1 and player.get_ammo() > 0:
                        bullet = Bullet(player.get_pos(), screen)
                        bullet.spawn(event.pos[0], event.pos[1])
                        bullets.append(bullet)
                        player.set_ammo(-1)

            field.render(screen)
            player.render(screen)

            if len(enemies) < level and len(bosses) != 0:
                enemy = Enemy(random.randint(0, size[0]), random.choice([-2, size[1] + 2]), random.randint(0, size[0]),
                              random.randint(0, size[1]), random.randint(20, 50), all_sprites)
                enemies.append(enemy)

            for enemy in enemies:
                enemy_sprite = enemy.get_sprite()
                enemy_sprite.rect.x, enemy_sprite.rect.y = enemy.get_pos_for_attack()[0], enemy.get_pos_for_attack()[1]
                if enemy.get_pos_for_attack()[1] <= 0:
                    enemy.spawn(size)
                else:
                    enemy.move(size)
                    if enemy.get_attack() == 0:
                        enemy_bullet = Bullet((enemy.get_pos_for_attack()[0], enemy.get_pos_for_attack()[1]), screen)
                        enemy_bullet.spawn(player.get_pos_for_attack()[0], player.get_pos_for_attack()[1])
                        enemy_bullets.append(enemy_bullet)
                enemy.render(screen)

                all_sprites.update()
                if enemy.get_health() <= 0:
                    enemy_sprite.rect.x, enemy_sprite.rect.y = -1000, -1000
                    enemies.remove(enemy)

            for boss in bosses:
                boss_sprite.rect.x, boss_sprite.rect.y = boss.get_pos_for_attack()[0], boss.get_pos_for_attack()[1]
                boss.render(screen)
                if boss.get_health() <= 0:
                    bosses.remove(boss)
                    boss_sprite.rect.x, boss_sprite.rect.y = -1000, -1000
                else:
                    enemy_bullet = Bullet((boss.get_pos_for_attack()[0] + boss.get_pos_for_attack()[2] // 2,
                                           boss.get_pos_for_attack()[1] + boss.get_pos_for_attack()[3] // 2), screen)
                    enemy_bullet.spawn(player.get_pos_for_attack()[0], player.get_pos_for_attack()[1])
                    enemy_bullets.append(enemy_bullet)
            if len(bosses) == 0:
                endgame = EndGame(size)
                endgame.render(screen)
                player.go_out(size, screen, level, name)
                MyWidget()

            if len(bosses) == 0:
                endgame = True
            else:
                endgame = False
            player.move(keys, size, endgame)
            if keys[pg.K_e]:
                player.open_case(field.send_cases())

            for enemy_bullet in enemy_bullets:
                enemy_bullet.render(screen)
                if enemy_bullet.attack(player):
                    enemy_bullets.remove(enemy_bullet)

            for bullet in bullets:
                bullet.render(screen)
                if bullet.attack(boss) if len(bosses) > 0 else 0:
                    bullets.remove(bullet)

                for enemy in enemies:
                    if bullet.attack(enemy) if len(enemies) > 0 else 0:
                        try:
                            bullets.remove(bullet)
                        except ValueError:
                            pass

                xy = bullet.get_pos()
                x = xy[0]
                y = xy[1]
                if x < 0 or x > size[0] or y < 0 or y > size[1]:
                    if bullet in bullets:
                        bullets.remove(bullet)

            if level == 1:
                f = pg.font.Font(None, 15)
                text = f.render('WASD - управление, SHIFT - бег, E - подбор патронов, P - Выход из игры',
                                True, (0, 200, 0))
                screen.blit(text, (text.get_rect(center=(size[0] // 2, size[1] - size[1] // 10))))

            all_sprites.draw(screen)

            if len(bosses) != 0:
                ui.render(player, boss, screen, size)
            else:
                ui.render(player, 0, screen, size)

        if len(players) == 0:
            f = pg.font.Font(None, 100)
            text = f.render(f'ТЫ ПРОИГРАЛ уровень: {level}', True, (200, 0, 0))
            screen.blit(text, (text.get_rect(center=(size[0] // 2, size[1] // 2))))
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.MOUSEBUTTONDOWN and event.button == 1):
                    running = False

        pg.display.flip()
        clock.tick(FPS)
    database(name, 'update', level)
    if not end:
        main(level, name)
    else:
        sys.exit()


def database(name, command, level=1):
    con = sqlite3.connect("database.db", timeout=10)
    name = str(name)
    level = int(level)
    data = [name, level]
    command = command
    cur = con.cursor()
    res = cur.execute('''SELECT Name, Level FROM records''')
    res = res.fetchall()
    if command == 'insert':
        cur.execute('''INSERT INTO records(Name, Level)
        VALUES (?, ?)''', data)
        con.commit()
    elif command == 'select':
        res = cur.execute('''SELECT Name, Level FROM records''')
        res = res.fetchall()
        for i in res:
            if i[0] == name:
                return i[1]

    elif command == 'update':
        data = data[::-1]
        cur.execute('''UPDATE records SET Level = ? WHERE Name = ?''', data)
    con.commit()
    con.close()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Main.ui', self)
        self.setWindowTitle('Эщкерп пром Карков')
        self.pixmap = QPixmap('EFT.jpg')
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)

        con = sqlite3.connect("database.db")
        self.con = con
        cur = con.cursor()
        res = cur.execute("SELECT Name FROM records")
        res = res.fetchall()
        res = [x[0] for x in res]
        if self.lineEdit_2.text() not in res:
            database(self.lineEdit_2.text(), 'insert', self.lineEdit.text())
        else:
            self.label_4.setText('Максимальный уровень: ' + str(database(self.lineEdit_2.text(), 'select')))
        con.commit()
        con.close()

        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.name)
        self.label.setGeometry(30, 30, 770, 461)
        self.label.resize(730, 430)

    def run(self):
        main(int(self.lineEdit.text()), self.lineEdit_2.text())
        sys.exit()

    def name(self):
        con = sqlite3.connect("database.db")
        self.con = con
        cur = con.cursor()
        res = cur.execute("SELECT Name FROM records")
        res = res.fetchall()
        res = [x[0] for x in res]
        if self.lineEdit_2.text() not in res:
            database(self.lineEdit_2.text(), 'insert', self.lineEdit.text())
        else:
            self.label_4.setText('Максимальный уровень: ' + str(database(self.lineEdit_2.text(), 'select')))
        con.commit()
        con.close()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
