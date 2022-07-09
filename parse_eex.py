import os
import sys
from until import *

test_eex = 'D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华/test.eex'
magic_eex = b'\x45\x45\x58\x00\x01\x02\x00\x00\x00\x00'


class parser_eex():
    def read_until(self, end):
        ret = b''
        end_len = len(end)
        ret = ret + self.f.read(end_len)
        if ret == end:
            return ret
        while True:
            # input("read")
            # print(ret)
            ret = ret + self.f.read(1)
            if ret[-end_len:] == end:
                return ret

    def read_u32(self):
        return u32(self.f.read(4))

    def read_u16(self):
        return u16(self.f.read(2))

    def read_magic(self, magic):
        # print(magic)
        # print(hex(self.f.tell()))
        buf = self.f.read(len(magic))
        # print(buf)
        if buf != magic:
            raise RuntimeError('format error expect {} but {}'.format(magic, buf))

    def read_bool(self):
        bool_msg = self.f.read(2)
        if bool_msg == '\x01\x00':
            return True
        elif bool_msg == '\x00\x00':
            return False

    def __init__(self, eex_path):
        self.parsed_event = []
        self.event_len = None
        self.section_state = None
        if not os.access(eex_path, os.F_OK | os.R_OK):
            raise RuntimeError("file not exist or permit denied")
        self.f = f = open(eex_path, 'rb')
        self.read_magic(magic_eex)
        self.scene_offset = []
        self.scene_offset.append(u32(f.read(4)))
        while f.tell() != self.scene_offset[0]:
            self.scene_offset.append(u32(f.read(4)))

        self.func_cmd = {
            0x0: self.cmd_event_end,
            0x1: self.cmd_child_event_start,
            0x2: self.cmd_inside_msg,
            0x3: self.cmd_else,
            0x4: self.cmd_ask_test,
            0x5: self.cmd_var_test,
            0x6: self.cmd_team_battle_set,
            0x7: self.cmd_battle_test,
            0x8: self.cmd_menu_control,
            0x9: self.cmd_sleep,
            0xa: self.cmd_init_part_var,
            0xb: self.cmd_var_set,
            0xc: self.cmd_end_section,
            0xd: self.cmd_end_scene,
            0xe: self.cmd_battle_failed,
            0xf: self.cmd_end_set

        }

    def get_scene_count(self):
        return len(self.scene_offset)

    def parse_cmd(self):
        cmd_type = self.read_u16()
        if cmd_type in self.func_cmd.keys():
            func = self.func_cmd[cmd_type]
            return cmd_type, func()
        else:
            return -1, -1

    def parse_scene(self, idx):
        self.section_state = 'test'
        print('section {}'.format(idx))
        self.f.seek(self.scene_offset[idx])
        section_len = self.read_u16()
        while True:
            cmd_type, ret = self.parse_cmd()
            if ret == 'end_event':
                break
            elif ret == -1:
                print('err type: {}')
        print('section end')
        pass

    def parse_all(self):
        for scene_idx in range(self.get_scene_count()):
            self.parse_scene(scene_idx)
        pass

    def cmd_event_end(self):
        #print('enter {}'.format(self.f.tell()))
        print('事件结束')
        if self.section_state == 'test':
            self.event_len = self.read_u16()
            self.section_state = 'event'
        elif self.section_state == 'event':
            return 'end_event'

        pass

    def cmd_child_event_start(self):
        print('子事件设定{')
        print('测试条件：',)
        cmd_type, ret = self.parse_cmd()
        event_len = self.read_u16()
        while True:
            cmd_type, ret = self.parse_cmd()
            if cmd_type == 0x00:
                break
        pass
        print('子事件结束}')

    def cmd_inside_msg(self):
        self.read_magic(b'\x05\x00')
        msg = self.read_until(b'\x00')
        print('内部消息 : {}'.format(msg))

    def cmd_else(self):
        print('else')

    def cmd_ask_test(self):
        self.read_magic(b'\x26\x00')
        bool_msg = self.read_bool()
        if bool_msg:
            print("询问测试 是")
        else:
            print("询问测试 否")

    def cmd_var_test(self):
        self.read_magic(b'\x35\x00')
        true_var = []
        false_var = []
        true_var_count = u16(self.f.read(2))
        for i in range(true_var_count):
            true_var.append(u16(self.f.read(2)))
        self.read_magic(b'\x35\x00')
        false_var_count = u16(self.f.read(2))
        for i in range(false_var_count):
            false_var.append(u16(self.f.read(2)))
        print('变量测试 true: {} false: {}'.format(true_var, false_var))

    def cmd_team_battle_set(self):
        self.read_magic(b'\x2e\x00')
        bool_msg = self.read_bool()
        self.read_magic(b'\x04\x00')
        unit_num = self.read_u32()
        enforce_on_unit = []
        enforce_out_unit = []
        for i in range(5):
            self.read_magic(b'\x38\x00')
            unit_id = self.read_u16()
            if unit_id != 0xffff:
                enforce_on_unit.append(unit_id)
        for i in range(5):
            self.read_magic(b'\x39\x00')
            unit_id = self.read_u16()
            if unit_id != 0xffff:
                enforce_out_unit.append(unit_id)
        print('我军出场设定 强制{}人 强制出场： {} 强制不出场： {}'.format(unit_num, enforce_on_unit, enforce_out_unit))

    def cmd_battle_test(self):
        print('出战测试')

    def cmd_menu_control(self):
        self.read_magic(b'\x2e\x00')
        bool_msg = self.read_bool()
        print('菜单控制 {}'.format(bool_msg))

    def cmd_sleep(self):
        self.read_magic(b'\x04\x00')
        sec = 10 * self.read_u32()
        print('延时 {}秒'.format(sec))

    def cmd_init_part_var(self):
        print('初始化局部变量')

    def cmd_var_set(self):
        self.read_magic(b'\x04\x00')
        var_idx = self.read_u32()
        self.read_magic(b'\x27\x00')
        bool_msg = self.read_bool()
        print("变量赋值 var_{} = {}".format(var_idx, bool_msg))

    def cmd_end_section(self):
        print('结束section')

    def cmd_end_scene(self):
        print('结束scene')

    def cmd_battle_failed(self):
        print('战斗失败')

    def cmd_end_set(self):
        self.read_magic(b'\x12\x00')
        end_type = self.read_u16()
        type_txt = {0: '红线', 1: '黄线', 2: '蓝线'}
        print('结局设定 {}'.format(type_txt[end_type]))


if __name__ == '__main__':
    p = parser_eex(test_eex)
    p.parse_all()
