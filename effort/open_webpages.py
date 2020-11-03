import webbrowser




for i in range(1, 101):
    webbrowser.open(f"http://localhost:8000/room/Effort_task_Both_Hanzlik/?participant_label=vt203_{i}", new=1)
webbrowser.open("http://localhost:8000/room_without_session/Effort_task_Both_Hanzlik/", new=1)