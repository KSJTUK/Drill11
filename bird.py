# 이것은 각 상태들을 객체로 구현한 것임.

# 새의 크기는 가로 세로가 2m가 되게 할 예정
# 새는 현재 가로가 전체 182p이므로
# PIXELPERMETER == 182 / 2m

BIRD_FRAME_PIXEL = (182, 163)
PIXEL_PER_METER = (182.0 / 2.0)
RUN_SPEED_KMPH = 10.0 # 20km/h
RUN_SPEED_MPM = RUN_SPEED_KMPH * 1000.0 / 60.0
RUN_SPEED_MPS = RUN_SPEED_MPM / 60.0
RUN_SPEED_PPS = RUN_SPEED_MPS * PIXEL_PER_METER

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8
FRAMES_PER_TIME = ACTION_PER_TIME * FRAMES_PER_ACTION

from pico2d import get_time, load_image, load_font, clamp,  SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from ball import Ball, BigBall
import game_world
import game_framework

# state event check
# ( state event type, event value )

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] == 'TIME_OUT'

# time_out = lambda e : e[0] == 'TIME_OUT'




# bird Run Speed
# fill here

# bird Action Speed
# fill here










class Idle:

    @staticmethod
    def enter(bird, e):
        if bird.face_dir == -1:
            bird.action = 0
        elif bird.face_dir == 1:
            bird.action = 0
        bird.dir = 0
        bird.frame = 0
        bird.frame_size = 4
        bird.wait_time = get_time() # pico2d import 필요
        pass

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()
        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_TIME * game_framework.frame_time) % bird.frame_size
        if get_time() - bird.wait_time > 2:
            bird.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def draw(bird):
        bird.image.clip_composite_draw(int(bird.frame) * BIRD_FRAME_PIXEL[0],
                                       bird.action * BIRD_FRAME_PIXEL[1], BIRD_FRAME_PIXEL[0], BIRD_FRAME_PIXEL[1],
                                       0, '', bird.x, bird.y,
                                       PIXEL_PER_METER, PIXEL_PER_METER) # 2미터



class Run:

    @staticmethod
    def enter(bird, e):
        if right_down(e) or left_up(e): # 오른쪽으로 RUN
            bird.dir, bird.action, bird.face_dir = 1, 1, 1
        elif left_down(e) or right_up(e): # 왼쪽으로 RUN
            bird.dir, bird.action, bird.face_dir = -1, 1, -1

        bird.frame_size = 5

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()

        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_TIME * game_framework.frame_time) % bird.frame_size
        # bird.x += bird.dir * 5
        bird.x += bird.dir * RUN_SPEED_PPS * game_framework.frame_time
        bird.x = clamp(25, bird.x, 1600-25)


    @staticmethod
    def draw(bird):
        bird.image.clip_composite_draw(int(bird.frame) * BIRD_FRAME_PIXEL[0],
                                       bird.action * BIRD_FRAME_PIXEL[1], BIRD_FRAME_PIXEL[0], BIRD_FRAME_PIXEL[1],
                                       0, '', bird.x, bird.y,
                                       PIXEL_PER_METER, PIXEL_PER_METER)



class Sleep:

    @staticmethod
    def enter(bird, e):
        bird.frame = 0
        bird.frame_size = 4
        pass

    @staticmethod
    def exit(bird, e):
        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_TIME * game_framework.frame_time) % bird.frame_size



    @staticmethod
    def draw(bird):
        if bird.face_dir == -1:
            bird.image.clip_composite_draw(int(bird.frame) * BIRD_FRAME_PIXEL[0],
                                           bird.action * BIRD_FRAME_PIXEL[1], BIRD_FRAME_PIXEL[0], BIRD_FRAME_PIXEL[1],
                                          -3.141592 / 2, '', bird.x + 25, bird.y - 25,
                                            PIXEL_PER_METER, PIXEL_PER_METER)
        else:
            bird.image.clip_composite_draw(int(bird.frame) * BIRD_FRAME_PIXEL[0],
                                           bird.action * BIRD_FRAME_PIXEL[1], BIRD_FRAME_PIXEL[0], BIRD_FRAME_PIXEL[1],
                                           3.141592 / 2, '', bird.x - 25, bird.y - 25,
                                           PIXEL_PER_METER, PIXEL_PER_METER)


class StateMachine:
    def __init__(self, bird):
        self.bird = bird
        self.cur_state = Idle
        self.transitions = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, space_down: Idle},
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, space_down: Run},
            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run}
        }

    def start(self):
        self.cur_state.enter(self.bird, ('NONE', 0))

    def update(self):
        self.cur_state.do(self.bird)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.bird, e)
                self.cur_state = next_state
                self.cur_state.enter(self.bird, e)
                return True

        return False

    def draw(self):
        self.cur_state.draw(self.bird)





class Bird:
    def __init__(self):
        self.x, self.y = 400, 300
        self.frame = 0
        self.frame_size = 4
        self.action = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('bird_animation.png')
        self.font = load_font('ENCR10B.TTF', 16)
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        self.item = 'Ball'


    def fire_ball(self):

        if self.item ==   'Ball':
            ball = Ball(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        elif self.item == 'BigBall':
            ball = BigBall(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        # if self.face_dir == -1:
        #     print('FIRE BALL LEFT')
        #
        # elif self.face_dir == 1:
        #     print('FIRE BALL RIGHT')

        pass

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.x - 60, self.y - 50, f'{get_time()}', (255, 255, 0))