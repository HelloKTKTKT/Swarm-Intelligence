import random
import cv2
import numpy as np
import matplotlib.pyplot as plt

dim_x = 2000
dim_y = 1000
RESOURCE_N0 = (400, 350)
RESOURCE_N1 = (1100, 450)
MIDDLE_N = (1000, 500)
NEST_N = (1000, 750)
NODE_RADI = 50

INIT = 0
FORAGE_0 = 1
FORAGE_1 = 2
TRANSFER = 3

WALK_STEP = 5
ROBOT_NUM = 30
TASK_SHIFT_DELAY = 1

stack_limit = 30
stack_control = [15, 15]
theta = 1
power_n = 2


class Robot:
    def __init__(self, index):
        self.index = index
        self.position = [random.randint(0, dim_x), (random.randint(0, dim_y))]
        self.task = [MIDDLE_N, MIDDLE_N, INIT]
        self.arrival_flag = [0, 0]
        self.loaded = False
        self.walk_step = WALK_STEP
        self.lineup = 0
        self.probability = [0, 0, 0]

    def move(self, c_stack):
        start_nd = cal_distance(self.task[0], self.position)
        end_nd = cal_distance(self.task[1], self.position)
        event = 'none'
        if self.arrival_flag[0] == 0:
            if start_nd[-1] <= NODE_RADI:
                self.arrival_flag[0] = 1
                if self.task[-1] == INIT:
                    self.arrival_flag[1] = 1
                    event = 'finish_init'
                elif self.task[-1] == FORAGE_0 or self.task[-1] == FORAGE_1:
                    event = 'arrive_source'
                elif self.task[-1] == TRANSFER:
                    event = 'arrive_nest'
                else:  # nothing left
                    pass
            else:
                ratio = self.walk_step / start_nd[-1]
                self.position[0] += round(start_nd[0] * ratio)
                self.position[1] += round(start_nd[1] * ratio)
                self.position = position_fix(self.position[0], self.position[1])
        elif self.arrival_flag[1] == 0:
            if end_nd[-1] <= NODE_RADI:
                self.arrival_flag[1] = 1
                if self.task[-1] == INIT:
                    event = 'finish_init'
                elif self.task[-1] == FORAGE_0:
                    if c_stack[0] < stack_limit:
                        event = 'unload_0_permit'
                    else:
                        event = 'unload_0_deny'
                elif self.task[-1] == FORAGE_1:
                    if c_stack[1] < stack_limit:
                        event = 'unload_1_permit'
                    else:
                        event = 'unload_1_deny'
                elif self.task[-1] == TRANSFER:
                    event = 'finish_transfer'
                else:  # nothing left
                    pass
            else:
                ratio = self.walk_step / end_nd[-1]
                self.position[0] += round(end_nd[0] * ratio)
                self.position[1] += round(end_nd[1] * ratio)
                self.position = position_fix(self.position[0], self.position[1])
        elif self.lineup > 0:
            self.lineup -= 1
            if self.lineup == 0:
                event = 'finish_transfer_lineup'
        else:  # waiting for empty space, or lining up
            pass
        return event

    def match_random(self, c_stack):
        #choice = random.randint(1, 3)

        stimuli_0 = stack_control[0] - c_stack[0]
        stimuli_1 = stack_control[1] - c_stack[1]
        stimuli_2 = min(-stimuli_0, -stimuli_1)
        if stimuli_0 <= 0:
            self.probability[0] = 0
        else:
            self.probability[0] = stimuli_0 ** power_n / (stimuli_0 ** power_n + theta ** power_n)

        if stimuli_1 <= 0:
            self.probability[1] = 0
        else:
            self.probability[1] = stimuli_1 ** power_n / (stimuli_1 ** power_n + theta ** power_n)

        if stimuli_2 <= 0:
            self.probability[2] = 0
        else:
            self.probability[2] = stimuli_2 ** power_n / (stimuli_2 ** power_n + theta ** power_n)

        sum_value = 0
        for i in range(len(self.probability)):
            sum_value += self.probability[i]
        if sum_value == 0:
            # self.rematch_random(c_stack)
            choice = 3
        else:
            p_list = []
            for i in range(len(self.probability)):
                p_list.append(self.probability[i] / sum_value)

            p_sum = [0, 0, 0]
            for i in range(len(p_sum)):
                for j in range(0, i + 1):
                    p_sum[i] += p_list[j]

            roll = random.randint(0, 1000) / 1000
            if roll <= p_sum[0]:
                choice = 1
            elif roll <= p_sum[1]:
                choice = 2
            else:
                choice = 3
        return choice

    def trigger(self, c_event, c_stack):
        if c_event == 'none':
            pass
        elif c_event == 'finish_init':
            new_task = self.match_random(c_stack)
            if new_task == FORAGE_0:
                self.task = [RESOURCE_N0, MIDDLE_N, FORAGE_0]
                self.arrival_flag = [0, 0]
            elif new_task == FORAGE_1:
                self.task = [RESOURCE_N1, MIDDLE_N, FORAGE_1]
                self.arrival_flag = [0, 0]
            elif new_task == TRANSFER:
                self.lineup = TASK_SHIFT_DELAY
            else:  # nothing left
                pass
        elif c_event == 'arrive_source':
            self.loaded = True
        elif c_event == 'arrive_nest':
            self.loaded = False
        elif c_event == 'unload_0_permit':
            c_stack[0] += 1
            self.loaded = 0
            new_task = self.match_random(c_stack)
            if new_task == FORAGE_0:
                self.task = [RESOURCE_N0, MIDDLE_N, FORAGE_0]
                self.arrival_flag = [0, 0]
            elif new_task == FORAGE_1:
                self.task = [RESOURCE_N1, MIDDLE_N, FORAGE_1]
                self.arrival_flag = [0, 0]
            elif new_task == TRANSFER:
                self.lineup = TASK_SHIFT_DELAY
            else:  # nothing left
                pass
        elif c_event == 'unload_0_deny':
            self.arrival_flag[1] = 0
        elif c_event == 'unload_1_permit':
            c_stack[1] += 1
            self.loaded = 0
            new_task = self.match_random(c_stack)
            if new_task == FORAGE_0:
                self.task = [RESOURCE_N0, MIDDLE_N, FORAGE_0]
                self.arrival_flag = [0, 0]
            elif new_task == FORAGE_1:
                self.task = [RESOURCE_N1, MIDDLE_N, FORAGE_1]
                self.arrival_flag = [0, 0]
            elif new_task == TRANSFER:
                self.lineup = TASK_SHIFT_DELAY
            else:  # nothing left
                pass
        elif c_event == 'unload_1_deny':
            self.arrival_flag[1] = 0
        elif c_event == 'finish_transfer':
            new_task = self.match_random(c_stack)
            if new_task == FORAGE_0:
                self.task = [RESOURCE_N0, MIDDLE_N, FORAGE_0]
                self.arrival_flag = [0, 0]
            elif new_task == FORAGE_1:
                self.task = [RESOURCE_N1, MIDDLE_N, FORAGE_1]
                self.arrival_flag = [0, 0]
            elif new_task == TRANSFER:
                if c_stack[0] > 0 and c_stack[1] > 0:
                    c_stack[0] -= 1
                    c_stack[1] -= 1
                    self.loaded = True
                    self.arrival_flag = [0, 0]
                    self.task = [NEST_N, MIDDLE_N, TRANSFER]
                else:
                    self.arrival_flag[1] = 0
            else:  # nothing left
                pass
        elif c_event == 'finish_transfer_lineup':
            if c_stack[0] > 0 and c_stack[1] > 0:
                c_stack[0] -= 1
                c_stack[1] -= 1
                self.loaded = True
                self.arrival_flag = [0, 0]
                self.task = [NEST_N, MIDDLE_N, TRANSFER]
            else:  # change to finish finish_transfer state, re-trigger event finish_transfer
                self.arrival_flag[1] = 0
                self.task = [NEST_N, MIDDLE_N, TRANSFER]
        else:
            pass
        return c_stack


