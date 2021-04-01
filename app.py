import tkinter as tk
from typing import Text
from db_worker import DBWorker
from excel_engine import ExcelReader
from tkinter import ttk


class MainApplication(tk.Frame):
	columns = ("#1","#2", "#3", "#4", "#5")
	tree = None
	weights = []
	teta = 0.8

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
	
	def validate(self, value):
		if value.strip() == "":
			return True
		elif value:
			try:
				float_val = float(value)
				
				if float_val * 100 >= 0 and float_val * 100 <= 100 and len(value[0:-2]) <= 2:
					return True
				else:
					return False
			except ValueError:
				return False
		else:
			return False

	def handle_click(self, event):
		if self.list_box.identify_region(event.x, event.y) == "separator":
			return "break"

	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.excel_book = ExcelReader("./zhurnal_aktivnosti.xlsx")
		self.dbworker = DBWorker("tmp.db")
		self.initUI()
		self.load_data_to_table()

		style = ttk.Style()
		style.map('Treeview', foreground=self.fixed_map(style, 'foreground'),
  			background=self.fixed_map(style, 'background'), rowheight=self.fixed_map(style, 'rowheight'))
		style.configure("Treeview.Heading", padding=25)
		style.configure("Treeview.Heading", font=(None, 8))

	def initUI(self):
		col_width = round(self.parent.winfo_screenwidth()/5)
		col_center = round(col_width / 2)
		
		# set refresh button
		refresh_button = tk.Button(self.parent, text="Обновить", command=self.update_table_data)
		refresh_button.place(x=col_width - col_center - 45, y=15, width = 90)
		# set up validation
		vcmd = self.parent.register(self.validate)
		
		# set weight fields
		for i in range(1, 5):
			label = tk.Label(self.parent, text=f"w{i}")
			label.place(x=col_width * (i+1) - col_center - 10, y=0, width = 20, height=20)
			w = tk.Entry(self.parent, validate = 'key', validatecommand = (vcmd, '%P'))
			w.place(x=col_width * (i+1) - col_center - 15, y=25, width = 30)
			self.weights.append(w)	

		# set table and headings
		self.parent.title("Нейронная сеть")
		cols = ('IP адрес', 'Количество символов в минуту',
				'Число запросов на сервер за 1 мин', 'Число запросов на сервер за 5 мин',
				'Число неудачных попыток\n входа в систему за 5 мин')
		self.list_box = ttk.Treeview(self.parent, columns=cols, show="headings", style="Treeview")
		for col in cols:
			self.list_box.heading(col, text=col)
			self.list_box.column(col, minwidth=100, width=round(self.parent.winfo_screenwidth()/len(cols)), stretch=tk.NO)
		
		self.list_box.place(x=0, y=50)
		self.list_box.bind("<Button-1>", self.handle_click)

		# set visuals for suspicious and safe entries
		self.list_box.tag_configure("sus", background = "#BF5959", foreground = "#ffffff")
		self.list_box.tag_configure ("safe", background = "#15CE46", foreground = "#ffffff")

	def load_data_to_table(self):
		self.data = self.dbworker.filter(table_name="activity_journal")
		counter = 0
		for (pk, ip, spm, rpm, rp5m, ua) in self.data:
			counter = counter + 1
			self.list_box.insert("", "end", values=(ip,spm,rpm,rp5m,ua))
		self.list_box.config(height=round(counter * 15))
		
		
	def clear_table_data(self):
		for i in self.list_box.get_children():
			self.list_box.delete(i)
	
	def update_table_data(self):
		self.clear_table_data()
		if self.data:
			counter = 0
			for (pk, ip, spm, rpm, rp5m, ua) in self.data:
				counter = counter + 1
				result = 0
				if(spm > 300):
					result += float(self.weights[0].get() or 0) * 1
				if(rpm > 10):
					result += float(self.weights[1].get() or 0) * 1
				if(rp5m > 60):
					result += float(self.weights[2].get() or 0) * 1
				if(ua > 10):
					result += float(self.weights[3].get() or 0) * 1

				if result >= self.teta:
					self.list_box.insert("", "end", values=(ip,spm,rpm,rp5m,ua), tag="sus")
				else:
					self.list_box.insert("", "end", values=(ip,spm,rpm,rp5m,ua), tag="safe")
					
		else:
			print("\033[91mData list is not exists\033[0m")


def main():
	root = tk.Tk()
	root.state('zoomed')
	app = MainApplication(root)
	root.mainloop()

if __name__ == "__main__":
	main()
	