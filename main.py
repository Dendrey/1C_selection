import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QCalendarWidget, QListWidget, QListWidgetItem, QDialog, 
                             QLabel, QLineEdit, QMessageBox)
from PyQt5.QtCore import pyqtSignal
import pandas as pd

def load_products(file_path):
    products = pd.read_csv(file_path)
    return products

def load_food_log(log_file):
    try:
        log = pd.read_csv(log_file)
    except FileNotFoundError:
        log = pd.DataFrame(columns=["food_item", "weight", "date"])
    return log

class CalorieCounterApp(QWidget):
    def __init__(self):
        self.products = load_products("products.csv")
        self.food_log = load_food_log("food_log.csv")  # Load existing food log
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Календарь
        calendar = QCalendarWidget(self)
        calendar.setGridVisible(True)
        layout.addWidget(calendar)

        # Список добавленной еды
        self.food_log_list = QListWidget(self)
        self.food_log_list.addItems(self.food_log['food_item'].tolist())
        layout.addWidget(self.food_log_list)

        # Кнопка "Добавить еду"
        add_food_button = QPushButton('Добавить еду', self)
        add_food_button.clicked.connect(self.openFoodList)
        layout.addWidget(add_food_button)

        self.setLayout(layout)
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Подсчёт калорий')

    def openFoodList(self):
        self.food_list_dialog = FoodListDialog(self)
        self.food_list_dialog.food_selected.connect(self.onFoodSelected)
        self.food_list_dialog.exec_()

    def onFoodSelected(self, food_item):
        QMessageBox.information(self, "Добавлено", f"Вы добавили: {food_item}")
        self.food_list_dialog.close()

    def updateFoodLogDisplay(self):
        self.food_log_list.clear()
        print(self.food_log['food_item'].tolist())
        self.food_log_list.addItems(self.food_log['food_item'].tolist())

    def save_food_log(self, food_item, weight):
        """Сохраняет добавленную еду в DataFrame и CSV."""
        today = pd.Timestamp.now().date()
        new_entry = pd.DataFrame([[food_item, weight, today]], columns=["food_item", "weight", "date"])
        self.food_log = pd.concat([self.food_log, new_entry], ignore_index=True)
        self.food_log.to_csv("food_log.csv", index=False)  # Save back to CSV

class FoodListDialog(QDialog):
    food_selected = pyqtSignal(str)  # Сигнал для передачи выбранной еды

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор еды')
        self.setGeometry(150, 150, 300, 400)

        layout = QVBoxLayout()

        # Список продуктов
        self.food_list = QListWidget(self)
        self.populateFoodList()  # Метод для заполнения списка едой
        layout.addWidget(self.food_list)

        self.setLayout(layout)

        # Подключаем событие нажатия на элемент списка
        self.food_list.itemDoubleClicked.connect(self.openWeightInputDialog)

    def populateFoodList(self):
        foods = load_products("products.csv")["product"].tolist()
        for food in foods:
            item = QListWidgetItem(food)
            self.food_list.addItem(item)

    def openWeightInputDialog(self, item):
        """Открывает окно для ввода массы для выбранной еды."""
        weight_input_dialog = WeightInputDialog(item.text(), self)
        weight_input_dialog.weight_submitted.connect(self.emitFoodSelected)
        weight_input_dialog.exec_()

    def emitFoodSelected(self, food_item, weight):
        self.food_selected.emit(f"{food_item} - {weight} г")
        self.parent().save_food_log(food_item, weight)  # Save food log in parent
        self.parent().updateFoodLogDisplay()

class WeightInputDialog(QDialog):
    weight_submitted = pyqtSignal(str, float)  # Сигнал для передачи выбранной массы

    def __init__(self, food_item, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Ввод массы для {food_item}')
        self.setGeometry(200, 200, 250, 150)

        layout = QVBoxLayout()

        label = QLabel(f'Введите массу для {food_item} (в граммах):', self)
        layout.addWidget(label)

        self.weight_input = QLineEdit(self)
        layout.addWidget(self.weight_input)

        submit_button = QPushButton('Добавить', self)
        submit_button.clicked.connect(self.submitWeight)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submitWeight(self):
        """Обрабатывает ввод массы и отправляет сигнал с её значением."""
        weight_text = self.weight_input.text()
        if weight_text.isdigit():
            weight = float(weight_text)
            self.weight_submitted.emit(self.parent().food_list.currentItem().text(), weight)
            self.accept()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите корректное значение массы.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CalorieCounterApp()
    ex.show()
    sys.exit(app.exec_())
