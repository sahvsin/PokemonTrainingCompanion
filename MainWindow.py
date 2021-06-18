from radioButtons import *


#from gen_reader import *


#MACROS
num_gens = 6
gen_btns_labels = ['genI', 'genII', 'genIII', 'genIV', 'genV', 'genVI']
func_btns_labels = ['IV Calculator', 'EV Calculator', 'Pokemon Growth Tracker']




#main/root window class
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Pokemon Trainer Companion")
        
        #create an encapsulating widget to nest layouts
        widge = QWidget()

        outer_layout = QVBoxLayout()
        intro_layout = QHBoxLayout()
        gen_btns_layout = QVBoxLayout()
        func_btns_layout = QVBoxLayout()
        btns_layout = QHBoxLayout()

        #introductory statement and directions
        label = QLabel("Welcome to the Pokemon Trainer Companion!\n Select your game's generation below and the funciton of interest.\n Either calculate IVs or EVs or track your Pokemon's stat growth.\n\n")
        label.setAlignment(Qt.AlignCenter)
        intro_layout.addWidget(label)

        #adding radio buttons for each Pokemon Gen
        gen_radio = GenRadioBtn(num_gens, gen_btns_labels, gen_btns_layout)
        gen_radio.setLayout(gen_btns_layout)
        func_radio = FuncRadioBtn(3, func_btns_labels, func_btns_layout, gen_radio)
        func_radio.setLayout(func_btns_layout)
        
        #grouping the buttons so I can select one from each group
        gen_group = QButtonGroup(widge)
        func_group = QButtonGroup(widge)

        for btn in gen_radio.btns:
            gen_group.addButton(btn)

        for btn in func_radio.btns:
            func_group.addButton(btn)
            btn.clicked.connect(self.closeWindow)

        self.Stk = QStackedWidget(self)
        self.Stk.addWidget(gen_radio)
        self.Stk.addWidget(func_radio)
        btns_layout.addWidget(self.Stk)

        #organizing the nesting of the layouts
        outer_layout.addLayout(intro_layout)
        outer_layout.addLayout(btns_layout)
        widge.setLayout(outer_layout)
        
        #toggle the gen and function layouts
        gen_radio.trigger.connect(self.display)

        self.setCentralWidget(widge)



    def display(self):
        self.Stk.setCurrentIndex(1)


    def closeWindow(self):
        self.close() 