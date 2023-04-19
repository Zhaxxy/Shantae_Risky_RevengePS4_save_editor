if __name__ == "__main__":
    from sys import exit as gfhr5yuhrtfchsxrt6
    print("This module cannot be run as a script.")
    gfhr5yuhrtfchsxrt6()


from io import BytesIO
from bitstring import BitArray as ba
import logging
import struct
import inspect

try:
    from Shantae_Risky_RevengePS4_save_editor.SAVE_OFFSETS import SAVE_DATA_INFO_READ_ONLY as offsets_n_stuff
except ModuleNotFoundError:
    from SAVE_OFFSETS import SAVE_DATA_INFO_READ_ONLY as offsets_n_stuff
#logging.basicConfig(level=logging.DEBUG)


"""

all of them are unsigned ints, unless specified  otherwise

data is stored in blocks or arrays or whatever, so i need to figure out what theese sections are, blocks are stored in little endian since its a ps4 save
each save entry (file select) stores theese blocks side by side, so when i say offset i mean the offset of the block for save 1, offsets relative to entire save file


look at the constants for more info, dont bother looking at the setter and getter functions, although some may
some custom code, ill be sure to point that out in the constants though
"""

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


def ensure_valid_value(value, constant, data_type_is,*,fix_the_value=False):
    """
    Raise a ValueError if the value is invalid
    param fix_the_value: if true try to fix the value if its invalid, if it cant then just raise ValueError
    param data_type_is: the data_type_is it should be, if its not here, just return the value
    param constant: a tuple in the format (offset,length), ignore the 'offset', the 'length' is in bits
    

    """
    
    if data_type_is not in ('int','uint','bytes'):
        return value
    
    if data_type_is == 'uint':
        max_value = 2**(constant[1])-1
        min_value = 0
    
        if not isinstance(value,int):
            raise ValueError(f'{value} is not a {data_type_is}')
    
        if value > max_value:
            if fix_the_value:
                logging.info(f'{value} is bigger than {max_value}, so returning {max_value}')
                return max_value
                
            raise ValueError(f'{value} is bigger than {max_value}! must be between {min_value} and {max_value} for {data_type_is} constant = {constant}')

        if value < min_value:
            if fix_the_value:
                logging.info(f'{value} is smaller than {min_value}, so returning {min_value}')
                return min_value
            
            raise ValueError(f'{value} is smaller than {min_value}! must be between {min_value} and {max_value} for {data_type_is} constant = {constant}')
    
    if data_type_is == 'int':
        max_value = 2**(constant[1]-1)-1
        min_value = 2**(constant[1]-1) * -1
        
        if not isinstance(value,int):
            raise ValueError(f'{value} is not a {data_type_is}')
        
        if value > max_value:
            if fix_the_value:
                logging.info(f'{value} is bigger than {max_value}, so returning {max_value}')
                return max_value

            raise ValueError(f'{value} is bigger than {max_value}! must be between {min_value} and {max_value} for {data_type_is} constant = {constant}')
        
        if value < min_value:
            if fix_the_value:
                logging.info(f'{value} is smaller than {min_value}, so returning {min_value}')
                return max_value
            
            raise ValueError(f'{value} is negative! must be between {min_value} and {max_value} for {data_type_is} constant = {constant}')

    if data_type_is == 'bytes':
        required_bytes_length = constant[1]//8
        entered_bytes_length = len(value)
        
        if entered_bytes_length != required_bytes_length:
            raise ValueError(f'{value.hex()} is {entered_bytes_length} bytes, it must be {required_bytes_length} bytes')

    return value


def is_path_a_comment(path_as_itr):
    return any('_comment' in json_dir for json_dir in path_as_itr if isinstance(json_dir, str))

def format_ingame_time(time_as_int):
    seconds = time_as_int // 60
    hours, extra_seconds = divmod(seconds,3600)
    minutes = extra_seconds // 60
    return f'{hours:02d}:{minutes:02d}'

def time2ingame_time(formated_ingame_time,must_be_in_use=True):
    hours, minutes = formated_ingame_time.split(':')
    total_minutes = (int(hours) * 60) + int(minutes)
    return min((total_minutes * 60)*60,1) if must_be_in_use else (total_minutes * 60)*60

def make_zeros_save():
    return b'\x76\xD4\xFE\x54'.ljust(0x800,b'\x00')

