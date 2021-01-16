import sys
import pandas as pd
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import *


class Food:

    def __init__(self, filename):
        self.filename = filename
        self.loaded = False
        self.hasChanges = False
        self.currentProductIndex = None

        self.df = pd.DataFrame(data=[], columns=["product", "proteins", "fats", "carbohydrates", "calories"])
        self.load()

    def load(self):
        """Loads products from csv file in object"""

        self.df = pd.read_csv(self.filename, index_col=False)
        self.loaded = True
        self.hasChanges = False

    def get_data_from_object(self):
        return self.df

    def update_key(self, old_key_data, new_key_data):
        """Updates key of the current selected product"""

        new = self.get_product(new_key_data)
        if new is not None:
            return False

        old = self.get_product(old_key_data)
        if old is None:
            return False

        self.df.iloc[self.currentProductIndex, 0] = new_key_data
        self.hasChanges = True
        return True

    def save_to_csv(self):
        if self.loaded and self.hasChanges:
            self.df.to_csv(self.filename, index=False)
            self.hasChanges = False

    def get_product(self, product):
        """Finds product and returns its index"""

        find = self.df[self.df["product"] == product]
        if find.empty:
            return None

        self.currentProductIndex = find.index
        return self.currentProductIndex

    def __add__(self, product):
        current_product = pd.Series(data={
            "product": product,
            "proteins": 0,
            "fats": 0,
            "carbohydrates": 0,
            "calories": 0})

        self.df = self.df.append(current_product, ignore_index=True)
        self.hasChanges = True
        return True

    def add_new_to_object(self, product_name):
        """Adds new product with zero default parameters"""

        product = self.get_product(product_name)
        if product is not None:
            return False

        self.__add__(product_name)
        self.currentProductIndex = self.df[self.df["product"] == product_name]
        return True

    def delete_by_name(self, product):
        founded_products = self.df[self.df["product"] == product]
        if founded_products is None:
            return False

        self.df = self.df.drop(founded_products.index)
        return True

    def get_current_product_data(self):
        if self.currentProductIndex is not None:
            return self.df.iloc[self.currentProductIndex, :]

    def update_current_product_data(self, array_data):
        self.df.loc[self.currentProductIndex, "proteins"] = array_data[0]
        self.df.loc[self.currentProductIndex, "fats"] = array_data[1]
        self.df.loc[self.currentProductIndex, "carbohydrates"] = array_data[2]
        self.df.loc[self.currentProductIndex, "calories"] = array_data[3]
        self.hasChanges = True
        return True


class Users:

    def __init__(self, filename):
        self.filename = filename
        self.loaded = False
        self.hasChanges = False
        self.currentUser = None

        self.df = pd.DataFrame(data=[], columns=["userName", "password", "sex", "age", "w", "h", "activity", "goal"])
        self.load()

    def load(self):
        """Loads users from csv file into virtual object"""

        self.df = pd.read_csv(self.filename, index_col=False)
        self.loaded = True
        self.hasChanges = False

    def save_to_csv(self):
        if not self.hasChanges:
            return True
        self.df.to_csv(self.filename, index=False)
        self.hasChanges = False

    def find(self, user_name, add_user):
        """Finds the user in object"""

        self.currentUser = self.df[self.df["userName"] == user_name]
        if self.currentUser.empty:
            if not add_user:
                return None

        return self.currentUser

    def add_new_to_object(self, user_name, password):
        """Adds new user with zero parameters"""

        self.currentUser = self.df[self.df["userName"] == user_name]
        if self.currentUser.empty:
            self.__add__(user_name, password)

        self.currentUser = self.df[self.df["userName"] == user_name]
        return self.currentUser

    def __add__(self, user_name, password):
        self.currentUser = pd.Series(data={
            "userName": user_name,
            "password": password,
            "sex": 0,
            "age": 0,
            "w": 0, "h": 0,
            "activity": 0, "goal": 0})

        self.df = self.df.append(self.currentUser, ignore_index=True)
        self.hasChanges = True
        return True

    def get_current_user(self):
        if self.currentUser is None:
            return None
        if self.currentUser.empty:
            return None
        return self.currentUser

    def get_current_user_data(self):
        if self.currentUser.empty:
            return None
        return self.currentUser.iloc[0]

    def set_current_user_data(self, col_index, int_value):
        index = self.currentUser.index
        self.df.loc[index, col_index] = int_value
        self.currentUser[col_index] = int_value
        self.hasChanges = True

    def is_unfilled_parameters(self):
        if self.currentUser.empty:
            return False
        if self.currentUser.iloc[0]["age"] == 0:
            return True

        return False

    def is_real_parameters(self):
        if self.currentUser.empty:
            return False

        age = self.currentUser.iloc[0]["age"]
        height = self.currentUser.iloc[0]["h"]
        weight = self.currentUser.iloc[0]["w"]

        if not (6 < age < 120 and 60 < height < 250 and 20 < weight < 600):
            return False

        return True


