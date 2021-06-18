import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pkmn_parser import *


pkmn_natures = ["", "Hardy (neutral)", "Lonely (+atk, -def)", "Brave (+atk, -speed)", "Adamant (+atk, -sp.atk)", "Naughty (+atk, -sp.def)", "Bold (+def, -atk)", "Docile (neutral)", "Relaxed (+def, -speed)", "Impish (+def, -sp.atk)", "Lax (+def, -sp.def)", "Timid (+speed, -atk)", "Hasty (+speed, -def)", "Serious (neutral)", "Jolly (+speed, -sp.atk)", "Naive (+speed, -sp.def)", "Modest (+sp.atk, -atk)", "Mild (+sp.atk, -def)", "Quiet (+sp.atk, -speed)", "Bashful (neutral)", "Rash (+sp.atk, -sp.def)", "Calm (+sp.def, -atk)", "Gentle (+sp.def, -def)", "Sassy (+sp.def, -speed)", "Careful (+sp.def, -sp.atk)", "Quirky (neutral)"]


#subwindow after choosing the generation
class SubWindow(QWidget):

    def __init__(self, title, gen, func):
        super().__init__()
        self.setWindowTitle(title)
        self.gen = gen
        self.func = func
        
        self.window_setup()
    
############### Subwindow Setup ###################################################################################

    def window_setup(self):
        '''
        sets up (builds) the interactable window (and fields) for the IV or EV calculators and displays it

        Input:
        self -- the SubWindow object itself since a lot of the values/variables are members intrinsic to this specific instance
        '''

        #instantiate the layers to use
        self.outer_layout = QVBoxLayout()
        self.top_row = QHBoxLayout()
        self.stats_layout = QGridLayout()
        self.btn_layout = QHBoxLayout()

        #printed output (error/success checking)
        self.printout = QLabel('\n')
        self.printout.setAlignment(Qt.AlignCenter)
    
        #build the Pokemon dataframe by reading from a CSV based on the generation
        self.pkmn_df = build_pkmn_df(self.gen)

        #the field where the user selects the Pokemon to process
        self.pkmn_name_layout = QVBoxLayout()
        self.pkmn_name_label = QLabel('Select Pokemon:')
        self.pkmn_name_box = QComboBox()
        self.pkmn_name_box.addItems(get_names(self.pkmn_df)[1:])
        self.pkmn_name_box.setStyleSheet("combobox-popup: 0")	#limit the number of items displayed when opening combobox to 10
        self.pkmn_name_layout.addWidget(self.pkmn_name_label)
        self.pkmn_name_layout.addWidget(self.pkmn_name_box)
        self.top_row.addLayout(self.pkmn_name_layout)

        #the field where the user enters the Pokemon level
        self.pkmn_lvl_layout = QVBoxLayout()
        self.pkmn_lvl_label = QLabel('Enter Level:')
        self.pkmn_lvl_entry = QLineEdit()
        self.pkmn_lvl_entry.setValidator(QIntValidator())
        self.pkmn_lvl_entry.setMaxLength(3)
        self.pkmn_lvl_layout.addWidget(self.pkmn_lvl_label)
        self.pkmn_lvl_layout.addWidget(self.pkmn_lvl_entry)
        self.top_row.addLayout(self.pkmn_lvl_layout)

        #the field where the user selects the Pokemon's nature (only exists for gen III+)
        if self.gen != "genI" and self.gen != "genII":
            self.pkmn_nature_layout = QVBoxLayout()
            self.pkmn_nature_label = QLabel('Select Nature:')
            self.pkmn_nature_box = QComboBox()
            self.pkmn_nature_box.addItems(pkmn_natures)
            self.pkmn_nature_box.setStyleSheet("combobox-popup: 0")
            
            self.pkmn_nature_layout.addWidget(self.pkmn_nature_label)
            self.pkmn_nature_layout.addWidget(self.pkmn_nature_box)
            self.top_row.addLayout(self.pkmn_nature_layout)
            self.natures_df = build_natures_df()

        #setup the labels for the stats grid based on whether computing EV or IV and if genI or not
        if self.func == "IV Calculator":
            if self.gen == "genI":
                stat_row_labels = ['Stats', 'EV (Stat Exp.)', 'Stat Range', 'IV (DV)']
                stat_col_labels = ['HP', 'Attack', 'Defense', 'Special', 'Speed']
            else:
                stat_row_labels = ['Stats', 'EV', 'Stat Range', 'IV']
                stat_col_labels = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
        elif self.func == "EV Calculator":
            if self.gen == "genI":
                stat_row_labels = ['Stats', 'IV (DV)', 'Stat Range', 'EV (Stat Exp.)']
                stat_col_labels = ['HP', 'Attack', 'Defense', 'Special', 'Speed']
            else:
                stat_row_labels = ['Stats', 'IV', 'Stat Range', 'EV']
                stat_col_labels = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
        

        num_stat_rows = len(stat_row_labels)
        num_stat_cols = len(stat_col_labels)

	#add the permiter/label fields for the stats grid
        for i in range(num_stat_cols):
            self.stats_layout.addWidget(QLabel(stat_col_labels[i]), 0, i+1)
        for i in range(num_stat_rows):
            self.stats_layout.addWidget(QLabel(stat_row_labels[i]), i+1, 0)

        #setup IV or EV Calculator specific fields
        if self.func[:2] == "IV":
            self.IV_setup(num_stat_cols, num_stat_rows, stat_col_labels)
        elif self.func[:2] == "EV":
            self.EV_setup(num_stat_cols, num_stat_rows, stat_col_labels)

        self.quit_btn = QPushButton("Exit")
        self.quit_btn.clicked.connect(self.close)

        self.btn_layout.addWidget(self.compute_btn)
        self.btn_layout.addWidget(self.quit_btn)

        #preparing the wrapper layout so every sub-layout becomes visible
        self.outer_layout.addLayout(self.top_row)
        self.outer_layout.addLayout(self.stats_layout)
        self.outer_layout.addWidget(self.printout)
        self.outer_layout.addLayout(self.btn_layout)

        self.setLayout(self.outer_layout)




