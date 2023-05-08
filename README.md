# Interface_tracker

Interface_tracker is a GUI for the analysis of vesicles, partly sucked up in a micropipette, undergoing a change in surface-to-volume ratio, causing the membrane of the vesicle to go deeper or less deep into the micropipette. The file [interface_tracker.py][interface_tracker.py] and [interface_tracker.ui][interface_tracker.ui] need to be in the same folder when running the .py file. Upon running the .py file, an interface opens where a time series of a vesicle that is partly sucked up in a micropipette. A rectangular ROI needs to be drawn around the interface. The 'Preview' buttons allows inspection of the ROI as a function of time. Pressing 'Analyse' tracks the interface throughout time. The 'Save' button saves a .txt file with the position in pixels per frame. A test file with the used parameters and expected analysis reults can be found in [this folder][test folder].

#

Shield: [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
[interface_tracker.py]: https://github.com/bart-vos/Interface_tracker/tree/main/Interface_tracker.py
[interface_tracker.ui]: https://github.com/bart-vos/Interface_tracker/tree/main/Interface_tracker.ui
[test folder]: https://github.com/bart-vos/Interface_tracker/tree/main/Test%20file/
