# Shantae_Risky_RevengePS4_save_editor
A python class for editing decrypted save files for the PS4 version of Shantae: Risky's Revenge - Director's Cut

# Decrypting and Encrypting Save (savedata.sav) #
## Using Apollo Save Tool ##
https://youtu.be/91V9F9QXsec

# Serialising and Deserialising Save (savedata.sav) #
```
git clone https://github.com/Zhaxxy/Shantae_Risky_RevengePS4_save_editor.git
pip install bitstring
```
If you don't want to use the class for editing the save directly (or would like to export to JSON to use elsewhere), you can do the following
```python
from Shantae_Risky_RevengePS4_save_editor import RiskyRevengeSav as sav

with open('savedata.sav','rb') as f:
  save = sav(f.read())

# Serialise the save into a dictionary 
save_dict = save.parse_to_dictionary()
"""
Do not edit any values that has a key that starts with '_comment'! They are comments just to tell you the limitaions of said value, usually max number
"""

# Do stuff with the dictionary (do not add or remove anything, just edit values)
save_dict['settings']['screen_mode'][0] = 'Wide (16:9)'

import json

with open('savedata.json','w') as f:
  json.dump(save_dict, f)

do_things_with_json_file(json_file_path='savedata.json')
```
## JSON or dictionary back to savedata.sav ##
```python
with open('savedata.json','r') as f:
  new_save_dict = json.load(f)
```

# Class Usage #
## Initialise savedata.sav file for editing ##
```
git clone https://github.com/Zhaxxy/Shantae_Risky_RevengePS4_save_editor.git
pip install bitstring
```

```python
from Shantae_Risky_RevengePS4_save_editor import RiskyRevengeSav as sav

with open('savedata.sav','rb') as f:
  save = sav(f.read())

# Print out a mockup of the File Select! menu
print(save)
```
## Editing and Reading Stuff from Save ##
In the get and set functions, the last argument will always be savenumber, this is how you access individual save files<br />
<br />
1 is File A, 2 is File B and 3 is File c

### Getting Values ###
if a value is specific to a save file, the function to get the value would have get_ prefixed to it
```python
# Print out the gems amount for File A
print(save.get_gems(1))

# Print out if you have the puppy (Wobble bell) in File C
print('I have a puppy in my inventory in File C is', save.get_has_puppy(3))

# Print out the amount of frames spent on File C
frames_spent = save.get_save_file_time(3)
print(frames_spent)
seconds = frames_spent // 60
```
### Editing Values ###
if a value is specific to a save file, the function to set the value would have set_ prefixed to it<br />
You'll put whatever value as the first argument, then the savenumber as the second argument<br />
<br />
If you try to enter a bad value, it will raise an error, look at varibles around line 60 and downwards to figure out what bad values are (like setting current_health to 999 wil raise error since its larger then 255) currentlly theres only uints and bools values. If you think would be better to change the values to the closest valid value automatically instead, let me know and I'll do that instead
<br />
<br />
Things you can have mutiple of usually require 2 things to be set, usually there will be function with has_ prefixed to it and a function with _count subfixed to it, i might make separate functions to do this automatically
```python
# Put the Magic Seal in your inventory for File B (doesn't show up ingame if the count is 0)
save.set_has_magic_seal(True,2)

# Makes the count of Magic Seals 1 for File B
save.set_magic_potions_count(1,2)

# Give you Sky's egg for File B
save.set_has_skys_egg(True,2)

# Make you have 7 hearts for File B
save.set_hearts(7,2)

# Will raise ValueError
save.set_current_magic(999,2)
```
### "Deleting" and "Making" Save Files ###
The game has 2 checks to see if save is in use or not<br />
The save time is bigger then 0 (at least 1 so 1 frame) and a boolean if the save is in use or not
<br />
<br />
So in order to "delete" a save, you can either set_save_file_time to 0 or set_is_used1 to False or both<br />
And to "make" a save you set_save_file_time to something bigger then 0 and set_is_used1 to True<br />(this does not reset the save, so if you used the previous method to delete, the values will be there)<br />
ingame the save does reset when you press NEW
```python
# Print out the gems amount for File A
print(save.get_gems(1)) # 786

# "Delete" File A
save.set_is_used1(False,1)

# Print gems amount
print(save.get_gems(1)) # 786 (notice it stayed the same)

# Print out current magic for File B (shown as a bar ingame but it stored as a 1 byte uint)
print(save.get_current_magic(2)) # 100 since 100 is full and deafult value
# Set it to 50
save.set_current_magic(50,2)

# "Make" "new" save in File B (It's already NEW)
save.set_is_used1(True,2)
save.set_save_file_time(1,2)

# Print out current magic (shown as a bar ingame but it stored as a 1 byte uint)
print(save.get_current_magic(2)) # 50 since the save using theese methods aren't effected 
```

### Cool Stuff ###
For the PS4 version at least, you cannot access the always running, its always set to true, however with this editor you can
```python
# Turn off always running for File C (have to run manually by holding circle)
save.set_always_running(False,3)
```
<br />
Most the time the ingame limits arent actually the limits (can lead to werid effects), and also doing things may not give you the desired effects<br />
Giving yourself the puppy for example won't let you give it back to the chef<br />
Setting your current health to 0 makes you god mode (can only die to falls), setting your hearts to 0 as well will make it stay as god mode even if pick up health<br /><br />
Try things out and see whats happens!

## Write the Save Back to The File ##
```python
with open('savedata.sav','wb') as f:
  f.write(save.export_save())
```
