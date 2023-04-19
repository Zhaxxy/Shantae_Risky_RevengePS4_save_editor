HUGE_NUMBER = 999**999
import unittest
from functools import reduce
import inspect
import secrets



import Shantae_Risky_RevengePS4_save_editor
from SAVE_OFFSETS import SAVE_DATA_INFO_READ_ONLY
SAVE_FILES_SLOTS = SAVE_DATA_INFO_READ_ONLY.SAVE_FILES_SLOTS 

def get_from_dict(dataDict, mapList, it_has_the_value_too=True):
    """Iterate nested dictionary"""
    if it_has_the_value_too: mapList = mapList[:-1]
    return reduce(lambda d, k: d[k], mapList, dataDict)

def edit_in_dict(dataDict, mapList, value,it_has_the_value_too=True):
    """Edit value in nested dictionary"""
    if it_has_the_value_too: mapList = mapList[:-1]
    get_from_dict(dataDict, mapList[:-1],False)[mapList[-1]] = value

def is_hex_string(s):
    """
    Made by chatGPT!
    """
    if not isinstance(s,str): return False
    from string import hexdigits
    return all(c in hexdigits for c in s.upper())

def get_nested_keys_and_values(d, path=None):
    """
    Made by chatGPT!
    """

    if path is None:
        path = []
    if isinstance(d, dict):
        for key, value in d.items():
            yield from get_nested_keys_and_values(value, path + [key])
    elif isinstance(d, list):
        for i, value in enumerate(d):
            yield from get_nested_keys_and_values(value, path + [i])
    else:
        yield path + [d]



empty_save_all_zeros = b'\x76\xD4\xFE\x54'.ljust(0x800,b'\x00')

import os
TESTS_DIR = 'tests'

