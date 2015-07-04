from PyQt4.QtGui import *
from PyQt4.QtCore import *
from my_gui import Ui_MainWindow

from countries import countries_list_and_code
from pyowm import OWM
from datetime import datetime
import string

class MyMainGui(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainGui, self).__init__(parent)
        self.setupUi(self)
        app.setStyle(QStyleFactory.create('Plastique'))

        API_key = '1330050f05c5c2c1f05e678136d1ebc2'
        self.owm = OWM(API_key)

        # get a list of countries and alpha2 codes
        self.countries_list, self.alpha2_code_list = countries_list_and_code()

        self.comboBox_country.addItems(self.countries_list)
        self.toolButton_search.clicked.connect(self.search_city)
        self.lineEdit_city.returnPressed.connect(self.search_city)
        self.toolButton_next.clicked.connect(self.next_page_of_three_hour_display)
        self.toolButton_previous.clicked.connect(self.previous_page_of_three_hour_display)

        self.toolButton_previous.setDisabled(True)
        self.three_hour_display_page_number = 1

        # disable the line below if you don't want to load weather for Berlin at start up
        self.initialize_display()

    def initialize_display(self):
        """Display weather for Berlin, Deustchland at startup"""

        self.search_query = "Berlin, DE"
        self.obs = self.owm.weather_at_place(self.search_query)
        self.lineEdit_city.setText("Berlin")
        self._display_five_day_forecast()
        self._make_three_hour_data()
        self._print_info()
        self.progressBar.setValue(0)

    def search_city(self):
        """Retrieves 5-day and 3-hourly data from OpenWeatherMap and then
        displays it in the GUI. Also updates progress bar while the data
        is being retrieved."""

        self.selected_country_name = self.comboBox_country.currentText()
        self.country_index = self.comboBox_country.currentIndex()
        self.city = self.lineEdit_city.text()
        if not self.selected_country_name == "Select a country to refine your search (optional)":
            self.selected_country_alpha2_code = self.alpha2_code_list[self.country_index-1]
            self.search_query = self.city + ',' + self.selected_country_alpha2_code
        else:
            self.search_query = self.city
        print(self.search_query)

        self.progressBar.setValue(25)
        self.obs = self.owm.weather_at_place(self.search_query)
        self.progressBar.setValue(50)
        self._display_five_day_forecast()
        self.progressBar.setValue(75)
        self._make_three_hour_data()
        self._print_info()
        self.progressBar.setValue(100)


    def _print_info(self):
        """Populates the fields -- such as longitude, latitude, windspeed, etc. -- in the
         top right corner of the GUI. It also updates city name and country name."""

        country_alpha2 = self.obs._location._country
        try:
            country_index = self.alpha2_code_list.index(country_alpha2)
            country_name = self.countries_list[country_index]
        except:
            country_name = country_alpha2

        time_reference = str(datetime.fromtimestamp(self.obs._weather._reference_time))
        self.label_date.setText(time_reference[8:10] + '/' + time_reference[5:7] + '/' + time_reference[0:4])
        self.label_time.setText(time_reference[10:16])

        longitude = str(self.obs._location._lon)
        latitude = str(self.obs._location._lat)
        city = self.obs._location._name
        summary = self.obs._weather._detailed_status # few clouds, heavy rain etc.

        sunrise_time_unix = self.obs._weather._sunrise_time # unix time
        sunset_time_unix = self.obs._weather._sunset_time
        sunrise_time = str(datetime.fromtimestamp(sunrise_time_unix))
        sunset_time = str(datetime.fromtimestamp(sunset_time_unix))
        humiditiy = str(self.obs._weather._humidity) + ' %'
        wind = self.obs._weather._wind
        wind_speed = str(wind['speed']) + ' m/s'
        try:
            wind_direction = str(wind['deg']) + ' Deg' # sometimes wind direction is not available
        except Exception as e:
            wind_direction = 'N/A'

        pressure_sea_and_press = self.obs._weather._pressure
        pressure = str(pressure_sea_and_press['press']) + ' hpa'
        visibility_distance = str(self.obs._weather._visibility_distance) + ' m'

        self.label_country.setText(country_name)
        self.label_city.setText(city)
        self.label_longitude.setText(str(longitude))
        self.label_latitude.setText(str(latitude))
        self.label_summary.setText(string.capwords(summary))
        self.label_sunrise.setText(sunrise_time[11:16])
        self.label_sunset.setText(sunset_time[11:16])
        self.label_humidity.setText(humiditiy)
        self.label_wind_speed.setText(wind_speed)
        self.label_direction.setText(wind_direction)
        self.label_pressure.setText(pressure)
        self.label_visibility.setText(visibility_distance)

    def _display_five_day_forecast(self):
        """Retrieves five-day forecast and then populates this data in all the
        GUI fields of 5-day forecast Tab."""

        self.fd = self.owm.daily_forecast(name=self.search_query, limit = 5)

        # day 1
        day1 = self.fd._forecast._weathers[0]
        datetime_unix = day1._reference_time
        dtu = datetime.fromtimestamp(datetime_unix)
        day_of_the_week = dtu.strftime("%A")
        self.label_5day_day1.setText(day_of_the_week)

        dtu= str(dtu)
        self.label_5day_day1_date.setText(dtu[8:10] + '/' + dtu[5:7] + '/' + dtu[0:4])

        self.label_5day_day1_desc.setText(string.capwords(day1._status))
        icon_path = ':/icons/' + day1._weather_icon_name + '.png'
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_5day_day1_pic.setIcon(icon)
        self.label_5day_day1_min.setText(str(round(day1._temperature['min'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day1_max.setText(str(round(day1._temperature['max'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day1_morn.setText(str(round(day1._temperature['morn'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day1_day.setText(str(round(day1._temperature['day'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day1_even.setText(str(round(day1._temperature['eve'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day1_night.setText(str(round(day1._temperature['night'] - 273.15, 2)) + ' \u00b0C')

        # day 2
        day2 = self.fd._forecast._weathers[1]
        datetime_unix = day2._reference_time
        dtu = datetime.fromtimestamp(datetime_unix)
        day_of_the_week = dtu.strftime("%A")

        dtu= str(dtu)
        self.label_5day_day2_date.setText(dtu[8:10] + '/' + dtu[5:7] + '/' + dtu[0:4])

        self.label_5day_day2.setText(day_of_the_week)
        self.label_5day_day2_desc.setText(string.capwords(day2._status))
        icon_path = ':/icons/' + day2._weather_icon_name + '.png'
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_5day_day2_pic.setIcon(icon)
        self.label_5day_day2_min.setText(str(round(day2._temperature['min'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day2_max.setText(str(round(day2._temperature['max'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day2_morn.setText(str(round(day2._temperature['morn'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day2_day.setText(str(round(day2._temperature['day'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day2_even.setText(str(round(day2._temperature['eve'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day2_night.setText(str(round(day2._temperature['night'] - 273.15, 2)) + ' \u00b0C')

        # day 3
        day3 = self.fd._forecast._weathers[2]
        datetime_unix = day3._reference_time
        dtu = datetime.fromtimestamp(datetime_unix)
        day_of_the_week = dtu.strftime("%A")

        dtu= str(dtu)
        self.label_5day_day3_date.setText(dtu[8:10] + '/' + dtu[5:7] + '/' + dtu[0:4])

        self.label_5day_day3.setText(day_of_the_week)
        self.label_5day_day3_desc.setText(string.capwords(day3._status))
        icon_path = ':/icons/' + day3._weather_icon_name + '.png'
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_5day_day3_pic.setIcon(icon)
        self.label_5day_day3_min.setText(str(round(day3._temperature['min'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day3_max.setText(str(round(day3._temperature['max'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day3_morn.setText(str(round(day3._temperature['morn'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day3_day.setText(str(round(day3._temperature['day'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day3_even.setText(str(round(day3._temperature['eve'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day3_night.setText(str(round(day3._temperature['night'] - 273.15, 2)) + ' \u00b0C')

        # day 4
        day4 = self.fd._forecast._weathers[3]
        datetime_unix = day4._reference_time
        dtu = datetime.fromtimestamp(datetime_unix)
        day_of_the_week = dtu.strftime("%A")

        dtu= str(dtu)
        self.label_5day_day4_date.setText(dtu[8:10] + '/' + dtu[5:7] + '/' + dtu[0:4])

        self.label_5day_day4.setText(day_of_the_week)
        self.label_5day_day4_desc.setText(string.capwords(day4._status))
        icon_path = ':/icons/' + day4._weather_icon_name + '.png'
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_5day_day4_pic.setIcon(icon)
        self.label_5day_day4_min.setText(str(round(day4._temperature['min'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day4_max.setText(str(round(day4._temperature['max'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day4_morn.setText(str(round(day4._temperature['morn'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day4_day.setText(str(round(day4._temperature['day'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day4_even.setText(str(round(day4._temperature['eve'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day4_night.setText(str(round(day4._temperature['night'] - 273.15, 2)) + ' \u00b0C')

        # day 5
        day5 = self.fd._forecast._weathers[4]
        datetime_unix = day5._reference_time
        dtu = datetime.fromtimestamp(datetime_unix)
        day_of_the_week = dtu.strftime("%A")

        dtu= str(dtu)
        self.label_5day_day5_date.setText(dtu[8:10] + '/' + dtu[5:7] + '/' + dtu[0:4])

        self.label_5day_day5.setText(day_of_the_week)
        self.label_5day_day5_desc.setText(string.capwords(day5._status))
        icon_path = ':/icons/' + day5._weather_icon_name + '.png'
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_5day_day5_pic.setIcon(icon)
        self.label_5day_day5_min.setText(str(round(day5._temperature['min'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day5_max.setText(str(round(day5._temperature['max'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day5_morn.setText(str(round(day5._temperature['morn'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day5_day.setText(str(round(day5._temperature['day'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day5_even.setText(str(round(day5._temperature['eve'] - 273.15, 2)) + ' \u00b0C')
        self.label_5day_day5_night.setText(str(round(day5._temperature['night'] - 273.15, 2)) + ' \u00b0C')

    def _make_three_hour_data(self):
        """Retrieves three-hourly forecast."""

        self.fc= self.owm.three_hours_forecast(self.search_query)
        self.weathers = self.fc._forecast._weathers
        self.weather_list = []
        for i in range(0, self.weathers.__len__()):
            w = self.weathers[i]
            self.weather_list.append(w)
        self._display_three_hour_data()

    def next_page_of_three_hour_display(self):
        """Displays three-hourly forecast for the next 8 data points."""

        if self.three_hour_display_page_number < 5:
            self.three_hour_display_page_number += 1
            self._display_three_hour_data()

        if self.three_hour_display_page_number == 4:
            self.toolButton_next.setDisabled(True)
        else:
            self.toolButton_next.setDisabled(False)

        if not self.three_hour_display_page_number == 1:
            self.toolButton_previous.setDisabled(False)

        self._update_page_number()

    def previous_page_of_three_hour_display(self):
        """Displays three-hourly forecast for the previous 8 data points."""

        if self.three_hour_display_page_number > 1:
            self.three_hour_display_page_number -= 1
            self._display_three_hour_data()

        if self.three_hour_display_page_number == 1:
            self.toolButton_previous.setDisabled(True)
        else:
            self.toolButton_next.setDisabled(False)
            
        self._update_page_number()

    def _update_page_number(self):
        """Updates page numbers while the user is pressing next and previous buttons"""

        if self.three_hour_display_page_number == 1:
            self.label_page_number.setText("Page 1 of 4")
        elif self.three_hour_display_page_number == 2:
            self.label_page_number.setText("Page 2 of 4")
        elif self.three_hour_display_page_number == 3:
            self.label_page_number.setText("Page 3 of 4")
        elif self.three_hour_display_page_number == 4:
            self.label_page_number.setText("Page 4 of 4")


    def _display_three_hour_data(self):
        """This function displays the three-hourly weather data at various location
        in the 3-hour forecast Tab"""

        if self.three_hour_display_page_number == 1:
            data = self.weather_list[0]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_0_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[1]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_1_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[2]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_2_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[3]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_3_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[4]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_4_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[5]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_5_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[6]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_6_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[7]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_7_location(time, date, icon_path, min_temp, max_temp)

        if self.three_hour_display_page_number == 2:
            data = self.weather_list[8]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_0_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[9]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_1_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[10]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_2_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[11]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_3_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[12]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_4_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[13]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_5_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[14]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_6_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[15]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_7_location(time, date, icon_path, min_temp, max_temp)

        if self.three_hour_display_page_number == 3:
            data = self.weather_list[16]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_0_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[17]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_1_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[18]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_2_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[19]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_3_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[20]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_4_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[21]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_5_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[22]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_6_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[23]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_7_location(time, date, icon_path, min_temp, max_temp)

        if self.three_hour_display_page_number == 4:
            data = self.weather_list[24]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_0_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[25]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_1_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[26]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_2_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[27]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_3_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[28]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_4_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[29]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_5_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[30]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_6_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[31]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_7_location(time, date, icon_path, min_temp, max_temp)

        if self.three_hour_display_page_number == 5:
            data = self.weather_list[32]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_0_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[33]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_1_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[34]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_2_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[35]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_3_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[36]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_4_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[37]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_5_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[38]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_6_location(time, date, icon_path, min_temp, max_temp)

            data = self.weather_list[39]
            time, date, icon_path, min_temp, max_temp = self._get_relevent_data(data)
            self._display_in_7_location(time, date, icon_path, min_temp, max_temp)


    def _get_relevent_data(self, data):
        """A convenience function to time data and temperature in proper format."""

        datetime_unix =  data._reference_time
        dtu = str(datetime.fromtimestamp(datetime_unix))
        date = dtu[8:10] + '/' + dtu[5:7] + '/' + dtu[0:4]
        time = dtu[11:16]
        min_temp = str(round(data._temperature['temp_min'] - 273.15, 2)) + ' \u00b0C'
        max_temp = str(round(data._temperature['temp_max'] - 273.15, 2)) + ' \u00b0C'
        icon_path = ':/icons/' + data._weather_icon_name + '.png'
        return time, date, icon_path, min_temp, max_temp

    def _display_in_0_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 0th location in 3-hour forecast tab"""

        self.label_0_time.setText(time)
        self.label_0_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_0_pic.setIcon(icon)
        self.label_0_min.setText(min_temp)
        self.label_0_max.setText(max_temp)

    def _display_in_1_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 1st location in 3-hour forecast tab"""

        self.label_1_time.setText(time)
        self.label_1_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_1_pic.setIcon(icon)
        self.label_1_min.setText(min_temp)
        self.label_1_max.setText(max_temp)

    def _display_in_2_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 2nd location in 3-hour forecast tab"""

        self.label_2_time.setText(time)
        self.label_2_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_2_pic.setIcon(icon)
        self.label_2_min.setText(min_temp)
        self.label_2_max.setText(max_temp)

    def _display_in_3_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 3rd location in 3-hour forecast tab"""

        self.label_3_time.setText(time)
        self.label_3_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_3_pic.setIcon(icon)
        self.label_3_min.setText(min_temp)
        self.label_3_max.setText(max_temp)

    def _display_in_4_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 4th location in 3-hour forecast tab"""

        self.label_4_time.setText(time)
        self.label_4_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_4_pic.setIcon(icon)
        self.label_4_min.setText(min_temp)
        self.label_4_max.setText(max_temp)

    def _display_in_5_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 5th location in 3-hour forecast tab"""

        self.label_5_time.setText(time)
        self.label_5_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_5_pic.setIcon(icon)
        self.label_5_min.setText(min_temp)
        self.label_5_max.setText(max_temp)

    def _display_in_6_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 6th location in 3-hour forecast tab"""

        self.label_6_time.setText(time)
        self.label_6_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_6_pic.setIcon(icon)
        self.label_6_min.setText(min_temp)
        self.label_6_max.setText(max_temp)

    def _display_in_7_location(self, time, date, icon_path, min_temp, max_temp):
        """Sets text and icons in the 7th location in 3-hour forecast tab"""

        self.label_7_time.setText(time)
        self.label_7_date.setText(date)
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path))
        self.toolButton_7_pic.setIcon(icon)
        self.label_7_min.setText(min_temp)
        self.label_7_max.setText(max_temp)



if __name__ == "__main__":
    app = QApplication([])
    my_gui = MyMainGui()
    my_gui.show()
    app.exit(app.exec_())