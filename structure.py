'''
'''



'''
定义一些常量
'''
'''
可变参数
'''
SEGNUM = 1 # 计划处理的路段个数，i.e.，10就是前10个
ITERATION = 1200 # 迭代次数，每一次相当于1.5秒
P1 = 0.94
P2 = 0.5
P3 = 0.2
RECORDPROCESS = False
SDVPERCENTAGE = 0.5 # SDV占比
'''
不可变参数
'''
CELL_LENGTH = 4  # 元胞长度
UNITIME = 1.5
INITSPEED = 0
INF = 1000000000000
SOURCEFILE = '2017_MCM_Problem_C_Data.xlsx'
ON = True
OFF = False
LEFT = -1
RIGHT = 1
SDVT = 'SDV'
NSDVT = 'NSDV'


'''
'''
# import pandas as pd
import random
# from CONSTANT import *
'''
计算最小安全距离
0 cell/turn <= speed <= 10 cell/turn
MSD 单位为 cell，为整数
'''
def MSD(speed):

    speed2MSD = {
        '0': 1,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 5,
        '5': 9,
        '6': 12,
        '7': 16,
        '8': 22,
        '9': 27,
        '10': 32
    }
    return speed2MSD[str(speed)]
def MSDSDV(speed):

    speed2MSD = {
        '0': 1,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 5,
        '5': 9,
        '6': 12,
        '7': 16,
        '8': 22,
        '9': 26,
        '10': 31
    }
    return speed2MSD[str(speed)]

'''
前后两车之间的最大距离
也就是计算可以加速的最小车距
0 cell/turn <= speed <= 10 cell/turn
MSD 单位为 cell，为整数
'''
def MD(speed):
    speed2MD = {
        '0': 1,
        '1': 1,
        '2': 3,
        '3': 6,
        '4': 9,
        '5': 13,
        '6': 18,
        '7': 24,
        '8': 30,
        '9': 36,
        '10': 42
    }
    return speed2MD[str(speed)]

'''
计算两个SDV之间的最小安全距离
'''
def Dmin(a, b):
    if a.type == SDVT and b.type == SDVT:
        return Dmin_SDV_SDV(a.speed, MSD(max(b.speed - 2, 0)))
    return MSD(a.speed)
'''
计算SVD之间的最小距离
'''
def Dmin_SDV_SDV(speed,breakingdistance):
    return max(MSD(speed) - breakingdistance + 1,1)
'''
计算平均速度
'''
def averagespeed(speeds):
    return sum(speeds) / len(speeds)
'''
保存数据
'''
def save(writer,time,data):
    ans = {}
    for lane in range(1,len(data) + 1):
        ans[lane] = []
        for pos in range(1,len(data[lane])):
            if data[lane][pos] == None:
                ans[lane].append(None)
            else:
                ans[lane].append(1 if data[lane][pos].type == 'SDV' else 0)
    df = pd.DataFrame(data=ans)
    df.to_excel(writer,index=False,sheet_name=str(time) + 'unit time')
    return

