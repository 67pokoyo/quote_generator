import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Dict

DATA_FILE = "quotes_history.json"

# Предопределённые цитаты (текст, автор, тема)
DEFAULT_QUOTES = [
    {"text": "Будь изменением, которое хочешь видеть в мире", "author": "Махатма Ганди", "topic": "Мотивация"},
    {"text": "Я мыслю, следовательно, существую", "author": "Рене Декарт", "topic": "Философия"},
    {"text": "Единственный способ делать великую работу — любить то, что ты делаешь", "author": "Стив Джобс", "topic": "Мотивация"},
    {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы", "author": "Джон Леннон", "topic": "Жизнь"},
    {"text": "Не суди о человеке по его друзьям. У Иуды они были безупречны", "author": "Поль Верлен", "topic": "Философия"},
    {"text": "Успех — это способность идти от неудачи к неудаче, не теряя энтузиазма", "author": "Уинстон Черчилль", "topic": "Успех"},
    {"text": "Лучший способ предсказать будущее — изобрести его", "author": "Алан Кей", "topic": "Будущее"},
    {"text": "Сложнее всего начать действовать, все остальное зависит от упорства", "author": "Амелия Эрхарт", "topic": "Мотивация"},
    {"text": "Знание — сила", "author": "Фрэнсис Бэкон", "topic": "Образование"},
    {"text": "Тот, кто не может изменить своих мыслей, не может ничего изменить", "author": "Джордж Бернард Шоу", "topic": "Философия"},
]


class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        # Данные
        self.quotes = []  # Все доступные цитаты
        self.history = []  # История сгенерированных цитат
        self.current_filter_author = None
        self.current_filter_topic = None

        self.load_data()
        self.setup_ui()
        self.update_quote_list()

    # ---------- Работа с JSON ----------
    def load_data(self):
        """Загрузка цитат и истории из JSON"""
        # Загружаем предопределённые цитаты
        self.quotes = DEFAULT_QUOTES.copy()

        # Загружаем историю из файла
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = data.get("history", [])
                    # Загружаем добавленные пользователем цитаты
                    user_quotes = data.get("user_quotes", [])
                    self.quotes.extend(user_quotes)
            except (json.JSONDecodeError, IOError):
                messagebox.showerror("Ошибка", "Не удалось загрузить файл истории")
                self.history = []

    def save_data(self):
        """Сохранение истории и пользовательских цитат в JSON"""
        # Определяем, какие цитаты добавил пользователь
        default_texts = [q["text"] for q in DEFAULT_QUOTES]
        user_quotes = [q for q in self.quotes if q["text"] not in default_texts]

        data = {
            "history": self.history,
            "user_quotes": user_quotes
        }
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    # ---------- UI ----------
    def setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель: генерация цитаты
        top_frame = ttk.LabelFrame(main_frame, text="🎲 Генератор цитат", padding=10)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        self.generate_btn = ttk.Button(top_frame, text="✨ Сгенерировать случайную цитату",
                                        command=self.generate_quote, width=30)
        self.generate_btn.pack(pady=5)

        # Отображение текущей цитаты
        quote_frame = ttk.Frame(top_frame)
        quote_frame.pack(fill=tk.X, pady=10)

        self.quote_text = tk.Text(quote_frame, height=6, wrap=tk.WORD, font=("Arial", 11, "italic"),
                                   state=tk.DISABLED)
        self.quote_text.pack(fill=tk.BOTH, expand=True)

        # Средняя панель: фильтрация и добавление цитат
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.X, pady=(0, 10))

        # Фильтрация
        filter_frame = ttk.LabelFrame(middle_frame, text="🔍 Фильтрация", padding=10)
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Label(filter_frame, text="Фильтр по автору:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.author_filter_var = tk.StringVar()
        self.author_filter_combo = ttk.Combobox(filter_frame, textvariable=self.author_filter_var,
                                                 values=["Все авторы"], state="readonly", width=25)
        self.author_filter_combo.grid(row=0, column=1, padx=5, pady=5)
        self.author_filter_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        ttk.Label(filter_frame, text="Фильтр по теме:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.topic_filter_var = tk.StringVar()
        self.topic_filter_combo = ttk.Combobox(filter_frame, textvariable=self.topic_filter_var,
                                                values=["Все темы"], state="readonly", width=25)
        self.topic_filter_combo.grid(row=1, column=1, padx=5, pady=5)
        self.topic_filter_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        clear_filter_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Добавление новой цитаты
        add_frame = ttk.LabelFrame(middle_frame, text="➕ Добавить новую цитату", padding=10)
        add_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        ttk.Label(add_frame, text="Текст цитаты:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.new_text_entry = ttk.Entry(add_frame, width=40)
        self.new_text_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.new_author_entry = ttk.Entry(add_frame, width=40)
        self.new_author_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.new_topic_entry = ttk.Entry(add_frame, width=40)
        self.new_topic_entry.grid(row=2, column=1, padx=5, pady=5)

        add_quote_btn = ttk.Button(add_frame, text="📝 Добавить цитату", command=self.add_quote)
        add_quote_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Нижняя панель: история цитат
        history_frame = ttk.LabelFrame(main_frame, text="📜 История сгенерированных цитат", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True)

        # Список истории с прокруткой
        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                           font=("Arial", 10), height=10)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        self.history_listbox.bind("<<ListboxSelect>>", self.on_history_select)

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.clear_history_btn = ttk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history)
        self.clear_history_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(btn_frame, text="💾 Экспорт истории", command=self.export_history)
        self.export_btn.pack(side=tk.LEFT, padx=5)

    def update_quote_list(self):
        """Обновление списка отображаемых цитат для фильтрации"""
        # Обновляем выпадающие списки фильтров
        all_authors = sorted(set([q["author"] for q in self.quotes]))
        all_topics = sorted(set([q["topic"] for q in self.quotes]))

        self.author_filter_combo["values"] = ["Все авторы"] + all_authors
        self.topic_filter_combo["values"] = ["Все темы"] + all_topics

    def get_filtered_quotes(self):
        """Возвращает цитаты с учётом текущих фильтров"""
        filtered = self.quotes.copy()

        if self.current_filter_author and self.current_filter_author != "Все авторы":
            filtered = [q for q in filtered if q["author"] == self.current_filter_author]

        if self.current_filter_topic and self.current_filter_topic != "Все темы":
            filtered = [q for q in filtered if q["topic"] == self.current_filter_topic]

        return filtered

    def generate_quote(self):
        """Генерация случайной цитаты из отфильтрованного списка"""
        filtered_quotes = self.get_filtered_quotes()

        if not filtered_quotes:
            messagebox.showwarning("Нет цитат", "Нет цитат, соответствующих выбранным фильтрам!")
            return

        # Выбираем случайную цитату
        selected_quote = random.choice(filtered_quotes)

        # Добавляем в историю с временной меткой
        quote_entry = {
            "text": selected_quote["text"],
            "author": selected_quote["author"],
            "topic": selected_quote["topic"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.insert(0, quote_entry)  # Добавляем в начало списка
        self.save_data()
        self.update_history_display()

        # Отображаем цитату в верхнем поле
        self.display_quote(selected_quote)

        messagebox.showinfo("Успех", "Цитата сгенерирована и добавлена в историю!")

    def display_quote(self, quote):
        """Отображение выбранной цитаты"""
        self.quote_text.config(state=tk.NORMAL)
        self.quote_text.delete("1.0", tk.END)

        display_text = f'"{quote["text"]}"\n\n'
        display_text += f"— {quote["author"]}\n"
        display_text += f"📌 Тема: {quote["topic"]}"

        self.quote_text.insert("1.0", display_text)
        self.quote_text.config(state=tk.DISABLED)

    def update_history_display(self):
        """Обновление отображения истории"""
        self.history_listbox.delete(0, tk.END)

        for entry in self.history:
            display = f"[{entry['generated_at']}] {entry['author']}: {entry['text'][:50]}..."
            self.history_listbox.insert(tk.END, display)

    def on_history_select(self, event):
        """Показ выбранной цитаты из истории"""
        selection = self.history_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < len(self.history):
            quote = self.history[idx]
            self.display_quote(quote)

    def add_quote(self):
        """Добавление новой цитаты пользователем с валидацией"""
        text = self.new_text_entry.get().strip()
        author = self.new_author_entry.get().strip()
        topic = self.new_topic_entry.get().strip()

        # Валидация
        if not text:
            messagebox.showwarning("Ошибка ввода", "Текст цитаты не может быть пустым!")
            return
        if not author:
            messagebox.showwarning("Ошибка ввода", "Имя автора не может быть пустым!")
            return
        if not topic:
            messagebox.showwarning("Ошибка ввода", "Тема не может быть пустой!")
            return

        # Проверка на дубликат
        for q in self.quotes:
            if q["text"].lower() == text.lower():
                messagebox.showwarning("Ошибка", "Такая цитата уже существует!")
                return

        # Добавляем новую цитату
        new_quote = {
            "text": text,
            "author": author,
            "topic": topic
        }
        self.quotes.append(new_quote)
        self.save_data()
        self.update_quote_list()

        # Очищаем поля
        self.new_text_entry.delete(0, tk.END)
        self.new_author_entry.delete(0, tk.END)
        self.new_topic_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", "Цитата успешно добавлена!")

    def apply_filters(self, event=None):
        """Применение фильтров"""
        self.current_filter_author = self.author_filter_var.get()
        self.current_filter_topic = self.topic_filter_var.get()

    def clear_filters(self):
        """Сброс всех фильтров"""
        self.current_filter_author = None
        self.current_filter_topic = None
        self.author_filter_var.set("Все авторы")
        self.topic_filter_var.set("Все темы")
        messagebox.showinfo("Фильтры", "Фильтры сброшены")

    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_data()
            self.update_history_display()
            messagebox.showinfo("История", "История очищена")

    def export_history(self):
        """Экспорт истории в JSON файл"""
        if not self.history:
            messagebox.showwarning("Экспорт", "Нет истории для экспорта")
            return

        export_file = f"quotes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Экспорт", f"История экспортирована в файл:\n{export_file}")
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {e}")


# ---------- ТЕСТЫ ----------
import unittest
import tempfile
import sys


class TestQuoteGenerator(unittest.TestCase):
    def setUp(self):
        """Подготовка к тестам"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()

        global DATA_FILE
        self.original_data_file = DATA_FILE
        globals()['DATA_FILE'] = self.temp_file.name

        self.root = tk.Tk()
        self.app = QuoteGenerator(self.root)

    def tearDown(self):
        """Очистка после тестов"""
        self.root.destroy()
        globals()['DATA_FILE'] = self.original_data_file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    # Позитивные тесты
    def test_generate_quote_valid(self):
        """Тест генерации цитаты при наличии цитат"""
        before_count = len(self.app.history)
        self.app.generate_quote()
        self.assertEqual(len(self.app.history), before_count + 1)

    def test_add_quote_valid(self):
        """Тест добавления корректной цитаты"""
        before_count = len(self.app.quotes)
        self.app.new_text_entry.insert(0, "Тестовая цитата")
        self.app.new_author_entry.insert(0, "Тестовый автор")
        self.app.new_topic_entry.insert(0, "Тестовая тема")
        self.app.add_quote()
        self.assertEqual(len(self.app.quotes), before_count + 1)

    # Негативные тесты
    def test_add_quote_empty_text(self):
        """Тест добавления цитаты с пустым текстом"""
        before_count = len(self.app.quotes)
        self.app.new_text_entry.insert(0, "")
        self.app.new_author_entry.insert(0, "Автор")
        self.app.new_topic_entry.insert(0, "Тема")
        self.app.add_quote()
        self.assertEqual(len(self.app.quotes), before_count)

    def test_add_quote_empty_author(self):
        """Тест добавления цитаты с пустым автором"""
        before_count = len(self.app.quotes)
        self.app.new_text_entry.insert(0, "Текст")
        self.app.new_author_entry.insert(0, "")
        self.app.new_topic_entry.insert(0, "Тема")
        self.app.add_quote()
        self.assertEqual(len(self.app.quotes), before_count)

    def test_add_quote_empty_topic(self):
        """Тест добавления цитаты с пустой темой"""
        before_count = len(self.app.quotes)
        self.app.new_text_entry.insert(0, "Текст")
        self.app.new_author_entry.insert(0, "Автор")
        self.app.new_topic_entry.insert(0, "")
        self.app.add_quote()
        self.assertEqual(len(self.app.quotes), before_count)

    def test_add_duplicate_quote(self):
        """Тест добавления дубликата цитаты"""
        self.app.new_text_entry.insert(0, "Я мыслю, следовательно, существую")
        self.app.new_author_entry.insert(0, "Рене Декарт")
        self.app.new_topic_entry.insert(0, "Философия")
        before_count = len(self.app.quotes)
        self.app.add_quote()
        self.assertEqual(len(self.app.quotes), before_count)

    # Граничные тесты
    def test_filter_by_author(self):
        """Тест фильтрации по автору"""
        self.app.current_filter_author = "Махатма Ганди"
        filtered = self.app.get_filtered_quotes()
        for quote in filtered:
            self.assertEqual(quote["author"], "Махатма Ганди")

    def test_filter_by_topic(self):
        """Тест фильтрации по теме"""
        self.app.current_filter_topic = "Мотивация"
        filtered = self.app.get_filtered_quotes()
        for quote in filtered:
            self.assertEqual(quote["topic"], "Мотивация")

    def test_clear_history(self):
        """Тест очистки истории"""
        self.app.history = [{"text": "test", "author": "test", "topic": "test", "generated_at": "now"}]
        self.app.clear_history()
        self.assertEqual(len(self.app.history), 0)

    def test_generate_with_empty_filter(self):
        """Тест генерации с фильтром, не дающим результатов"""
        self.app.current_filter_author = "Несуществующий автор"
        # Должен показать предупреждение, но не упасть
        self.app.generate_quote()  # Не должно вызвать ошибку


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.argv.pop(1)
        unittest.main()
    else:
        root = tk.Tk()
        app = QuoteGenerator(root)
        root.mainloop()