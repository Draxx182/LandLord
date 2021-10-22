Currently testing LandLord.py. There are bugs like making the property.bin a little bigger in terms of size, I will fix that.
For now, I want to focus on whether or not this thing actually works or not, feel free to DM @Draxx#9906 if it breaks anything.

# Usage + Json Explanation
Drag and Drop property.bin into LandLord.exe and it'll create a folder with the property header, and a folder filled with table jsons.
1. String Table Json: What name the game pulls from property.bin. Basically a base for the other tables.
2. GMT Table Json: Animations registered in property.bin
3. MEP Table Json: Particle effects registered in property.bin
4. Move Block Json: The meat of the moves, deciding how the game handles different moves.
5. Unk Data/Unk-Block Data: Don't ask me.

# Warning
Once Exe has been created, it may come up as malware by windows defender. I assure you it's not, but if you don't trust it then feel free to not use it.

# Credit
A massive thank you to HeartlessSeph who found out the pointers for property.bin. Thanks to Retraso for providing some base code. Sutando for providing me with the PyBinaryReader.
A thank you to Spoon722, musashi man, kuandik and Emerge for testing out the property.bin.
Thank you to you for checking this tool out. I hope you enjoy.

Without you, this project would've been worthless.
