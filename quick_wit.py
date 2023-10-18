import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import hashlib

class PDFSpeedReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Speed Reader")

        # Convert PNG icon to ICO format
        icon_image = Image.open("assets/quick_wit_icon.png")
        self.icon = ImageTk.PhotoImage(icon_image)
        self.root.iconphoto(True, self.icon)


        self.current_page_index = 0
        self.current_book = ""
        self.pdf_path = ""
        self.words = []
        self.pages = []
        self.word_index = 0
        self.history = {}
        self.libratanian = Librarian()
        self.books_history = BooksHistory()

        self.speed = 1100  # Default speed: Words per minute
        self.paused = False

        # Style for themed widgets
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat")
        self.style.map("TButton", background=[('active', '!disabled', 'lightblue')])

        # Text display label
        self.text_label = tk.Label(root, text="", font=("Helvetica", 24))
        self.text_label.pack(padx=20, pady=20)

        # Load PDF button
        self.load_pdf_button = ttk.Button(root, text="Load PDF", command=self.load_pdf)
        self.load_pdf_button.pack(pady=10)

        self.book_name = ttk.Entry(root, text="Book Name:")
        self.book_name.pack(pady=10)
        self.book_name.insert(0, "Book Name")

        # Start button to begin reading
        self.start_button = ttk.Button(root, text="Start reading", command=self.start_reading)
        self.start_button.pack(pady=10)

        # Stop button to pause reading
        self.stop_button = ttk.Button(root, text="Pause", command=self.stop_reading)
        self.stop_button.pack(pady=10)
        self.stop_button.config(state=tk.DISABLED)

        # Resume button to resume reading after stopping
        self.resume_button = ttk.Button(root, text="Continue", command=self.resume_reading)
        self.resume_button.pack(pady=10)
        self.resume_button.config(state=tk.DISABLED)

        # Previous button to go back reading after stopping
        self.previous_button = ttk.Button(root, text="Previous word", command=self.previous_reading)
        self.previous_button.pack(pady=10)
        self.previous_button.config(state=tk.DISABLED)

        # Next button to go next reading after stopping
        self.next_button = ttk.Button(root, text="Next word", command=self.next_reading)
        self.next_button.pack(pady=10)
        self.next_button.config(state=tk.DISABLED)

        # Speed control (WPM)
        self.speed_label = ttk.Label(root, text="Speed (WPM):")
        self.speed_label.pack()

        # Label to display the current WPM value
        self.wpm_label = ttk.Label(root, text=f"{self.speed} WPM")
        self.wpm_label.pack()

        self.speed_scale = ttk.Scale(root, from_=100, to=3000, orient=tk.HORIZONTAL, length=300, command=self.update_speed)
        self.speed_scale.set(self.speed)
        self.speed_scale.pack()

    def load_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.pdf_path:
            self.pages = self.libratanian.get_book(self.pdf_path)
        self.history.update(self.books_history.load())
        self.current_page_index, self.word_index = self.history.get(self.pdf_path, (0, 0))

    def save_progress(self):
        self.history[self.pdf_path] = (self.current_page_index, self.word_index)
        self.books_history.save(self.history)

    def stop_reading(self):
        """Pause the reading process."""
        self.save_progress()
        self.paused = True
        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
        self.previous_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)

    def resume_reading(self):
        """Resume the reading process."""
        self.paused = False
        self.resume_button.config(state=tk.DISABLED)
        self.start_reading()

    def previous_reading(self):
        """Resume the reading process."""
        self.paused = True
        self.previous_button.config(state=tk.NORMAL)
        word = self.words[self.word_index]
        self.text_label.config(text=word)
        self.word_index -= 1

        # Ensure non-zero speed
        delay = 60.0 / (self.speed + 1e-6)

        # Update the GUI
        self.root.update()

    def next_reading(self):
        """Resume the reading process."""
        self.paused = True
        self.next_button.config(state=tk.NORMAL)
        word = self.words[self.word_index]
        self.text_label.config(text=word)
        self.word_index += 1

        # Ensure non-zero speed
        delay = 60.0 / (self.speed + 1e-6)

        # Update the GUI
        self.root.update()

    def previous_page(self):
        """Resume the reading process."""
        self.paused = True
        self.previous_page.config(state=tk.NORMAL)
        word = self.words[self.word_index]
        self.text_label.config(text=word)
        self.word_index -= 1

        # Ensure non-zero speed
        delay = 60.0 / (self.speed + 1e-6)

        # Update the GUI
        self.root.update()

    def next_page(self):
        """Resume the reading process."""
        self.paused = True
        self.next_page.config(state=tk.NORMAL)
        word = self.words[self.word_index]
        self.text_label.config(text=word)
        self.word_index += 1

        # Ensure non-zero speed
        delay = 60.0 / (self.speed + 1e-6)

        # Update the GUI
        self.root.update()

    def get_words(self):
        return self.pages[self.current_page_index]

    def start_reading(self):
        """Start the reading process."""
        if not self.pdf_path:
            messagebox.showerror("Error", "Please load a PDF first.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.load_pdf_button.config(state=tk.DISABLED)
        self.speed_scale.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)  # Enable Stop button
        self.resume_button.config(state=tk.DISABLED)  # Disable Resume button

        # Ensure non-zero speed
        delay = 60.0 / (self.speed + 1e-6)



        self.words = self.get_words()
        while self.word_index < len(self.words) and not self.paused:
            word = self.words[self.word_index]
            self.text_label.config(text=word)

            self.word_index += 1

            # Ensure non-zero speed
            delay = 60.0 / (self.speed + 1e-6)

            # Update the GUI
            self.root.update()

            if self.word_index == len(self.words) - 1:
                self.word_index = 0
                self.current_page_index += 1
                self.words = self.get_words()
                continue

            if self.current_page_index == len(self.pages) - 1:
                delay *= 3  # Display the last word for a longer time

            self.save_progress()
            time.sleep(delay)

        if self.word_index == len(self.words):
            self.text_label.config(text="Reading Complete")

        self.start_button.config(state=tk.NORMAL)
        self.load_pdf_button.config(state=tk.NORMAL)
        self.speed_scale.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)  # Disable Stop button
        self.resume_button.config(state=tk.NORMAL)  # Enable Resume button

    def update_speed(self, value):
        """Update the reading speed (WPM) and display the current WPM value."""
        self.speed = int(float(value))
        self.wpm_label.config(text=f"{self.speed} WPM")


