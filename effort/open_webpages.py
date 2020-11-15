import webbrowser

labels = [
"sEiIKjd1",
"xuyhzeS2",
"pgeitcE3",
"EtkxcDk4",
"oupauqC5",
"GoXtZTz6",
"tkYgmSc7",
"pUhwbpx8",
"FnyZkwx9",
"QruFdIb10",
"FVaTjZm11",
"nzalsqm12",
"NxdmwTu13",
"bVnvEdo14",
"OLBiywv15",
"StzlNyj16",
"fiTNIsr17",
"xvQwDqd18",
"KeCaEWe19",
"hFLoveR20",
"ysBNxoX21",
"lMNoKru22",
"ynhqFbz23",
"lGcpsBI24",
]

#for i in range(1, 51):
for i in labels:
    webbrowser.open(f"http://192.168.0.206:8000/room/Effort_task_Both_Hanzlik/?participant_label={i}", new=1)
   # webbrowser.open(f"http://localhost:8000/room/Effort_task_Both_Hanzlik/?participant_label=vt203_{i}", new=1)

# http://192.168.0.206:8000/room/Effort_task_Both_Hanzlik/?participant_label=vt203_1