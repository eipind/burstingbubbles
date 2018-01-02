from tkinter import *
from tkinter.messagebox import showerror
import datacollection.reddit.settings as rs

class Inputer:

    def _validate(self):
        query = {}

        for entry in self._entries:
            field = str(entry[0])
            text = str(entry[1].get()).strip()
            if text == '' or text == '':
                showerror("Error!", "Please fill in the fields.")
                return False
            elif field == 'Query:' and len(text) >= 512:
                showerror("Error!", "Query must be less than 512 characters.")
                return False
            elif field == 'Limit:':
                if not text.isdigit():
                    showerror("Error!", "Limit must be a digit.")
                    return False
                if int(text) > 100 or int(text) < 5:
                    showerror("Error!", "Limit must be between 5 and 100.")
                    return False

            query[field] = text
        self._query = query
        return True

    def _collect(self, event=None):
        isValid = self._validate()
        if(isValid):
            self._root.destroy()

    def _quit(self, event=None):
        print("Goodbye!")
        exit(0)

    def get_query(self):
        return self._query

    def _add_to_form_textboxes(self, root, textfields):
        for field in textfields:
            row = Frame(root)
            lab = Label(row, width=10, text=field, anchor='w')
            ent = Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            self._entries.append((field, ent))

    def _add_to_form_listboxes(self, root, listboxdict):
        for key, values in listboxdict.items():
            row = Frame(root)
            lab = Label(row, width=10, text=key, anchor='w')

            var = StringVar(root)

            if key == 'Links from:':
                var.set(values[rs.SEARCH_TIME_PREFERED_INDEX])
            elif key == 'Sorted by:':
                var.set(values[rs.SEARCH_SORT_PREFERED_INDEX])
            else:
                var.set(values[0])

            ent = OptionMenu(row, var, *values)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)

            self._entries.append((key, var))

    def __init__(self):
        self._root = Tk()
        self._query = {}
        self._entries = []

        textfields = "Query:", "Subreddit:", 'Limit:'
        listboxfields = {"Sorted by:": [value.title() for value in rs.SEARCH_SORT], "Links from:": [value.title() for value in rs.SEARCH_TIME_PERIOD]}

        self._root.title("Bursting Bubbles")
        self._add_to_form_textboxes(self._root, textfields)
        self._add_to_form_listboxes(self._root, listboxfields)

        self._root.bind("<Return>", self._collect)
        b1 = Button(self._root, text="Enter", command=self._collect)
        b1.pack(side=LEFT, padx=5, pady=5)
        b2 = Button(self._root, text="Quit", command=self._quit)
        b2.pack(side=LEFT, padx=5, pady=5)

        self._root.protocol("WM_DELETE_WINDOW", self._quit)
        self._root.resizable(width=False, height=False)
        self._root.mainloop()
