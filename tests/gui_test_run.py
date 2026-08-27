import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime

from run_tests import CATEGORIES, run_tests

class TestRunnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Runner Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0d1117')

        self.setup_styles()
        self.create_widgets()
        self.refresh_list()
        self.running = False
        self.current_logs = []
        self.current_full_output = ""
        self.current_stats = None

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        colors = {
            'bg': '#0d1117',
            'bg2': '#161b22',
            'border': '#30363d',
            'text': '#c9d1d9',
            'text2': '#8b949e',
            'accent': '#58a6ff',
            'hover': '#1f6feb'
        }

        style.configure('GitHub.TButton',
                        background=colors['bg2'],
                        foreground=colors['text'],
                        borderwidth=1,
                        padding=(12, 6))
        style.map('GitHub.TButton',
                  background=[('active', colors['hover'])],
                  foreground=[('active', 'white')])

        style.configure('GitHub.TFrame',
                        background=colors['bg'])
        style.configure('GitHub.TLabelframe',
                        background=colors['bg2'],
                        foreground=colors['text'],
                        bordercolor=colors['border'])
        style.configure('GitHub.TLabelframe.Label',
                        background=colors['bg2'],
                        foreground=colors['text'])

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, style='GitHub.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        left_frame = ttk.Frame(main_frame, style='GitHub.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        list_label = tk.Label(left_frame, text="Test Categories",
                              bg='#0d1117', fg='#c9d1d9',
                              font=('Segoe UI', 12, 'bold'), anchor='w')
        list_label.pack(fill=tk.X, pady=(0, 8))

        list_container = ttk.Frame(left_frame, style='GitHub.TFrame')
        list_container.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            list_container,
            bg='#161b22',
            fg='#c9d1d9',
            selectbackground='#1f6feb',
            selectforeground='white',
            font=('Segoe UI', 10),
            borderwidth=1,
            relief='flat',
            highlightthickness=1,
            highlightcolor='#30363d'
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(left_frame, style='GitHub.TFrame')
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Run", style='GitHub.TButton',
                   command=self.run_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Add", style='GitHub.TButton',
                   command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", style='GitHub.TButton',
                   command=self.delete_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", style='GitHub.TButton',
                   command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Logs", style='GitHub.TButton',
                   command=self.show_logs).pack(side=tk.LEFT, padx=5)

        right_frame = ttk.Frame(main_frame, style='GitHub.TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        output_label = tk.Label(right_frame, text="Results",
                                bg='#0d1117', fg='#c9d1d9',
                                font=('Segoe UI', 12, 'bold'), anchor='w')
        output_label.pack(fill=tk.X, pady=(0, 8))

        self.output = scrolledtext.ScrolledText(
            right_frame,
            bg='#161b22',
            fg='#c9d1d9',
            insertbackground='#c9d1d9',
            font=('Consolas', 10),
            borderwidth=1,
            relief='flat',
            highlightthickness=1,
            highlightcolor='#30363d',
            wrap=tk.WORD
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        self.output.tag_config('info', foreground='#58a6ff')
        self.output.tag_config('success', foreground='#3fb950')
        self.output.tag_config('error', foreground='#f85149')
        self.output.tag_config('warning', foreground='#d29922')
        self.output.tag_config('stats', foreground='#c9d1d9', font=('Consolas', 11, 'bold'))

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for key in sorted(CATEGORIES.keys(), key=lambda x: int(x)):
            self.listbox.insert(tk.END, f"{key}. {CATEGORIES[key]['name']}")

    def log(self, message, tag='info'):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.output.insert(tk.END, log_entry + '\n', tag)
        self.output.see(tk.END)
        self.current_logs.append(log_entry)

    def display_stats(self, stats):
        if not stats:
            return

        self.output.insert(tk.END, "\n" + "=" * 50 + "\n", 'stats')
        self.output.insert(tk.END, "TEST RESULTS SUMMARY\n", 'stats')
        self.output.insert(tk.END, "=" * 50 + "\n", 'stats')

        if stats['total'] > 0:
            self.output.insert(tk.END, f"Total tests:  {stats['total']}\n", 'stats')
            self.output.insert(tk.END, f"Passed:       {stats['passed']}\n",
                               'success' if stats['passed'] > 0 else 'stats')
            self.output.insert(tk.END, f"Failed:       {stats['failed']}\n",
                               'error' if stats['failed'] > 0 else 'stats')
            self.output.insert(tk.END, f"Errors:       {stats['errors']}\n",
                               'error' if stats['errors'] > 0 else 'stats')
            self.output.insert(tk.END, f"Skipped:      {stats['skipped']}\n",
                               'warning' if stats['skipped'] > 0 else 'stats')
            self.output.insert(tk.END, "=" * 50 + "\n", 'stats')

            if stats['failed'] == 0 and stats['errors'] == 0:
                self.output.insert(tk.END, "STATUS: ALL TESTS PASSED\n", 'success')
            else:
                self.output.insert(tk.END, f"STATUS: {stats['failed'] + stats['errors']} TESTS FAILED\n", 'error')
        else:
            self.output.insert(tk.END, "No tests were collected\n", 'warning')

        self.output.insert(tk.END, "=" * 50 + "\n\n", 'stats')
        self.output.see(tk.END)

    def run_selected(self):
        if self.running:
            messagebox.showwarning("Warning", "Tests are already running!")
            return

        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a category first!")
            return

        selected = self.listbox.get(selection[0])
        key = selected.split('.')[0]

        if key not in CATEGORIES:
            messagebox.showerror("Error", "Category not found!")
            return

        self.running = True
        self.output.delete(1.0, tk.END)
        self.current_logs = []
        self.current_full_output = ""
        self.current_stats = None

        def run_thread():
            try:
                path = CATEGORIES[key]['path']
                self.root.after(0, lambda: self.log(f"Running tests in: {path}", 'info'))
                self.root.after(0, lambda: self.log("-" * 40, 'info'))

                result, output, stats = run_tests(path)

                self.current_full_output = output
                self.current_stats = stats
                self.root.after(0, lambda: self.display_stats(stats))

                if result == 0:
                    self.root.after(0, lambda: self.log(f"Exit code: {result}", 'success'))
                else:
                    self.root.after(0, lambda: self.log(f"Exit code: {result}", 'error'))

            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error: {str(e)}", 'error'))
            finally:
                self.root.after(0, lambda: setattr(self, 'running', False))

        threading.Thread(target=run_thread, daemon=True).start()

    def add_category(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Category")
        dialog.geometry("400x200")
        dialog.configure(bg='#0d1117')
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, style='GitHub.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Category Name:", style='GitHub.TLabelframe.Label').pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(frame, text="Path:", style='GitHub.TLabelframe.Label').pack(anchor=tk.W, pady=(0, 5))
        path_entry = ttk.Entry(frame, width=40)
        path_entry.pack(fill=tk.X, pady=(0, 20))

        btn_frame = ttk.Frame(frame, style='GitHub.TFrame')
        btn_frame.pack(fill=tk.X)

        def save():
            name = name_entry.get().strip()
            path = path_entry.get().strip()

            if not name or not path:
                messagebox.showerror("Error", "Both fields are required!")
                return

            if any(cat['name'] == name for cat in CATEGORIES.values()):
                messagebox.showerror("Error", f"Category '{name}' already exists!")
                return

            new_key = str(max(int(k) for k in CATEGORIES.keys()) + 1)
            CATEGORIES[new_key] = {"name": name, "path": path}

            dialog.destroy()
            self.refresh_list()
            messagebox.showinfo("Success", f"Category '{name}' added!")

        ttk.Button(btn_frame, text="Save", style='GitHub.TButton', command=save).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", style='GitHub.TButton', command=dialog.destroy).pack(side=tk.RIGHT)

    def delete_category(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a category to delete!")
            return

        selected = self.listbox.get(selection[0])
        key = selected.split('.')[0]

        if key not in CATEGORIES:
            messagebox.showerror("Error", "Category not found!")
            return

        category_name = CATEGORIES[key]['name']

        if category_name == "ALL TESTS":
            messagebox.showerror("Error", "Cannot delete ALL TESTS category!")
            return

        if messagebox.askyesno("Confirm", f"Delete category '{category_name}'?"):
            del CATEGORIES[key]
            self.refresh_list()
            messagebox.showinfo("Success", f"Category '{category_name}' deleted!")

    def show_logs(self):
        if not self.current_full_output and not self.current_logs:
            messagebox.showinfo("Logs", "No logs available. Run some tests first!")
            return

        log_window = tk.Toplevel(self.root)
        log_window.title("Full Test Output")
        log_window.geometry("1000x700")
        log_window.configure(bg='#0d1117')

        log_frame = ttk.Frame(log_window, style='GitHub.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        log_label = tk.Label(log_frame, text="Complete pytest Output",
                             bg='#0d1117', fg='#c9d1d9',
                             font=('Segoe UI', 12, 'bold'), anchor='w')
        log_label.pack(fill=tk.X, pady=(0, 10))

        log_text = scrolledtext.ScrolledText(
            log_frame,
            bg='#161b22',
            fg='#c9d1d9',
            insertbackground='#c9d1d9',
            font=('Consolas', 9),
            borderwidth=1,
            relief='flat',
            highlightthickness=1,
            highlightcolor='#30363d',
            wrap=tk.WORD
        )
        log_text.pack(fill=tk.BOTH, expand=True)

        if self.current_full_output:
            log_text.insert(tk.END, self.current_full_output, 'output')
        else:
            for entry in self.current_logs:
                if "Error" in entry or "failed" in entry.lower():
                    log_text.insert(tk.END, entry + '\n', 'error')
                elif "passed" in entry.lower() or "success" in entry.lower():
                    log_text.insert(tk.END, entry + '\n', 'success')
                else:
                    log_text.insert(tk.END, entry + '\n', 'info')

        log_text.tag_config('info', foreground='#58a6ff')
        log_text.tag_config('success', foreground='#3fb950')
        log_text.tag_config('error', foreground='#f85149')
        log_text.tag_config('output', foreground='#c9d1d9')

        log_text.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(log_frame, style='GitHub.TFrame')
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        btn_close = ttk.Button(btn_frame, text="Close", style='GitHub.TButton',
                               command=log_window.destroy)
        btn_close.pack(side=tk.RIGHT)

if __name__ == "__main__":
    root = tk.Tk()
    app = TestRunnerGUI(root)
    root.mainloop()