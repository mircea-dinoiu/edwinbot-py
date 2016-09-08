class PMEvents:
    def on_pm_connect(self, pm):
        pass

    def on_pm_disconnect(self, pm):
        pass

    def on_pm_ping(self, pm):
        pass

    def on_pm_message(self, pm, user, body):
        pass

    def on_pm_offline_message(self, pm, user, body):
        pass

    def on_pm_contact_list_receive(self, pm):
        pass

    def on_pm_block_list_receive(self, pm):
        pass

    def on_pm_contact_add(self, pm, user):
        pass

    def on_pm_connect1(self, pm, user, idle, status):
        pass

    def on_pm_contact_remove(self, pm, user):
        pass

    def on_pm_block(self, pm, user):
        pass

    def on_pm_unblock(self, pm, user):
        pass

    def on_pm_idle(self, pm, idle):
        pass

    def on_pm_contact_online(self, pm, user):
        pass

    def on_pm_contact_offline(self, pm, user):
        pass