'''
定义关键的类
'''
class HIGHWAY():
    ''''''
    '''
    初始化函数
    :param length: 道路长度，单位是m
    :param lane_num: 车道个数
    :param name: 路段编号，或者是本地存储数据时使用的文件名
    '''
    def __init__(self, length, lane_num,name):
        self.speeds = []
        self.begin = False
        self.begin_time = 1
        self.counter = 0
        self.name = name
        self.writer = pd.ExcelWriter('data/' + name + '.xls')
        self.dir = 0
        self.out = []
        self.lanes = {}
        self.cell_num = int(length / CELL_LENGTH)
        self.moniter = self.cell_num / 2
        self.lane_num = lane_num
        if int(length / CELL_LENGTH) != length / CELL_LENGTH:
            self.cell_num += 1
        for id in range(lane_num):
            self.lanes[id + 1] = []
            self.lanes[id + 1].append(NSDV(id + 1, INITSPEED, NSDVT))
            for i in range(self.cell_num):
                self.lanes[id + 1].append(None)
        self.beifen = {}
        for id in range(lane_num):
            self.beifen[id + 1] = []
            self.beifen[id + 1].append(None)
            for i in range(self.cell_num):
                self.beifen[id + 1].append(None)
        return

    def get_front(self, lane, pos):
        ret = None
        pos += 1
        while True:
            if pos > self.cell_num:
                break
            if self.lanes[lane][pos] == None:
                pos += 1
                continue
            ret = self.lanes[lane][pos]
            break
        return ret

    def get_delta_d(self, v1, v2):
        lane1 = v1.lane
        lane2 = v2.lane
        if lane1 != lane2:
            return None
        return abs(v1.pos - v2.pos)

    def add(self, lane, speed, type):
        new = None
        if type == NSDVT:
            new = NSDV(lane, speed, type)
        else:
            new = SDV(lane, speed, type)
        self.lanes[lane][0] = new
        return

    def get_train_head(self, lane, pos):
        num = 1
        head = None
        while True:
            pos += 1
            if pos > self.cell_num:
                break
            tmp = self.lanes[lane][pos]
            if tmp == None:
                continue
            if tmp.type == SDVT:
                num += 1
                head = tmp
                continue
            if tmp.type == NSDVT:
                break
        if num >= 3:
            return head
        return None

    def get_side_dir(self, lane, pos, dir):
        ret = None
        lane = lane + dir
        if lane < 1 or lane > self.lane_num:
            return ret,INF
        initpos = pos
        while True:
            tmp = self.lanes[lane][pos]
            if tmp != None:
                ret = tmp
                break
            pos += 1
            if pos > self.cell_num:
                break
        return ret, pos - initpos

    def get_side(self, lane, pos):
        lcar, ldis = self.get_side_dir(lane, pos, LEFT)
        rcar, rdis = self.get_side_dir(lane, pos, RIGHT)
        retdis = min(ldis, rdis)
        retcar = lcar if ldis == retdis else rcar
        retdir = LEFT if ldis == retdis else RIGHT
        return retcar, retdir

    def get_sideback(self, lane, pos, dir):
        ret = None
        lane = lane + dir
        while True:
            tmp = self.lanes[lane][pos]
            if tmp != None:
                ret = tmp
                break
            pos -= 1
            if pos < 0:
                break
        return ret

    def get_back(self, lane, pos):
        ret = None
        while True:
            tmp = self.lanes[lane][pos]
            if tmp != None:
                ret = tmp
                break
            pos -= 1
            if pos < 0:
                break
        return ret

    def source(self):
        for i in range(1, self.lane_num + 1):
            if self.lanes[i][1] == None:
                self.lanes[i][0].pos = 1
                front = self.get_front(i,1)
                if front == None:
                    self.lanes[i][0].speed = 10
                    delta = INF
                    front = VEHICLE(i,10,NSDVT)
                else:
                    self.lanes[i][0].speed = front.speed
                    delta = abs(self.lanes[i][0].pos - front.pos)
                if self.lanes[i][0].type == SDVT and front.type == SDVT:
                    threshold = Dmin(self.lanes[i][0],front)
                else:
                    threshold = MSD(self.lanes[i][0].speed)
                if delta > threshold:
                    self.lanes[i][1] = self.lanes[i][0]
                    if random.random() <= SDVPERCENTAGE:
                        self.lanes[i][0] = SDV(i, INITSPEED, SDVT)
                    else:
                        self.lanes[i][0] = NSDV(i, INITSPEED, NSDVT)
        return

    def update(self,tmptime):
        for lane in range(1, self.lane_num + 1):
            for pos in range(1, self.cell_num + 1):
                # NSDV and SDV's change_lane
                vehi = self.lanes[lane][pos]
                if vehi == None:
                    continue
                front = self.get_front(lane, pos)
                # delta_front = self.get_delta_d(vehi,front)
                head = None
                side, self.dir = self.get_side(lane, pos)
                if side == None:
                    side = VEHICLE(lane+self.dir,0,NSDVT)
                back = self.get_back(lane, pos)
                sideback = self.get_sideback(lane, pos, self.dir)
                if vehi.type == NSDVT:
                    vehi.change_lane(front, side, back, sideback)
                elif vehi.type == SDVT:
                    head = self.get_train_head(lane, pos)
                    vehi.change_lane(front, side, back, sideback, head)
        for lane in range(1, self.lane_num + 1):
            for pos in range(1, self.cell_num + 1):
                vehi = self.lanes[lane][pos]
                if vehi == None:
                    continue
                if vehi.turninglight != 0:
                    vehi.lane += vehi.turninglight
                    vehi.turninglight = 0
                    self.lanes[vehi.lane][pos] = vehi
                    self.lanes[lane][pos] = None
        for lane in range(1, self.lane_num + 1):
            for pos in range(1, self.cell_num + 1):
                vehi = self.lanes[lane][pos]
                if vehi == None:
                    continue
                front = self.get_front(lane, pos)
                delta_front = None
                if front == None:
                    delta_front = self.cell_num - vehi.pos
                else:
                    delta_front = self.get_delta_d(vehi, front)
                # NSDV and SDV's update
                # print(lane,pos)
                if vehi.type == NSDVT:
                    vehi.update(delta_front, front)
                elif vehi.type == SDVT:
                    head = self.get_train_head(lane, pos)
                    vehi.update(delta_front, front, head)
        self.out = []
        for lane in range(1, self.lane_num + 1):
            for pos in range(1, self.cell_num + 1):
                vehi = self.lanes[lane][pos]
                if vehi == None:
                    continue
                newpos = vehi.speed + vehi.pos
                if vehi.pos <= self.moniter and newpos >= self.moniter:
                    if self.begin == True:
                        self.counter += 1
                    else:
                        self.begin = True
                        self.counter += 1
                if newpos > self.cell_num:
                    vehi.pos = newpos - self.cell_num
                    self.out.append(vehi)
                    self.speeds.append(self.cell_num * 4 / ((tmptime - vehi.begin) * 1.5))
                    self.lanes[lane][pos] = None
                    continue
                vehi.pos = newpos
                self.beifen[lane][newpos] = vehi
                self.lanes[lane][pos] = None
        for lane in range(1, self.lane_num + 1):
            for pos in range(1, self.cell_num + 1):
                self.lanes[lane][pos] = self.beifen[lane][pos]
                self.beifen[lane][pos] = None
        self.source()
        return

    def save(self, time):
        # data = {}
        # data[time] = []
        # for i in range(1, self.cell_num + 1):
        #     num = 0
        #     for j in range(1, self.lane_num + 1):
        #         if self.lanes[j][i] == None:
        #             continue
        #         num += 1
        #     data[time].append(num)
        # df = pd.DataFrame(data)
        # df.to_csv('data/' + str(time) + 'unittime.csv', index=False)
        return

    def run(self):
        for i in range(1, ITERATION + 1):
            label = self.begin
            self.update(i)
            # set初始时间
            for j in range(1, self.lane_num + 1):
                if self.lanes[j][1] == None:
                    continue
                self.lanes[j][1].begin = i
            if self.begin != label:
                self.begin_time = i
            if RECORDPROCESS == True:
                save(self.writer,i,self.lanes)
            # print('complete one iteration!',i)
        if RECORDPROCESS == True:
            self.writer.save()
            self.writer.close()
        #配置信息存储
        file = open('data/ans.txt','a')
        # file.write('run time:' + str(ITERATION) + '* 1.5s\n')
        # file.write('cell number:' + str(self.cell_num) + '\n')
        # file.write('lane number:' + str(self.lane_num) + '\n')
        # file.write('sdv percentage:' + str(SDVPERCENTAGE) + '\n')
        ans = self.counter / (ITERATION - self.begin_time) * 3600 * 24 / 1.5 # 计算车流量
        # file.write('traffic flow:' + str(ans) + '\n')
        # # file.write(':' + str() + '\n')
        file.write(str(SDVPERCENTAGE) + '\t' + str(ans) + '\t' + str(averagespeed(self.speeds)) + '\n')
        file.close()
        print(str(SDVPERCENTAGE) + '\t' + str(ans) + '\t' + str(averagespeed(self.speeds)))
        return


