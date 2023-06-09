class SAVE_DATA_INFO_READ_ONLY:
    GLOBAL_ENDIAN = 'little'
    SAVE_FILES_SLOTS = (1,2,3)
    SAVE_FILES_SLOTS_INGAME = ('Not a valid save slot (raise an error if accessed maybe)','File A','File B','File C')
    #offsets and lengths, each block needs its block offset and length, and each data in the block needs its bit offset and length

    #special offsets, are not spefic to each save file
    SCREEN_MODE = 0x494,1
    SCREEN_MOD_BITS = 6,2
    SCREEN_MODE_INGAME = ('Square (4:3) with Borders','Square (4:3)','Wide (16:9)','Original')

    MUSIC_VOLUME = 0x490,1
    MUSIC_VOLUME_BITS = 0, MUSIC_VOLUME[1]*8

    SOUND_VOLUME = 0x491,1
    SOUND_VOLUME_BITS = 0, SOUND_VOLUME[1]*8






    GEMS_AND_STUFF = 0x27c,2
    GEMS_BITS = 6,10
    ALWAYS_RUNNING_BIT = 2,1
    IS_USED1_BIT = 1,1
    HEARTS_BITS = 3,3

    MAGIC_HEALTH_VIALS = 0x282,1
    MAGIC_POTIONS_COUNT_BITS = 0,4
    HEALTH_VIALS_COUNT_BITS = 4,4


    ITEMS_WITH_AMOUNTS1 = 0x286,2
    GOLDEN_SQUID_BABY_COUNT_BITS = 9,2
    MAGIC_SEALS_COUNT_BITS = 7,2
    MAGIC_JAMS_COUNT_BITS = 11,5



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
    HAS_MAGIC_JAM_BIT = 5,1

    SAVE_FILE_TIME = 0x308,4
    SAVE_FILE_TIME_BITS = 0, SAVE_FILE_TIME[1]*8

    MASSIVE_BLOCK_CHECKPOINT = 0x328,16
    AREA_RELATIVE_Y_POS_BITS = 0, 3 * 8
    AREA_RELATIVE_X_POS_BITS = 32, 3 * 8
    LAST_8_BYTES_BITS = 64, 8*8

    CURRENT_HEALTH = 0x358,1
    CURRENT_HEALTH_BITS = 0, CURRENT_HEALTH[1]*8

    CURRENT_MAGIC = 0x35B,1
    CURRENT_MAGIC_BITS = 0, CURRENT_MAGIC[1]*8