class MainWindow(QMainWindow):

    actionUser_is_Enable_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        uic.loadUi('MainWindow.ui', self)

        self.FoodsTable = Food("Food.csv")
        self.UsersTable = Users("users.csv")
        self.user_max_calories = [0, 0, 0, 0]
        self.Username_Button.setText("None")
        self.menuUser.setEnabled(False)

        self.summary_proteins = int()
        self.summary_fats = int()
        self.summary_carboh = int()
        self.summary_calories = int()

        self.actionLogin.triggered.connect(self.login)
        self.Username_Button.clicked.connect(self.login)

        self.actionSave_all.triggered.connect(self.save_all)
        self.actionExit.triggered.connect(self.exit)

        self.actionChangeUserParametersMenu.triggered.connect(self.change_user_parameters)
        self.UserChangeParameters_Button.clicked.connect(self.change_user_parameters)

        self.actionChangeFoodName.triggered.connect(self.food_list_change_food_name)
        self.actionUser_is_Enable_signal.connect(self.user_is_enable)

        self.AddFoodToUserMenu_Button.clicked.connect(self.user_menu_add_food_from_food_list)
        self.tableMenu.cellChanged.connect(self.user_menu_change_food_volume)

        self.AddFoodButton.clicked.connect(self.food_list_add_food)
        self.actionAddFood.triggered.connect(self.food_list_add_food)
        self.RemoveFoodButton.clicked.connect(self.food_list_remove_food)
        self.actionRemoveFood.triggered.connect(self.food_list_remove_food)

        self.dialogLogin = Login(self)
        self.dialogParameters = ChangeParameters(self)

    def login(self):
        self.dialogLogin.init_parameters()
        self.dialogLogin.show()

    def save_all(self):
        self.UsersTable.save_to_csv()
        self.FoodsTable.save_to_csv()

    def change_user_parameters(self):
        user = self.UsersTable.get_current_user()
        if user is None:
            QMessageBox.information(self, "Error", "There is no user loaded!")
            return False

        if self.dialogParameters.load_user_parameters():
            self.dialogParameters.show()

    def calculate_calories(self):
        """Saves parameters and writes it into main window.
        Calculates calories and other parameters per day.
        Writes it into labels. Gives suggestions about healthy weight"""

        user = self.UsersTable.get_current_user()
        if user is None:
            return False

        if self.UsersTable.is_unfilled_parameters():
            return False

        if not self.UsersTable.is_real_parameters():
            return False

        calories = float()
        what_to_do_with_weight = float()
        age = user.iloc[0]['age']
        height = user.iloc[0]['h']
        weight = user.iloc[0]['w']
        male = user.iloc[0]['sex']
        activity = user.iloc[0]['activity']
        goal = user.iloc[0]['goal']

        imt = weight / ((height * 0.01) ** 2)
        if imt < 18.5:
            QMessageBox.information(self, "Advice", "Your weight is small.\n"
                                                    "You should gain some weight")
        elif 18.5 <= imt < 25:
            QMessageBox.information(self, "Advice", "Your weight is normal.\n"
                                                    "You should maintain it")
        elif 25 <= imt < 30:
            QMessageBox.information(self, "Advice", "You have an excess weight.\n"
                                                    "You should lose some weight")
        elif 30 <= imt < 35:
            QMessageBox.information(self, "Advice", "You have a grade 1 obesity!\n"
                                                    "You need to lose weight!")
        elif 35 <= imt < 40:
            QMessageBox.information(self, "Advice", "You have a grade 2 obesity!\n"
                                                    "You need to lose weight!")
        elif imt >= 40:
            QMessageBox.information(self, "Advice", "You have a grade 3 obesity!\n"
                                                    "You need to lose weight!")

        if goal == 0:
            what_to_do_with_weight = 0.85
        if goal == 1:
            what_to_do_with_weight = 1
        if goal == 2:
            what_to_do_with_weight = 1.15

        if male:
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) + (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.097 * height) + (4.33 * age)

        if activity == 0:
            calories = bmr * 1.375
        elif activity == 1:
            calories = bmr * 1.55
        elif activity == 2:
            calories = bmr * 1.725
        elif activity == 3:
            calories = bmr * 1.9

        calories *= what_to_do_with_weight

        if goal == 2:
            proteins = int(calories * 0.15 / 4)
            fats = int(calories * 0.20 / 9)
            carbohydrates = int(calories * 0.65 / 4)
        else:
            proteins = int(calories * 0.15 / 4)
            fats = int(calories * 0.25 / 9)
            carbohydrates = int(calories * 0.6 / 4)
        calories = int(calories)

        self.user_max_calories = [proteins, fats, carbohydrates, calories]
        self.MaxProteinValue.setText(str(proteins))
        self.MaxFatsValue.setText(str(fats))
        self.MaxCarbohValue.setText(str(carbohydrates))
        self.MaxCaloriesValue.setText(str(calories))

        self.HeightLabel.setText(str(height) + " cm")
        self.WeightLabel.setText(str(weight) + " kg")

    def compare_calories(self):
        """Compares sum of calories from user menu to max calories for user per day"""

        self.MaxProteinValue.setStyleSheet('color: black')
        self.MaxFatsValue.setStyleSheet('color: black')
        self.MaxCarbohValue.setStyleSheet('color: black')
        self.MaxCaloriesValue.setStyleSheet('color: black')

        if self.summary_proteins > self.user_max_calories[0]:
            self.ProteinValue.setStyleSheet('color: red')
        else:
            self.ProteinValue.setStyleSheet('color: black')

        if self.summary_fats > self.user_max_calories[1]:
            self.FatsValue.setStyleSheet('color: red')
        else:
            self.FatsValue.setStyleSheet('color: black')

        if self.summary_carboh > self.user_max_calories[2]:
            self.CarbohValue.setStyleSheet('color: red')
        else:
            self.CarbohValue.setStyleSheet('color: black')

        if self.summary_calories > self.user_max_calories[3]:
            self.CaloriesValue.setStyleSheet('color: red')
        else:
            self.CaloriesValue.setStyleSheet('color: black')

    @pyqtSlot(str, str)
    def user_is_enable(self, login, password):
        """Enables the action "User" """

        self.user_menu_init()
        self.calculate_calories()
        self.user_menu_calculate()

        self.Username_Button.setText(login)
        self.menuUser.setEnabled(True)

    def exit(self):

        action = QMessageBox.question(self, "Question", "Do you want to save all before exit?",
                                      QMessageBox.Yes | QMessageBox.No)
        if action == QMessageBox.Yes:
            self.UsersTable.save_to_csv()
            self.FoodsTable.save_to_csv()
            sys.exit()

        sys.exit()

    def food_list_load_all(self):
        df = self.FoodsTable.get_data_from_object()
        headers = df.columns.values.tolist()

        self.tableFoods.setColumnCount(len(headers))
        self.tableFoods.setColumnWidth(0, 85)
        self.tableFoods.setColumnWidth(1, 20)
        self.tableFoods.setColumnWidth(2, 20)
        self.tableFoods.setColumnWidth(3, 20)
        self.tableFoods.setColumnWidth(4, 20)
        self.tableFoods.setHorizontalHeaderLabels(headers)

        for i, row in df.iterrows():
            self.tableFoods.setRowCount(self.tableFoods.rowCount() + 1)

            for j in range(self.tableFoods.columnCount()):
                self.tableFoods.setItem(i, j, QTableWidgetItem(str(row[j])))
                if j == 0 or j == 4:
                    self.tableFoods.item(i, j).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.tableFoods.cellChanged.connect(self.food_list_change_nutrients)

    def food_list_add_food(self):
        new_row = self.tableFoods.rowCount() + 1
        product = self.FoodsTable.add_new_to_object("New Product " + str(new_row))
        if product is None:
            QMessageBox.information(self, "Error", "Product is exist")
            return False

        self.tableFoods.cellChanged.disconnect(self.food_list_change_nutrients)

        self.tableFoods.setRowCount(new_row)
        self.tableFoods.setItem(new_row - 1, 0, QTableWidgetItem("New Product " + str(new_row)))
        self.tableFoods.item(new_row - 1, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.tableFoods.setItem(new_row - 1, 1, QTableWidgetItem("0.0"))
        self.tableFoods.setItem(new_row - 1, 2, QTableWidgetItem("0.0"))
        self.tableFoods.setItem(new_row - 1, 3, QTableWidgetItem("0.0"))
        self.tableFoods.setItem(new_row - 1, 4, QTableWidgetItem("0.0"))

        self.tableFoods.cellChanged.connect(self.food_list_change_nutrients)

    def food_list_remove_food(self):
        selected_row = self.tableFoods.currentRow()
        if selected_row < 0:
            return False

        product_name = self.tableFoods.item(selected_row, 0).text()
        if self.FoodsTable.delete_by_name(product_name):
            self.tableFoods.removeRow(selected_row)

    def food_list_change_food_name(self):
        selected_row = self.tableFoods.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "Error", "You haven't selected any food!")
            return False

        product_name = self.tableFoods.item(selected_row, 0).text()
        new_product, ok_is_pressed = QInputDialog.getText(self, "Input new product name",
                                                          "Product name:", QLineEdit.Normal, product_name)
        if ok_is_pressed and new_product != '':
            if not self.FoodsTable.update_key(product_name, str(new_product)):
                QMessageBox.information(self, "Error", "Product is not changed", QMessageBox.Ok)
                return False

            self.tableFoods.setItem(selected_row, 0, QTableWidgetItem(new_product))

    def food_list_change_nutrients(self, n_row, n_col):
        """Checks if parameters have been changed correctly"""

        if n_col == 0 or n_col == 4:
            return False
        elif self.tableFoods.item(n_row, 0) is None:
            return False

        food_name = self.tableFoods.item(n_row, 0).text()
        product = self.FoodsTable.get_product(food_name)
        if product is None:
            return False

        product_data = self.FoodsTable.get_current_product_data()
        if product_data.empty:
            return False

        old_value = product_data.iloc[0, n_col]
        try:
            p = float(self.tableFoods.item(n_row, 1).text())
            f = float(self.tableFoods.item(n_row, 2).text())
            c = float(self.tableFoods.item(n_row, 3).text())
        except ValueError:
            QMessageBox.information(self, "Error", "The value must be number!")
            self.tableFoods.setItem(n_row, n_col, QTableWidgetItem(str(old_value)))
            return False

        if p < 0:
            QMessageBox.information(self, "Error", "Proteins cannot be negative!")
            self.tableFoods.setItem(n_row, n_col, QTableWidgetItem(str(old_value)))
            return False
        if f < 0:
            QMessageBox.information(self, "Error", "Fats cannot be negative!")
            self.tableFoods.setItem(n_row, n_col, QTableWidgetItem(str(old_value)))
            return False
        if c < 0:
            QMessageBox.information(self, "Error", "Carbohydrates cannot be negative!")
            self.tableFoods.setItem(n_row, n_col, QTableWidgetItem(str(old_value)))
            return False

        self.FoodsTable.update_current_product_data([p, f, c, p * 4 + c * 4 + f * 9])
        self.tableFoods.setItem(n_row, 4, QTableWidgetItem(str(int(p * 4 + c * 4 + f * 9))))
        self.user_menu_calculate()

    def user_menu_add_food_from_food_list(self):
        user = self.UsersTable.get_current_user()
        if user is None:
            QMessageBox.information(self, "Error", "There is no user loaded!")
            return False

        row = self.tableFoods.currentRow()
        col = 0
        item = self.tableFoods.item(row, col)

        try:
            food_name = item.text()     # Catching this helps when trying to add food with no user loaded
        except:
            QMessageBox.information(self, "Error", "You have not choose the product!")
            return False

        if self.MaxProteinValue.text() == "":
            QMessageBox.information(self, "Error", "You have not entered the parameters!")
            return False

        product = self.FoodsTable.get_product(food_name)
        if product is None:
            QMessageBox.information(self, "Error", "Problem to search food !")
            return False

        product_data = self.FoodsTable.get_current_product_data()
        if product_data.empty:
            QMessageBox.information(self, "Error", "Problem to get food data !")
            return False

        self.user_menu_create_new_row(food_name)
        self.user_menu_calculate()
        return True

    def user_menu_remove_food(self, selected_row):
        self.tableMenu.removeRow(selected_row)

    def user_menu_init(self):
        self.tableMenu.setRowCount(0)
        self.tableMenu.setColumnCount(3)
        self.tableMenu.setColumnWidth(0, 85)
        self.tableMenu.setColumnWidth(1, 70)
        self.tableMenu.setColumnWidth(2, 65)

        self.tableMenu.setHorizontalHeaderLabels(["Product", "Volume, g", "Calories"])

    def user_menu_create_new_row(self, product):
        new_row = self.tableMenu.rowCount() + 1
        self.tableMenu.setRowCount(new_row)
        self.tableMenu.setItem(new_row - 1, 0, QTableWidgetItem(product))
        self.tableMenu.setItem(new_row - 1, 1, QTableWidgetItem("100"))
        self.tableMenu.setItem(new_row - 1, 2, QTableWidgetItem("0"))

    def user_menu_change_food_volume(self, n_row, n_col):
        """Removes food if value in volume column is zero"""

        if n_col == 1:
            value = self.tableMenu.item(n_row, 1).text()
            if value == "0":
                self.user_menu_remove_food(n_row)

            self.user_menu_calculate()

    def user_menu_calculate(self):
        """Calculates calories and other parameters from user's menu"""

        row_count = self.tableMenu.rowCount()
        sum_cal = [0, 0, 0, 0]
        for i in range(row_count):
            if self.tableMenu.item(i, 0) is None:
                continue
            try:
                coefficient = round(int(self.tableMenu.item(i, 1).text()) / 100, 6)
            except:
                coefficient = 0

            food_name = self.tableMenu.item(i, 0).text()
            product = self.FoodsTable.get_product(food_name)
            if product is None:
                continue
            product_data = self.FoodsTable.get_current_product_data()
            if product_data.empty:
                continue

            sum_cal[0] += int(coefficient * product_data["proteins"])
            sum_cal[1] += int(coefficient * product_data["fats"])
            sum_cal[2] += int(coefficient * product_data["carbohydrates"])
            sum_cal[3] += int(coefficient * product_data["calories"])

            coefficient_calories = float(product_data["calories"] / 100)
            menu_calories = str(int((coefficient_calories * int(self.tableMenu.item(i, 1).text()))))
            self.tableMenu.setItem(i, 2, QTableWidgetItem(menu_calories))

            self.tableMenu.item(i, 2).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tableMenu.item(i, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.summary_proteins = sum_cal[0]
        self.summary_fats = sum_cal[1]
        self.summary_carboh = sum_cal[2]
        self.summary_calories = sum_cal[3]

        self.ProteinValue.setText(str(self.summary_proteins))
        self.FatsValue.setText(str(self.summary_fats))
        self.CarbohValue.setText(str(self.summary_carboh))
        self.CaloriesValue.setText(str(self.summary_calories))

        self.compare_calories()
        return sum_cal


class Login(QDialog):

    def __init__(self, parent):
        self.parent = parent
        super().__init__()
        uic.loadUi('Login.ui', self)

        self.PasswordLine.setEchoMode(QLineEdit.Password)
        self.LoginButton.clicked.connect(self.login_clicked)

    def init_parameters(self):
        self.LoginLine.setText("")
        self.PasswordLine.setText("")

    def login_clicked(self):
        login = self.LoginLine.text()
        password = self.PasswordLine.text()

        if login == "" or password == "":
            QMessageBox.information(self, 'Error', "You have not entered\n  login or password!")
            return False

        user = self.parent.UsersTable.find(login, False)
        if user is None:
            action = QMessageBox.question(self, "Error", "There is no user with this login.\n"
                                                         "Do you want to register new?",
                                          QMessageBox.Yes | QMessageBox.No)
            if action == QMessageBox.Yes:
                user = self.parent.UsersTable.add_new_to_object(login, password)
                if user is None:
                    QMessageBox.information(self, "Error", "Cannot add user!")
                    return False
            else:
                return False
        else:
            user_data = self.parent.UsersTable.get_current_user_data()
            if not (user_data["password"] == password):
                QMessageBox.information(self, "Error", "Wrong password!")
                return False

        self.parent.actionUser_is_Enable_signal.emit(login, password)
        Login.close(self)


class ChangeParameters(QDialog):

    def __init__(self, parent):
        self.parent = parent
        super().__init__()
        uic.loadUi('Parameters.ui', self)

        self.SaveButton.clicked.connect(self.save)
        self.CloseButton.clicked.connect(self.close_window)

    def load_user_parameters(self):
        """Loads user parameters after login"""

        user = self.parent.UsersTable.get_current_user_data()
        if user.empty:
            QMessageBox.information(self, 'Error', "Error when reading user data!")
            return False

        age = user['age']
        height = user['h']
        weight = user['w']
        sex = user['sex']
        activity = user['activity']
        goal = user['goal']

        self.AgeLine.setText(str(age))
        self.WeightLine.setText(str(weight))
        self.HeightLine.setText(str(height))
        self.Sex_comboBox.setCurrentIndex(sex)
        self.Activity_comboBox.setCurrentIndex(activity)
        self.goal_comboBox.setCurrentIndex(goal)

        return True  # True is permission for opening the dialog window - parameters

    def save(self):
        """Checks if parameters are between real parameters.
        If True, writes user login, password and parameters in the object"""

        age = self.AgeLine.text()
        weight = self.WeightLine.text()
        height = self.HeightLine.text()
        sex = self.Sex_comboBox.currentIndex()
        activity = self.Activity_comboBox.currentIndex()
        goal = self.goal_comboBox.currentIndex()

        try:
            age = int(age)
            weight = int(weight)
            height = int(height)
        except ValueError:
            QMessageBox.information(self, 'Error', "The parameters are not numbers!")
            return False

        if not 6 < age < 120:
            QMessageBox.information(self, "Error", "The age is not real! \n (should be from 6 to 120)")
            return False
        if not 60 < height < 250:
            QMessageBox.information(self, "Error", "The height is not real! \n (should be from 60 to 250)")
            return False
        if not 20 < weight < 600:
            QMessageBox.information(self, "Error", "The weight is not real! \n (should be from 20 to 600)")
            return False

        self.parent.UsersTable.set_current_user_data("age", age)
        self.parent.UsersTable.set_current_user_data("w", weight)
        self.parent.UsersTable.set_current_user_data("h", height)
        self.parent.UsersTable.set_current_user_data("sex", sex)
        self.parent.UsersTable.set_current_user_data("activity", activity)
        self.parent.UsersTable.set_current_user_data("goal", goal)

        self.parent.calculate_calories()
        self.parent.compare_calories()
        ChangeParameters.close(self)

    def close_window(self):
        ChangeParameters.close(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = MainWindow()
    calc.food_list_load_all()
    calc.show()
    sys.exit(app.exec_())
