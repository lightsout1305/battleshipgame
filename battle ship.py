from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Shot out of the board!'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Space already shot once!'


class BoardWrongShipException(BoardException):
    pass


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class Ship:
    def __init__(self, fore, length, orient):
        self.fore = fore
        self.length = length
        self.orient = orient
        self.lives = length

    @property
    def points(self):
        ship_points = []
        for i in range(self.length):
            cur_x = self.fore.x
            cur_y = self.fore.y

            if self.orient == 0:
                cur_x += i

            elif self.orient == 1:
                cur_y += i

            ship_points.append(Point(cur_x, cur_y))

        return ship_points

    def hit(self, shot):
        return shot in self.points


class Board:
    def __init__(self, hidden=False, size=6):
        self.hidden = hidden
        self.size = size
        self.count = 0
        self.field = [['O'] * size for _ in range(size)]
        self.occupied = []
        self.ships_quantity = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' | '

        if self.hidden:
            res = res.replace('▇', 'O')
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, 1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.points:
            for dx, dy in near:
                cur = Point(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.occupied:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.occupied.append(cur)

    def add_ship(self, ship):
        for d in ship.points:
            if self.out(d) or d in self.occupied:
                raise BoardWrongShipException()
        for d in ship.points:
            self.field[d.x][d.y] = '▇'
            self.occupied.append(d)

        self.ships_quantity.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.occupied:
            raise BoardUsedException()

        self.occupied.append(d)

        for ship in self.ships_quantity:
            if d in ship.points:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Ship destroyed!')
                    return False
                else:
                    print('Ship hit!')
                    return True

        self.field[d.x][d.y] = '.'
        print('Missed!')
        return False

    def start_game(self):
        self.occupied = []

    def defeat(self):
        return self.count == len(self.ships_quantity)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def turn(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class Computer(Player):
    def ask(self):
        d = Point(randint(0, 5), randint(0, 5))
        print(f'Computer turn: {d.x + 1}, {d.y + 1}')
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Your turn: ").split()

            if len(cords) != 2:
                print("Type two coordinates!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Numbers required!")
                continue

            x, y = int(x), int(y)

            return Point(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hidden = True
        self.comp = Computer(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for lth in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), lth, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.start_game()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    @staticmethod
    def greet():
        print('-------------------------------')
        print('Welcome to the Battleship game!')
        print('-------------------------------')
        print('    To choose where to shoot   ')
        print('         Type two digits       ')
        print('   The first one is the line   ')
        print('  The second one is the column ')

    def print_boards(self):
        print('-' * 20)
        print('User board')
        print(self.us.board)
        print('-' * 20)
        print('Computer board')
        print(self.comp.board)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print('-' * 20)
                repeat = self.us.turn()
            else:
                print('-' * 20)
                print('Computer turn:')
                repeat = self.comp.turn()
            if repeat:
                num -= 1

            if self.comp.board.defeat():
                self.print_boards()
                print('-' * 20)
                print('You won!')
                break

            if self.us.board.defeat():
                self.print_boards()
                print('-' * 20)
                print('Computer won!')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