def check_save(save_bytes):
    return save_bytes.startswith(b'\x76\xD4\xFE\x54') and len(save_bytes) == 0x800

def check_dictionary_save(save_dictionary,check_values_too=True):
    placeholder_save_bytes = make_zeros_save()
    placeholder_save = RiskyRevengeSav(placeholder_save_bytes)
    template_dict = placeholder_save.parse_to_dictionary()

    for template_key, entered_key in zip(get_nested_keys_and_values(template_dict), get_nested_keys_and_values(save_dictionary)):
        if is_path_a_comment(template_key):
            if template_key != entered_key:
                return False
        if template_key[:-1] != entered_key[:-1]:
            return False
    if check_values_too:
        try:
            RiskyRevengeSav.from_dictionary(save_dictionary)
        except:
            return False
    
    
    return True

def max_int(bits_size,*,is_uint=True):
    return 2**bits_size-1 if is_uint else (2**bits_size-1)//2



def change_endianes(data,endianes):  
    if endianes.lower() == 'little':
        data = bytearray(data)
        data.reverse()
        return data
    elif endianes.lower() == 'big':
        return data
    else:
        raise ValueError(f'{endianes} is not a valid endian, use little or big')

def unjsonify_string(json_key_string: str) -> str:
    return json_key_string.replace('_',' ')

def jsonify_string(key_string: str) -> str:
    return key_string.replace(' ','_')

