from secondWindow import *



#radio buttons used to decide which generation of game the user is playing
class GenRadioBtn(QWidget):

    trigger = pyqtSignal()
    
    def __init__(self, num_btns, btn_labels, layout):
        super(GenRadioBtn, self).__init__()

        label_layout = QHBoxLayout()
        btns_layout = QHBoxLayout()

        label = QLabel("Select the game generation:\n")
        label.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(label)

        self.btns = list()

        #create a radio button widget for each option
        for i in range(num_btns):
            
            self.btns.append(QRadioButton(btn_labels[i]))

            #checking whether/when a button is pressed 
            self.btns[i].toggled.connect(lambda:self.onClicked(self.btns[i]))

            btns_layout.addWidget(self.btns[i])

        layout.addLayout(label_layout)
        layout.addLayout(btns_layout)


    
    
    
    #function that checks for when a button is clicked and services accordingly
    def onClicked(self, radBtn):
        
        radBtn = self.sender()
        if radBtn.isChecked():
            print(radBtn.text() +" is selected")
            self.trigger.emit()
           






#radio buttons to decide the current function 
class FuncRadioBtn(QWidget):

    def __init__(self, num_btns, btn_labels, layout, gen_rads):
        super(FuncRadioBtn, self).__init__()

        label_layout = QHBoxLayout()
        btns_layout = QHBoxLayout()

        label = QLabel("Select the operation:\n")
        label.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(label)

        self.btns = list()

        #create a radio button widget for each option
        for i in range(num_btns):
            
            self.btns.append(QRadioButton(btn_labels[i]))

            #checking whether/when a button is pressed 
            self.btns[i].toggled.connect(lambda:self.onClicked(self.btns[i], gen_rads))

            btns_layout.addWidget(self.btns[i])

        layout.addLayout(label_layout)
        layout.addLayout(btns_layout)

        self.hide()


    #function that creates and shows a subwindow on command
    def create_subwindow(self, title, gen, func):

        #create a subwindow only if one doesn't already exist
        if self.subwindow is None:
            self.subwindow = SubWindow(title, gen, func)
        self.subwindow.show()
    
    
    #function that checks for when a button is clicked and services accordingly
    def onClicked(self, radBtn, gen_rads):
        
        radBtn = self.sender()
        if radBtn.isChecked():
            self.subwindow = None       #no subwindow created yet
           
            #check if there is already a gen radio button selected
            #if so, open the sub window
            for btn in gen_rads.btns:
                if btn.isChecked():
                    self.create_subwindow(btn.text() + " " + radBtn.text(), btn.text(), radBtn.text())
                    break
                
            print(radBtn.text() +" is selected")






