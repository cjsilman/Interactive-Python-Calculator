import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QLineEdit, 
                               QSizePolicy, QPushButton, 
                               QWidget, QHBoxLayout, 
                               QGridLayout)
from collections import deque
import copy
import math

BUTTON_HEIGHT = 70
operator_list = ['+', '_', 'x', '\u00F7']

class Calculator(QWidget):
    def __init__(self, parent=None):
        #Creates the entire GUI for the calculator
        #Holds all methods of the GUI
        super(Calculator, self).__init__(parent)

        #This double-ended queue holds the entire expression
        self.expression_deque = deque()
        self.operand = "0"
        self.operatorPresent = False

        content_layout = QGridLayout()
        content_layout.setSpacing(0)

        #Set up text displays
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMaxLength(40)
        self.display.setTextMargins(0, 40, 10, 30) #left, top, right, bottom
        self.display.setFont(QFont('Arial', 40))
        content_layout.addWidget(self.display, 0, 0, 1, 5) #left, top, right, bottom

        self.prev_display = QLineEdit("")
        self.prev_display.setReadOnly(True)
        self.prev_display.setMaxLength(40)
        self.prev_display.setTextMargins(0, 0, 0, 0)
        self.prev_display.setFont(QFont('Arial', 10))
        self.prev_display.setStyleSheet("color: grey")
        content_layout.addWidget(self.prev_display, 0, 0, 2, 20)

        #Define all button variables
        pointButton = QPushButton(".")
        changeSignButton = QPushButton("\261")
        backspaceButton = QPushButton("\u232B")
        clearButton = QPushButton("C")
        clearAllbutton = QPushButton("CE")
        divButton = QPushButton("\u00F7")
        multButton = QPushButton("x")
        minusButton = QPushButton("-")
        plusButton = QPushButton("+")
        calculateButton = QPushButton("=")
        percentButton = QPushButton("%")
        inverseButton = QPushButton("\u215F\U0001D465")
        squareButton = QPushButton("\U0001D465\u00b2")
        rootButton = QPushButton("\u221a\U0001D465")

        number_1 = QPushButton("1")
        number_2 = QPushButton("2")
        number_3 = QPushButton("3")
        number_4 = QPushButton("4")
        number_5 = QPushButton("5")
        number_6 = QPushButton("6")
        number_7 = QPushButton("7")
        number_8 = QPushButton("8")
        number_9 = QPushButton("9")
        number_0 = QPushButton("0")

        #Define what happens when buttons are clicked
        number_1.clicked.connect(lambda: self.numberClicked(1))
        number_2.clicked.connect(lambda: self.numberClicked(2))
        number_3.clicked.connect(lambda: self.numberClicked(3))
        number_4.clicked.connect(lambda: self.numberClicked(4))
        number_5.clicked.connect(lambda: self.numberClicked(5))
        number_6.clicked.connect(lambda: self.numberClicked(6))
        number_7.clicked.connect(lambda: self.numberClicked(7))
        number_8.clicked.connect(lambda: self.numberClicked(8))
        number_9.clicked.connect(lambda: self.numberClicked(9))
        number_0.clicked.connect(lambda: self.numberClicked(0))

        divButton.clicked.connect(lambda: self.operatorClicked("\u00F7"))
        multButton.clicked.connect(lambda: self.operatorClicked("x"))
        minusButton.clicked.connect(lambda: self.operatorClicked("_"))
        plusButton.clicked.connect(lambda: self.operatorClicked("+"))

        pointButton.clicked.connect(self.addPoint)
        backspaceButton.clicked.connect(self.backspace)

        changeSignButton.clicked.connect(self.negate)
        percentButton.clicked.connect(self.percent)
        inverseButton.clicked.connect(self.inverse)
        squareButton.clicked.connect(self.square)
        rootButton.clicked.connect(self.root)

        calculateButton.clicked.connect(self.performCalculation)

        clearButton.clicked.connect(self.displayClear)
        clearAllbutton.clicked.connect(self.displayClear)
        buttons = [
                (percentButton, clearAllbutton, clearButton, backspaceButton),
                (inverseButton, squareButton, rootButton, divButton),
                (number_7, number_8, number_9, multButton),
                (number_4, number_5, number_6, minusButton),
                (number_1, number_2, number_3, plusButton),
                (changeSignButton, number_0, pointButton, calculateButton)
                ]

        #Place all buttons on the screen
        row = 1
        for buttonRow in buttons:
            col = 0
            for button in buttonRow:
                button.setMinimumHeight(70)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                content_layout.addWidget(button, row, col)
                if row == 6 and col == 3:
                    button.setObjectName("equals")
                if row in [3, 4, 5, 6] and col in [0, 1, 2]:
                    button.setObjectName("mainButtons")
                col += 1
            row += 1

        main_widget = QWidget()
        main_widget.setLayout(content_layout)

        layout = QHBoxLayout()
        layout.addWidget(main_widget, 4)
        self.setLayout(layout)

    def numberClicked(self, num):
        #This section checks whether there is a 0 or err present, and if so, remove it when adding a non-zero number
        if (self.operand == "0" and num != 0) or (self.display.text() == "Err") or (self.display.text() == "0"):
            if len(self.expression_deque) == 0:
                self.display.clear()
            if len(self.expression_deque) == 1:
                read_value = self.expression_deque.pop()
                if read_value == "0":
                    self.display.clear()
                else:
                    self.expression_deque.append(read_value)
        
        #This does the same as above, but makes sure we can't add multiple zeros without other numbers
        last_operand = self.collectOperand()
        if (last_operand == "00"):
            self.expression_deque.pop()

        self.operand = str(num)
            
        self.expression_deque.append(num)
        self.forceScreenUpdate()

        self.sizeCheck()
        

    def operatorClicked(self, operator):    
        #If there is already an operator present, and another operator is placed after a number
        #we want to run the calculation for the previous expression, then add the new operator
        if self.operatorPresent == True:
            last_appended = self.expression_deque.pop()
            self.expression_deque.append(last_appended)
            if (last_appended in operator_list):
                return
            print("Operator already present!")
            self.operatorPresent = False
            self.performCalculation()

        #If someone tries to add an operator to a divide by zero error, we turn it into a zero
        if self.display.text() == "Err":
            self.display.setText("0")

        #If there is already an operator placed as the last character, don't add another!
        if len(self.expression_deque) != 0:
            last_appended = self.expression_deque.pop()
            if last_appended in operator_list: #Check if last added was operator
                self.expression_deque.append(last_appended) #If it was operator, don't add another operator
                return
            else:
                self.expression_deque.append(last_appended)
                self.operatorPresent = True
        else:
            self.expression_deque.append(0)

        self.expression_deque.append(operator)
        if str(operator) == '_':
            operator = '-'
        self.display.setText(self.display.text() + str(operator))

        self.sizeCheck()

    def backspace(self):
        #Simply removes the last character added to the queue and updates the screen
        if len(self.expression_deque) != 0:
            self.display.setText(self.display.text()[:-1])
            read_value = self.expression_deque.pop()
            if read_value in operator_list:
                self.operatorPresent = False

        if len(self.expression_deque) == 0: 
            self.display.setText("0")

        self.updatePrevDisplay("")

    def addPoint(self):
        operand = self.collectOperand()
        if operand.count('.') == 0:
            self.display.setText(self.display.text() + str("."))
            self.expression_deque.append(".")

    def negate(self):
        operand = self.collectOperand()
        operand = -(float(operand))
        self.replaceQueue(operand)
        self.forceScreenUpdate()

    def percent(self):
        operand1, operator, operand2 = self.collectOperand(force_both = True)

        if operand2 == None:
            self.replaceQueue(0)
            self.forceScreenUpdate()
            self.updatePrevDisplay("0")
            return
        else:
            operand1 = float(operand1)
            operand2 = float(operand2)

        #Find what the operator value is to do correct computation
        if operator == '+':
            percent_value = (operand1 * (operand2/100))
        elif operator == '_':
            operator = '-'
            percent_value = (operand1 * (operand2/100))
        elif operator == 'x':
            percent_value = ((operand2/100))
        elif operator == '\u00F7':
            percent_value = ((operand2/100))


        self.replaceQueue(percent_value)
        self.performCalculation()
        

    def inverse(self):
        operand = self.collectOperand()

        if float(operand) == 0:
            self.divByZeroError()
            return

        new_operand = 1/float(operand)
        self.replaceQueue(new_operand)
        self.forceScreenUpdate()
        self.updatePrevDisplay(f"1/({operand}) =")

    def square(self):
        operand = self.collectOperand()
        new_operand = float(operand)**2
        self.replaceQueue(new_operand)
        self.forceScreenUpdate()
        self.updatePrevDisplay(f"({operand})\u00B2 =")

    def root(self):
        operand = self.collectOperand()
        new_operand = math.sqrt(float(operand))
        self.replaceQueue(new_operand)
        self.forceScreenUpdate()
        self.updatePrevDisplay(f"(\u221A{operand}) =")


    def collectOperand(self, force_both=False):
        #Collects the most relevant recent opperand
        #4 + 27 -> 27
        #53 -> 53
        #43 + 0 -> 0
        copied_deque = copy.copy(self.expression_deque)
        operand = "0"
        prev_operand = None
        operator = ""

        while len(copied_deque) != 0:
            read_character = str(copied_deque.popleft())
            if read_character not in operator_list:
                if read_character != "0" and operand == "0":
                    operand = ""
                operand += read_character
            else:
                prev_operand = operand
                operator = read_character
                operand = "0"

        if force_both == True:
            if prev_operand == None:
                return(operand, "x", None)
            else:
                return(prev_operand, operator, operand)
        else:
            return operand

    def replaceQueue(self, operand):
        #Replaces the most revelant (recent) operand with the one given
        if float(operand) - int(operand) == 0:
            operand = int(operand)

        while len(self.expression_deque) != 0:
            read_character = str(self.expression_deque.pop())
            if read_character in operator_list:
                self.expression_deque.append(read_character)
                break

        for character in str(operand):
            self.expression_deque.append(character)

    def forceScreenUpdate(self):
        #Forces the screen to update itself and show what is in the deque
        copied_deque = copy.copy(self.expression_deque)
        expression = ""
        while len(copied_deque) != 0:
            read_character = str(copied_deque.popleft())
            if read_character == '_':
                read_character = '-'
            expression += read_character

        if expression != self.display.text():
            self.display.setText(expression)

        self.sizeCheck()

    def updatePrevDisplay(self, output):
        #Updates the previous equation display
        self.prev_display.clear()
        self.prev_display.setText(output)

    def performCalculation(self):
        #This is what actually evaluates the expression in the deque
        
        #This portion reads everything from the deque and places the operands and operator into a list
        expression = ""
        while len(self.expression_deque) != 0:
            read_value = str(self.expression_deque.popleft())
            if read_value not in operator_list:
                expression += read_value
            else:
                expression_list = []
                expression_list.append(float(expression))
                expression_list.append(read_value)
                expression = ""
        
        #If there is no input, the expression_list doesn't exist. So we need to handle that in a special way
        try:
            expression_list.append(float(expression))

            #This takes all values from the list and assigns them to easy to understand variables
            operand1 = expression_list[0]
            operator = expression_list[1]
            operand2 = expression_list[2]
        except:
            if expression == "":
                for string in expression_list:
                    if string not in operator_list:
                        if float(string) - int(string) == 0:
                            string = int(string)
                    for character in str(string):
                        self.expression_deque.append(character)
            else:
                for character in expression:
                    self.expression_deque.append(character)
            print("Invalid expression")
            return
        
        
        #Calculations are done with the operands
        if operator == '+':
            finalValue = operand1 + operand2
        elif operator == '_':
            operator = '-'
            finalValue = operand1 - operand2
        elif operator == 'x':
            finalValue = operand1*operand2
        elif operator == '\u00F7':
            #Prevents a div by zero exception
            if operand2 != 0:
                finalValue = operand1/operand2
            else:
                expression_list.clear()
                self.divByZeroError()
                return

        print(f"{operand1} {operator} {operand2}")

        #Update the previous equation display with the equation we just ran
        self.updatePrevDisplay(f"{operand1} {operator} {operand2} =")

        self.display.clear()
        self.expression_deque.clear()

        if finalValue - int(finalValue) == 0:
            finalValue = int(finalValue)

        for character in str(finalValue):
            self.display.setText(self.display.text() + str(character))
            self.expression_deque.append(character)
        
        print(f"={finalValue}")
        self.operand = str(finalValue)
        expression_list.clear()
        self.operatorPresent = False
        self.sizeCheck()

        

    def displayClear(self):
        self.expression_deque.clear()
        self.display.clear()
        self.operatorPresent = False
        self.sizeCheck()
        self.display.setText("0")
        self.prev_display.setText("")
        self.operand = "0"
        

    def divByZeroError(self):
        self.expression_deque.clear()
        self.operatorPresent = False
        self.operand = "0"
        self.sizeCheck()
        self.display.setText("Err")
        self.updatePrevDisplay("DivByZero")
        print("\n=Err")

    def sizeCheck(self):
        sizes = [(8, 35), (10, 28), (15,23), (18,18), (23, 15), (30, 10)]
        for expression_length, font_size in sizes:
            if len(self.expression_deque) > expression_length:
                self.display.setFont(QFont('Arial', font_size))

        if len(self.expression_deque) < 5:
            self.display.setFont(QFont('Arial', 40))
        

if __name__ == "__main__":
    app = QApplication()

    w = Calculator()
    w.setWindowTitle("Calculator")
    w.resize(200, 600)
    w.show()

    with open("Style_sheets/style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())