class Task:
    manager = None
    target = None
    timeout = None
    function = None
    is_interval = None
    args = None
    kw = None

    def cancel(self):
        """Sugar for remove task."""
        self.manager.remove_task(self)