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
In the get and set functions, the last agrument will always be savenumber, this is how you access indidvdual save files<br />
1 is File A, 2 is File B and 3 is File c
```python
# Print out the gems amount for File A
print(save.get_gems(1))

```

# Write the save back to the file
```python
with open('savedata.sav','wb') as f:
  f.write(save.export_save())
```
