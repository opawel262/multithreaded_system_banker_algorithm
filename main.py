import threading
from time import perf_counter
import tkinter as tk

DEFAULT_PARAMETERS = {
    "available": [10, 9, 10],
    "maximum": [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
    "allocation": [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
}


class BankersAlgorithm:
    def __init__(self, available, maximum, allocation):
        self.available = available
        self.maximum = maximum
        self.allocation = allocation
        self.lock = threading.Lock()
        self.need = [[i - j for i, j in zip(max_i, alloc_j)] for max_i, alloc_j in zip(maximum, allocation)]
        self.len_resources = len(available)
        self.start = perf_counter()

    def request_resources(self, num_process, request_res,  console_info):

        self.lock.acquire()
        if self.request_is_valid(num_process, request_res):
            alloc_copy = self.allocation.copy()
            avail_copy = self.available.copy()
            need_copy = self.need.copy()

            for i in range(self.len_resources):
                alloc_copy[num_process][i] += request_res[i]
                need_copy[num_process][i] -= request_res[i]
                avail_copy[i] -= request_res[i]

            if self.is_sequence_state_safe(alloc_copy, avail_copy, need_copy):
                self.allocation = alloc_copy
                self.available = avail_copy
                self.need = [[i - j for i, j in zip(max_i, alloc_j)] for max_i, alloc_j
                             in zip(self.maximum, alloc_copy)]
                self.lock.release()
                time_stamp = perf_counter()
                console_info.append([True, num_process, request_res, round(time_stamp - self.start, 4)])

            else:
                self.lock.release()
                time_stamp = perf_counter()
                console_info.append([True, num_process, request_res, round(time_stamp - self.start, 4)])

        else:
            self.lock.release()
            time_stamp = perf_counter()
            console_info.append([False, num_process, request_res, round(time_stamp - self.start, 4)])

    def request_is_valid(self, num_process, request_res):
        for k in range(self.len_resources):
            if request_res[k] > self.need[num_process][k]:
                return False
            if request_res[k] > self.available[k]:
                return False
        return True

    def is_sequence_state_safe(self, allocation, available, need):
        work = available.copy()
        finish = [False] * len(allocation)
        i = 0  # Initialize i
        while not all(finish):
            if finish[i] is False and self.is_less_or_equal(need[i], work):
                work = [work[j] + allocation[i][j] for j in range(self.len_resources)]
                finish[i] = True

            i += 1
            if i == len(allocation):
                i = 0

        return all(finish)

    def release_resources(self, num_process, release_res, console_info):
        self.lock.acquire()
        if self.release_is_valid(num_process, release_res):
            alloc_copy = self.allocation.copy()
            avail_copy = self.available.copy()

            for i in range(self.len_resources):
                alloc_copy[num_process][i] -= release_res[i]
                avail_copy[i] += release_res[i]

            self.allocation = alloc_copy
            self.available = avail_copy
            self.need = [[i - j for i, j in zip(max_i, alloc_j)] for max_i, alloc_j in zip(self.maximum, alloc_copy)]
            self.lock.release()
            time_stamp = perf_counter()

            console_info.append([True, num_process, release_res, round(time_stamp - self.start, 4)])
        else:
            self.lock.release()
            time_stamp = perf_counter()
            console_info.append([False, num_process, release_res, round(time_stamp - self.start, 4)])

    def release_is_valid(self, num_process, release_res) -> bool:
        for i in range(self.len_resources):
            if release_res[i] > self.allocation[num_process][i]:
                return False
        return True

    def return_str_current_state_of_system(self) -> str:
        str_info = ""
        str_info += f"Available resources:\n {self.available}"
        str_info += f"\n\nCurrent allocation"

        for i in range(len(self.allocation)):
            str_info += f"\nProcess {i}: {self.allocation[i]}"

        str_info += f"\n\nMaximum allocation"

        for i in range(len(self.maximum)):
            str_info += f"\nProcess {i}: {self.maximum[i]}"

        return str_info

    @staticmethod
    def is_less_or_equal(a, b):
        for i in range(len(a)):
            if a[i] > b[i]:
                return False
        return True


def hide_indicators() -> None:
    request_indicate.config(bg="#b3b3b3")
    release_indicate.config(bg="#b3b3b3")
    settings_indicate.config(bg="#b3b3b3")


def restart_color_buttons() -> None:
    request_btn.config(bg="#b3b3b3")
    release_btn.config(bg="#b3b3b3")
    settings_btn.config(bg="#b3b3b3")


def indicate_button(label: tk.Label, button: tk.Button, page) -> None:
    hide_indicators()
    restart_color_buttons()
    label.config(bg="#353535")
    button.config(bg="#a3a3a3")
    destroy_pages()
    page()


def add_to_list(listbox: tk.Listbox, entry_process: tk.Entry, entry_res_1: tk.Entry, entry_res_2: tk.Entry,
                entry_res_3: tk.Entry, data_list: list) -> None:
    process = entry_process.get()
    res_1 = entry_res_1.get()
    res_2 = entry_res_2.get()
    res_3 = entry_res_3.get()
    if int(process) < 0 or int(process) > 4 or process == "" or res_1 == "" or res_2 == "" or res_3 == "":
        return
    listbox.insert(tk.END, f"Process {process}: [{res_1}, {res_2}, {res_3}]")
    data_list.append([process, res_1, res_2, res_3])


def submit_requests(data_list: list, request_listbox: tk.Listbox, data_l: tk.Label, data_console_l: tk.Text) -> None:
    threads = []
    info_to_console = []
    for i in range(len(data_list)):
        t = threading.Thread(target=system_management.request_resources, args=(int(data_list[i][0]),
                                                                               [int(data_list[i][1]),
                                                                                int(data_list[i][2]),
                                                                                int(data_list[i][3])],
                                                                               info_to_console))
        threads.append(t)

    for t in threads:
        t.start()
        t.join()

    str_info = ""
    for i in range(len(info_to_console)):
        if info_to_console[i][0]:
            str_info += (f"{info_to_console[i][3]}s :Request {info_to_console[i][2]} for process "
                         f"{info_to_console[i][1]} is valid\n")
        else:
            str_info += (f"{info_to_console[i][3]}s :Request {info_to_console[i][2]} for process "
                         f"{info_to_console[i][1]} is invalid\n")

    data_l.config(text=system_management.return_str_current_state_of_system())
    data_console_l.config(state="normal")
    data_console_l.delete("1.0", tk.END)  # Clear previous content
    data_console_l.insert(tk.END, "".join(str_info))  # Join list elements with newline
    data_console_l.config(state="disabled")
    request_listbox.delete(0, tk.END)
    data_list.clear()


def submit_releases(data_list: list, release_listbox: tk.Listbox, data_l: tk.Label, data_console_l: tk.Text) -> None:
    threads = []
    info_to_console = []
    for i in range(len(data_list)):
        t = threading.Thread(target=system_management.release_resources, args=(int(data_list[i][0]),
                                                                               [int(data_list[i][1]),
                                                                                int(data_list[i][2]),
                                                                                int(data_list[i][3])],
                                                                               info_to_console))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    str_info = ""
    for i in range(len(info_to_console)):
        if info_to_console[i][0]:
            str_info += (f"{info_to_console[i][3]}s :Release {info_to_console[i][2]} for process "
                         f"{info_to_console[i][1]} is valid\n")
        else:
            str_info += (f"{info_to_console[i][3]}s :Release {info_to_console[i][2]} for process "
                         f"{info_to_console[i][1]} is invalid\n")

    data_l.config(text=system_management.return_str_current_state_of_system())
    data_console_l.config(state="normal")
    data_console_l.delete("1.0", tk.END)  # Clear previous content
    data_console_l.insert(tk.END, "".join(str_info))  # Join list elements with newline
    data_console_l.config(state="disabled")
    release_listbox.delete(0, tk.END)
    data_list.clear()


def request_page(data_l: tk.Label, data_console_label: tk.Label):
    request_frame = tk.Frame(main_frame, bg="#f2f2f2", height=600, width=524, bd=0)
    lb = tk.Label(request_frame, text="Which process? (0-4)", font=('bold', 15), bg="#f2f2f2", bd=0)

    lb.place(x=45, y=20)
    entry_process = tk.Entry(request_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_process.place(x=45, y=60, width=150, height=35)
    lb_res_1 = tk.Label(request_frame, text="Resource nr. 1", font=('bold', 15), bg="#f2f2f2",
                        bd=0, )
    lb_res_1.place(x=45, y=120)
    entry_res_1 = tk.Entry(request_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_1.place(x=45, y=160, width=150, height=35)

    lb_res_2 = tk.Label(request_frame, text="Resource nr. 2", font=('bold', 15), bg="#f2f2f2",
                        bd=0, )
    lb_res_2.place(x=45, y=210)
    entry_res_2 = tk.Entry(request_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_2.place(x=45, y=250, width=150, height=35)

    lb_res_3 = tk.Label(request_frame, text="Resource nr. 3", font=('bold', 15), bg="#f2f2f2",
                        bd=0, )
    lb_res_3.place(x=45, y=300)
    entry_res_3 = tk.Entry(request_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_3.place(x=45, y=340, width=150, height=35)

    # Creating a Listbox in request_frame
    request_listbox = tk.Listbox(request_frame, selectmode=tk.NONE, font=('bold', 12), bd=0)
    request_listbox.place(x=300, y=20, width=190, height=350)
    data_list = []
    add_to_list_btn = tk.Button(request_frame, font=('bold', 15), text="Add request to list", width=20, height=2,
                                bg="#b3b3b3", bd=0,
                                command=lambda: add_to_list(request_listbox, entry_process, entry_res_1, entry_res_2,
                                                            entry_res_3, data_list))
    add_to_list_btn.place(x=45, y=400)

    # Add sample items to the Listbox for demonstration

    submit_btn = tk.Button(request_frame, font=('bold', 14), text="Send requests at once", width=17, height=2,
                           bg="#b3b3b3", bd=0, command=lambda: submit_requests(data_list, request_listbox, data_l,
                                                                               data_console_label))
    submit_btn.place(x=300, y=400)

    request_frame.pack()


def release_page(data_l: tk.Label, data_console_label: tk.Label):
    release_frame = tk.Frame(main_frame, bg="#f2f2f2", height=600, width=524, bd=0)
    lb = tk.Label(release_frame, text="Which process? (0-4)", font=('bold', 15), bg="#f2f2f2",
                  bd=0, )
    lb.place(x=45, y=20)
    entry_process = tk.Entry(release_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_process.place(x=45, y=60, width=150, height=35)
    lb_res_1 = tk.Label(release_frame, text="Resource nr. 1", font=('bold', 15), bg="#f2f2f2",
                        bd=0, )
    lb_res_1.place(x=45, y=120)
    entry_res_1 = tk.Entry(release_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_1.place(x=45, y=160, width=150, height=35)

    lb_res_2 = tk.Label(release_frame, text="Resource nr. 2", font=('bold', 15), bg="#f2f2f2",
                        bd=0, )
    lb_res_2.place(x=45, y=210)
    entry_res_2 = tk.Entry(release_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_2.place(x=45, y=250, width=150, height=35)

    lb_res_3 = tk.Label(release_frame, text="Resource nr. 3", font=('bold', 15), bg="#f2f2f2",
                        bd=0, )
    lb_res_3.place(x=45, y=300)
    entry_res_3 = tk.Entry(release_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_3.place(x=45, y=340, width=150, height=35)

    # Creating a Listbox in request_frame
    request_listbox = tk.Listbox(release_frame, selectmode=tk.NONE, font=('bold', 12), bd=0)
    request_listbox.place(x=300, y=20, width=190, height=350)
    data_list = []
    add_to_list_btn = tk.Button(release_frame, font=('bold', 15), text="Add release to list", width=20, height=2,
                                bg="#b3b3b3", bd=0,
                                command=lambda: add_to_list(request_listbox, entry_process, entry_res_1, entry_res_2,
                                                            entry_res_3, data_list))
    add_to_list_btn.place(x=45, y=400)

    # Add sample items to the Listbox for demonstration

    submit_btn = tk.Button(release_frame, font=('bold', 14), text="Send releases at once", width=17, height=2,
                           bg="#b3b3b3", bd=0, command=lambda: submit_releases(data_list, request_listbox, data_l,
                                                                               data_console_label))
    submit_btn.place(x=300, y=400)

    release_frame.pack()


def change_max_system(entry_process_max, entry_res1, entry_res2, entry_res3, data_l: tk.Label):
    if (int(entry_process_max.get()) > 4 or int(entry_process_max.get()) < 0 or entry_res1.get() == ""
            or entry_res2.get() == "" or entry_res3.get() == ""):
        return

    system_management.maximum[int(entry_process_max.get())] = [int(entry_res1.get()), int(entry_res2.get()),
                                                               int(entry_res3.get())]
    system_management.need = [[i - j for i, j in zip(max_i, alloc_j)] for max_i, alloc_j in
                              zip(system_management.maximum, system_management.allocation)]
    data_l.config(text=system_management.return_str_current_state_of_system())


def change_alloc_system(entry_process_alloc, entry_res1, entry_res2, entry_res3, data_l: tk.Label):
    if (int(entry_process_alloc.get()) > 4 or int(entry_process_alloc.get()) < 0 or entry_res1.get() == ""
            or entry_res2.get() == "" or entry_res3.get() == ""):
        return
    if (int(entry_res1.get()) > system_management.maximum[int(entry_process_alloc.get())][0] or int(entry_res2.get()) >
            system_management.maximum[int(entry_process_alloc.get())][1] or int(entry_res3.get()) >
            system_management.maximum[int(entry_process_alloc.get())][2]):
        return
    
    
    system_management.allocation[int(entry_process_alloc.get())] = [int(entry_res1.get()), int(entry_res2.get()),
                                                                    int(entry_res3.get())]
    system_management.need = [[i - j for i, j in zip(max_i, alloc_j)] for max_i, alloc_j in
                              zip(system_management.maximum, system_management.allocation)]
    data_l.config(text=system_management.return_str_current_state_of_system())


def change_avail_system(entry_res1, entry_res2, entry_res3, data_l: tk.Label):
    if entry_res1.get() == "" or entry_res2.get() == "" or entry_res3.get() == "":
        return

    system_management.available = [int(entry_res1.get()), int(entry_res2.get()), int(entry_res3.get())]
    data_l.config(text=system_management.return_str_current_state_of_system())


def settings_page(data_l: tk.Label):
    settings_frame = tk.Frame(main_frame, bg="#f2f2f2", height=600, width=524)
    lb = tk.Label(settings_frame, width=20, height=2, text="System parameters",
                  font=('bold', 15), bg="#f2f2f2", bd=0)
    lb.place(x=150, y=20)

    # Maximum values
    lb_process = tk.Label(settings_frame, width=20, height=2, text="Process nr",
                          font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_process.place(x=70, y=55)
    entry_process_max = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_process_max.place(x=130, y=110, width=50, height=25)

    entry_process_alloc = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_process_alloc.place(x=230, y=110, width=50, height=25)

    lb_res_1_max = tk.Label(settings_frame, text="Max 1", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_1_max.place(x=130, y=150)  # Adjusted x and y coordinates
    entry_res_1_max = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_1_max.place(x=130, y=190, width=50, height=25)

    lb_res_2_max = tk.Label(settings_frame, text="Max 2", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_2_max.place(x=130, y=250)  # Adjusted x and y coordinates
    entry_res_2_max = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_2_max.place(x=130, y=290, width=50, height=25)

    lb_res_3_max = tk.Label(settings_frame, text="Max 3", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_3_max.place(x=130, y=350)  # Adjusted x and y coordinates
    entry_res_3_max = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_3_max.place(x=130, y=390, width=50, height=25)
    entry_button_max = tk.Button(settings_frame, font=('bold', 9), text="Change max", width=13, height=1, bg="#b3b3b3",
                                 bd=0, command=lambda: change_max_system(entry_process_max, entry_res_1_max,
                                                                         entry_res_2_max, entry_res_3_max, data_l))
    entry_button_max.place(x=100, y=450)

    # Allocation values
    lb_res_1_alloc = tk.Label(settings_frame, text="Alloc 1", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_1_alloc.place(x=230, y=150)  # Adjusted x and y coordinates
    entry_res_1_alloc = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_1_alloc.place(x=230, y=190, width=50, height=25)

    lb_res_2_alloc = tk.Label(settings_frame, text="Alloc 2", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_2_alloc.place(x=230, y=250)  # Adjusted x and y coordinates
    entry_res_2_alloc = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_2_alloc.place(x=230, y=290, width=50, height=25)

    lb_res_3_alloc = tk.Label(settings_frame, text="Alloc 3", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_3_alloc.place(x=230, y=350)  # Adjusted x and y coordinates
    entry_res_3_alloc = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_3_alloc.place(x=230, y=390, width=50, height=25)
    entry_button_alloc = tk.Button(settings_frame, font=('bold', 9), text="Change allocated", width=13, height=1,
                                   bg="#b3b3b3", bd=0, command=lambda: change_alloc_system(entry_process_alloc,
                                                                                           entry_res_1_alloc,
                                                                                           entry_res_2_alloc,
                                                                                           entry_res_3_alloc, data_l))
    entry_button_alloc.place(x=210, y=450)

    # Available values
    lb_res_1_avail = tk.Label(settings_frame, text="Avail 1", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_1_avail.place(x=330, y=150)  # Adjusted x and y coordinates
    entry_res_1_avail = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_1_avail.place(x=330, y=190, width=50, height=25)

    lb_res_2_avail = tk.Label(settings_frame, text="Avail 2", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_2_avail.place(x=330, y=250)  # Adjusted x and y coordinates
    entry_res_2_avail = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_2_avail.place(x=330, y=290, width=50, height=25)

    lb_res_3_avail = tk.Label(settings_frame, text="Avail 3", font=('bold', 15), bg="#f2f2f2", bd=0)
    lb_res_3_avail.place(x=330, y=350)  # Adjusted x and y coordinates
    entry_res_3_avail = tk.Entry(settings_frame, font=('bold', 15), bg="#b3b3b3", bd=0)
    entry_res_3_avail.place(x=330, y=390, width=50, height=25)
    entry_button_avail = tk.Button(settings_frame, font=('bold', 9), text="Change available", width=13, height=1,
                                   bg="#b3b3b3", bd=0, command=lambda: change_avail_system(entry_res_1_avail,
                                                                                           entry_res_2_avail,
                                                                                           entry_res_3_avail, data_l))
    entry_button_avail.place(x=320, y=450)

    settings_frame.pack()


def destroy_pages():
    for frame in main_frame.winfo_children():
        frame.destroy()


if __name__ == '__main__':
    system_management = BankersAlgorithm(DEFAULT_PARAMETERS["available"], DEFAULT_PARAMETERS["maximum"],
                                         DEFAULT_PARAMETERS["allocation"])

    root = tk.Tk()
    root.geometry("1024x500")
    root.resizable(False, False)
    root.title("System management using Banker's algorithm")
    # System info frame
    system_info_frame = tk.Frame(root, bg="#c3c3c3", height=600, width=250)
    system_info_frame.pack(side=tk.RIGHT)
    label_info = tk.Label(system_info_frame, text="System info", font=('bold', 15), bg="#c1c1c1", bd=0, )
    label_info.place(x=70, y=20)
    label_info_floor = tk.Label(system_info_frame, text="", font=('bold', 15), bg="#353535", bd=0, )
    label_info_floor.place(x=20, y=60, width=210, height=5)
    data_frame = tk.Frame(system_info_frame, bg="#b3b3b3", height=600, width=250, highlightthickness=6,
                          highlightbackground="#c7c8c9", bd=5)
    data_frame.place(x=20, y=80, width=210, height=400)

    data_label = tk.Label(data_frame, text=system_management.return_str_current_state_of_system(), font=('bold', 8),
                          bg="#b3b3b3", bd=0)
    data_label.place(x=0, y=0, width=190, height=230)

    data_info_floor = tk.Label(data_frame, text="", font=('bold', 15), bg="#353535", bd=0, )
    data_info_floor.place(x=5, y=240, width=180, height=5)

    data_console_info = tk.Text(data_frame, wrap="word", font=('Arial', 9), bg="#a3a3a3", bd=0, state="disabled")
    data_console_info.place(x=10, y=250, width=170, height=120)

    scrollbar = tk.Scrollbar(data_frame, command=data_console_info.yview)
    scrollbar.place(x=175, y=250, height=120)

    data_console_info['yscrollcommand'] = scrollbar.set

    # Options frame
    options_frame = tk.Frame(root, bg="#c3c3c3", height=600, width=250)
    options_frame.pack(side=tk.LEFT)

    request_btn = tk.Button(options_frame, font=('bold', 15), text="Request process", width=20, height=2, bg="#b3b3b3",
                            bd=0, command=lambda: indicate_button(request_indicate, request_btn,
                                                                  lambda: request_page(data_label, data_console_info)))
    request_btn.place(x=10, y=100)

    request_indicate = tk.Label(options_frame, font=('bold', 15), text="", width=20, height=2,
                                bg="#b3b3b3", bd=0, )
    request_indicate.place(x=10, y=100, width=5, height=60)

    release_btn = tk.Button(options_frame, font=('bold', 15), text="Release process", width=20, height=2, bg="#b3b3b3",
                            bd=0, command=lambda: indicate_button(release_indicate, release_btn,
                                                                  lambda: release_page(data_label, data_console_info)))
    release_btn.place(x=10, y=170)

    release_indicate = tk.Label(options_frame, font=('bold', 15), text="", width=20, height=2,
                                bg="#b3b3b3", bd=0, )
    release_indicate.place(x=10, y=170, width=5, height=60)

    settings_btn = tk.Button(options_frame, font=('bold', 15), text="System settings", width=20, height=2, bg="#b3b3b3",
                             bd=0, command=lambda: indicate_button(settings_indicate, settings_btn,
                                                                   lambda: settings_page(data_label)))
    settings_btn.place(x=10, y=240)

    settings_indicate = tk.Label(options_frame, font=('bold', 15), text="", width=20, height=2,
                                 bg="#b3b3b3", bd=0)
    settings_indicate.place(x=10, y=240, width=5, height=60)

    main_frame = tk.Frame(root, bg="#f2f2f2", height=600, width=524, highlightthickness=6,
                          highlightbackground="#c7c8c9")
    main_frame.pack(side=tk.RIGHT)

    root.mainloop()
