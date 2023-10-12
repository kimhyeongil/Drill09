# 이것은 각 상태들을 객체로 구현한 것임.
import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a


def space_down(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == "TIME_OUT"


def right_down(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def a_down(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e):
            boy.dir, boy.action = -1, 0
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        print("Idle Exit")

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class AutoRun:
    @staticmethod
    def enter(boy, e):
        boy.action = 1
        boy.start_time = get_time()
        boy.dir = 1
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time >= 5.0:
            boy.state_machine.handle_event(("TIME_OUT", 0))
        if boy.x >= 800 or boy.x <= 0:
            boy.dir *= -1
            if boy.action == 0:
                boy.action = 1
            else:
                boy.action = 0
        boy.x += boy.dir * 20

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 35, 200, 200
        )


class Idle:
    nFrame = 8

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % Idle.nFrame
        if get_time() - boy.start_time > 3.0:
            boy.state_machine.handle_event(("TIME_OUT", 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class Sleep:
    @staticmethod
    def enter(boy, e):
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.action == 3:
            boy.image.clip_composite_draw(
                boy.frame * 100,
                boy.action * 100,
                100,
                100,
                math.pi / 2,
                "",
                boy.x - 25,
                boy.y - 25,
                100,
                100,
            )
        elif boy.action == 2:
            boy.image.clip_composite_draw(
                boy.frame * 100,
                boy.action * 100,
                100,
                100,
                -math.pi / 2,
                "",
                boy.x + 25,
                boy.y - 25,
                100,
                100,
            )
        pass


class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.state_table = {
            Sleep: {
                space_down: Idle,
                right_down: Run,
                left_down: Run,
                right_up: Run,
                left_up: Run,
            },
            Idle: {
                time_out: Sleep,
                right_down: Run,
                left_down: Run,
                right_up: Run,
                left_up: Run,
                a_down: AutoRun,
            },
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle},
            AutoRun: {
                right_down: Run,
                left_down: Run,
                right_up: Run,
                left_up: Run,
                time_out: Idle,
            },
        }

    def start(self):
        self.cur_state.enter(self.boy, ("START", 0))

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)

    def handle_event(self, event):  # state event handling
        for check_event, next_state in self.state_table[self.cur_state].items():
            if check_event(event):
                self.cur_state.exit(self.boy, event)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, event)
                return True  # 성공적으로 이벤트 변환
        return False  # 이벤트 소모 실패


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.dir = 0
        self.frame = 0
        self.action = 3
        self.image = load_image("animation_sheet.png")
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # pico2d event ----> state machine event
        self.state_machine.handle_event(("INPUT", event))

    def draw(self):
        self.state_machine.draw()