class RiskyRevengeSav:
    def __eq__(self, other):
        return self.export_save() == other.export_save()
    
    _current_editor_version = '0.91' # read only
    @property
    def current_version(self):
        return self._current_editor_version

    _current_dictionary_editor_version = '0.91' # read only
    @property
    def current_dictionary_version(self):
        return self._current_dictionary_editor_version
    
    @classmethod
    def from_dictionary(cls,parsed_dict):
        if parsed_dict['current_dictionary_editor_version_doNotEdit'] != cls._current_dictionary_editor_version:
            raise TypeError('Not a vlaldu idk temp')

        save = cls(bytearray.fromhex(parsed_dict['doNotEditThis']))

        for x in get_nested_keys_and_values(parsed_dict):
            if is_path_a_comment(x): continue
            
            for savenumber in offsets_n_stuff.SAVE_FILES_SLOTS:
                if x[0] != jsonify_string(offsets_n_stuff.SAVE_FILES_SLOTS_INGAME[savenumber]): continue
                
                if x[1] == 'misc':
                    if x[2] == 'is_used1': save.set_is_used1(x[-1],savenumber)
                    if x[2] == 'save_file_time': save.set_save_file_time(x[-1],savenumber)
                    if x[2] == 'always_running': save.set_always_running(x[-1],savenumber)
  
                if x[1] == 'location':
                    if x[2] == 'x': save.set_area_relative_x_pos(x[-1],savenumber)
                    if x[2] == 'y': save.set_area_relative_y_pos(x[-1],savenumber)
                    if x[2] == 'checkpoint_bytes': save.set_last_8_bytes(bytes.fromhex(x[-1]),savenumber)
                

                if x[1] == 'gems': save.set_gems(x[-1],savenumber)
                if x[1] == 'current_health': save.set_current_health(x[-1],savenumber)
                if x[1] == 'hearts': save.set_hearts(x[-1],savenumber)
                if x[1] == 'current_magic': save.set_current_magic(x[-1],savenumber)
                
                if x[1] == 'inventory':
                    if x[-2] == 'in_inventory':
                        hasser = getattr(save,f'set_has_{x[-3]}')
                        hasser(x[-1],savenumber)
                    if x[-2] == 'count':
                        try:
                            hasser_count = getattr(save,f'set_{x[-3]}_count')
                        except AttributeError:
                            hasser_count = getattr(save,f'set_{x[-3]}s_count')
                        hasser_count(x[-1],savenumber)

            if x[0] == 'settings':
                if 'screen_mode' in x:
                    save.screen_mode = x[-1]
                if 'music_volume' in x:
                    save.music_volume = x[-1]
                if 'sound_volume' in x:
                    save.sound_volume = x[-1]
        return save
    def parse_to_dictionary(self):
        methods = [attr for attr in inspect.getmembers(self) if inspect.isroutine(attr[1])]

        parsed_dict = {'current_dictionary_editor_version_doNotEdit':self.current_dictionary_version,
                       'doNotEditThis':self.export_save().hex(),
                       }

        for savenumber in offsets_n_stuff.SAVE_FILES_SLOTS:
            save_name_ingame = jsonify_string(offsets_n_stuff.SAVE_FILES_SLOTS_INGAME[savenumber])
            save_data_dict = {save_name_ingame:{}}
            sa = save_data_dict[save_name_ingame]
            sa.update({'misc':{}})
            misc = sa['misc']

            misc['is_used1'] = self.get_is_used1(savenumber)
            misc['save_file_time'] = [self.get_save_file_time(savenumber),{'_comment_max':max_int(offsets_n_stuff.SAVE_FILE_TIME_BITS[1])}]
            misc['always_running'] = self.get_always_running(savenumber)


            
            sa.update({'location':{}})
            lo = sa['location']

            lo['x'] = [self.get_area_relative_x_pos(savenumber),   {'_comment_max':max_int(offsets_n_stuff.AREA_RELATIVE_X_POS_BITS[1])} ]
            lo['y'] = [self.get_area_relative_y_pos(savenumber),   {'_comment_max':max_int(offsets_n_stuff.AREA_RELATIVE_Y_POS_BITS[1])}]
            lo['checkpoint_bytes'] = [self.get_last_8_bytes(savenumber).hex(),{'_comment_required_byte_length':'It needs to be 8 bytes long'}]

            sa['gems'] = [self.get_gems(savenumber), {'_comment_max':max_int(offsets_n_stuff.GEMS_BITS[1])}]
            sa['hearts'] = [self.get_hearts(savenumber), {'_comment_max':max_int(offsets_n_stuff.HEARTS_BITS[1])}]
            sa['current_health'] = [self.get_current_health(savenumber), {'_comment_max':max_int(offsets_n_stuff.CURRENT_HEALTH_BITS[1])}]
            sa['current_magic'] = [self.get_current_magic(savenumber),   {'_comment_max':max_int(offsets_n_stuff.CURRENT_MAGIC_BITS[1])}]

            sa.update({'inventory':{}})
            inv = sa['inventory']
            for method in methods:
                if method[0].startswith('get_'):
                    if 'has_' in method[0]:
                        uhhh = method[0].split('has_')[-1]
                        has_count = False
                        for method2 in methods:
                            if method2[0].startswith('get_'):
                                if 'count' in method2[0] and uhhh in method2[0]:
                                    has_count = method2
                        if has_count:
                            the_constant_strname = has_count[0].replace('get_','').upper() + '_BITS'
                            the_constant = getattr(offsets_n_stuff, the_constant_strname)
                            

                            inv.update({uhhh:{'in_inventory':method[1](savenumber),'count':has_count[1](savenumber),'_comment_max_count':max_int(the_constant[1])}})
                        else:
                            inv.update({uhhh:{'in_inventory':method[1](savenumber)}})

            parsed_dict.update(save_data_dict)        
        
        parsed_dict.update({'settings':{}})
        se = parsed_dict['settings']

        se['screen_mode'] = [self.screen_mode,{'_comment_valid_options':list(offsets_n_stuff.SCREEN_MODE_INGAME)}]
        se['music_volune'] = [self.music_volume,{'_comment_max':max_int(offsets_n_stuff.MUSIC_VOLUME_BITS[1])}]
        se['sound_volume'] = [self.sound_volume,{'_comment_max':max_int(offsets_n_stuff.SOUND_VOLUME_BITS[1])}]

        return parsed_dict

    def _read_data(self,
                    offset_n_length,
                    savenumber,
                    bit_offset_n_length,
                    data_type_is='uint',
                    *,
                    endianness='little'):
        
        if data_type_is == 'bytes': logging.warning('You really should not be using the bytes data_type_is, so the order will not swap if little endian')
        
        
        if savenumber not in offsets_n_stuff.SAVE_FILES_SLOTS:
            raise ValueError(f'{savenumber} not a valid save file number')
        
        new_offset = (offset_n_length[0] - offset_n_length[1]) + (offset_n_length[1]*savenumber)
        self._savedata.seek(new_offset)
        new_data = self._savedata.read(offset_n_length[1])
        self._savedata.seek(0)
        
        logging.debug(f'Orignal block is: {new_data.hex()}')
        
        new_bitarray = ba(bytes=change_endianes(new_data,endianness))
        logging.debug(f'We read the block as: {new_bitarray.tobytes().hex()}')


        the_raw_bits = new_bitarray[bit_offset_n_length[0]:bit_offset_n_length[0] + bit_offset_n_length[1]]
        logging.debug(f'Got the bits: {"0x"+the_raw_bits.tobytes().hex() if bit_offset_n_length[1] % 8 == 0 else the_raw_bits.bin}')


        ############# methods here
        if data_type_is.lower() == 'uint':
            return the_raw_bits.uint
        elif data_type_is.lower() == 'int':
            return the_raw_bits.int
        elif data_type_is.lower() == 'bool':
            return bool(the_raw_bits.uint)
        elif data_type_is == 'float':
            float_bytes = the_raw_bits.tobytes()
            return struct.unpack('>f', float_bytes)[0]

        elif data_type_is.lower() == 'bytes':
            return change_endianes(the_raw_bits.tobytes(),endianness)


        elif data_type_is.lower() == 'time': #DONT USE THIS METHOD, JUST MANUPLATE THE INT MANUALLY!
            time_count = the_raw_bits.uint
            return datetime.timedelta(seconds=time_count//60)
        else:
            raise NotImplementedError(f'{data_type_is} data type is not supported')
        ############# methods here        
        
    def _write_data(self,
                    offset_n_length,
                    savenumber,
                    bit_offset_n_length,
                    value,
                    data_type_is='uint',
                    *,
                    endianness=offsets_n_stuff.GLOBAL_ENDIAN):
        
        if data_type_is == 'bytes': logging.warning('You really should not be using the bytes data_type_is, so the order will not swap if little endian')
        
        if savenumber not in offsets_n_stuff.SAVE_FILES_SLOTS:
            raise ValueError(f'{savenumber} not a valid save file number')
        

        
        value = ensure_valid_value(value,bit_offset_n_length,data_type_is)
        
        
        new_offset = (offset_n_length[0] - offset_n_length[1]) + (offset_n_length[1]*savenumber)
        if type(value) == int: printvalue = hex(value)
        else: printvalue = value
        logging.debug(f'offset is {hex(new_offset)} old offset is {hex(offset_n_length[0])} value is {printvalue}')
        self._savedata.seek(new_offset)
        new_data = self._savedata.read(offset_n_length[1])
        self._savedata.seek(0)
        
        new_bitarray = ba(bytes=change_endianes(new_data,endianness))
        
        
        

        ############# methods here
        if data_type_is.lower() == 'bytes':
            new_value = ba(bytes=change_endianes(value,endianness))
        elif data_type_is.lower() == 'float':
            float_byets_value = struct.pack('>f', value)
            new_value = ba(bytes=float_byets_value)
        elif data_type_is.lower() == 'uint':
            new_value = ba(uint=value,length=bit_offset_n_length[1])
        elif data_type_is.lower() == 'int':
            new_value = ba(int=value,length=bit_offset_n_length[1])
        elif data_type_is.lower() == 'bool':
            new_value = 1 if value else 0
        elif data_type_is.lower() == 'time':
            new_value = value.total_seconds()*60
        else:
            raise NotImplementedError(f'{data_type_is} data type is not supported')
        ############## methods here
        og = len(new_bitarray)
        new_bitarray[bit_offset_n_length[0]:bit_offset_n_length[0] + bit_offset_n_length[1]] = new_value
        assert og == len(new_bitarray)
        new_bytes_to_write = change_endianes(new_bitarray.bytes,offsets_n_stuff.GLOBAL_ENDIAN)
        self._savedata.seek(new_offset)
        self._savedata.write(new_bytes_to_write)
        self._savedata.seek(0)
    

    
    def __init__(self,savedata_sav_bytes):
        self._savedata = BytesIO(savedata_sav_bytes)
        
    def export_save(self):
        return self._savedata.getvalue()

    def check_if_used(self,savenumber):
        return self.get_save_file_time(savenumber) < 1 or not self.get_is_used1(savenumber)
    
    def __str__(self):
        if self.get_save_file_time(1) < 1 or not self.get_is_used1(1):
            time1 = 'NEW'
        else:
            time1 = format_ingame_time(self.get_save_file_time(1))
            
        if self.get_save_file_time(2) < 1 or not self.get_is_used1(2):
            time2 = 'NEW'
        else:
            time2 = format_ingame_time(self.get_save_file_time(2))
            
        if self.get_save_file_time(3) < 1 or not self.get_is_used1(3):
            time3 = 'NEW'
        else:
            time3 = format_ingame_time(self.get_save_file_time(3))
        
        
        return f'File A: {time1}\nFile B: {time2}\nFile C: {time3}'
        

    def get_gems(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. GEMS_BITS,
        'uint')

    def set_gems(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. GEMS_BITS,
        value,
        'uint')

    def get_always_running(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. ALWAYS_RUNNING_BIT,
        'bool')

    def set_always_running(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. ALWAYS_RUNNING_BIT,
        value,
        'bool')

    def get_is_used1(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. IS_USED1_BIT,
        'bool')

    def set_is_used1(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. IS_USED1_BIT,
        value,
        'bool')

    def get_hearts(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. HEARTS_BITS,
        'uint')

    def set_hearts(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. GEMS_AND_STUFF,
        savenumber,
        offsets_n_stuff. HEARTS_BITS,
        value,
        'uint')

    def get_magic_potions_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_HEALTH_VIALS,
        savenumber,
        offsets_n_stuff. MAGIC_POTIONS_COUNT_BITS,
        'uint')

    def set_magic_potions_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_HEALTH_VIALS,
        savenumber,
        offsets_n_stuff. MAGIC_POTIONS_COUNT_BITS,
        value,
        'uint')

    def get_health_vials_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_HEALTH_VIALS,
        savenumber,
        offsets_n_stuff. HEALTH_VIALS_COUNT_BITS,
        'uint')

    def set_health_vials_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_HEALTH_VIALS,
        savenumber,
        offsets_n_stuff. HEALTH_VIALS_COUNT_BITS,
        value,
        'uint')

    def get_golden_squid_baby_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. ITEMS_WITH_AMOUNTS1,
        savenumber,
        offsets_n_stuff. GOLDEN_SQUID_BABY_COUNT_BITS,
        'uint')

    def set_golden_squid_baby_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. ITEMS_WITH_AMOUNTS1,
        savenumber,
        offsets_n_stuff. GOLDEN_SQUID_BABY_COUNT_BITS,
        value,
        'uint')

    def get_magic_seals_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. ITEMS_WITH_AMOUNTS1,
        savenumber,
        offsets_n_stuff. MAGIC_SEALS_COUNT_BITS,
        'uint')

    def set_magic_seals_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. ITEMS_WITH_AMOUNTS1,
        savenumber,
        offsets_n_stuff. MAGIC_SEALS_COUNT_BITS,
        value,
        'uint')

    def get_magic_jams_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. ITEMS_WITH_AMOUNTS1,
        savenumber,
        offsets_n_stuff. MAGIC_JAMS_COUNT_BITS,
        'uint')

    def set_magic_jams_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. ITEMS_WITH_AMOUNTS1,
        savenumber,
        offsets_n_stuff. MAGIC_JAMS_COUNT_BITS,
        value,
        'uint')

    def get_has_map(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAP_BIT,
        'bool')

    def set_has_map(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAP_BIT,
        value,
        'bool')

    def get_has_fireball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_FIREBALL_BIT,
        'bool')

    def set_has_fireball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_FIREBALL_BIT,
        value,
        'bool')

    def get_has_spitfire(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SPITFIRE_BIT,
        'bool')

    def set_has_spitfire(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SPITFIRE_BIT,
        value,
        'bool')

    def get_has_flamethrower(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_FLAMETHROWER_BIT,
        'bool')

    def set_has_flamethrower(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_FLAMETHROWER_BIT,
        value,
        'bool')

    def get_has_pike_ball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PIKE_BALL_BIT,
        'bool')

    def set_has_pike_ball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PIKE_BALL_BIT,
        value,
        'bool')

    def get_has_super_pike_ball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SUPER_PIKE_BALL_BIT,
        'bool')

    def set_has_super_pike_ball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SUPER_PIKE_BALL_BIT,
        value,
        'bool')

    def get_has_mega_pike_ball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MEGA_PIKE_BALL_BIT,
        'bool')

    def set_has_mega_pike_ball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MEGA_PIKE_BALL_BIT,
        value,
        'bool')

    def get_has_storm_puff(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_STORM_PUFF_BIT,
        'bool')

    def set_has_storm_puff(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_STORM_PUFF_BIT,
        value,
        'bool')

    def get_has_crush_puff(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_CRUSH_PUFF_BIT,
        'bool')

    def set_has_crush_puff(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_CRUSH_PUFF_BIT,
        value,
        'bool')

    def get_has_mega_puff(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MEGA_PUFF_BIT,
        'bool')

    def set_has_mega_puff(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MEGA_PUFF_BIT,
        value,
        'bool')

    def get_has_prohibition_sign(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PROHIBITION_SIGN_BIT,
        'bool')

    def set_has_prohibition_sign(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PROHIBITION_SIGN_BIT,
        value,
        'bool')

    def get_has_hearts_holder(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_HEARTS_HOLDER_BIT,
        'bool')

    def set_has_hearts_holder(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_HEARTS_HOLDER_BIT,
        value,
        'bool')

    def get_has_golden_squid_baby(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_GOLDEN_SQUID_BABY_BIT,
        'bool')

    def set_has_golden_squid_baby(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_GOLDEN_SQUID_BABY_BIT,
        value,
        'bool')

    def get_has_monkey_dance(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MONKEY_DANCE_BIT,
        'bool')

    def set_has_monkey_dance(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MONKEY_DANCE_BIT,
        value,
        'bool')

    def get_has_elphant_dance(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ELPHANT_DANCE_BIT,
        'bool')

    def set_has_elphant_dance(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ELPHANT_DANCE_BIT,
        value,
        'bool')

    def get_has_mermaid_dance(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MERMAID_DANCE,
        'bool')

    def set_has_mermaid_dance(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MERMAID_DANCE,
        value,
        'bool')

    def get_has_attract_magic(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ATTRACT_MAGIC_BIT,
        'bool')

    def set_has_attract_magic(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ATTRACT_MAGIC_BIT,
        value,
        'bool')

    def get_has_magic_fill(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_FILL_BIT,
        'bool')

    def set_has_magic_fill(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_FILL_BIT,
        value,
        'bool')

    def get_has_silky_cream(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SILKY_CREAM_BIT,
        'bool')

    def set_has_silky_cream(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SILKY_CREAM_BIT,
        value,
        'bool')

    def get_has_super_silky_cream(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SUPER_SILKY_CREAM_BIT,
        'bool')

    def set_has_super_silky_cream(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SUPER_SILKY_CREAM_BIT,
        value,
        'bool')

    def get_has_puppy(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PUPPY_BIT,
        'bool')

    def set_has_puppy(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PUPPY_BIT,
        value,
        'bool')

    def get_has_tasty_meal(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_TASTY_MEAL_BIT,
        'bool')

    def set_has_tasty_meal(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_TASTY_MEAL_BIT,
        value,
        'bool')

    def get_has_skys_egg(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SKYS_EGG_BIT,
        'bool')

    def set_has_skys_egg(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SKYS_EGG_BIT,
        value,
        'bool')

    def get_has_scuttle_deed(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SCUTTLE_DEED_BIT,
        'bool')

    def set_has_scuttle_deed(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_SCUTTLE_DEED_BIT,
        value,
        'bool')

    def get_has_ammo_town_passport(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_AMMO_TOWN_PASSPORT_BII,
        'bool')

    def set_has_ammo_town_passport(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_AMMO_TOWN_PASSPORT_BII,
        value,
        'bool')

    def get_has_coffee_beans(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_COFFEE_BEANS_BIT,
        'bool')

    def set_has_coffee_beans(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_COFFEE_BEANS_BIT,
        value,
        'bool')

    def get_has_broken_coffee_machine(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_BROKEN_COFFEE_MACHINE_BIT,
        'bool')

    def set_has_broken_coffee_machine(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_BROKEN_COFFEE_MACHINE_BIT,
        value,
        'bool')

    def get_has_zombie_latte(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ZOMBIE_LATTE_BIT,
        'bool')

    def set_has_zombie_latte(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ZOMBIE_LATTE_BIT,
        value,
        'bool')

    def get_has_plastic_explosives(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PLASTIC_EXPLOSIVES,
        'bool')

    def set_has_plastic_explosives(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PLASTIC_EXPLOSIVES,
        value,
        'bool')

    def get_has_forest_key(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_FOREST_KEY_BIT,
        'bool')

    def set_has_forest_key(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_FOREST_KEY_BIT,
        value,
        'bool')

    def get_has_plastic_explosives(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PLASTIC_EXPLOSIVES_BIT,
        'bool')

    def set_has_plastic_explosives(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_PLASTIC_EXPLOSIVES_BIT,
        value,
        'bool')

    def get_has_monkey_bullet(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MONKEY_BULLET_BIT,
        'bool')

    def set_has_monkey_bullet(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MONKEY_BULLET_BIT,
        value,
        'bool')

    def get_has_elphant_stomp(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ELPHANT_STOMP_BIT,
        'bool')

    def set_has_elphant_stomp(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_ELPHANT_STOMP_BIT,
        value,
        'bool')

    def get_has_mermaid_bubble(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MERMAID_BUBBLE_BIT,
        'bool')

    def set_has_mermaid_bubble(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MERMAID_BUBBLE_BIT,
        value,
        'bool')

    def get_has_top_half_skull(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_TOP_HALF_SKULL_BIT,
        'bool')

    def set_has_top_half_skull(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_TOP_HALF_SKULL_BIT,
        value,
        'bool')

    def get_has_bottom_half_skull(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_BOTTOM_HALF_SKULL_BIT,
        'bool')

    def set_has_bottom_half_skull(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_BOTTOM_HALF_SKULL_BIT,
        value,
        'bool')

    def get_has_bottom_half_skull(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_BOTTOM_HALF_SKULL_BIT,
        'bool')

    def set_has_bottom_half_skull(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_BOTTOM_HALF_SKULL_BIT,
        value,
        'bool')

    def get_has_magic_seal(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_SEAL_BIT,
        'bool')

    def set_has_magic_seal(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_SEAL_BIT,
        value,
        'bool')

    def get_has_magic_jam(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. RANDOM_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_JAM_BIT,
        'bool')

    def set_has_magic_jam(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. RANDOM_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_JAM_BIT,
        value,
        'bool')


    def get_has_magic_potion(self,savenumber: int):
        has_magic_potion1 =  RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_POTION1_BIT,
        'bool')

        has_magic_potion2 =  RiskyRevengeSav._read_data(self,
        offsets_n_stuff. RANDOM_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_POTION2_BIT,
        'bool')

        if has_magic_potion1 != has_magic_potion2:
            raise ValueError(f'WTF {has_magic_potion1 = } {has_magic_potion2 = }')
        return has_magic_potion1

    def set_has_magic_potion(self,value,savenumber: int):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_POTION1_BIT,
        value,
        'bool')

        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. RANDOM_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_MAGIC_POTION2_BIT,
        value,
        'bool')

    def get_has_health_vial(self,savenumber: int):
        has_health_vial1 =  RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_HEALTH_VIAL1_BIT,
        'bool')

        has_health_vial2 =  RiskyRevengeSav._read_data(self,
        offsets_n_stuff. RANDOM_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_HEALTH_VIAL2_BIT,
        'bool')

        if has_health_vial1 != has_health_vial2:
            raise ValueError(f'WTF {has_health_vial1 = } {has_health_vial2 = }')
        return has_health_vial1

    def get_area_relative_y_pos(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff.  MASSIVE_BLOCK_CHECKPOINT,
        savenumber,
        offsets_n_stuff.  AREA_RELATIVE_Y_POS_BITS,
        'uint')

    def set_area_relative_y_pos(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff.  MASSIVE_BLOCK_CHECKPOINT,
        savenumber,
        offsets_n_stuff.  AREA_RELATIVE_Y_POS_BITS,
        value,
        'uint')

    def get_area_relative_x_pos(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff.  MASSIVE_BLOCK_CHECKPOINT,
        savenumber,
        offsets_n_stuff.  AREA_RELATIVE_X_POS_BITS,
        'uint')

    def set_area_relative_x_pos(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff.  MASSIVE_BLOCK_CHECKPOINT,
        savenumber,
        offsets_n_stuff.  AREA_RELATIVE_X_POS_BITS,
        value,
        'uint')

    def get_last_8_bytes(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff.  MASSIVE_BLOCK_CHECKPOINT,
        savenumber,
        offsets_n_stuff.  LAST_8_BYTES_BITS,
        'bytes')

    def set_last_8_bytes(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff.  MASSIVE_BLOCK_CHECKPOINT,
        savenumber,
        offsets_n_stuff.  LAST_8_BYTES_BITS,
        value,
        'bytes')

    def set_has_health_vial(self,value,savenumber: int):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MAGIC_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_HEALTH_VIAL1_BIT,
        value,
        'bool')

        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. RANDOM_ITEMS,
        savenumber,
        offsets_n_stuff. HAS_HEALTH_VIAL2_BIT,
        value,
        'bool')

    def get_save_file_time(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. SAVE_FILE_TIME,
        savenumber,
        offsets_n_stuff. SAVE_FILE_TIME_BITS,
        'uint')

    def set_save_file_time(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. SAVE_FILE_TIME,
        savenumber,
        offsets_n_stuff. SAVE_FILE_TIME_BITS,
        value,
        'uint')

    def get_current_health(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. CURRENT_HEALTH,
        savenumber,
        offsets_n_stuff. CURRENT_HEALTH_BITS,
        'uint')

    def set_current_health(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. CURRENT_HEALTH,
        savenumber,
        offsets_n_stuff. CURRENT_HEALTH_BITS,
        value,
        'uint')

    def get_current_magic(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. CURRENT_MAGIC,
        savenumber,
        offsets_n_stuff. CURRENT_MAGIC_BITS,
        'uint')

    def set_current_magic(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. CURRENT_MAGIC,
        savenumber,
        offsets_n_stuff. CURRENT_MAGIC_BITS,
        value,
        'uint')

    # def _get_screen_mode(self):
        # return  RiskyRevengeSav._read_data(self,
        # offsets_n_stuff. SCREEN_MODE,
        # 1,
        # offsets_n_stuff. SCREEN_MOD_BITS,
        # 'uint')


    # def _set_screen_mode(self,value):
        # RiskyRevengeSav._write_data(self,
        # offsets_n_stuff. SCREEN_MODE,
        # 1,
        # offsets_n_stuff. SCREEN_MOD_BITS,
        # value,
        # 'uint')

    @property
    def screen_mode(self):
        raw_bits = RiskyRevengeSav._read_data(self,
        offsets_n_stuff. SCREEN_MODE,
        1,
        offsets_n_stuff. SCREEN_MOD_BITS,
        'uint')       
        return offsets_n_stuff.SCREEN_MODE_INGAME[raw_bits]
    @screen_mode.setter
    def screen_mode(self,value):
        screen_mode_bits = offsets_n_stuff.SCREEN_MOD_BITS
    
        all_indexs = [n for n in range(max_int(screen_mode_bits[1])+1)] #include the last number

        #maybe use chatgpt to match closest thing?
        raw_bits = value if value in all_indexs else offsets_n_stuff.SCREEN_MODE_INGAME.index(value)

        
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. SCREEN_MODE,
        1,
        screen_mode_bits,
        raw_bits,
        'uint')
        
    @property
    def music_volume(self):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. MUSIC_VOLUME,
        1,
        offsets_n_stuff. MUSIC_VOLUME_BITS,
        'uint')

    @music_volume.setter
    def music_volume(self,value):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. MUSIC_VOLUME,
        1,
        offsets_n_stuff. MUSIC_VOLUME_BITS,
        value,
        'uint')

    @property
    def sound_volume(self):
        return RiskyRevengeSav._read_data(self,
        offsets_n_stuff. SOUND_VOLUME,
        1,
        offsets_n_stuff. SOUND_VOLUME_BITS,
        'uint')

    @sound_volume.setter
    def sound_volume(self,value):
        RiskyRevengeSav._write_data(self,
        offsets_n_stuff. SOUND_VOLUME,
        1,
        offsets_n_stuff. SOUND_VOLUME_BITS,
        value,
        'uint')





    #global TESTTTTT
    #TESTTTTT = 24,1




    # global bytes_TESTTTTT
    # bytes_TESTTTTT = MAGIC_ITEMS
    # global type_TESTTTTT
    # type_TESTTTTT = 'bool'



    # def get_test(self,savenumber: int):
    #     return RiskyRevengeSav._read_data(self,
    #     bytes_TESTTTTT,
    #     savenumber,
    #     TESTTTTT,
    #     type_TESTTTTT)

    # def set_test(self,value,savenumber: int):
    #     RiskyRevengeSav._write_data(self,
    #     bytes_TESTTTTT,
    #     savenumber,
    #     TESTTTTT,
    #     value,
    #     type_TESTTTTT)
