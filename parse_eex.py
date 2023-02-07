import os
import sys
from until import *
import traceback

test_eex = 'D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华/test.eex'
magic_eex = b'\x45\x45\x58\x00\x01\x02\x00\x00\x00\x00'


class parser_eex():
    def add_event(self, data):
        self.parsed_event.append(data)

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
        self.stack = Stack()
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
            0xf: self.cmd_end_set,
            0x11: self.cmd_script_goto,
            0x12: self.cmd_switch_window,
            0x13: self.cmd_case,
            0x14: self.cmd_dialogue,
            0x15: self.cmd_dialogue2,
            0x16: self.cmd_info,
            0x17: self.cmd_location_name,
            0x18: self.cmd_event_name,
            0x19: self.cmd_winner_condition,
            0x1a: self.cmd_winner_condition_display,
            0x1b: self.cmd_is_fallback_display,
            0x1c: self.cmd_draw,
            0x1d: self.cmd_palette_set,
            0x1e: self.cmd_people_redraw,
            0x1f: self.cmd_map_vision_switch,
            0x20: self.cmd_people_face_status_set,
            0x21: self.cmd_battle_item_add,
            0x22: self.cmd_play_video,
            0x23: self.cmd_play_sound_effect,
            0x24: self.cmd_play_track,
            0x25: self.cmd_people_enter_location_test,
            0x26: self.cmd_people_enter_area_test,
            0x27: self.cmd_backgroud_set,
            0x29: self.cmd_map_face_display,
            0x2a: self.cmd_map_face_move,
            0x2b: self.cmd_map_face_disapeer,
            0x2c: self.cmd_map_dialog_display,
            0x2d: self.cmd_people_click_test,
            0x2e: self.cmd_people_near_test,
            0x2f: self.cmd_clear_people,
            0x30: self.cmd_people_display,
            0x31: self.cmd_people_disappear,
            0x32: self.cmd_people_move,
            0x33: self.cmd_people_turn,
            0x34: self.cmd_people_action,
            0x35: self.cmd_people_image_change,
            0x36: self.cmd_people_status_test,
            0x37: self.cmd_global_var_tset,
            0x38: self.cmd_people_status_set,
            0x39: self.cmd_people_lv_up,
            0x3a: self.cmd_global_var_set,
            0x3b: self.cmd_people_team_set,
            0x3c: self.cmd_people_team_test,
            0x3d: self.cmd_obtain_weapon,
            0x3e: self.cmd_join_equipt_set,
            0x3f: self.cmd_round_num_test,
            0x40: self.cmd_action_test,
            0x41: self.cmd_battle_num_test,
            0x42: self.cmd_battle_winner_test1,
            0x43: self.cmd_battle_winner_test2,
            0x44: self.cmd_battle_init,
            0x45: self.cmd_battle_global_var_set,
            0x46: self.cmd_allies_appearances_set,
            0x47: self.cmd_enermy_apprarances_set,
            0x48: self.cmd_enermy_equipt_set,
            0x49: self.cmd_battle_end,
            0x4a: self.cmd_team_appearances_force_set,
            0x4b: self.cmd_team_appearances_set,
            0x4c: self.cmd_hide_people_display,
            0x4d: self.cmd_people_battle_status_set,
            0x4e: self.cmd_people_ai_set,
            0x4f: self.cmd_people_battle_turn_set,
            0x50: self.cmd_people_battle_action_set,
            0x51: self.cmd_battle_resume_action,
            0x52: self.cmd_change_battle_type,
            0x53: self.cmd_battle_fallback,
            0x54: self.cmd_battle_fallback_test,
            0x55: self.cmd_battle_reborn,
            0x56: self.cmd_weather_type_set,
            0x57: self.cmd_current_weather_set,
            0x58: self.cmd_battle_barrier_set,
            0x59: self.cmd_battle_bounty_set,
            0x5a: self.cmd_battle_operation_begin,
            0x5b: self.cmd_battle_highlight_area,
            0x5c: self.cmd_battle_highlight_people,
            0x5d: self.cmd_round_max_set,
            0x5e: self.cmd_people_diff_test,
            0x5f: self.cmd_solo_end,
            0x60: self.cmd_solo_people_display,
            0x61: self.cmd_solo_res_display,
            0x62: self.cmd_solo_dead,
            0x63: self.cmd_solo_dialog,
            0x64: self.cmd_solo_action,
            0x65: self.cmd_solo_atk1,
            0x66: self.cmd_solo_atk2,
            0x67: self.cmd_chapter_name,
            0x68: self.cmd_solo_begin,
            0x69: self.cmd_narrator,
            0x6a: self.cmd_none,
            0x6b: self.cmd_magic_display
        }

    def get_scene_count(self):
        return len(self.scene_offset)

    def parse_cmd(self):
        cmd_type = self.read_u16()
        print('cmd type: {}'.format(hex(cmd_type)))
        if cmd_type in self.func_cmd.keys():
            func = self.func_cmd[cmd_type]
            return cmd_type, func()
        else:
            return -1, -1

    def parse_scene(self, idx):
        print('secen {}'.format(idx))
        self.f.seek(self.scene_offset[idx])
        section_count = self.read_u16()
        for i in range(section_count):
            self.stack.push(self.parsed_event)
            self.parsed_event = []
            section_len = self.read_u16()
            self.section_state = 'test'
            while True:
                cmd_type, ret = self.parse_cmd()
                if ret == 'end_event':
                    break
                elif ret == -1:
                    print('err type: {}')
            print('section end')
            parent_data = self.stack.pop()
            parent_data.append(self.parsed_event)
            self.parsed_event = parent_data
        pass

    def parse_all(self):
        try:
            scene_object = {}
            for scene_idx in range(self.get_scene_count()):
                self.stack.push(self.parsed_event)
                self.parsed_event = []
                self.parse_scene(scene_idx)
                parent_data = self.stack.pop()
                parent_data.append(self.parsed_event)
                self.parsed_event = parent_data
            pass
            return self.parsed_event
        except Exception as e:
            print("{},err found at : {}".format(e,hex(self.f.tell())))
            raise e

    def cmd_event_end(self):
        cmd = {"type" : 0x00}

        # print('enter {}'.format(self.f.tell()))
        print('事件结束')
        if self.section_state == 'test':
            self.event_len = self.read_u16()
            self.section_state = 'event'
        elif self.section_state == 'event':
            return 'end_event'
        pass

    def cmd_child_event_start(self):
        cmd = {"type", 0x01}
        #self.add_event(cmd)

        print('子事件设定{')
        print('测试条件：', )
        self.stack.push(self.parsed_event)
        self.parsed_event = []
        cmd_type, ret = self.parse_cmd()
        event_len = self.read_u16()
        while True:
            cmd_type, ret = self.parse_cmd()
            if cmd_type == 0x00:
                break
        pass
        parent_data = self.stack.pop()
        parent_data.append(self.parsed_event)
        self.parsed_event = parent_data
        print('子事件结束}')

    def cmd_inside_msg(self):
        cmd = {'type': 0x02}
        self.read_magic(b'\x05\x00')
        msg = self.read_until(b'\x00')
        print('内部消息 : {}'.format(msg))
        cmd['msg'] = msg

        self.add_event(cmd)

    def cmd_else(self):
        cmd = {'type': 0x03}
        self.add_event(cmd)
        print('else')

    def cmd_ask_test(self):
        cmd = {'type': 0x04}
        self.read_magic(b'\x26\x00')
        bool_msg = self.read_bool()
        cmd['bool'] = bool_msg
        self.add_event(cmd)


    def cmd_var_test(self):
        cmd = {'type': 0x05}
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
        cmd['true_var'] = true_var
        cmd['false_var'] = false_var
        self.add_event(cmd)

    def cmd_team_battle_set(self):
        cmd = {'type': 0x05}

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
        cmd['count'] = unit_num
        cmd['enforce_on'] = enforce_on_unit
        cmd['enforce_out'] = enforce_out_unit
        print('我军出场设定 强制{}人 强制出场： {} 强制不出场： {}'.format(unit_num, enforce_on_unit, enforce_out_unit))
        self.add_event(cmd)

    def cmd_battle_test(self):
        cmd = {'type': 0x06}
        self.add_event(cmd)
        print('出战测试')

    def cmd_menu_control(self):
        cmd = {'type': 0x08}
        self.read_magic(b'\x2e\x00')
        bool_msg = self.read_bool()
        cmd['bool'] = bool_msg
        print('菜单控制 {}'.format(bool_msg))
        self.add_event(cmd)

    def cmd_sleep(self):
        cmd = {'type': 0x09}
        self.read_magic(b'\x04\x00')
        sec = 10 * self.read_u32()
        cmd['value'] : sec
        print('延时 {}秒'.format(sec))
        self.add_event(cmd)

    def cmd_init_part_var(self):
        cmd = {'type': 0x0a}
        print('初始化局部变量')
        self.add_event(cmd)

    def cmd_var_set(self):
        cmd = {'type': 0x0b}
        self.read_magic(b'\x04\x00')
        var_idx = self.read_u32()
        cmd['var_idx'] = var_idx
        self.read_magic(b'\x27\x00')
        bool_msg = self.read_bool()
        cmd['value'] = bool_msg
        print("变量赋值 var_{} = {}".format(var_idx, bool_msg))
        self.add_event(cmd)

    def cmd_end_section(self):
        cmd = {'type': 0x0c}
        self.add_event(cmd)
        print('结束section')

    def cmd_end_scene(self):
        cmd = {'type': 0x0d}
        self.add_event(cmd)
        print('结束scene')

    def cmd_battle_failed(self):
        cmd = {'type': 0x0e}
        self.add_event(cmd)
        print('战斗失败')

    def cmd_end_set(self):
        cmd = {'type': 0x0f}
        self.read_magic(b'\x12\x00')
        end_type = self.read_u16()
        type_txt = {0: '红线', 1: '黄线', 2: '蓝线'}
        cmd['end_type'] = end_type
        print('结局设定 {}'.format(type_txt[end_type]))

    def cmd_clear_people(self):
        cmd = {'type': 0x2f}
        self.add_event(cmd)
        # self.read_magic(b'\x2f\x00')
        print('清除人物')

    def read_people(self):
        self.read_magic(b'\x02\x00')
        return self.read_u16()

    def read_people_lv(self):
        self.read_magic(b'\x3e\x00')
        return self.read_u16()

    def read_equipt_lv(self):
        self.read_magic(b'\x49\x00')
        return self.read_u16()

    def cmd_people_team_set(self):
        cmd = {'type': 0x3b}
        # self.read_magic(b'\x3b\x00')
        people_id = self.read_people()
        self.read_magic(b'\x0e\x00')
        action = self.read_bool()
        people_lv = self.read_people_lv()

        cmd['people_id'] = people_id
        cmd['bool'] = action
        cmd['people_lv'] = people_lv
        self.add_event(cmd)

    def read_operator(self):
        self.read_magic(b'\x34\x00')
        return self.read_u16()

    def read_value(self):
        self.read_magic(b'\x04\x00')
        return self.read_u32()

    def cmd_init_global_var(self):
        # self.read_magic(b'\x3a\x00')
        self.read_magic(b'\x28\x00')
        var_type = self.read_u16()
        operator = self.read_operator()
        value = self.read_value()

    def cmd_join_equipt_set(self):
        cmd = {'type': 0x03e}
        people_id = self.read_people()
        self.read_magic(b'\x3b\x00')
        weapon_id = self.read_u16()
        weapon_lv = self.read_equipt_lv()
        self.read_magic(b'\x3c\x00')
        armor_id = self.read_u16()
        armor_lv = self.read_equipt_lv()
        self.read_magic(b'\x3d\x00')
        aux_id = self.read_u16()

        cmd['people_id'] = people_id
        cmd['weapon_id'] = weapon_id
        cmd['weapon_lv'] = weapon_lv
        cmd['armor_id']  = armor_id
        cmd['armor_lv']  = armor_lv
        cmd['aux_id']    = aux_id

        self.add_event(cmd)

    def cmd_backgroud_set(self):
        cmd = {'type': 0x27}
        self.read_magic(b'\x2d\x00')
        backgroud_type = self.read_u16()
        self.read_magic(b'\x0c\x00')
        outside_id = self.read_u16()
        self.read_magic(b'\x1a\00')
        chinese_map_id = self.read_u16()
        self.read_magic(b'\x1c\x00')
        inside_id = self.read_u16()
        self.read_magic(b'\x15\x00')
        battle_id = self.read_u16()

        cmd['background_type'] = backgroud_type
        cmd['outside_map_id'] = outside_id
        cmd['chinese_map_id'] = chinese_map_id
        cmd['inside_map_id'] = inside_id
        cmd['battle_map_id'] = battle_id
        self.add_event(cmd)


    def cmd_script_goto(self):
        cmd = {'type': 0x11}
        self.read_magic(b'\x37\x00')
        value = self.read_u16()
        cmd['value'] = value
        self.add_event(cmd)

    def cmd_switch_window(self):
        cmd = {'type': 0x11}
        dialog = self.read_msg()
        people_id = self.read_people()
        cmd['dialog'] = dialog
        cmd['people_id'] = people_id
        self.add_event(cmd)

    def read_msg(self):
        self.read_magic(b'\x05\x00')
        return self.read_until(b'\x00')

    def cmd_case(self):
        cmd = {'type': 0x13}
        value = self.read_value()
        cmd['value'] = value
        self.add_event(cmd)

    def cmd_dialogue(self):
        cmd = {'type': 0x14}
        msg = self.read_msg()
        cmd['msg'] = msg
        self.add_event(cmd)

    def cmd_dialogue2(self):
        cmd = {'type': 0x15}
        people_id = self.read_people()
        people_id2 = self.read_people()
        msg = self.read_msg()
        cmd['people_id'] = people_id
        cmd['people_id2'] = people_id2
        cmd['msg'] = msg
        self.add_event(cmd)

    def cmd_info(self):
        cmd = {'type': 0x16}
        msg = self.read_msg()
        cmd['msg'] = msg
        self.add_event(cmd)

    def cmd_location_name(self):
        cmd = {'type': 0x17}
        msg = self.read_msg()
        cmd['msg'] = msg
        self.add_event(cmd)

    def cmd_event_name(self):
        cmd = {'type': 0x18}
        msg = self.read_msg()
        self.add_event(cmd)


    def cmd_winner_condition(self):
        cmd = {'type': 0x19}
        msg = self.read_msg()
        self.add_event(cmd)


    def cmd_winner_condition_display(self):
        cmd = {'type': 0x1a}
        msg = self.read_msg()
        self.add_event(cmd)


    def cmd_is_fallback_display(self):
        cmd = {'type': 0x1b}
        people_id = self.read_people()
        self.read_magic(b'\x27\x00')
        is_display = self.read_bool()
        self.add_event(cmd)


    def cmd_draw(self):
        cmd = {'type': 0x1c}
        self.add_event(cmd)
        pass

    def cmd_palette_set(self):
        cmd = {'type': 0x1d}
        self.add_event(cmd)
        pass

    def cmd_people_redraw(self):
        cmd = {'type': 0x1e}
        self.add_event(cmd)
        pass

    def cmd_map_vision_switch(self):
        cmd = {'type': 0x1f}
        x = self.read_value()
        y = self.read_value()
        self.add_event(cmd)


    def cmd_people_face_status_set(self):
        cmd = {'type': 0x20}
        self.read_magic(b'\x4a\x00')
        value = self.read_u16()
        self.add_event(cmd)


    def read_bool_arg(self):
        self.read_magic(b'\x26\x00')
        return self.read_bool()

    def cmd_battle_item_add(self):
        cmd = {'type': 0x21}
        x = self.read_value()
        y = self.read_value()
        self.read_magic(b'\x10\x00')
        type = self.read_u16()
        unkonw_bool = self.read_bool_arg()
        unkonw_bool2 = self.read_bool_arg()
        self.add_event(cmd)


    def cmd_play_video(self):
        cmd = {'type': 0x22}
        self.read_magic(b'\x1b\x00')
        video_id = self.read_u16()
        self.add_event(cmd)


    def cmd_play_track(self):
        cmd = {'type': 0x24}
        self.read_magic(b'\x09\x00')
        track_id = self.read_u16()
        self.add_event(cmd)


    def cmd_play_sound_effect(self):
        cmd = {'type': 0x23}

        self.read_magic(b'\x1e\x00')
        se_id = self.read_u16()
        play_count = self.read_value()

        cmd['se_id'] = se_id
        cmd['count'] = play_count
        self.add_event(cmd)


    def cmd_people_enter_location_test(self):
        cmd = {'type': 0x25}
        people_id = self.read_people()
        x = self.read_value()
        y = self.read_value()
        self.add_event(cmd)


    def cmd_people_enter_area_test(self):
        cmd = {'type': 0x26}
        people_id = self.read_people()
        x1 = self.read_value()
        y1 = self.read_value()
        x2 = self.read_value()
        y2 = self.read_value()
        self.add_event(cmd)


    def cmd_map_face_display(self):
        cmd = {'type': 0x29}
        people_id = self.read_people()
        x = self.read_value()
        y = self.read_value()
        self.add_event(cmd)


    def cmd_map_face_move(self):
        cmd = {'type': 0x2a}
        people_id = self.read_people()
        x = self.read_value()
        y = self.read_value()
        self.add_event(cmd)


    def cmd_map_face_disapeer(self):
        cmd = {'type': 0x2b}
        people_id = self.read_people()
        self.add_event(cmd)


    def cmd_map_dialog_display(self):
        cmd = {'type': 0x2c}
        msg = self.read_msg()
        is_switch_page = self.read_bool_arg()
        is_switch_line = self.read_bool_arg()
        is_wait = self.read_bool_arg()
        self.add_event(cmd)


    def cmd_people_click_test(self):
        cmd = {'type': 0x2d}
        people_id = self.read_people()
        cmd['people_id'] = people_id
        self.add_event(cmd)


    def cmd_people_near_test(self):
        cmd = {'type': 0x2e}
        people_id = self.read_people()
        people_id2 = self.read_people()
        is_near_atk = self.read_bool_arg()
        self.add_event(cmd)


    def read_dire(self):
        self.read_magic(b'\x2b\x00')
        return self.read_u16()

    def cmd_people_display(self):
        cmd = {'type': 0x30}
        people_id = self.read_people()
        x = self.read_value()
        y = self.read_value()
        dire = self.read_dire()
        action = self.read_action()

        cmd['people_id'] = people_id
        cmd['location'] = [x, y]
        cmd['dire'] =dire
        cmd['action'] = action
        self.add_event(cmd)

    def cmd_people_disappear(self):
        cmd = {'type': 0x31}
        self.read_magic(b'\x2c\x00')
        is_area = self.read_bool()
        people_id = self.read_people()
        x1 = self.read_value()
        y1 = self.read_value()
        x2 = self.read_value()
        y2 = self.read_value()
        self.add_event(cmd)


    def cmd_people_move(self):
        cmd = {'type': 0x32}
        self.read_magic(b'\x40\x00')
        is_battle_idx = self.read_bool()
        people_id = self.read_people()
        battle_id = self.read_value()
        x = self.read_value()
        y = self.read_value()
        dire = self.read_dire()
        self.add_event(cmd)


    def read_action(self):
        self.read_magic(b'\x0d\x00')
        return self.read_u16()

    def cmd_people_turn(self):
        cmd = {'type': 0x33}
        people_id = self.read_people()
        action_id = self.read_action()
        dire = self.read_dire()
        self.add_event(cmd)


    def cmd_people_action(self):
        cmd = {'type': 0x34}
        people_id = self.read_people()
        action_id = self.read_action()
        self.add_event(cmd)


    def cmd_people_image_change(self):
        cmd = {'type': 0x35}
        people_id = self.read_people()
        self.read_magic(b'\x13\x00')
        iamge_id = self.read_u16()
        self.add_event(cmd)


    def read_attr(self):
        self.read_magic(b'\x23\x00')
        return self.read_u16()

    def read_operator2(self):
        self.read_magic(b'\x24\x00')
        return self.read_u16()

    def cmd_people_status_test(self):
        cmd = {'type': 0x36}
        people_id = self.read_people()
        attr_id = self.read_attr()
        value = self.read_value()
        operator = self.read_operator2()
        self.add_event(cmd)


    def cmd_global_var_tset(self):
        cmd = {'type': 0x37}
        self.read_magic(b'\x28\x00')
        var_type = self.read_u16()
        value = self.read_value()
        operator = self.read_operator2()
        self.add_event(cmd)


    def cmd_people_status_set(self):
        cmd = {'type': 0x38}
        people_id = self.read_people()
        attr_id = self.read_attr()
        operator = self.read_operator()
        value = self.read_value()
        self.add_event(cmd)


    def cmd_people_lv_up(self):
        cmd = {'type': 0x39}
        people_id = self.read_people()
        value = self.read_value()
        self.add_event(cmd)


    def cmd_global_var_set(self):
        cmd = {'type': 0x3a}
        self.read_magic(b'\x28\x00')
        var_type = self.read_u16()
        operator = self.read_operator()
        value = self.read_value()

        cmd['var_type'] = var_type
        cmd['operator'] = operator
        cmd['value'] = value
        self.add_event(cmd)


    def cmd_people_team_test(self):
        cmd = {'type': 0x3c}
        people_id = self.read_people()
        self.read_magic(b'\x0e\x00')
        is_join = self.read_bool()
        lv = self.read_people_lv()
        self.add_event(cmd)


    def read_item_lv(self):
        self.read_magic(b'\x49\x00')
        return self.read_u16()

    def cmd_obtain_weapon(self):
        cmd = {'type': 0x3d}
        self.read_magic(b'\x17\x00')
        item_id = self.read_u16()
        item_lv = self.read_item_lv()
        is_action = self.read_bool_arg()
        people_id = self.read_people()
        self.add_event(cmd)


    def cmd_round_num_test(self):
        cmd = {'type': 0x3f}
        round = self.read_value()
        operator = self.read_operator2()
        self.add_event(cmd)


    def read_type_u16(self, type_id):
        self.read_magic(p16(type_id))
        return self.read_u16()

    def cmd_action_test(self):
        cmd = {'type': 0x40}
        action_side = self.read_type_u16(0x48)
        self.add_event(cmd)


    def cmd_battle_num_test(self):
        cmd = {'type': 0x41}
        battle_side = self.read_type_u16(0x03)
        value = self.read_value()
        operator = self.read_operator2()
        self.read_magic(b'\x3f\x00')
        is_area = self.read_bool()
        x1 = self.read_value()
        y1 = self.read_value()
        x2 = self.read_value()
        y2 = self.read_value()
        self.add_event(cmd)


    def cmd_battle_winner_test1(self):
        cmd = {'type': 0x42}
        self.add_event(cmd)



    def cmd_battle_winner_test2(self):
        cmd = {'type': 0x43}
        self.add_event(cmd)


    def cmd_battle_init(self):
        cmd = {'type': 0x45}
        self.add_event(cmd)


    def read_weather_type(self):
        return self.read_type_u16(0x47)

    def cmd_battle_global_var_set(self):
        cmd = {'type': 0x45}
        unkonw_bool = self.read_bool_arg()
        unkonw_bool2 = self.read_bool_arg()
        gourd_num = self.read_value()
        people_lv = self.read_people_lv()
        self.read_type_u16(0x32)
        enermy_boos_id = self.read_people()
        self.read_type_u16(0x32)
        team_boss_id = self.read_people()
        weather_type = self.read_weather_type()
        weather_start = self.read_type_u16(0x47)
        self.add_event(cmd)


    def cmd_allies_appearances_set(self):
        cmd = {'type': 0x46}
        people_id = self.read_people()
        is_hide = self.read_bool_arg()
        x = self.read_value()
        y = self.read_value()
        dire = self.read_dire()
        people_lv = self.read_people_lv()
        max_troop = self.read_type_u16(0x45)
        ai_type = self.read_type_u16(0x07)
        self.add_event(cmd)


    def cmd_enermy_apprarances_set(self):
        cmd = {'type': 0x47}
        people_id = self.read_people()
        is_hide = self.read_bool_arg()
        x = self.read_value()
        y = self.read_value()
        dire = self.read_dire()
        people_lv = self.read_people_lv()
        max_troop = self.read_type_u16(0x45)
        ai_type = self.read_type_u16(0x07)
        self.add_event(cmd)


    def cmd_enermy_equipt_set(self):
        cmd = {'type': 0x48}
        people_id = self.read_people()
        weapon_id = self.read_type_u16(0x3b)
        weapon_lv = self.read_item_lv()
        armor_id = self.read_type_u16(0x3c)
        armor_lv = self.read_item_lv()
        support_id = self.read_type_u16(0x3d)
        support_lv = self.read_item_lv()
        self.add_event(cmd)


    def cmd_battle_end(self):
        cmd = {'type': 0x49}
        self.add_event(cmd)


    def cmd_team_appearances_force_set(self):
        cmd = {'type': 0x4a}
        value = self.read_value()
        allow_id = []
        for i in range(5):
            allow_id.append(self.read_type_u16(0x38))
        not_allow_id = []
        for i in range(5):
            not_allow_id.append(self.read_type_u16(0x39))
        self.add_event(cmd)


    def cmd_team_appearances_set(self):
        cmd = {'type': 0x4b}
        people_id = self.read_people()
        x = self.read_value()
        y = self.read_value()
        dire = self.read_dire()
        is_hide = self.read_bool_arg()
        self.add_event(cmd)


    def cmd_hide_people_display(self):
        cmd = {'type': 0x4c}
        self.read_magic(b'\x40\x00')
        is_battle_id = self.read_bool()
        people_id = self.read_people()
        battle_id = self.read_value()
        self.add_event(cmd)


    def cmd_people_battle_status_set(self):
        cmd = {'type': 0x4d}
        people_type = self.read_type_u16(0x41)
        people_id = self.read_people()
        battle_id = self.read_value()
        x1 = self.read_value()
        y1 = self.read_value()
        x2 = self.read_value()
        y2 = self.read_value()
        battle_side = self.read_type_u16(0x03)
        attr = self.read_type_u16(0x2f)
        sign_type = self.read_type_u16(0x18)
        status_type = self.read_type_u16(0x30)
        hp = self.read_value()
        mp = self.read_value()
        self.add_event(cmd)


    def read_is_area(self):
        self.read_magic(b'\x2c\00')
        return self.read_bool()

    def cmd_people_ai_set(self):
        cmd = {'type': 0x4e}
        is_area = self.read_is_area()
        people_id = self.read_people()
        x1 = self.read_value()
        y1 = self.read_value()
        x2 = self.read_value()
        y2 = self.read_value()
        battle_side = self.read_type_u16(0x03)
        ai_type = self.read_type_u16(0x07)
        people_id_ai = self.read_people()
        x_ai = self.read_value()
        y_ai = self.read_value()
        self.add_event(cmd)


    def cmd_people_battle_turn_set(self):
        cmd = {'type': 0x4f}
        people_id = self.read_people()
        poeple_id2 = self.read_people()
        dire = self.read_dire()
        is_turn = self.read_bool_arg()
        sleep_before = self.read_bool_arg()
        sleep_after = self.read_bool_arg()
        self.add_event(cmd)


    def cmd_people_battle_action_set(self):
        cmd = {'type': 0x50}
        people_id = self.read_people()
        battle_action = self.read_type_u16(0x46)
        sleep_before = self.read_bool_arg()
        sleep_after = self.read_bool_arg()
        self.add_event(cmd)


    def cmd_battle_resume_action(self):
        cmd = {'type': 0x51}
        self.add_event(cmd)


    def cmd_change_battle_type(self):
        cmd = {'type': 0x52}
        people_id = self.read_people()
        troop_type = self.read_type_u16(0x03)
        self.add_event(cmd)


    def cmd_battle_fallback(self):
        cmd = {'type': 0x53}
        is_area = self.read_is_area()
        people_id = self.read_people()
        x1 = self.read_value()
        y1 = self.read_value()
        x2 = self.read_value()
        y2 = self.read_value()
        battle_side = self.read_type_u16(0x03)
        is_die = self.read_bool_arg()
        self.add_event(cmd)


    def cmd_battle_fallback_test(self):
        cmd = {'type': 0x54}
        self.add_event(cmd)


    def cmd_battle_reborn(self):
        cmd = {'type': 0x55}
        people_type = self.read_type_u16(0x40)
        people_id = self.read_people()
        battle_id = self.read_value()
        x = self.read_value()
        y = self.read_value()
        dire = self.read_dire()
        self.add_event(cmd)


    def cmd_weather_type_set(self):
        cmd = {'type': 0x56}
        weather_type = self.read_weather_type()
        self.add_event(cmd)


    def cmd_current_weather_set(self):
        cmd = {'type': 0x57}
        current_weather = self.read_type_u16(0x22)
        self.add_event(cmd)


    def read_type_bool(self, type_id):
        self.read_magic(p16(type_id))
        return self.read_bool()

    def cmd_battle_barrier_set(self):
        cmd = {'type': 0x58}
        barrier_id = self.read_type_u16(0x42)
        is_display = self.read_type_bool(0x43)
        tile_type = self.read_type_u16(0x44)
        x = self.read_value()
        y = self.read_value()
        self.read_bool_arg()
        self.read_bool_arg()
        self.add_event(cmd)


    def cmd_battle_bounty_set(self):
        cmd = {'type': 0x59}
        money = self.read_value()
        item = []
        for i in range(3):
            item_id = self.read_type_u16(0x17)
            item_lv = self.read_type_u16(0x49)
        is_end = self.read_bool()
        self.add_event(cmd)


    def cmd_battle_operation_begin(self):
        cmd = {'type': 0x5a}
        self.add_event(cmd)


    def cmd_battle_highlight_area(self):
        cmd = {'type': 0x5b}
        x1 = self.read_value()
        y1 = self.read_value()
        x2 = self.read_value()
        y2 = self.read_value()
        is_battle = self.read_bool()
        self.add_event(cmd)


    def cmd_battle_highlight_people(self):
        cmd = {'type': 0x5c}
        people_id = self.read_people()
        self.add_event(cmd)


    def cmd_round_max_set(self):
        cmd = {'type': 0x5d}
        operator = self.read_operator()
        value = self.read_value()
        self.add_event(cmd)


    def cmd_people_diff_test(self):
        cmd = {'type': 0x5e}
        people_id = self.read_people()
        people_id2 = self.read_people()
        self.add_event(cmd)


    def cmd_solo_end(self):
        cmd = {'type': 0x5f}
        self.add_event(cmd)


    def cmd_solo_people_display(self):
        cmd = {'type': 0x60}
        is_our_people = self.read_bool()
        msg = self.read_msg()
        solo_action = self.read_type_u16(0x4c)
        self.add_event(cmd)


    def cmd_solo_res_display(self):
        cmd = {'type': 0x61}
        self.add_event(cmd)


    def cmd_solo_dead(self):
        cmd = {'type': 0x62}
        is_out_people = self.read_bool()
        self.add_event(cmd)


    def cmd_solo_dialog(self):
        cmd = {'type': 0x63}
        is_our_people = self.read_bool()
        msg = self.read_msg()
        is_sleep = self.read_bool()
        self.add_event(cmd)


    def cmd_solo_action(self):
        cmd = {'type': 0x64}
        is_our_people = self.read_bool()
        solo_action = self.read_type_u16(0x4c)
        self.add_event(cmd)


    def cmd_solo_atk1(self):
        cmd = {'type': 0x65}
        is_our_people = self.read_bool()
        solo_action = self.read_type_u16(0x4d)
        self.add_event(cmd)


    def cmd_solo_atk2(self):
        cmd = {'type': 0x66}
        is_our_people = self.read_bool()
        solo_action = self.read_type_u16(0x4e)
        self.add_event(cmd)

    def cmd_chapter_name(self):
        cmd = {'type': 0x67}
        value = self.read_value()
        msg = self.read_msg()
        self.add_event(cmd)

    def cmd_solo_begin(self):
        cmd = {'type': 0x68}
        people_id = self.read_people()
        people_id2 = self.read_people()
        self.add_event(cmd)

    def cmd_narrator(self):
        cmd = {'type': 0x69}
        msg = self.read_msg()
        self.add_event(cmd)

    def cmd_none(self):
        cmd = {'type': 0x6a}
        self.add_event(cmd)

    def cmd_magic_display(self):
        cmd = {'type': 0x6b}
        x = self.read_value()
        y = self.read_value()
        magic_id = self.read_type_u16(0x4b)
        unkonw = self.read_bool()
        self.add_event(cmd)


if __name__ == '__main__':
    for i in range(59):

        p = parser_eex("eex_ccz/R_{:0>2d}.eex".format(i))
        r1 = p.parse_all()
        # print(r1)
        # print(json_format(r1))
        f = open('eex_json/R_{:0>2d}.json'.format(i), 'w')
        f.write(json_format(r1))
        f.close()
