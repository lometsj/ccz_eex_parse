import os
import json
import struct
from until import *

global config_data
global parse_data
parse_data = dict()


def parse_unit(ccz_path):
    unit_data = []
    # print(config_data)
    count = int(config_data['Game_Unit_Count'], 16)
    offset = int(config_data['Game_Unit_Offset'], 16)
    des_offset = int(config_data['Imsg_UnitOriginal_Offset'], 16)
    cri_offset = int(config_data['Imsg_Critical_Offset'], 16)
    print(hex(offset))

    data_fd = open(ccz_path + "/Data.e5", "rb")
    des_fd = open(ccz_path + "/Imsg.e5", "rb")
    cri_fd = open(ccz_path + "/Imsg.e5", "rb")

    data_fd.seek(offset)
    des_fd.seek(des_offset)
    cri_fd.seek(cri_offset)

    for i in range(count):
        unit_one = {}
        unit_one['id'] = i
        unit_one['name'] = data_fd.read(13).decode('GBK').replace('\x00', '')
        unit_one['face'] = u16(data_fd.read(2))
        unit_one['pmapobj'] = u8(data_fd.read(1))
        cri_idx = u8(data_fd.read(1))
        # cri_fd.seek(cri_offset+cri_idx*0xc8)
        unit_one['cri'] = cri_idx  # cri_fd.read(0xc8).decode('GBK').replace('\x00','')
        unit_one['camp'] = u8(data_fd.read(1))
        unit_one['Str'] = u8(data_fd.read(1)) * 2
        unit_one['Vit'] = u8(data_fd.read(1)) * 2
        unit_one['Int'] = u8(data_fd.read(1)) * 2
        unit_one['Avg'] = u8(data_fd.read(1)) * 2
        unit_one['Luk'] = u8(data_fd.read(1)) * 2
        unit_one['hp'] = u16(data_fd.read(2))
        unit_one['mp'] = u8(data_fd.read(1))
        unit_one['force'] = u8(data_fd.read(1))
        unit_one['lv'] = u16(data_fd.read(2))
        unit_one['weapon'] = u8(data_fd.read(1))
        unit_one['armor'] = u8(data_fd.read(1))
        unit_one['ancillary'] = u8(data_fd.read(1))
        if i <= 0xad:
            unit_one['describe'] = des_fd.read(0xc8).decode("GBK").replace('\x00', '')
        # print(unit_one)
        unit_data.append(unit_one)
    parse_data['unit_data'] = unit_data

    data_fd.close()
    des_fd.close()
    cri_fd.close()
    # print(parse_data)


def parse_item(ccz_path):
    item_data = []
    offset = int(config_data['Game_Item_Offset'], 16)
    des_offset = int(config_data['Imsg_Item_Offset'], 16)
    count = int(config_data['Game_Item_Count'], 16)

    data_fd = open(ccz_path + "/Data.e5", "rb")
    des_fd = open(ccz_path + "/Imsg.e5", "rb")

    data_fd.seek(offset)
    des_fd.seek(des_offset)
    for i in range(count):
        item_one = {}
        item_one['id'] = i
        item_one['name'] = data_fd.read(17).decode('GBK').replace('\x00', '')
        item_one['type'] = u8(data_fd.read(1))
        item_one['specil_eff'] = u8(data_fd.read(1))
        item_one['price'] = u8(data_fd.read(1)) * 100
        item_one['icon'] = u8(data_fd.read(1))
        item_one['base_value'] = u8(data_fd.read(1))
        item_one['specil_eff_value'] = u8(data_fd.read(1))
        item_one['upgrade_value'] = u8(data_fd.read(1))
        item_one['is_special'] = u8(data_fd.read(1))
        item_one['describe'] = des_fd.read(0xc8).decode("GBK").replace('\x00', '')
        item_data.append(item_one)
        # print(item_one)

    parse_data['item_data'] = item_data
    data_fd.close()
    des_fd.close()


def parse_shop(ccz_path):
    shop_data = []
    offset = int(config_data['Game_Shop_Offset'], 16)

    data_fd = open(ccz_path + "/Data.e5", 'rb')

    data_fd.seek(offset)
    for i in range(58):
        shop_one = {}
        shop_one['id'] = i
        shop_one['open_warehouse_unit'] = u16(data_fd.read(2))
        shop_one['shop_shop_unit'] = u16(data_fd.read(2))
        equips = []
        for j in range(16):
            equip_id = u8(data_fd.read(1))
            if equip_id == 0xff:
                continue
            equips.append(equip_id)
        shop_one['equips'] = equips

        consumables = []
        for j in range(16):
            consumables_id = u8(data_fd.read(1))
            if consumables_id == 0xff:
                continue

            consumables.append(consumables_id)
        shop_one['consumables'] = consumables
        # print(shop_one)
        shop_data.append(shop_one)

    parse_data['shop_data'] = shop_data
    data_fd.close()



