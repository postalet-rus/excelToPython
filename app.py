import tkinter as tk
from db_worker import DBWorker
from excel_engine import ExcelReader
from tkinter import ttk


class MainApplication(tk.Frame):
	columns = ("#1","#2", "#3", "#4", "#5")
	tree = None

	@staticmethod
	def fixed_map(style, option):
		# Fix for setting text colour for Tkinter 8.6.9
		# From: https://core.tcl.tk/tk/info/509cafafae
		#
		# Returns the style map for 'option' with any styles starting with
		# ('!disabled', '!selected', ...) filtered out.

		# style.map() returns an empty list for missing options, so this
		# should be future-safe.
		return [elm for elm in style.map('Treeview', query_opt=option) if
			elm[:2] != ('!disabled', '!selected')]

	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.excel_book = ExcelReader("C:/Users/Postalet/Desktop/zhurnal_aktivnosti.xlsx")
		self.dbworker = DBWorker("tmp.db")
		self.initUI()
		self.load_data_to_table()

		style = ttk.Style()
		style.map('Treeview', foreground=self.fixed_map(style, 'foreground'),
  			background=self.fixed_map(style, 'background'))
		style.configure("Treeview.Heading", font=(None, 8))

	def initUI(self):
		self.parent.title("Нейронная сеть")
		cols = ('IP адрес', 'Количество символов в минуту',
				'Число запросов на сервер за 1 мин', 'Число запросов на сервер за 5 мин',
				'Число неудачных попыток входа в систему за 5 мин')
		self.list_box = ttk.Treeview(self.parent, columns=cols, show="headings")
		for col in cols:
			self.list_box.heading(col, text=col)
			self.list_box.column(col, minwidth=100, width=round(self.parent.winfo_screenwidth()/len(cols)), stretch=tk.NO)
		
		self.list_box.place(relx=0.5, rely=0.9, anchor = tk.S)

	def load_data_to_table(self):
		data = self.dbworker.filter(table_name="activity_journal")
		self.clear_table_data()
		counter = 0
		for (pk, ip, spm, rpm, rp5m, ua) in data:
			counter = counter + 1
			if(rpm > 5):
				self.list_box.insert("", "end", values=(ip,spm,rpm,rp5m,ua), tag="oddrow")
			else:	
				self.list_box.insert("", "end", values=(ip,spm,rpm,rp5m,ua))
			self.list_box.tag_configure ("oddrow", background = "#B61C26")
		self.list_box.config(height=round(self.parent.winfo_screenheight() * 0.03))
		
		
	def clear_table_data(self):
		for i in self.list_box.get_children():
			self.list_box.delete(i)

	@staticmethod
	def get_style(value):
		if value:
			return "red.TLabel"

def main():
	root = tk.Tk()
	root.state('zoomed')
	app = MainApplication(root)
	root.mainloop()

if __name__ == "__main__":
	main()
	