class TestRiskyRevengeSav(unittest.TestCase):
    def test_parse_unparse_json(self):
        test_save = Shantae_Risky_RevengePS4_save_editor.RiskyRevengeSav(empty_save_all_zeros)
        the_json = test_save.parse_to_dictionary()
        del test_save
        
        for xpath in get_nested_keys_and_values(the_json):
            if Shantae_Risky_RevengePS4_save_editor.is_path_a_comment(xpath): continue
            
            if xpath[0] == 'current_dictionary_editor_version_doNotEdit': continue
            if xpath[0] == 'doNotEditThis': continue
            
            if isinstance(xpath[-1],bool):
                edit_in_dict(the_json,xpath,True)
            elif isinstance(xpath[-1],int):
                edit_in_dict(the_json,xpath,2) #seems pretty safe
            elif is_hex_string(xpath[-1]) and xpath[2] == 'checkpoint_bytes':
                edit_in_dict(the_json,xpath,'0000000000000002') 
            elif isinstance(xpath[-1],str) and xpath[1] == 'screen_mode':
                edit_in_dict(the_json,xpath,'Square (4:3)')
            else:
                raise ValueError(f'idk what {xpath} is')# fix it later
        
        test_save = Shantae_Risky_RevengePS4_save_editor.RiskyRevengeSav.from_dictionary(the_json)
        
        methods = [attr for attr in inspect.getmembers(test_save) if inspect.isroutine(attr[1])]
        get_methods = list(filter(lambda meth: meth[0].startswith('get_'),methods))
        
        for getter in get_methods:
            for savenumber in SAVE_FILES_SLOTS:
                value = getter[1](savenumber)
                if isinstance(value,int) and not isinstance(value, bool):
                    self.assertEqual(value, 2)
                if isinstance(value,bool):
                    self.assertTrue(value)
                if isinstance(value,str):
                    self.assertEqual(value, 'Square (4:3)')
                if isinstance(value,bytes) or isinstance(value,bytearray):
                    self.assertEqual(value, b'\x00\x00\x00\x00\x00\x00\x00\x02')

    def test_save_checker(self):
        save_with_bad_header  = b'\x6e\x76\x7A\x72'.ljust(0x800,b'\x00')
        self.assertFalse(Shantae_Risky_RevengePS4_save_editor.check_save(save_with_bad_header))
        
        save_with_short_length = b'\x76\xD4\xFE\x54'.ljust(0x799,b'\x00')
        self.assertFalse(Shantae_Risky_RevengePS4_save_editor.check_save(save_with_short_length))
        
        save_with_big_length = b'\x76\xD4\xFE\x54'.ljust(0x801,b'\x00')
        self.assertFalse(Shantae_Risky_RevengePS4_save_editor.check_save(save_with_big_length))
        
        random_save = b'\x76\xD4\xFE\x54' + secrets.token_bytes(0x800-4)
        self.assertTrue(Shantae_Risky_RevengePS4_save_editor.check_save(random_save))
        
    def test_max_ints_raises_errors(self):
        test_save = Shantae_Risky_RevengePS4_save_editor.RiskyRevengeSav(empty_save_all_zeros)
        methods = [attr for attr in inspect.getmembers(test_save) if inspect.isroutine(attr[1])]
        
        get_methods = list(filter(lambda meth: meth[0].startswith('get_'),methods))
        set_methods = list(filter(lambda meth: meth[0].startswith('set_'),methods))
        
        for getter,setter in zip(get_methods,set_methods):
            for savenumber in SAVE_FILES_SLOTS:
                value = getter[1](savenumber)
                if isinstance(value,int) and not isinstance(value, bool):
                    with self.assertRaises(ValueError):
                        setter[1](HUGE_NUMBER,savenumber)
                    with self.assertRaises(ValueError):
                        setter[1](-1,savenumber)

    def test_random_save(self):
        with open(os.path.join(TESTS_DIR,'random_save','savedata.sav'),'rb') as f:
            leh_bytes = f.read()
        
        save1_parsed_from_dict = Shantae_Risky_RevengePS4_save_editor.RiskyRevengeSav(leh_bytes)
        save_dict = save1_parsed_from_dict.parse_to_dictionary()

        save = Shantae_Risky_RevengePS4_save_editor.RiskyRevengeSav.from_dictionary(save_dict)
        self.assertEqual(save,save1_parsed_from_dict)

        


        save2_tested_all_setters = Shantae_Risky_RevengePS4_save_editor.RiskyRevengeSav(leh_bytes)
        methods = [attr for attr in inspect.getmembers(save2_tested_all_setters) if inspect.isroutine(attr[1])]
        get_methods = list(filter(lambda meth: meth[0].startswith('get_'),methods))
        set_methods = list(filter(lambda meth: meth[0].startswith('set_'),methods))

        for getter, setter in zip(get_methods,set_methods):
            for savenumber in SAVE_FILES_SLOTS:
                setter[1](getter[1](savenumber),savenumber)
        
        save2_tested_all_setters.screen_mode = save2_tested_all_setters.screen_mode
        save2_tested_all_setters.music_volume = save2_tested_all_setters.music_volume
        save2_tested_all_setters.sound_volume = save2_tested_all_setters.sound_volume
        self.assertEqual(save,save2_tested_all_setters)
        
        self.assertEqual(save.get_gems(1), 534)
        self.assertEqual(save.get_gems(2), 496)
        self.assertEqual(save.get_magic_potions_count(1), 6)
        self.assertEqual(save.get_health_vials_count(1), 8)
        self.assertTrue(save.get_has_storm_puff(1))
        self.assertTrue(save.get_has_monkey_dance(1))
        self.assertEqual(save.get_hearts(1), 3)
        self.assertEqual(save.get_current_health(1), 12)
        self.assertEqual(save.get_current_magic(1), 100)
        self.assertTrue(save.get_has_map(1))
        self.assertFalse(save.get_has_golden_squid_baby(1))
        self.assertEqual(save.screen_mode, 'Wide (16:9)')
        self.assertTrue(save.get_has_magic_fill(1))
        self.assertEqual(save.get_magic_seals_count(1), 3)
        self.assertTrue(save.get_has_magic_seal(1))


        formated_time_file_a = Shantae_Risky_RevengePS4_save_editor.format_ingame_time(save.get_save_file_time(1))
        self.assertEqual(formated_time_file_a,'01:37')

        formated_time_file_b = Shantae_Risky_RevengePS4_save_editor.format_ingame_time(save.get_save_file_time(2))
        self.assertEqual(formated_time_file_b,'01:30')

        self.assertFalse(save.get_is_used1(3))

        self.assertFalse(save.get_has_puppy(1))
        self.assertFalse(save.get_has_puppy(2))
        self.assertFalse(save.get_has_puppy(3))

        self.assertEqual(save.get_area_relative_x_pos(1),83520)
        self.assertEqual(save.get_area_relative_y_pos(1),71935)