def cal_distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    distance = (dx ** 2 + dy ** 2) ** 0.5
    result = [dx, dy, distance]
    return result


def position_fix(x, y):
    if x > dim_x:
        x = 2 * dim_x - x
    elif x < 0:
        x = -x
    if y > dim_y:
        y = 2 * dim_y - y
    elif y < 0:
        y = -y
    return [x, y]


def spawn_robot():
    r_list = []
    for i in range(ROBOT_NUM):
        tem_robot = Robot(i)
        r_list.append(tem_robot)
    return r_list


def mouse_click_1(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        current_r_num = len(param)
        tem_robot = Robot(current_r_num)
        tem_robot.position = [x, y]
        param.append(tem_robot)
    elif event == cv2.EVENT_RBUTTONDOWN:
        while True:
            value = cv2.waitKey(1)
            if value == 32:
                break
    else:
        pass


def draw_map():
    map1 = np.zeros((dim_y, dim_x, 3), np.uint8)
    cv2.rectangle(map1, (0, 0), (dim_x + 1, dim_y + 1), (255, 255, 255), -1)
    cv2.circle(map1, RESOURCE_N0, NODE_RADI, (80, 80, 80), -1)
    cv2.circle(map1, RESOURCE_N1, NODE_RADI, (180, 180, 80), -1)
    cv2.circle(map1, MIDDLE_N, NODE_RADI, (50, 220, 120), -1)
    cv2.circle(map1, NEST_N, NODE_RADI, (100, 100, 200), -1)
    return map1


def plot_stack(stack_l, stack_m):
    x_axis = []
    for i in range(len(stack_l)):
        x_axis.append(i)
    plt.plot(x_axis, stack_l, label="stack_0")
    plt.plot(x_axis, stack_m, label="stack_1")
    plt.legend(loc="upper right")
    plt.grid(None)
    plt.xlabel("Time")
    plt.ylabel("Stack")
    plt.title("Stack_change")
    plt.show()


def main():
    cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    map1 = draw_map()
    map1_blank = draw_map()
    font = cv2.FONT_HERSHEY_SIMPLEX
    robot_list = spawn_robot()
    time = 2000
    stack = [30, 30]
    stack_list_0 = []
    stack_list_1 = []
    while time > 0:
        cv2.setMouseCallback('test', mouse_click_1, robot_list)
        stack_list_0.append(stack[0])
        stack_list_1.append(stack[1])
        stack_text_0 = 'stack_0: ' + str(stack[0])
        stack_text_1 = 'stack_1: ' + str(stack[1])
        rob_text = 'robot number: ' + str(len(robot_list))
        cv2.putText(map1, stack_text_0, (100, 100), font, 1, (50, 10, 80), 2)
        cv2.putText(map1, stack_text_1, (100, 200), font, 1, (50, 10, 80), 2)
        cv2.putText(map1, rob_text, (100, 300), font, 1, (50, 10, 80), 2)
        time -= 1
        for robot in robot_list:
            # robot.check_received_msg()
            # robot.update_state()
            # robot.update_neighbor_info()
            # if robot.loaded == False:
            #     robot.make_decision()
            # for neighbor in robot.neighbor:
            #     robot.send_msg(neighbor, info)
            cv2.circle(map1, (robot.position[0], robot.position[1]), 3, (0, 0, 0), -1)
            move_event = robot.move(stack)
            stack = robot.trigger(move_event, stack)
        cv2.imshow('test', map1)
        cv2.waitKey(1)
        map1[:] = map1_blank[:]
    plot_stack(stack_list_0, stack_list_1)


main()
