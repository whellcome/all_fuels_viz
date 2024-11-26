"""
The module contains classes designed for constructing and comparing charts
of exchange prices for various types of fuel and natural gas.
The dataset contains data from August 2000 to the end of the last month.
dataset project: https://www.kaggle.com/datasets/guillemservera/fuels-futures-data
"""
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import filedialog, messagebox


class GetWigetsFrame(tk.Frame):
    """
    The main class of the program is responsible for constructing the form and interaction of elements
    """

    def __init__(self, render_params=None, *args, **options):
        """
        Initialization of the Frame, description of the main elements
        :param render_params: General parameters for the arrangement of elements can be set externally
        :param args:
        :param options:
        """
        super().__init__(*args, **options)
        if render_params is None:
            render_params = {}
        self.__render_params = render_params if render_params else dict(sticky="ew", padx=5, pady=2)

        self.df = pd.DataFrame()
        self.fnamevar = tk.StringVar(self, "")
        self.plot_data_types = []

        self.label1 = tk.Label(self, text="", font=("Helvetica", 12))
        self.frame1 = ttk.Frame(self, width=100, borderwidth=1, relief="solid", padding=(2, 2)) # canvas parameters
        self.frame2 = ttk.Frame(self, width=220) # plot_1 parameters
        self.frame3 = ttk.Frame(self, width=220) # plot_2 parameters
        self.frame4 = ttk.Frame(self.frame2, width=110) # plot_1 checkboxes
        self.frame5 = ttk.Frame(self.frame3, width=110) # plot_2 checkboxes

        self.date_start_1 = self.new_date(self.frame2)
        self.date_end_1 = self.new_date(self.frame2)
        self.date_start_2 = self.new_date(self.frame3)
        self.date_end_2 = self.new_date(self.frame3)

        # columns to plot in the one area
        self.check_cols1 = dict.fromkeys(["open", "high", "low", "close", "volume"])
        self.check_cols2 = dict.fromkeys(["open", "high", "low", "close", "volume"])

        self.plot = PlotFrame(self, (8, 10))

        self.set_canvas_conf()
        self.create_widgets()

    def get_plot_columns(self, check_cols, plot):
        cols = ["date"]
        for x in check_cols.keys():
            if check_cols[x].get():
                cols.append(x)
        if len(cols) == 1:
            messagebox.showwarning(f"{plot}. No data to plot!", "Select at least one plotting data checkbox!")
            return False
        return cols

    def btn_show(self):
        """
        Implementation of the "Show" button click event
        Based on the form data, a dataframe is generated for plotting and sent for drawing.
        In the case when the comparison mode is selected, a list with two dataframes is sent
        """
        fname = self.fnamevar.get()
        if not fname:
            return None
        cols = self.get_plot_columns(self.check_cols1, "Plot 1")
        if not cols:
            return None

        self.plot.clearplot()
        df_graf = self.df[(self.df.date <= self.date_end_1.get_date()) &
                          (self.df.date >= self.date_start_1.get_date()) &
                          (self.df.commodity == self.combobox_plot_data.get())]

        df_graf = df_graf[cols].set_index("date")

        if self.combobox_canv_param.get() == "1x1 (1 plot)":
            self.plot.plot_graf(df_graf, self.combobox_plot_data.get())
        else:  # the comparison mode is selected
            df_graf2 = self.df[(self.df.date <= self.date_end_2.get_date()) &
                               (self.df.date >= self.date_start_2.get_date()) &
                               (self.df.commodity == self.combobox_plot_data2.get())]
            cols = self.get_plot_columns(self.check_cols2, "Plot 2")
            if not cols:
                return None
            df_graf2 = df_graf2[cols].set_index("date")

            titles = [self.combobox_plot_data.get(), self.combobox_plot_data2.get()]
            self.plot.plot_graf([df_graf, df_graf2], titles)

    def btn_clear(self):
        """Implementation of the "Clear" button click event"""
        self.plot.clearplot()

    def btn_openf(self):
        """
        Implementation of the "File Open" button click event
        After selecting a file, the data is loaded and cleared.
        If successful, the program continues and loads elements for selecting plotting options
        If unsuccessful, prompts to select another file or exit the program
        """
        fname = filedialog.askopenfilename(filetypes=[("csv files", "*.csv")])
        if fname:
            must_clean = messagebox.askquestion("Clean the file?", "Do you want to restore the data?") == "yes"
            try:
                self.df = pd.read_csv(fname, sep=";" if must_clean else ",",
                                      usecols=["ticker", "commodity", "date", "open", "high", "low", "close", "volume"])

                if must_clean:
                    self.data_cleaning()
                self.df.date = pd.to_datetime(self.df.date).dt.date
                print(1)
                self.fnamevar.set(fname)
                print(2)
                self.label1['text'] = f"File for data analysis: \"{self.fnamevar.get().split('/')[-1]}\""
                print(3)
                self.label1.update()
                print(4)
                self.recreate_plot_widgets()
            except Exception as e:
                print(e)
                if messagebox.askquestion("Can't read the file!", "Do you want to choose another file?") == "yes":
                    self.btn_openf()
                else:
                    self.quit()

    def get_dtype(self, s):
        datatypes = {"BZ=F": "Brent Crude Oil", "CL=F": "Crude Oil", "HO=F": "Heating Oil",
                     "NG=F": "Natural Gas", "RB=F": "RBOB Gasoline"}
        return datatypes[s]

    def del_dots(self, s):
        """Removing dots from a line except the first one"""
        l = s.split(".")
        if l:
            return l.pop(0) + "." + "".join(l)
        else:
            return "0"

    def normalize_value(self, s, min=15, max=150):
        """Bringing data adequately to historical data on maximum and minimum values"""

        if s < min:
            return self.normalize_value(abs(s) * 10, min, max)
        elif s > max:
            return self.normalize_value(s / 10, min, max)
        else:

            return s

    def normalize_serie(self, colname):
        df2 = pd.read_csv('all_fuels_data.csv', sep=',')
        for f in self.plot_data_types:
            filtered_obj = self.df.loc[self.df['commodity'] == f, colname]

            df2_filtered = df2.loc[df2['commodity'] == f, colname].apply(abs)

            # desc = filtered_obj.describe()
            # delta = desc["75%"] - desc["25%"]
            # min, max = desc["25%"] - 1.5 * delta, desc["75%"] + 1.5 * delta

            desc = df2_filtered.describe()
            min, max = desc["min"], desc["max"]
            print(f)
            print(desc)
            print(filtered_obj.describe())
            filtered_obj = self.df[colname].apply(self.normalize_value, args=(min, max))




    def data_cleaning(self):
        """Cleaning dataframe data and casting types to the required ones"""
        self.df.loc[self.df['date'].str.contains('.'), 'date'] = pd.to_datetime(self.df['date'], dayfirst=True)
        self.df.date = pd.to_datetime(self.df.date).dt.date

        self.df["commodity"] = self.df["ticker"].apply(self.get_dtype)

        self.df['close'] = self.df['close'].apply(self.del_dots)
        self.df['close'] = pd.to_numeric(self.df['close'], errors='coerce')
        self.df = self.df.dropna(subset=['date', 'commodity', 'close'])

        self.plot_data_types = list(self.df.commodity.unique())
        self.normalize_serie('close')

        print(self.df.close)
        # self.df.loc[self.df['commodity'] != "Natural Gas", 'close'] = self.df['close'].apply(self.normalize_value)
        #
        # self.df.loc[self.df['commodity'] == "Natural Gas", 'close'] = self.df['close'].apply(self.normalize_value,
        #                                                                                      args=(2, 10))


    def new_date(self, frame=None):
        """Creating Date Entry Fields"""
        if not frame:
            frame = self
        return DateEntry(frame, width=12, foreground='white', background='darkblue', borderwidth=2,
                         locale='de_DE', date_pattern='dd.mm.yyyy')

    def canv_param_selected(self, event):
        """
        Implementation of the "Type of figure" change event
        The plotting area is rebuilt according to the selected value
        """
        selection = self.combobox_canv_param.get()
        self.plot.canvas.get_tk_widget().pack_forget()  # remove previous
        self.plot.update_canvas(self, (8, 10), selection)
        self.plot.canvas.draw()
        self.render(self.plot.canvas.get_tk_widget(), dict(columnspan=5, row=4, column=0))
        self.render(NavigationToolbar2Tk(self.plot.canvas, self, pack_toolbar=False),
                    dict(row=5, column=0, columnspan=2))
        if not self.df.empty:
            self.recreate_plot_widgets()

    def set_canvas_conf(self):
        """Setting list of "Type of figure" values """
        widgetparams = ["1x1 (1 plot)", "1x2 (2 plots horisontal)", "2x1 (2 plots vertical)"]
        self.combobox_canv_param = ttk.Combobox(self.frame1, values=widgetparams, state="readonly", justify="right")
        self.combobox_canv_param.set(widgetparams[0])
        self.combobox_canv_param.bind("<<ComboboxSelected>>", self.canv_param_selected)

    def canv_plot_data_selected(self, event):
        """Implementation of the "Data type" change event"""
        pass

    def set_plot_data(self):
        """
        Setting list of "Data type" values
        The list is built from the unique values of the "commodity" column of the dataframe
        """
        self.plot_data_types = list(self.df.commodity.unique())
        self.combobox_plot_data = ttk.Combobox(self.frame2, values=self.plot_data_types, state="readonly", width=15)
        self.combobox_plot_data.set(self.plot_data_types[0])
        self.combobox_plot_data.bind("<<ComboboxSelected>>", self.canv_plot_data_selected)
        self.combobox_plot_data2 = ttk.Combobox(self.frame3, values=self.plot_data_types, state="readonly", width=15)
        self.combobox_plot_data2.set(self.plot_data_types[0])
        self.combobox_plot_data2.bind("<<ComboboxSelected>>", self.canv_plot_data_selected)

    def render(self, obj=None, render_params=None):
        """
        Perform element creation and rendering in one command. Without creating a variable unnecessarily.
        Combines general parameters for the arrangement of elements and parameters for a specific element.
        :param obj: Element to rendering
        :param render_params: Dictionary with element parameters
        :return: Rendered element
        """
        if obj:
            render_params = render_params if render_params else {}
            united_pack_params = self.__render_params.copy()
            united_pack_params.update(render_params)
            obj.grid(united_pack_params)
        return obj

    def dates_selected(self, event):
        """
        Implementation of the Period date change event
        Checking the correctness of the interval
        """
        if self.date_end_1.get_date() < self.date_start_1.get_date():
            messagebox.showwarning("End day warning", "End day is less than start day!")
            self.date_end_1.set_date(self.maxd)
        if self.date_end_2.get_date() < self.date_start_2.get_date():
            messagebox.showwarning("End day warning", "End day is less than start day!")
            self.date_end_2.set_date(self.maxd)

    def checked_graf(self):
        """Implementation of the "Plotting data" checked event"""
        pass

    def recreate_checkboxes(self, dc, mframe):
        i=1
        for col in dc.keys():
            dc[col] = tk.BooleanVar()
            self.render(ttk.Checkbutton(mframe, text=col, variable=dc[col], command=self.checked_graf),
                        dict(row=0, column=i, padx=2))
            i += 1
        dc["close"].set(True)

    def recreate_plot_widgets(self):
        """Rebuilding plotting parameter fields"""
        self.frame3.grid_remove()
        self.render(tk.Label(self.frame2, text="Plot 1 parameters:"), dict(row=0, column=0, columnspan=2, sticky="w"))
        self.render(self.frame4, dict(row=0, column=2, columnspan=4))
        self.render(tk.Label(self.frame4, text="Plotting data:"), dict(row=0, column=0))
        self.recreate_checkboxes(self.check_cols1, self.frame4)
        self.set_plot_data()
        self.render(tk.Label(self.frame2, text="Data type:"), dict(row=1, column=0))
        self.render(self.combobox_plot_data, dict(row=1, column=1, sticky="e"))

        self.mind, self.maxd = self.df.date[0], self.df.date[len(self.df.date) - 1]
        self.date_start_1.config(mindate=self.mind, maxdate=self.maxd)
        self.date_start_1.bind("<<DateEntrySelected>>", self.dates_selected)
        self.date_end_1.config(mindate=self.mind, maxdate=self.maxd)
        self.date_end_1.bind("<<DateEntrySelected>>", self.dates_selected)
        self.date_start_1.set_date(self.maxd)
        self.date_end_1.set_date(self.maxd)
        self.render(ttk.Label(self.frame2, text='Period'), dict(row=1, column=3))
        self.render(self.date_start_1, dict(row=1, column=4))
        self.render(self.date_end_1, dict(row=1, column=5))

        if self.combobox_canv_param.get() != "1x1 (1 plot)":
            self.frame3.grid()
            self.render(tk.Label(self.frame3, text="Plot 2 parameters:"),
                        dict(row=0, column=0, columnspan=2, sticky="w"))
            self.render(self.frame5, dict(row=0, column=2, columnspan=4))
            self.render(tk.Label(self.frame5, text="Plotting data:"), dict(row=0, column=0))
            self.recreate_checkboxes(self.check_cols2, self.frame5)

            self.render(tk.Label(self.frame3, text="Data type:"), dict(row=1, column=0))
            self.render(self.combobox_plot_data2, dict(row=1, column=1, sticky="e"))
            self.render(ttk.Label(self.frame3, text='Period'), dict(row=1, column=3))
            self.date_start_2.config(mindate=self.mind, maxdate=self.maxd)
            self.date_start_2.bind("<<DateEntrySelected>>", self.dates_selected)
            self.date_end_2.config(mindate=self.mind, maxdate=self.maxd)
            self.date_end_2.bind("<<DateEntrySelected>>", self.dates_selected)
            self.date_start_2.set_date(self.maxd)
            self.date_end_2.set_date(self.maxd)
            self.render(self.date_start_2, dict(row=1, column=4))
            self.render(self.date_end_2, dict(row=1, column=5))

    def create_widgets(self):
        """Building the main widgets at the beginning of program execution"""
        self.render(self)
        self.render(tk.Label(self, text="Statistics for oils and natural gas prices", font=("Helvetica", 14)),
                    dict(row=0, column=0, columnspan=2, pady=5))
        self.render(self.label1, dict(row=0, column=2, columnspan=3))
        self.render(tk.Button(self, text="File Open", command=self.btn_openf), dict(row=2, column=0))

        self.render(self.frame1, dict(row=2, column=1))
        self.render(tk.Label(self.frame1, text="Type of figure:"), dict(row=0, column=0, sticky="w"))
        self.render(self.combobox_canv_param, dict(row=0, column=1, sticky="e"))

        self.render(tk.Button(self, text="Show!", command=self.btn_show, font=("Helvetica", 12)), dict(row=2, column=3))

        self.render(self.frame2, dict(row=3, column=0, columnspan=2))
        self.render(self.frame3, dict(row=3, column=3, columnspan=2))

        self.render(self.plot.canvas.get_tk_widget(), dict(row=4, column=0, columnspan=5))

        self.render(NavigationToolbar2Tk(self.plot.canvas, self, pack_toolbar=False),
                    dict(row=5, column=0, columnspan=2))
        self.render(tk.Button(self, text="Clear", command=self.btn_clear), dict(row=5, column=3))
        self.render(tk.Button(self, text="Quit", command=self.quit), dict(row=5, column=4))

        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i, weight=2, uniform='column')
        self.grid_columnconfigure(2, weight=1, uniform='column')

