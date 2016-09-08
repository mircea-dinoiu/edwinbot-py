# Python imports
import threading
import time

# Project imports
from util import cron
from util import temp
from engine.chatango.manager.Stream import StreamManager


class Base(StreamManager):
    def stop(self):
        # Set the running flag to false
        self._running = False

        # Remove "unused" chatrooms from the database
        rooms = self.db.get_rooms(False)

        for room in rooms:
            # Select unblock listed rooms
            room_data = self.db.get_room_data(room)
            # Avoid removing rooms that the bot is connected to or the default rooms
            if room not in self.get_room_names() and not room_data['default']:
                self.db.remove_room(room)

        # Disconnect from chatrooms
        for conn in list(self._rooms.values()):
            conn.disconnect(reconnect=False)

        # Save db store
        root_path = self.db.get_config('root_path')

        temp.save(self.db.store['bet_list'], 'bet_list', root_path)
        temp.save(self.db.store['shapeshiftings'], 'shapeshiftings', root_path)
        temp.save(self.db.store['redirects'], 'redirects', root_path)
        temp.save(self.db.store['speak'], 'speak', root_path)
        temp.save(self.db.store['vote_game'], 'vote_game', root_path)
        temp.save(self.db.store['lotteries'], 'lotteries', root_path)
        temp.save(self.db.store['cannons'], 'cannons', root_path)

    def cron_job(self, job):
        """
        Launches a job in a Thread

        @type job: function
        @param job: reference to the function to launch
        """
        threading.Thread(
            target=job,
            args=(self,)
        ).start()

    def cron_manager(self):
        """
        Cron jobs method
        Checks if is the time for some cron activities and eventually launches the jobs
        """
        while self._running:
            if len(self.get_room_names()) < 1:
                self.stop()

            now = int(time.time())

            # CONTINUOUSLY
            if time.time() - self.db.get_info('boot_time') > 10:
                cron.level_lottery(self)
                cron.coins_lottery(self)

            # 1 HOUR
            if now - self.db.get_config('cron_1h') > 3600 - 1:
                self.db.set_config('cron_1h', 3600, 'add')

                # Jobs
                self.cron_job(cron.unpark)

            # 2 HOURS
            if now - self.db.get_config('cron_2h') > 3600 * 2 - 1:
                self.db.set_config('cron_2h', 3600 * 2, 'add')

            # 3 HOURS
            if now - self.db.get_config('cron_3h') > 3600 * 3 - 1:
                self.db.set_config('cron_3h', 3600 * 3, 'add')

                # Jobs
                self.cron_job(cron.bank_interest)

            # 6 HOURS
            if now - self.db.get_config('cron_6h') > 3600 * 6 - 1:
                self.db.set_config('cron_6h', 3600 * 6, 'add')

            # 12 HOURS
            if now - self.db.get_config('cron_12h') > 3600 * 12 - 1:
                self.db.set_config('cron_12h', 3600 * 12, 'add')

            # 24 HOURS
            if now - self.db.get_config('cron_24h') > 3600 * 24 - 1:
                self.db.set_config('cron_24h', 3600 * 24, 'add')

                # Jobs
                self.cron_job(cron.bank_earnings)
                self.cron_job(cron.level_downgrade)