class VEHICLE():
    def __init__(self, lane, speed, type):
        self.speed = speed
        self.lane = lane
        self.pos = 0
        self.backlight = OFF
        self.type = type
        self.turninglight = OFF
        self.begin = 0
        return


class NSDV(VEHICLE):
    def __init__(self, lane, speed, type):
        VEHICLE.__init__(self, lane, speed, type)
        return

    def update(self, delta_d, front):
        self.backlight = OFF
        if front == None:
            if self.speed < 10:
                self.speed += 1
            return
        def caution_probability():
            ret = 0
            if front.backlight == ON and delta_d > MSD(self.speed) and delta_d < MD(self.speed):
                ret = P1
            if front.backlight == OFF and delta_d > MSD(self.speed) and delta_d < MD(self.speed):
                ret = P2
            if self.speed == 0:
                ret = P3
            return ret

        P = caution_probability()
        R = random.random()

        if P >= R:
            if self.speed > 0:
                self.speed -= 1
                self.backlight = ON
        if delta_d <= MSD(self.speed):
            if self.speed > 0:
                self.speed -= 1
                self.backlight = ON
            return
        if P < R and (delta_d > MD(self.speed) or (front.backlight == OFF and delta_d > MSD(self.speed))):
            if self.speed < 10:
                self.speed += 1
                self.backlight = OFF
            return
        return

    def change_lane(self, front, side, back, sideback):
        if front == None:
            front = VEHICLE(self.lane,0,NSDVT)
            front.pos = INF
        LCM = abs(self.pos - front.pos) < MD(self.speed) and front.speed < self.speed \
              and (abs(self.pos - side.pos) > MD(self.speed) or side.speed > self.speed)
        if LCM == False:
            return
        msd = MSD(self.speed)
        LCS = abs(self.pos - front.pos) > msd and abs(self.pos - side.pos) > msd and abs(self.pos - sideback.pos) > msd \
              and back.turninglight != LEFT if side.lane < self.lane else RIGHT
        if LCS == False:
            return

        def caution_probability():
            '''
            计算概率
            :return:
            '''
            delta_d = abs(self.pos - front.pos)
            ret = 0
            if front.backlight == ON and delta_d > MSD(self.speed) and delta_d < MD(self.speed):
                ret = P1
            if front.backlight == OFF and delta_d > MSD(self.speed) and delta_d < MD(self.speed):
                ret = P2
            if self.speed == 0:
                ret = P3
            return ret

        LCP = caution_probability() >= random.random()
        if LCP == False:
            return
        self.turninglight = LEFT if side.lane < self.lane else RIGHT
        return