class PlotFrame:
    """Helper class for plotting"""

    def __init__(self, masterframe, size, fig_param="1x1 (1 plot)"):
        """
        Initialization of the "Plotter", description of the main elements
        :param masterframe: Object of main Frame
        :param size: Size of plotting area
        :param fig_param: Plotting area parameter for one or two graphs
        """
        canv_param = (1, 1) if "1x1" in fig_param else (1, 2) if "1x2" in fig_param else (2, 1)
        self.fig, self.ax = plt.subplots(canv_param[0], canv_param[1])
        # self.fig.suptitle("Statistics", fontsize=16)
        self.fig.figsize = size
        self.canvas = FigureCanvasTkAgg(self.fig, master=masterframe)
        self.is_one_plot = canv_param[0] == canv_param[1]

    def update_canvas(self, masterframe, size, fig_param="1x1 (1 plot)"):
        """Update of the "Plotter" elements"""
        canv_param = (1, 1) if "1x1" in fig_param else (1, 2) if "1x2" in fig_param else (2, 1)
        self.fig, self.ax = plt.subplots(canv_param[0], canv_param[1])
        # self.fig.suptitle("Statistics", fontsize=16)
        self.fig.figsize = size
        self.canvas = FigureCanvasTkAgg(self.fig, master=masterframe)
        self.is_one_plot = canv_param[0] == canv_param[1]


    def plot_graf(self, df, title):
        """
        Drawing a graph
        :param df: Dataframe or list of dataframes
        :param title: title of the plotting area
        :return: None
        """
        if self.is_one_plot:
            self.fig.suptitle("Statistics for " + title, fontsize=16)
            df.plot(ax=self.ax)
        else:
            # self.fig.suptitle(f"Comparison for {title[0]} and {title[1]}", fontsize=16)
            df[0].plot(ax=self.ax[0])
            self.ax[0].set_title(title[0], y=1.0, pad=-10)
            df[1].plot(ax=self.ax[1])
            self.ax[1].set_title(title[1], y=1.0, pad=-10)
        self.canvas.draw()

    def clearplot(self):
        """Clear of the plotting area"""
        if self.is_one_plot:
            self.ax.cla()  # clear axes
        else:
            self.ax[0].cla()
            self.ax[1].cla()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Projekt Arbeit")
    app = GetWigetsFrame(master=root, padx=20, pady=10)
    app.mainloop()
