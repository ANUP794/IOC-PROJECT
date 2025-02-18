import PyPDF2
import pyttsx3
from tkinter import Tk, filedialog, messagebox, Button, Label, Frame, StringVar, Entry, OptionMenu
from tkinter import ttk
import threading

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Global variables
is_paused = False
remaining_text = ""
speech_thread = None
selected_pages = []

def pdf_to_text(file_path, start_page, end_page):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        total_pages = len(reader.pages)
        
        # Ensure valid range
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            messagebox.showerror("Error", "Invalid page range selected.")
            return ""
        
        for i in range(start_page - 1, end_page):  # Convert to zero-based index
            text += reader.pages[i].extract_text() or ""
            update_progress((i - (start_page - 1) + 1) / (end_page - start_page + 1) * 100)
        
        return text

def text_to_speech(text, speed, voice_type):
    global is_paused, remaining_text
    engine.setProperty('rate', speed)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id if voice_type == "Male" else voices[1].id)
    
    sentences = text.split(". ")
    for i, sentence in enumerate(sentences):
        if is_paused:
            remaining_text = ". ".join(sentences[i:])
            break
        engine.say(sentence)
        engine.runAndWait()
    
    if not is_paused:
        remaining_text = ""
        messagebox.showinfo("Success", "PDF has been converted to speech!")

def update_progress(value):
    progress['value'] = value
    root.update_idletasks()

def start_conversion():
    global is_paused, remaining_text, speech_thread
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    if file_path:
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
            
            try:
                start_page = int(start_page_entry.get())
                end_page = int(end_page_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Enter valid page numbers.")
                return
            
            convert_button.config(state="disabled")
            pause_button.config(state="normal", text="Pause")
            progress['value'] = 0
            
            speed = int(speed_var.get())
            voice_type = voice_var.get()
            
            def convert():
                global is_paused, remaining_text
                try:
                    text = pdf_to_text(file_path, start_page, end_page)
                    if text.strip():
                        if remaining_text:
                            text = remaining_text
                        text_to_speech(text, speed, voice_type)
                    else:
                        messagebox.showerror("Error", "The selected PDF pages do not contain any text.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    convert_button.config(state="normal")
                    pause_button.config(state="disabled", text="Pause")
                    is_paused = False
            
            speech_thread = threading.Thread(target=convert)
            speech_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            convert_button.config(state="normal")

def toggle_pause():
    global is_paused, speech_thread
    if is_paused:
        is_paused = False
        pause_button.config(text="Pause")
        if remaining_text:
            speech_thread = threading.Thread(target=lambda: text_to_speech(remaining_text, int(speed_var.get()), voice_var.get()))
            speech_thread.start()
    else:
        is_paused = True
        pause_button.config(text="Resume")
        engine.stop()

# GUI setup
root = Tk()
root.title("Anup VOC IT Converter")
root.geometry("600x350")

options_frame = Frame(root)
options_frame.pack(pady=10)

Label(options_frame, text="Start Page:").grid(row=0, column=0, padx=5, pady=5)
start_page_entry = Entry(options_frame, width=5)
start_page_entry.grid(row=0, column=1, padx=5, pady=5)
start_page_entry.insert(0, "1")

Label(options_frame, text="End Page:").grid(row=0, column=2, padx=5, pady=5)
end_page_entry = Entry(options_frame, width=5)
end_page_entry.grid(row=0, column=3, padx=5, pady=5)
end_page_entry.insert(0, "1")

Label(options_frame, text="Speech Speed:").grid(row=1, column=0, padx=5, pady=5)
speed_var = StringVar(value="150")
speed_menu = OptionMenu(options_frame, speed_var, "75", "100", "150", "200", "250")
speed_menu.grid(row=1, column=1, padx=5, pady=5)

Label(options_frame, text="Voice Type:").grid(row=2, column=0, padx=5, pady=5)
voice_var = StringVar(value="Male")
voice_menu = OptionMenu(options_frame, voice_var, "Male", "Female")
voice_menu.grid(row=2, column=1, padx=5, pady=5)

style = ttk.Style()
style.theme_use('default')
style.configure("colored.Horizontal.TProgressbar", background='red')

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", style="colored.Horizontal.TProgressbar")
progress.pack(pady=20)

convert_button = Button(root, text="Convert PDF to Speech", command=start_conversion)
convert_button.pack(pady=10)

pause_button = Button(root, text="Pause", state="disabled", command=toggle_pause)
pause_button.pack(pady=10)

root.mainloop()