def parse_force(ccz_path):
    force_data = []
    offset = int(config_data['Game_Force_Offset'], 16)
    des_offset = int(config_data['Imsg_Force_Offset'], 16)
    exe_offset = int(config_data['Exe_Force_offset'], 16)
    count = int(config_data['Game_Force_Count'], 16)

    data_fd = open(ccz_path + '/Data.e5', 'rb')
    des_fd = open(ccz_path + '/Imsg.e5', 'rb')
    exe_fd = open(ccz_path + '/Ekd5.exe', 'rb')

    data_fd.seek(offset)
    des_fd.seek(des_offset)
    exe_fd.seek(exe_offset)
    for i in range(count):
        force_one = {}
        force_one['id'] = i
        force_one['name'] = exe_fd.read(8).decode('GBK').replace('\x00', '')
        force_one['des'] = des_fd.read(0xc8).decode('GBK').replace('\x00', '')
        if i == 0x0e:
            exe_fd.read(4)
        force_one['speed'] = u8(data_fd.read(1))
        force_one['hit_area'] = u8(data_fd.read(1))
        force_one['atk'] = u8(data_fd.read(1))
        force_one['def'] = u8(data_fd.read(1))
        force_one['mag'] = u8(data_fd.read(1))
        force_one['crt'] = u8(data_fd.read(1))
        force_one['mor'] = u8(data_fd.read(1))
        force_one['hp'] = u8(data_fd.read(1))
        force_one['mp'] = u8(data_fd.read(1))
        type_hold = []
        for j in range(18):
            type = u8(data_fd.read(1))
            if type == 1:
                type_hold.append(j)
        force_one['type_hold'] = type_hold
        # print(force_one)
        force_data.append(force_one)
    parse_data['force_data'] = force_data
    data_fd.close()
    des_fd.close()
    exe_fd.close()

def parse_terrain(ccz_path):
    terrain_data = []
    offset = int(config_data['Game_Terrain_Offset'], 16)
    force_count = int(config_data['Game_Force_Count'], 16)
    data_fd = open(ccz_path + '/Data.e5', 'rb')

    data_fd.seek(offset)

    for i in range(force_count):
        terrain_buff_one = []
        terrain_speed_one = []
        terrain_one = {}
        for j in range(30):
            terrain_buff_one.append(u8(data_fd.read(1)))
        for j in range(30):
            terrain_speed_one.append(u8(data_fd.read(1)))
        terrain_one['buff'] = terrain_buff_one
        terrain_one['speed'] = terrain_speed_one
        terrain_one['force_id'] = i
        # print(terrain_one)
        terrain_data.append(terrain_one)
    parse_data['terrain_data'] = terrain_data
    data_fd.close()


def parse_magic(ccz_path):
    magic_data = []
    offset = int(config_data['Game_Magic_Offset'], 16)
    des_offset = int(config_data['Imsg_Magic_Offset'], 16)
    count = int(config_data['Game_Magic_Count'], 16)
    force_count = int(config_data['Game_Force_Count'], 16)

    des_fd = open(ccz_path + "/Imsg.e5", 'rb')
    data_fd = open(ccz_path + "/Data.e5", 'rb')

    data_fd.seek(offset)
    des_fd.seek(des_offset)
    for i in range(count):
        magic_one = {}
        magic_one['id'] = i
        magic_one['name'] = data_fd.read(11).decode('GBK').replace('\x00', '')
        magic_one['des'] = des_fd.read(0xc8).decode('GBK').replace('\x00', '')
        magic_one['type'] = u8(data_fd.read(1))
        magic_one['eff_on'] = u8(data_fd.read(1))
        magic_one['hit_area'] = u8(data_fd.read(1))
        magic_one['eff_area'] = u8(data_fd.read(1))
        magic_one['mp'] = u8(data_fd.read(1))
        magic_one['icon'] = u8(data_fd.read(1))
        learn_lv = []
        for j in range(force_count):
            learn_lv.append(u8(data_fd.read(1)))
        magic_one['learn_lv'] = learn_lv
        # print(magic_one)
        magic_data.append(magic_one)
    parse_data['magic_data'] = magic_data
    des_fd.close()
    data_fd.close()


if __name__ == "__main__":
    f = open("ccz_origin.json", "r")
    json_data = f.read()
    config_data = json.loads(json_data)
    print(config_data)
    parse_unit("D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华")
    parse_item("D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华")
    parse_shop("D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华")
    parse_force("D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华")
    parse_terrain("D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华")
    parse_magic("D:/ccz_origin/三国志曹操传简体中文经典版 [水木清华特别版v4带全部动画].ccz.水木年华")

    f_out = open('parse.json', 'w', encoding='utf-8')
    f_out.write(json.dumps(parse_data, sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=False))
    # print(json.dumps(parse_data, sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=False))
