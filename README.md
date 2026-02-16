
---
Цей скрипт завантажує дані з Google Sheets, перетворює їх у розширену таблицю за правилом **"unit ladder"**, а потім додає їх у шар ArcGIS як об'єкти `Feature`.

---

## 🔹 Установка

### 1. Клонуйте репозиторій

```bash
git clone https://github.com/Baranotik15/Test_for_M1MT
cd Test_for_M1MT
```

### 2. Створіть віртуальне середовище

```bash
python -m venv .venv
```

### 3. Активуйте віртуальне середовище

* **Windows:**

```bash
.venv\Scripts\activate
```

* **Mac / Linux:**

```bash
source .venv/bin/activate
```

### 4. Встановіть залежності

```bash
pip install -r requirements.txt
```

---

## 🔹 Настройка `.env`

Створіть файл `.env` у корні проєкту:

```bash
touch .env
```

Додайте змінну `item_id`:

```dotenv
item_id="2250ee027e04401dae8c72e09159af25"
```

> ⚠️ Файл має бути схожий на `env_sample`.

---

## 🔹 Тести

```bash
python -m pytest
```

---

## 🔹 Запуск скрипта

```bash
python main.py
```

Скрипт запросить URL Google Sheet. Введіть його у форматі:

```text
https://docs.google.com/spreadsheets/d/12846JbH2PwR0wN8eLVnosg4xujw-04gKyyD6RuElc-4/edit?gid=0#gid=0
```

Після цього скрипт:

* Парсить URL та отримує `sheet_id` та `gid`.
* Завантажує таблицю в `pandas.DataFrame`.
* Перетворює колонки `long` та `lat` у числовий формат.
* Застосовує правило "unit ladder" для колонок `Значення 1-10`.
* Мапує дані для коректного заповнення шарів у ArcGIS.
* Завантажує дані в шар ArcGIS пакетами по 500 об'єктів.

---

## 🔹 Структура Google Sheet

* `Дата`
* `Область`
* `Місто`
* `Значення 1` … `Значення 10`
* `long` — довгота
* `lat` — широта

---

## 🔹 Примітки

* Якщо дані в колонках `long` та `lat` мають кому як десятковий роздільник, скрипт автоматично замінює її на крапку.
* Пусті значення в колонках `Значення 1-10` замінюються на 0.
* Помилки при додаванні об'єктів виводяться в консоль, інші пакети продовжують завантажуватися.

---


## English Version

This script loads data from Google Sheets, transforms it into an expanded table using the **"unit ladder"** rule, and then adds it to an ArcGIS layer as `Feature` objects.

---

## 🔹 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Baranotik15/Test_for_M1MT
cd Test_for_M1MT
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

* **Windows:**

```bash
.venv\Scripts\activate
```

* **Mac / Linux:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔹 Configure `.env`

Create a `.env` file in the project root:

```bash
touch .env
```

Add the variable `item_id`:

```dotenv
item_id="2250ee027e04401dae8c72e09159af25"
```

> ⚠️ The file should resemble `env_sample`.

---

## 🔹 Tests

```bash
python -m pytest
```

---

## 🔹 Run the script

```bash
python main.py
```

The script will ask for the Google Sheet URL. Enter it like:

```text
https://docs.google.com/spreadsheets/d/12846JbH2PwR0wN8eLVnosg4xujw-04gKyyD6RuElc-4/edit?gid=0#gid=0
```

After that, the script will:

* Parse the URL and get `sheet_id` and `gid`.
* Load the sheet into a `pandas.DataFrame`.
* Convert `long` and `lat` columns to numeric format.
* Apply the "unit ladder" rule for columns `Значення 1-10`.
* Map data for correct ArcGIS layer population.
* Upload data to the ArcGIS layer in batches of 500 features.

---

## 🔹 Google Sheet structure

* `Date`
* `Region`
* `City`
* `Value 1` … `Value 10`
* `long` — longitude
* `lat` — latitude

---

## 🔹 Notes

* If the data in `long` and `lat` uses a comma as the decimal separator, the script automatically replaces it with a dot.
* Empty values in columns `Value 1-10` are replaced with 0.
* Errors when adding features are printed to the console; other batches continue uploading.
