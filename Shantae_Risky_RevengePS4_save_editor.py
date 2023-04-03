from io import BytesIO
from bitstring import BitArray as ba





"""

all of them are unsigned ints, unless specified  otherwise

data is stored in blocks or arrays or whatever, so i need to figure out what theese sections are, blocks are stored in little endian since its a ps4 save
each save entry (file select) stores theese blocks side by side, so when i say offset i mean the offset of the block for save 1, offsets relative to entire save file


look at the constants for more info, dont bother looking at the setter and getter functions, although some may
some custom code, ill be sure to point that out in the constants though
"""



def format_ingame_time(time_as_int):
    seconds = time_as_int // 60
    hours, extra_seconds = divmod(seconds,3600)
    minutes = extra_seconds // 60
    return f'{hours:02d}:{minutes:02d}'

def time2ingame_time(formated_ingame_time,must_be_in_use=True):
    hours, minutes = formated_ingame_time.split(':')
    total_minutes = (int(hours) * 60) + int(minutes)
    return min((total_minutes * 60)*60,1) if must_be_in_use else (total_minutes * 60)*60

def check_save(save_bytes):
    return save_bytes.startswith(b'\x76\xD4\xFE\x54') and len(save_bytes) == 0x800


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


class RiskyRevengeSav:
    GLOBAL_ENDIAN = 'little'
    SAVE_FILES_SLOTS = {1,2,3}
    #offsets and lengths, each block needs its block offset and length, and each data in the block needs its bit offset and length
    
    GEMS_AND_STUFF = 0x27c,2
    GEMS_BITS = 6,10
    ALWAYS_RUNNING_BIT = 2,1
    IS_USED1_BIT = 1,1
    HEARTS_BITS = 3,3
    
    MAGIC_HEALTH_VIALS = 0x282,1
    MAGIC_POTIONS_COUNT_BITS = 0,4
    HEALTH_VIALS_COUNT_BITS = 3,4


    ITEMS_WITH_AMOUNTS1 = 0x286,2
    GOLDEN_SQUID_BABY_COUNT_BITS = 9,2
    MAGIC_SEALS_COUNT_BITS = 7,2
    MAJIC_JAMS_COUNT_BITS = 11,5

    #global TESTTTTT
    #TESTTTTT = 24,1




    MAGIC_ITEMS = 0x290,8
    HAS_MAP_BIT = 60,1
    HAS_FIREBALL_BIT = 59,1
    HAS_SPITFIRE_BIT = 58,1
    HAS_FLAMETHROWER_BIT = 57,1
    HAS_PIKE_BALL_BIT = 56,1
    HAS_SUPER_PIKE_BALL_BIT = 55,1
    HAS_MEGA_PIKE_BALL_BIT = 54,1
    HAS_STORM_PUFF_BIT = 53,1
    HAS_CRUSH_PUFF_BIT = 52,1
    HAS_MEGA_PUFF_BIT = 51,1
    HAS_PROHIBITION_SIGN_BIT = 50,1 #clearly a placeholder, again just dont access this, should always be false
    HAS_HEARTS_HOLDER_BIT = 49,1  #dont, dont use this, should always be true also it breaks the shop
    HAS_GOLDEN_SQUID_BABY_BIT = 47,1 #Note if its 0, then theres no indication ingame that you have it!
    HAS_MONKEY_DANCE_BIT = 46,1
    HAS_ELPHANT_DANCE_BIT = 45,1
    HAS_MERMAID_DANCE = 44,1
    HAS_ATTRACT_MAGIC_BIT = 43,1
    HAS_MAGIC_FILL_BIT = 42,1
    HAS_SILKY_CREAM_BIT = 41,1
    HAS_SUPER_SILKY_CREAM_BIT = 40,1
    HAS_PUPPY_BIT = 39,1
    HAS_TASTY_MEAL_BIT = 38,1
    HAS_SKYS_EGG_BIT = 37,1
    HAS_SCUTTLE_DEED_BIT = 36,1
    HAS_AMMO_TOWN_PASSPORT_BII = 35,1
    HAS_COFFEE_BEANS_BIT = 34,1
    HAS_BROKEN_COFFEE_MACHINE_BIT = 33,1
    HAS_ZOMBIE_LATTE_BIT = 32,1
    HAS_FOREST_KEY_BIT = 31,1
    HAS_PLASTIC_EXPLOSIVES_BIT = 30,1
    HAS_MONKEY_BULLET_BIT = 29,1
    HAS_ELPHANT_STOMP_BIT = 28,1
    HAS_MERMAID_BUBBLE_BIT = 27,1
    HAS_TOP_HALF_SKULL_BIT = 26,1
    HAS_BOTTOM_HALF_SKULL_BIT = 25,1
    HAS_MAGIC_SEAL_BIT = 24,1 #Note if its 0, then theres no indication ingame that you have it!
    HAS_HEALTH_VIAL1_BIT = 23,1 
    HAS_MAGIC_POTION1_BIT = 22,1


    RANDOM_ITEMS = 0x2a8,4
    HAS_MAGIC_POTION2_BIT = 3,1 #V Note these do not HAVE to be checked for it to work, and nethier does the ones in MAGIC_ITEMS, the game checks for ethier one but ingame it sets both of them to 1 so i do it too, probably has their reasons
    HAS_HEALTH_VIAL2_BIT = 4,1  #^
    HAS_MAJIC_JAM_BIT = 5,1

    SAVE_FILE_TIME = 0x308,4
    SAVE_FILE_TIME_BITS = 0,32
    
    CURRENT_HEALTH = 0x358,1
    CURRENT_HEALTH_BITS = 0,8
    
    CURRENT_MAGIC = 0x35B,1
    CURRENT_MAGIC_BITS = 0,8

    def _read_data(self,
                    offset_n_length,
                    savenumber,
                    bit_offset_n_length,
                    data_type_is='uint',
                    *,
                    endianness='little'):
        
        if savenumber not in RiskyRevengeSav.SAVE_FILES_SLOTS:
            raise ValueError(f'{savenumber} not a valid save file number')
        
        new_offset = (offset_n_length[0] - offset_n_length[1]) + (offset_n_length[1]*savenumber)
        self._savedata.seek(new_offset)
        new_data = self._savedata.read(offset_n_length[1])
        self._savedata.seek(0)
        
        new_bitarray = ba(bytes=change_endianes(new_data,endianness))

        ############# methods here
        if data_type_is.lower() == 'uint':
            return new_bitarray[bit_offset_n_length[0]:bit_offset_n_length[0] + bit_offset_n_length[1]].uint
        elif data_type_is.lower() == 'int':
            return new_bitarray[bit_offset_n_length[0]:bit_offset_n_length[0] + bit_offset_n_length[1]].int
        elif data_type_is.lower() == 'bool':
            return bool(new_bitarray[bit_offset_n_length[0]:bit_offset_n_length[0] + bit_offset_n_length[1]].int)



        elif data_type_is.lower() == 'time': #DONT USE THIS METHOD, JUST MANUPLATE THE INT MANUALLY!
            time_count = new_bitarray[bit_offset_n_length[0]:bit_offset_n_length[0] + bit_offset_n_length[1]].uint
            return datetime.timedelta(seconds=time_count//60) #but i wanna manuplate the indivdual frames >:(
        else:
            raise NotImplementedError(f'{data_type_is} date type is not supported')
        ############# methods here        
        
    def _write_data(self,
                    offset_n_length,
                    savenumber,
                    bit_offset_n_length,
                    value,
                    data_type_is='uint',
                    *,
                    endianness=GLOBAL_ENDIAN):
        
        if savenumber not in RiskyRevengeSav.SAVE_FILES_SLOTS:
            raise ValueError(f'{savenumber} not a valid save file number')
        
        if max_int(bit_offset_n_length[1]) < value and data_type_is == 'uint':
            raise ValueError(f'Value is bigger then {max_int(bit_offset_n_length[1])}, wont work')
        if data_type_is == 'uint' and value < 0:
            raise ValueError('uint values cannot be negative')
        
        
        new_offset = (offset_n_length[0] - offset_n_length[1]) + (offset_n_length[1]*savenumber)
        self._savedata.seek(new_offset)
        new_data = self._savedata.read(offset_n_length[1])
        self._savedata.seek(0)
        
        new_bitarray = ba(bytes=change_endianes(new_data,endianness))
        
        
        

        ############# methods here
        if data_type_is.lower() == 'uint':
            new_value = ba(uint=value,length=bit_offset_n_length[1])
        elif data_type_is.lower() == 'int':
            new_value = ba(int=value,length=bit_offset_n_length[1])
        elif data_type_is.lower() == 'bool':
            new_value = 1 if value else 0
        elif data_type_is.lower() == 'time':
            new_value = value.total_seconds()
        else:
            raise NotImplementedError(f'{data_type_is} date type is not supported')
        new_bitarray[bit_offset_n_length[0]:bit_offset_n_length[0] + bit_offset_n_length[1]] = new_value
        ############## methods here
        new_bytes_to_write = change_endianes(new_bitarray.bytes,RiskyRevengeSav.GLOBAL_ENDIAN)
        self._savedata.seek(new_offset)
        self._savedata.write(new_bytes_to_write)
        self._savedata.seek(0)
    

    
    def __init__(self,savedata_sav_bytes):
        self._savedata = BytesIO(savedata_sav_bytes)
        
    def export_save(self):
        return self._savedata.getvalue()

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
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  GEMS_BITS,
        'uint')

    def set_gems(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  GEMS_BITS,
        value,
        'uint')

    def get_always_running(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  ALWAYS_RUNNING_BIT,
        'uint')

    def set_always_running(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  ALWAYS_RUNNING_BIT,
        value,
        'uint')

    def get_is_used1(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  IS_USED1_BIT,
        'bool')

    def set_is_used1(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  IS_USED1_BIT,
        value,
        'bool')

    def get_hearts(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  HEARTS_BITS,
        'uint')

    def set_hearts(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  GEMS_AND_STUFF,
        savenumber,
        RiskyRevengeSav.  HEARTS_BITS,
        value,
        'uint')

    def get_magic_potions_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_HEALTH_VIALS,
        savenumber,
        RiskyRevengeSav.  MAGIC_POTIONS_COUNT_BITS,
        'uint')

    def set_magic_potions_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_HEALTH_VIALS,
        savenumber,
        RiskyRevengeSav.  MAGIC_POTIONS_COUNT_BITS,
        value,
        'uint')

    def get_health_vials_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_HEALTH_VIALS,
        savenumber,
        RiskyRevengeSav.  HEALTH_VIALS_COUNT_BITS,
        'uint')

    def set_health_vials_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_HEALTH_VIALS,
        savenumber,
        RiskyRevengeSav.  HEALTH_VIALS_COUNT_BITS,
        value,
        'uint')

    def get_golden_squid_baby_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  ITEMS_WITH_AMOUNTS1,
        savenumber,
        RiskyRevengeSav.  GOLDEN_SQUID_BABY_COUNT_BITS,
        'uint')

    def set_golden_squid_baby_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  ITEMS_WITH_AMOUNTS1,
        savenumber,
        RiskyRevengeSav.  GOLDEN_SQUID_BABY_COUNT_BITS,
        value,
        'uint')

    def get_magic_seals_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  ITEMS_WITH_AMOUNTS1,
        savenumber,
        RiskyRevengeSav.  MAGIC_SEALS_COUNT_BITS,
        'uint')

    def set_magic_seals_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  ITEMS_WITH_AMOUNTS1,
        savenumber,
        RiskyRevengeSav.  MAGIC_SEALS_COUNT_BITS,
        value,
        'uint')

    def get_majic_jams_count(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  ITEMS_WITH_AMOUNTS1,
        savenumber,
        RiskyRevengeSav.  MAJIC_JAMS_COUNT_BITS,
        'uint')

    def set_majic_jams_count(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  ITEMS_WITH_AMOUNTS1,
        savenumber,
        RiskyRevengeSav.  MAJIC_JAMS_COUNT_BITS,
        value,
        'uint')

    def get_has_map(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAP_BIT,
        'bool')

    def set_has_map(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAP_BIT,
        value,
        'bool')

    def get_has_fireball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_FIREBALL_BIT,
        'bool')

    def set_has_fireball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_FIREBALL_BIT,
        value,
        'bool')

    def get_has_spitfire(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SPITFIRE_BIT,
        'bool')

    def set_has_spitfire(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SPITFIRE_BIT,
        value,
        'bool')

    def get_has_flamethrower(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_FLAMETHROWER_BIT,
        'bool')

    def set_has_flamethrower(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_FLAMETHROWER_BIT,
        value,
        'bool')

    def get_has_pike_ball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PIKE_BALL_BIT,
        'bool')

    def set_has_pike_ball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PIKE_BALL_BIT,
        value,
        'bool')

    def get_has_super_pike_ball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SUPER_PIKE_BALL_BIT,
        'bool')

    def set_has_super_pike_ball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SUPER_PIKE_BALL_BIT,
        value,
        'bool')

    def get_has_mega_pike_ball(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MEGA_PIKE_BALL_BIT,
        'bool')

    def set_has_mega_pike_ball(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MEGA_PIKE_BALL_BIT,
        value,
        'bool')

    def get_has_storm_puff(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_STORM_PUFF_BIT,
        'bool')

    def set_has_storm_puff(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_STORM_PUFF_BIT,
        value,
        'bool')

    def get_has_crush_puff(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_CRUSH_PUFF_BIT,
        'bool')

    def set_has_crush_puff(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_CRUSH_PUFF_BIT,
        value,
        'bool')

    def get_has_mega_puff(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MEGA_PUFF_BIT,
        'bool')

    def set_has_mega_puff(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MEGA_PUFF_BIT,
        value,
        'bool')

    def get_has_prohibition_sign(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PROHIBITION_SIGN_BIT,
        'bool')

    def set_has_prohibition_sign(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PROHIBITION_SIGN_BIT,
        value,
        'bool')

    def get_has_hearts_holder(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_HEARTS_HOLDER_BIT,
        'bool')

    def set_has_hearts_holder(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_HEARTS_HOLDER_BIT,
        value,
        'bool')

    def get_has_golden_squid_baby(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_GOLDEN_SQUID_BABY_BIT,
        'bool')

    def set_has_golden_squid_baby(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_GOLDEN_SQUID_BABY_BIT,
        value,
        'bool')

    def get_has_monkey_dance(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MONKEY_DANCE_BIT,
        'bool')

    def set_has_monkey_dance(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MONKEY_DANCE_BIT,
        value,
        'bool')

    def get_has_elphant_dance(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ELPHANT_DANCE_BIT,
        'bool')

    def set_has_elphant_dance(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ELPHANT_DANCE_BIT,
        value,
        'bool')

    def get_has_mermaid_dance(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MERMAID_DANCE,
        'bool')

    def set_has_mermaid_dance(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MERMAID_DANCE,
        value,
        'bool')

    def get_has_attract_magic(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ATTRACT_MAGIC_BIT,
        'bool')

    def set_has_attract_magic(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ATTRACT_MAGIC_BIT,
        value,
        'bool')

    def get_has_magic_fill(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_FILL_BIT,
        'bool')

    def set_has_magic_fill(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_FILL_BIT,
        value,
        'bool')

    def get_has_silky_cream(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SILKY_CREAM_BIT,
        'bool')

    def set_has_silky_cream(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SILKY_CREAM_BIT,
        value,
        'bool')

    def get_has_super_silky_cream(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SUPER_SILKY_CREAM_BIT,
        'bool')

    def set_has_super_silky_cream(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SUPER_SILKY_CREAM_BIT,
        value,
        'bool')

    def get_has_puppy(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PUPPY_BIT,
        'bool')

    def set_has_puppy(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PUPPY_BIT,
        value,
        'bool')

    def get_has_tasty_meal(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_TASTY_MEAL_BIT,
        'bool')

    def set_has_tasty_meal(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_TASTY_MEAL_BIT,
        value,
        'bool')

    def get_has_skys_egg(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SKYS_EGG_BIT,
        'bool')

    def set_has_skys_egg(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SKYS_EGG_BIT,
        value,
        'bool')

    def get_has_scuttle_deed(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SCUTTLE_DEED_BIT,
        'bool')

    def set_has_scuttle_deed(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_SCUTTLE_DEED_BIT,
        value,
        'bool')

    def get_has_ammo_town_passport(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_AMMO_TOWN_PASSPORT_BII,
        'bool')

    def set_has_ammo_town_passport(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_AMMO_TOWN_PASSPORT_BII,
        value,
        'bool')

    def get_has_coffee_beans(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_COFFEE_BEANS_BIT,
        'bool')

    def set_has_coffee_beans(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_COFFEE_BEANS_BIT,
        value,
        'bool')

    def get_has_broken_coffee_machine(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_BROKEN_COFFEE_MACHINE_BIT,
        'bool')

    def set_has_broken_coffee_machine(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_BROKEN_COFFEE_MACHINE_BIT,
        value,
        'bool')

    def get_has_zombie_latte(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ZOMBIE_LATTE_BIT,
        'bool')

    def set_has_zombie_latte(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ZOMBIE_LATTE_BIT,
        value,
        'bool')

    def get_has_plastic_explosives(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PLASTIC_EXPLOSIVES,
        'bool')

    def set_has_plastic_explosives(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PLASTIC_EXPLOSIVES,
        value,
        'bool')

    def get_has_forest_key(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_FOREST_KEY_BIT,
        'bool')

    def set_has_forest_key(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_FOREST_KEY_BIT,
        value,
        'bool')

    def get_has_plastic_explosives(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PLASTIC_EXPLOSIVES_BIT,
        'bool')

    def set_has_plastic_explosives(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_PLASTIC_EXPLOSIVES_BIT,
        value,
        'bool')

    def get_has_monkey_bullet(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MONKEY_BULLET_BIT,
        'bool')

    def set_has_monkey_bullet(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MONKEY_BULLET_BIT,
        value,
        'bool')

    def get_has_elphant_stomp(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ELPHANT_STOMP_BIT,
        'bool')

    def set_has_elphant_stomp(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_ELPHANT_STOMP_BIT,
        value,
        'bool')

    def get_has_mermaid_bubble(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MERMAID_BUBBLE_BIT,
        'bool')

    def set_has_mermaid_bubble(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MERMAID_BUBBLE_BIT,
        value,
        'bool')

    def get_has_top_half_skull(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_TOP_HALF_SKULL_BIT,
        'bool')

    def set_has_top_half_skull(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_TOP_HALF_SKULL_BIT,
        value,
        'bool')

    def get_has_bottom_half_skull(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_BOTTOM_HALF_SKULL_BIT,
        'bool')

    def set_has_bottom_half_skull(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_BOTTOM_HALF_SKULL_BIT,
        value,
        'bool')

    def get_has_bottom_half_skull(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_BOTTOM_HALF_SKULL_BIT,
        'bool')

    def set_has_bottom_half_skull(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_BOTTOM_HALF_SKULL_BIT,
        value,
        'bool')

    def get_has_magic_seal(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_SEAL_BIT,
        'bool')

    def set_has_magic_seal(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_SEAL_BIT,
        value,
        'bool')

    def get_has_majic_jam(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  RANDOM_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAJIC_JAM_BIT,
        'bool')

    def set_has_majic_jam(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  RANDOM_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAJIC_JAM_BIT,
        value,
        'bool')


    def get_has_magic_potion(self,savenumber: int):
        has_magic_potion1 =  RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_POTION1_BIT,
        'bool')

        has_magic_potion2 =  RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  RANDOM_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_POTION2_BIT,
        'bool')

        if has_magic_potion1 != has_magic_potion2:
            raise ValueError(f'WTF {has_magic_potion1 = } {has_magic_potion2 = }')
        return has_magic_potion1

    def set_has_magic_potion(self,value,savenumber: int):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_POTION1_BIT,
        value,
        'bool')

        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  RANDOM_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_MAGIC_POTION2_BIT,
        value,
        'bool')

    def get_has_health_vial(self,savenumber: int):
        has_health_vial1 =  RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_HEALTH_VIAL1_BIT,
        'bool')

        has_health_vial2 =  RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  RANDOM_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_HEALTH_VIAL2_BIT,
        'bool')

        if has_health_vial1 != has_health_vial2:
            raise ValueError(f'WTF {has_health_vial1 = } {has_health_vial2 = }')
        return has_health_vial1

    def set_has_health_vial(self,value,savenumber: int):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  MAGIC_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_HEALTH_VIAL1_BIT,
        value,
        'bool')

        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  RANDOM_ITEMS,
        savenumber,
        RiskyRevengeSav.  HAS_HEALTH_VIAL2_BIT,
        value,
        'bool')

    def get_save_file_time(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  SAVE_FILE_TIME,
        savenumber,
        RiskyRevengeSav.  SAVE_FILE_TIME_BITS,
        'uint')

    def set_save_file_time(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  SAVE_FILE_TIME,
        savenumber,
        RiskyRevengeSav.  SAVE_FILE_TIME_BITS,
        value,
        'uint')

    def get_current_health(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  CURRENT_HEALTH,
        savenumber,
        RiskyRevengeSav.  CURRENT_HEALTH_BITS,
        'uint')

    def set_current_health(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  CURRENT_HEALTH,
        savenumber,
        RiskyRevengeSav.  CURRENT_HEALTH_BITS,
        value,
        'uint')

    def get_current_magic(self,savenumber):
        return RiskyRevengeSav._read_data(self,
        RiskyRevengeSav.  CURRENT_MAGIC,
        savenumber,
        RiskyRevengeSav.  CURRENT_MAGIC_BITS,
        'uint')

    def set_current_magic(self,value,savenumber):
        RiskyRevengeSav._write_data(self,
        RiskyRevengeSav.  CURRENT_MAGIC,
        savenumber,
        RiskyRevengeSav.  CURRENT_MAGIC_BITS,
        value,
        'uint')

    












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


        

def main():
    from os import path
    if not path.isfile('savedata.sav'):
        input('savedata.sav not found, press enter to exit')
        from sys import exit as exitsys
        exitsys()
        
    
    with open('savedata.sav','rb') as f:
        og = f.read()
        save = RiskyRevengeSav(og)



    print(save)
    
    

    with open('savedata.sav','wb') as f:
        f.write(save.export_save())



if __name__ == '__main__':
    main()