class SDV(VEHICLE):
    def __init__(self, lane, speed, type):
        VEHICLE.__init__(self, lane, speed, type)
        self.accelerating = False
        return

    def update(self, delta_d, front, train_head=None):
        self.backlight = OFF
        self.accelerating = False
        if front == None:
            if self.speed < 10:
                self.speed += 1
                self.backlight = OFF
                self.accelerating = True
            return
        breakingdistance = MSD(max(front.speed - 2, 0))
        D_min_SDV_SDV = Dmin_SDV_SDV(self.speed, breakingdistance)
        if delta_d > MD(self.speed):
            if self.speed < 10:
                self.speed += 1
                self.backlight = OFF
                self.accelerating = True
            return
        if front.type == NSDVT and front.backlight == OFF and delta_d >= MSD(self.speed):
            if self.speed < 10:
                self.speed += 1
                self.backlight = OFF
                self.accelerating = True
            return
        if front.type == SDVT and delta_d > D_min_SDV_SDV:
            if self.speed < 10:
                self.speed += 1
                self.backlight = OFF
                self.accelerating = True
            return
        if delta_d < D_min_SDV_SDV:
            if self.speed > 0:
                self.speed -= 1
                self.backlight = ON
                self.accelerating = False
            return
        if train_head == None:
            return
        if delta_d >= D_min_SDV_SDV and train_head.accelerating == True:
            if self.speed < 10:
                self.speed += 1
                self.backlight = OFF
                self.accelerating = True
            return

    def change_lane(self, front, side, back, sideback, head=None):
        if front == None:
            front = VEHICLE(self.lane,0,NSDVT)
            front.pos = INF
        delta_front = abs(front.pos - self.pos)
        delta_side = abs(side.pos - self.pos)
        LCM = None
        if head == None:
            LCM = (abs(self.pos - front.pos) < MD(self.speed) and front.speed < self.speed
                   and (abs(self.pos - side.pos) > MD(self.speed) or side.speed > self.speed)) \
                  or (front.turninglight == LEFT if side.lane < self.lane else RIGHT and front.type == SDVT)
        else:
            LCM = (abs(self.pos - front.pos) < MD(self.speed) and front.speed < self.speed
                   and (abs(self.pos - side.pos) > MD(self.speed) or side.speed > self.speed)) \
                  or (front.turninglight == LEFT if side.lane < self.lane else RIGHT and front.type == SDVT) \
                  or (head.turninglight == LEFT if side.lane < self.lane else RIGHT)
        delta_sideback = abs(self.pos - sideback.pos)
        LCS = (delta_front > Dmin(self, front)) and (delta_side > Dmin(self, side)) and (
                delta_sideback > Dmin(sideback, self)) \
              and (back.turninglight != LEFT or back.type == SDVT)
        if LCM and LCS:
            self.turninglight = LEFT if side.lane < self.lane else RIGHT
        return



# from utils import *#包含计算函数以及实现类
# from CONSTANT import *#包含参数配置
import pandas as pd
import time

if __name__ == '__main__':
    df = pd.read_excel(SOURCEFILE)[['Route_ID','startMilepost','endMilepost','Number of Lanes DECR MP direction ','Number of Lanes INCR MP direction']]
    data = df.values
    route_id = 5
    seg_id = 1
    # choice = input('input 1 for iterations calculation!inupt 2 for specified calculation!')
    for t in range(1001):
        SDVPERCENTAGE = t / 1000
        print(SDVPERCENTAGE)
        for i in range(SEGNUM):
            start = time.time()
            if route_id != int(data[i][0]):
                seg_id = 1
            way = HIGHWAY((float(data[i][2]) - float(data[i][1])) * 1000,int(data[i][3]) + int(data[i][4]),str(route_id) + '-' + str(seg_id) + '-' + str(SDVPERCENTAGE))
            way.run()
            seg_id += 1
            print(time.time() - start)