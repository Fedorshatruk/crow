def set_turn_timers(session, timer):
    """
    Для каждой новой сессии функция должна создавать таймеры с установленными временами хода.
    При старте хода должен запускаться таймер этого хода.
    По истечении времени таймера должен начинаться новый ход.
    Таймер работает таким образом, что он идёт даже когда сервер отключен.
    """
    turn_set = session.turn.all()

    for turn in turn_set:
        timer.objects.create(duration_in_minutes=turn.turn_time, state=timer.STATE.PAUSED)
