# Shantae_Risky_RevengePS4_save_editor
A python class for editing decrypted save files for the PS4 version of Shantae: Risky's Revenge - Director's Cut


# Initialise savedata.sav file for editing
```python
from Shantae_Risky_RevengePS4_save_editor import RiskyRevengeSav as sav

with open('savedata.sav','rb') as f:
  save = sav(f.read())

# Print out a mockup of the File Select! menu
print(save)
```
# Editing and reading stuff from save
In the get and set functions, the last argument will always be savenumber, this is how you access individual save files<br />
<br />
1 is File A, 2 is File B and 3 is File c

## Getting Values ##
if a value is specific to a save file, the function to get the value would have get_ prefixed to it
```python
# Print out the gems amount for File A
print(save.get_gems(1))

# Print out if you have the puppy (Wobble bell) in File C
print('I have a puppy in my inventory in File C is', save.get_has_puppy(3))
```
## Editing Values ##
if a value is specific to a save file, the function to get the value would have set_ prefixed to it<br />
You'll put whatever value as the first argument, then the savenumber as the second argument<br />
<br />
(Some things may require 2 things to be set, usually there will be function with has_ prefixed to it and a function with _count subfixed to it)
```python
# Put the Magic Seal in your inventory for File B (doesn't show up ingame if the count is 0)
save.set_has_magic_seal(True,2)

# Makes the count of Magic Seals 1 for File B
save.set_magic_potions_count(1,2)
```


# Write the save back to the file
```python
with open('savedata.sav','wb') as f:
  f.write(save.export_save())
```