############### IV STUFF ##########################################################################################

    def IV_setup(self, num_stat_cols, num_stat_rows, stat_col_labels):
        '''
        building fields specific to the IV computation subWindow and displaying it to the user

        Inputs:
        self -- the subWindow object itself since a lot of the values/variables are members intrinsic to this specific instance
        num_stat_cols --the number of columns in the stats grid
        num_stat_rows -- the number of rows in the stats grid
        stat_col_labels -- the stats grid column labels (i.e. HP, Attack, etc.)
        '''
 
        #placeholders
        self.stats = list()     #vector of stat fields
        self.ev = list()        #vector of ev's
        self.stat_range = list()
        self.IV_labels = list()

        for i in range(num_stat_cols):

            #making the stats fields/boxes
            self.stats.append(QLineEdit())
            self.stats[i].setValidator(QIntValidator())
            self.stats[i].setMaxLength(3)
            self.stats_layout.addWidget(self.stats[i], 1, i+1)

            #making the EV fields/boxes
            self.ev.append(QLineEdit())
            self.ev[i].setValidator(QIntValidator())
            self.ev[i].setMaxLength(3)
            self.stats_layout.addWidget(self.ev[i], 2, i+1)

            #making the stat range fields/boxes
            self.stat_range.append(QLabel("N/A"))
            self.stats_layout.addWidget(self.stat_range[i], num_stat_rows - 1, i+1)

            #making the IV placeholders
            self.IV_labels.append(QLabel("N/A"))
            self.stats_layout.addWidget(self.IV_labels[i], num_stat_rows, i+1)

        #the button the user clicks that will take all of the user entered parameters to compute the Pokemon's IVs
        self.compute_btn = QPushButton("Compute IVs")
        self.compute_btn.clicked.connect(lambda: self.checkIV(stat_col_labels))




    def checkIV(self, stat_labels):
        '''
        the acutal compute button intself, that takes in all the user-filled data and tries to compute all the possible IV's for each stat and their possible stat ranges and displays them on the GUI/window

        Inputs:
        self -- the SubWindow object itself since a lot of the values/variables are members intrinsic to this specific instance
        stat_labels -- the grid column labels (the labels of the stats themselves, i.e. HP, Attack, etc.)
        '''


        def list2string(intlist, delim = ', '):
            '''
            translates a Python list to a character-separated (comma by default) string

            Inputs:
            intlist -- the Python list (assumes ints for now)
            delim -- the separating/delimiting character

            Output:
            a readable Python string of the lists contents
            ''' 
            s = [str(i) for i in intlist]
            return delim.join(s)


        def fillNA(num_stats):
            '''
            fills the label fields (user can't write into) with N/A's

            Input:
            num_stats -- the number of columns (a.k.a number of stats)
            '''
            for i in range(num_stats):
                self.IV_labels[i].setText("N/A")
                self.stat_range[i].setText("N/A")
            


        #get the pokemon's base stats
        cur_pkmn = self.pkmn_name_box.currentText()
        pkmn_base_stats = get_base_stats(self.pkmn_df, cur_pkmn, self.gen, stat_labels)[0]
        num_stats = len(stat_labels)
        
        #get its current level
        if self.pkmn_lvl_entry.text() == '':
            self.printout.setText("\nMissing Level!  Cannot compute possible IV's or stat range.\n")
            fillNA(num_stats)
            return
        else:
            cur_lvl = self.pkmn_lvl_entry.text()

        #initialize dictionaries to hold its current stats and EV's
        cur_stats = dict()
        cur_ev = dict()
        possible_iv = dict()
        possible_stat_range = dict()




        def computeIV(base_stat, stat_exp, cur_stat, stat_label, nature=1):
             '''
            uses the different Pokemon Stat formulas (depends on stat and gen) to figure out the possible IV's given certain parameters

            Inputs:
            base_stat -- the Pokemon's base stat for this stat (fixed, depends on Pokemon species)
            stat_exp -- the Pokemon's stat experience (a.k.a effort value or EV) gained throughout training
            cur_stat -- the Pokemon's current stats (not to be confused with base stats)
            stat_labels -- the label of the current stat beign computed (i.e. HP, Attack, Defense, etc.)
            nature -- the nature modification value (positive = 1.1, negative = 0.9, neutral/default = 1)

            Outputs:
            iv -- possible IV's for this current stat
            stat_range -- range of possible values of this stat given the current Pokemon's species, level, and EV's
            '''

                   
            from math import floor, ceil, sqrt

            iv = list()
            stat_range = list()

            if self.gen == 'genI' or self.gen == 'genII':

                #genI/II IV/DV go from 0 to 15
                for val in range(16):

                    #stat formulas
                    if stat_label == 'HP':
                        comp = int(cur_lvl) + 10 + floor((int(cur_lvl)/100)*(2*int(base_stat) + 2*val + floor(ceil(sqrt(int(stat_exp)))/4)))
                    else:
                        comp = 5 + floor((int(cur_lvl)/100)*(2*int(base_stat) + 2*val + floor(ceil(sqrt(int(stat_exp)))/4)))
                    stat_range.append(comp)

                    #if the computed stat is the same as the current stat, then this is a possible IV
                    if cur_stat != '' and comp == int(cur_stat):
                        iv.append(val)
               
            #genIII+ IV go from 0 to 31
            else:
                for val in range(32):

                    #stat formulas
                    if stat_label == 'HP':
                        comp = int(cur_lvl) + 10 + floor((int(cur_lvl)/100)*(2*int(base_stat) + val + floor(stat_exp/4)))
                    else:
                        comp = floor(float(nature) * (5 + floor((int(cur_lvl)/100)*(2*int(base_stat) + val + floor(stat_exp/4)))))
                    stat_range.append(comp)

                    #if the computed stat is the same as the current stat, then this is a possible IV
                    if cur_stat != '' and comp == int(cur_stat):
                        iv.append(val)
               
            stat_range = [min(stat_range), max(stat_range)]
            return iv, stat_range





        #flag raised if no missing information
        stat_flag = True
        all_ev_valid = True
        missing_stats = list()
        ivalid_ev = list()

        if self.gen == 'genI' or self.gen == 'genII':

            #get its current stats and EV's, then compute possible IVs
            for i in range(num_stats):

                this_stat = True
                validEV = True

                #get current stats (does NOT accept blank fields)
                if self.stats[i].text() == '':
                    print("Missing stat" + " " + stat_labels[i])
                    stat_flag = False
                    this_stat = False
                    missing_stats.append(stat_labels[i])
                    self.IV_labels[i].setText("N/A")
                cur_stats[stat_labels[i]] = self.stats[i].text()

                #get current EV's (default/blank -> 0)
                if self.ev[i].text() == '':
                    cur_ev[stat_labels[i]] = 0
                elfi int(self.ev[i].text()) > 65535:
                    all_ev_valid = False
                    validEV = False
                else:
                    cur_ev[stat_labels[i]] = self.ev[i].text()

                #compute IV's
                #Brute force (still O(16) or O(32) -> O(1) regardless)
                if validEV:
                    if i == 0:
                        possible_iv[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeIV(pkmn_base_stats[i], cur_ev[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i])
                    else:
                        possible_iv[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeIV(pkmn_base_stats[i], cur_ev[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i])    
            
                    #update stat ranges
                    self.stat_range[i].setText(list2string(possible_stat_range[stat_labels[i]], delim = '-'))
                
                    if this_stat:
                        #update the IV labels
                        self.IV_labels[i].setText(list2string(possible_iv[stat_labels[i]]))
                else:
                    invalid_ev.appen(stat_labels[i])

            if stat_flag and all_ev_valid:
                self.printout.setText("\nSuccessfully computed possible IV's and stats ranges! Press again to rerun!\n")
            elif all_ev_valid:
                self.printout.setText("\nMissing " + list2string(missing_stats) + " stats! Successfully computed all stat ranges though!\n")
            elif stat_flag:
                self.printout.setText("\n" + list2string(invalid_ev) + " EV's cannot exceed 65535!")
            else:
                self.printout.setText("\n" + list2string(invalid_ev) + " EV's cannot exceed 65535 and missing " + list2string(missing_stats) + " stats!")

        else:

            #get its current stats, EV's, and nature then compute possible IVs            
            #get current nature
            if self.pkmn_nature_box.currentText() != '':
                nature = self.pkmn_nature_box.currentText().partition(' ')[0]
                nature_stats = get_stat_mods(self.natures_df, nature, stat_labels[1:])[0]

                for i in range(num_stats):

                    this_stat = True
                    validEV = True

                    #get current stats (does NOT accept blank fields)
                    if self.stats[i].text() == '':
                        print("Missing stat" + " " + stat_labels[i])
                        stat_flag = False
                        this_stat = False
                        missing_stats.append(stat_labels[i])
                        self.IV_labels[i].setText("N/A")
                    cur_stats[stat_labels[i]] = self.stats[i].text()

                    #get current EV's (default/blank -> 0)
                    if self.ev[i].text() == '':
                        cur_ev[stat_labels[i]] = 0
                    elif int(self.ev[i].text()) > 256:
                        all_ev_valid = False
                        validEV = False
                    else:
                        cur_ev[stat_labels[i]] = self.ev[i].text()

                    #compute IV's
                    #Brute force (O(32) -> O(1) regardless)
                    if validEV:
                        if i == 0:
                            possible_iv[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeIV(pkmn_base_stats[i], cur_ev[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i])
                        else:
                            possible_iv[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeIV(pkmn_base_stats[i], cur_ev[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i], nature_stats[i-1])    
            
                        #update stat ranges
                        self.stat_range[i].setText(list2string(possible_stat_range[stat_labels[i]], delim = '-'))

                        if this_stat:
                    	    #update the IV labels
                    	    self.IV_labels[i].setText(list2string(possible_iv[stat_labels[i]]))
                    else:
                        invalid_ev.append(stat_labels[i])

                if stat_flag and all_ev_valid:
                    self.printout.setText("\nSuccessfully computed possible IV's and stats ranges! Press again to rerun!\n")
                elif all_ev_valid:
                    self.printout.setText("\nMissing " + list2string(missing_stats) + " stats! Successfully computed all stat ranges though!\n")
                elif stat_flag:
                    self.printout.setText("\n" + list2string(invalid_ev) + " EV's cannot exceed 256!")
                else:
                    self.printout.setText("\n" + list2string(invalid_ev) + " EV's cannot exceed 256 and missing " + list2string(missing_stats) + " stats!")

            #No nature, cannot proceed
            else:
                self.printout.setText("Missing Nature!  Cannot compute neither possible IVs nor stat ranges.")
                fillNA(num_stats)
       


    
############## EV STUFF ###########################################################################################


    def EV_setup(self, num_stat_cols, num_stat_rows, stat_col_labels):
        '''
        building the fields specific to the EV computation subWindow and displaying it to the user

        Inputs:
        self -- the SubWindow object itself since a lot of the values/variables are members intrinsic to this specific instance
        num_stat_cols --the number of columns in the stats grid
        num_stat_rows -- the number of rows in the stats grid
        stat_col_labels -- the stats grid column labels (i.e. HP, Attack, etc.)
        '''

        #placeholders
        self.stats = list()     #vector of stat fields
        self.iv = list()        #vector of iv's
        self.stat_range = list()
        self.EV_labels = list()


        for i in range(num_stat_cols):

            #making the stats fields/boxes
            self.stats.append(QLineEdit())
            self.stats[i].setValidator(QIntValidator())
            self.stats[i].setMaxLength(3)
            self.stats_layout.addWidget(self.stats[i], 1, i+1)

            #making the EV fields/boxes
            self.iv.append(QLineEdit())
            self.iv[i].setValidator(QIntValidator())
            self.iv[i].setMaxLength(3)
            self.stats_layout.addWidget(self.iv[i], 2, i+1)

            #making the stat range fields/boxes
            self.stat_range.append(QLabel("N/A"))
            self.stats_layout.addWidget(self.stat_range[i], num_stat_rows - 1, i+1)

            #making the IV placeholders
            self.EV_labels.append(QLabel("N/A"))
            self.stats_layout.addWidget(self.EV_labels[i], num_stat_rows, i+1)

        #the button the user clicks that will take all of the user entered parameters to compute the Pokemon's IVs
        self.compute_btn = QPushButton("Compute EVs")
        self.compute_btn.clicked.connect(lambda: self.checkEV(stat_col_labels))


    

    def checkEV(self, stat_labels):
        '''
        the acutal compute button intself, that takes in all the user-filled data and tries to compute all the possible EV's for each stat and their possible stat ranges and displays them on the GUI/window

        Inputs:
        self -- the subWindow object itself since a lot of the values/variables are members intrinsic to this specific instance
        stat_labels -- the grid column labels (the labels of the stats themselves, i.e. HP, Attack, etc.)
        '''


        def list2string(intlist, delim = ', '):
            '''
            translates a Python list to a character-separated (comma by default) string

            Inputs:
            intlist -- the Python list (assumes ints for now)
            delim -- the separating/delimiting character

            Output:
            a readable Python string of the lists contents
            '''
            s = [str(i) for i in intlist]
            return delim.join(s)


        def fillNA(num_stats):
            '''
            fills the label fields (user can't write into) with N/A's

            Input:
            num_stats -- the number of columns (a.k.a number of stats)
            '''
            for i in range(num_stats):
                self.EV_labels[i].setText("N/A")
                self.stat_range[i].setText("N/A")
            


        #get the pokemon's base stats
        cur_pkmn = self.pkmn_name_box.currentText()
        pkmn_base_stats = get_base_stats(self.pkmn_df, cur_pkmn, self.gen, stat_labels)[0]
        num_stats = len(stat_labels)
        
        #get its current level
        if self.pkmn_lvl_entry.text() == '':
            self.printout.setText("\nMissing Level!  Cannot compute possible EV's or stat range.\n")
            fillNA(num_stats)
            return
        else:
            cur_lvl = self.pkmn_lvl_entry.text()

        #initialize dictionaries to hold its current stats and EV's
        cur_stats = dict()
        cur_iv = dict()
        possible_ev = dict()
        possible_stat_range = dict()




        def computeEV(base_stat, iv, cur_stat, stat_label, nature=1):
            '''
            uses the different Pokemon Stat formulas (depends on stat and gen) to figure out the possible EV's given certain parameters

            Inputs:
            base_stat -- the Pokemon's base stat for this stat (fixed, depends on Pokemon species)
            iv -- the Pokemon's individual value (a.k.a diversification value) for this stat determined upon encounter
            cur_stat -- the Pokemon's current stats (not to be confused with base stats)
            stat_labels -- the label of the current stat beign computed (i.e. HP, Attack, Defense, etc.)
            nature -- the nature modification value (positive = 1.1, negative = 0.9, neutral/default = 1)

            Outputs:
            ev -- possible EV's for this current stat
            stat_range -- range of possible values of this stat given the current Pokemon's species, level, and IV's
            '''

            from math import floor, ceil, sqrt

            ev = list()
            stat_range = list()

            if self.gen == 'genI' or self.gen == 'genII':

                #genI/II EV (stat experience) go to 65535 (max 16-bit unsigned int)
                for val in range(65535):

                    #stat formulas
                    if stat_label == 'HP':
                        comp = int(cur_lvl) + 10 + floor((int(cur_lvl)/100)*(2*int(base_stat) + 2*int(iv) + floor(ceil(sqrt(val))/4)))
                    else:
                        comp = 5 + floor((int(cur_lvl)/100)*(2*int(base_stat) + 2*int(iv) + floor(ceil(sqrt(val))/4)))
                    stat_range.append(comp)

                    #if the computed stat is the same as the current stat, then this is a possible IV
                    if cur_stat != '' and comp == int(cur_stat):
                        ev.append(val)
               
            #genIII+ EV go from 0 to 256 (max 8-bit unsigned int)
            else:
                for val in range(256):

                    #stat formulas
                    if stat_label == 'HP':
                        comp = int(cur_lvl) + 10 + floor((int(cur_lvl)/100)*(2*int(base_stat) + int(iv) + floor(val/4)))
                    else:
                        comp = floor(float(nature) * (5 + floor((int(cur_lvl)/100)*(2*int(base_stat) + int(iv) + floor(val/4)))))
                    stat_range.append(comp)

                    #if the computed stat is the same as the current stat, then this is a possible IV
                    if cur_stat != '' and comp == int(cur_stat):
                        ev.append(val)
               
            stat_range = [min(stat_range), max(stat_range)]
            return ev, stat_range





        #flag raised if no missing information
        stat_flag = True
        all_iv_valid = True
        missing_stats = list()
        invalid_iv = list()

        if self.gen == 'genI' or self.gen == 'genII':

            #get its current stats and EV's, then compute possible IVs
            for i in range(num_stats):

                this_stat = True
                validIV = True
            
                #get current stats (does NOT accept blank fields)
                if self.stats[i].text() == '':
                    print("Missing stat" + " " + stat_labels[i])
                    stat_flag = False
                    this_stat = False
                    missing_stats.append(stat_labels[i])
                    self.EV_labels[i].setText("N/A")
                cur_stats[stat_labels[i]] = self.stats[i].text()

                #get current IV's (default/blank -> 0)
                if self.iv[i].text() == '':
                    cur_iv[stat_labels[i]] = 0
                elif int(self.iv[i].text()) > 15:
                    all_iv_valid = False
                    validIV = False
                else:
                    cur_iv[stat_labels[i]] = self.iv[i].text()

                #compute EV's
                #Brute force (O(n))
                if validIV:
                    if i == 0:
                        possible_ev[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeEV(pkmn_base_stats[i], cur_iv[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i])
                    else:
                        possible_ev[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeEV(pkmn_base_stats[i], cur_iv[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i])    
                
                    #update stat ranges
                    self.stat_range[i].setText(list2string(possible_stat_range[stat_labels[i]], delim = '-'))
                    
                    if this_stat:
                        #update the EV labels
                        if len(possible_ev[stat_labels[i]]) > 1:
                            ev_range = [possible_ev[stat_labels[i]][0], possible_ev[stat_labels[i]][-1]]
                            self.EV_labels[i].setText(list2string(ev_range, delim = '-'))
                        else:
                            self.EV_labels[i].setText(list2string(possible_ev[stat_labels[i]]))
                else:
                    invalid_iv.append(stat_labels[i])

            if stat_flag and all_iv_valid:
                self.printout.setText("\nSuccessfully computed possible EV's and stats ranges! Press again to rerun!\n")
            elif all_iv_valid:
                self.printout.setText("\nMissing " + list2string(missing_stats) + " stats! Successfully computed all stat ranges though!\n")
            elif stat_flag:
                self.printout.setText("\n" + list2string(invalid_iv) + " IV's cannot exceed 15!")
            else:
                self.printout.setText("\n" + list2string(invalid_iv) + " IV's cannot exceed 15 and missing " + list2string(missing_stats) + " stats!")

        else:

            #get its current stats, EV's, and nature then compute possible IVs            
            #get current nature
            if self.pkmn_nature_box.currentText() != '':
                nature = self.pkmn_nature_box.currentText().partition(' ')[0]
                nature_stats = get_stat_mods(self.natures_df, nature, stat_labels[1:])[0]

                for i in range(num_stats):

                    this_stat = True
                    validIV = True

                    #get current stats (does NOT accept blank fields)
                    if self.stats[i].text() == '':
                        print("Missing stat" + " " + stat_labels[i])
                        stat_flag = False
                        this_stat = False
                        missing_stats.append(stat_labels[i])
                        self.EV_labels[i].setText("N/A")
                    cur_stats[stat_labels[i]] = self.stats[i].text()

                    #get current IV's (default/blank -> 0)
                    if self.iv[i].text() == '':
                        cur_iv[stat_labels[i]] = 0
                    elif int(self.iv[i].text()) > 31:
                        all_iv_valid = False
                        validIV = False
                    else:
                        cur_iv[stat_labels[i]] = self.iv[i].text()

                    #compute EV's
                    #Brute force (O(n))
                    if validIV:
                        if i == 0:
                            possible_ev[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeEV(pkmn_base_stats[i], cur_iv[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i])
                        else:
                            possible_ev[stat_labels[i]], possible_stat_range[stat_labels[i]] = computeEV(pkmn_base_stats[i], cur_iv[stat_labels[i]], cur_stats[stat_labels[i]], stat_labels[i], nature_stats[i-1])    
                
                        #update stat ranges
                        self.stat_range[i].setText(list2string(possible_stat_range[stat_labels[i]], delim = '-'))

                        if this_stat:
                            #update the EV labels
                            if len(possible_ev[stat_labels[i]]) > 1:
                                ev_range = [possible_ev[stat_labels[i]][0], possible_ev[stat_labels[i]][-1]]
                                self.EV_labels[i].setText(list2string(ev_range, delim = '-'))
                            else:
                                self.EV_labels[i].setText(list2string(possible_ev[stat_labels[i]]))
                    else:
                        invalid_iv.append(stat_labels[i])
                
                if stat_flag and all_iv_valid:
                    self.printout.setText("\nSuccessfully computed possible EV's and stats ranges! Press again to rerun!\n")
                elif all_iv_valid:
                    self.printout.setText("\nMissing " + list2string(missing_stats) + " stats! Successfully computed all stat ranges though!\n") 
                elif stat_flag:
                    self.printout.setText("\n" + list2string(invalid_iv) + " IV's cannot exceed 31!")
                else:
                    self.printout.setText("\n" + list2string(invalid_iv) + " IV's cannot exceed 31 and missing " + list2string(missing_stats) + " stats!")


            #No nature, cannot proceed
            else:
                self.printout.setText("Missing Nature!  Cannot compute neither possible EVs nor stat ranges.")
                fillNA(num_stats)
       





############## Pokemon Trainer Companion ##########################################################################







