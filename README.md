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
