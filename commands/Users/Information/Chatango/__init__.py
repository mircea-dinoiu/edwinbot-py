# Project imports
from manager.Command.Utils import *


class Chatango(CommandUtils):
    # profile
    def command_profile(self):
        if not self.args:
            user = self.user
        else:
            username = self._get_user_uid(self.args[0])
            self._validate_username(username)
            user = get_user(username)

        try:
            stuff = str(request.urlopen('http://{0}.chatango.com'.format(user.uid)).read())

            age = stuff.split(
                '<span class="profile_text"><strong>Age:</strong></span></td><td><span class="profile_text">',
                1
            )[1].split(
                '<br /></span>',
                1
            )[0]

            gender = stuff.split(
                '<span class="profile_text"><strong>Gender:</strong></span></td><td><span class="profile_text">',
                1
            )[1].split(
                ' <br /></span>',
                1
            )[0]

            location = stuff.split(
                '<span class="profile_text"><strong>Location:</strong></span></td><td><span class="profile_text">',
                1
            )[1].split(
                ' <br /></span>',
                1
            )[0]

            picture = 'http://pop.sorch.info/pic/{0}.png'.format(user.uid)
            url = 'http://{0}.chatango.com'.format(user.uid)

            if self.pm:
                picture = '<i s="{0}" w="125" h="93.75"/>'.format(picture)

            profile_data = self._lang('PROFILE_DATA').format(
                url=url,
                age=age,
                gender=gender,
                location=location,
                picture=picture
            )
            self._message(profile_data)
        except:
            self._message(self._lang('ERROR_CH_USER_NOT_FOUND').format(
                self._user_color(user.uid)
            ))
            if self.log_level > 0:
                raise

    # bg
    def command_bg(self):
        if not self.args:
            username = self.user.uid
        else:
            username = self._get_user_uid(self.args[0])
            self._validate_username(username)

        picture = 'http://st.chatango.com/profileimg/{0}/{1}/{2}/msgbg.jpg'.format(
            username[0],
            username[1] if 1 != len(username) else username[0],
            username
        )

        if self.pm:
            picture = '<i s="{0}" w="125" h="93.75"/>'.format(picture)

        self._message(picture)

    # bgtime
    def command_bgtime(self):
        if not self.args:
            uid = self.user.uid
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)

        try:
            bg_time = get_bg_time(uid)

            if bg_time < time.time():
                self._message(self._lang('PREMIUM_HAD').format(
                    self._user_color(uid),
                    highlight(self._format_seconds(int(time.time()) - bg_time), 'Blue')
                ))
            else:
                self._message(self._lang('PREMIUM_HAS').format(
                    self._user_color(uid),
                    highlight(self._format_seconds(bg_time - int(time.time())), 'Blue')
                ))
        except:
            self._message(self._lang('PREMIUM_NEVER').format(
                self._user_color(uid)
            ))
            if self.log_level > 0:
                raise

    # mini
    def command_mini(self):
        if not self.args:
            uid = self.user.uid
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)

        try:
            stuff = str(
                request.urlopen(
                    'http://{0}.chatango.com'.format(uid)
                ).read().decode('utf-8')
            )
            stuff = everything_between(
                stuff,
                '<span class="profile_text"><!-- google_ad_section_start -->',
                '<!-- google_ad_section_end --></span>'
            )

            if len(stuff.strip()) > 0:
                self._message(stuff)
        except:
            self._message(self._lang('ERROR_CH_USER_NOT_FOUND').format(
                self._user_color(uid)
            ))
            if self.log_level > 0:
                raise

    # minihtml
    def command_minihtml(self):
        if not self.args:
            uid = self.user.uid
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)

        try:
            stuff = str(
                request.urlopen(
                    'http://{0}.chatango.com'.format(uid)
                ).read().decode('utf-8')
            )
            stuff = everything_between(
                stuff,
                '<span class="profile_text"><!-- google_ad_section_start -->',
                '<!-- google_ad_section_end --></span>'
            )

            if len(stuff.strip()) > 0:
                self._message(stuff, html=False)
        except:
            self._message(self._lang('ERROR_CH_USER_NOT_FOUND').format(
                self._user_color(uid)
            ))
            if self.log_level > 0:
                raise