class Librarian:

    def _get_hash_for_book(self, book):
        return hashlib.md5(book.encode()).hexdigest()

    def load_rsvp_book(self, book_name):
        with open(f"./books/{book_name}", "r", encoding="utf-8") as f:
            return eval(f.readlines())

    def _load_book(self, pdf_path):
        self.open_archive()
        book = self.books_archive.get(pdf_path)
        if book:
            doc = self.load_rsvp_book(book)
            return doc["content"]
        doc = fitz.open(pdf_path)
        pages = self._get_clear_pages(doc)
        self.save_rsvp_book(pdf_path, pages)
        return pages

    def _get_clear_words(self, text):
        while ".." in text:
            text = text.replace("..", ".")
        symbols = ".,!?:;"
        clean_words = []
        clean_word = ""
        for word in text.split():
            for char in word:
                if char.isalpha() or char.isdigit():
                    clean_word += char
                elif char in symbols:
                    clean_words.append("".join(clean_word))
                    clean_word = char
            clean_words.append("".join(clean_word))
            clean_word = ""

        return clean_words

    def _get_clear_pages(self, doc):
        """Extract text from a PDF file using PyMuPDF."""
        pages = []
        for page in doc:
            text = ""
            text += page.get_text()
            new_words = self._get_clear_words(text)
            if new_words:
                pages.append(new_words)
        return pages

    def open_archive(self):
        with open("library.json", "r", encoding="utf-8") as f:
            self.books_archive = json.load(f)

    def update_archive(self):
        with open("library.json", "w", encoding="utf-8") as f:
            json.dump(self.books_archive, f, indent=4)

    def get_book(self, path):
        return self._load_book(path)

    def save_rsvp_book(self, path, pages):
        book_name = f"{self._get_hash_for_book(path)}.rsvp"
        book = {
            "info": {
                "name": book_name,
                "pages": len(pages)
            },
            "content": pages
        }
        with open(f"./books/{book_name}", "w", encoding="utf-8") as f:
            f.writelines(book)
        self.books_archive[path] = book_name
        self.update_archive()


class BooksHistory:

    def _load_history(self):
        with open("history.json", "r", encoding="utf-8") as f:
            new_data = json.load(f)
        return new_data

    def _save_history(self, history):
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)

    def save(self, dict):
        self._save_history(dict)

    def load(self):
        return self._load_history()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSpeedReaderApp(root)
    root.mainloop()
