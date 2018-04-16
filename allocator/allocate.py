#!/usr/bin/env python

import csv
import sys
import os
import time
import datetime

from oauth2client import client
from googleapiclient import sample_tools
from optparse import OptionParser

service = None
parking_selection = []
spaces = []
parking = {}
parking_numbers = ["C6","C7","C8","C17","N/A"]

cal_entry_tmpl = {
    "summary": "",
    "start": {
        "date": "",
    },
    "end": {
        "date": "",
    }
}

def get_command_line_option_parser():
    parser = OptionParser(usage='%prog [options]',
                          description='Print out car park spaces and update Google calendar directly.')
    parser.add_option('-c', '--config-file', dest='config_file',
                      help='CSV file with ordered list of names and days selected.')
    parser.add_option('--add-calendar-entries', dest='update_cal', default=False, action='store_true',
                      help='Automatically add the entries to the specified calendar.')
    parser.add_option('-g', '--google-calendar', dest='calendar',
                      help='Name of the Google Calendar to update.')
    parser.add_option('-d', '--date-of-monday', dest='sdate', default=time.strftime("%Y-%m-%d"),
                      help='Date (YYYY-MM-DD) that the Monday starts on for this week.')
    parser.add_option('-s', '--number-of-spaces', dest='num_spaces', default=3,
                      help='Number os car park spaces there are (Default 3)')
    return parser

def init_spaces(num_spaces):
    for i in range(int(num_spaces)):
        spaces.append("Space " + str(i+1))
        parking[spaces[i]] = ['Free','Free','Free','Free','Free']

def day_to_number(day_string):
    return {
        'mon': 0,
        'tue': 1,
        'wed': 2,
        'thur': 3,
        'fri': 4}.get(day_string.lower(), 99)

def pick_weeks_spaces(space, from_bottom=False):
    tmp = parking_selection
    if from_bottom:
        tmp = reversed(parking_selection)
    for entry in tmp:
        name = entry[0]
        for day_string in entry[1:]:
            day_number = day_to_number(day_string)
            if day_number != 99 and parking[space][day_number] == "Free":
                already_has_another_space = False
                #Check that they don't already have a spot in the other spaces
                for i in spaces:
                    if parking[i][day_number] == name:
                        already_has_another_space = True
                if not already_has_another_space:
                    parking[space][day_number] = name
                    break

def get_google_cal_service():
    global service
    if not service:
        # Authenticate and construct service.
        service, flags = sample_tools.init(
            '', 'calendar', 'v3', __doc__, __file__,
            scope='https://www.googleapis.com/auth/calendar')
    return service

def get_cal_id_by_name(cal_name):
    service = get_google_cal_service()
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == cal_name:
                return calendar_list_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return None

def update_google_calendar(cal_id, date):
    dates = ["","","","","",""]
    last_date = date
    #Need the Sat as the very last so the end date for the friday is the Sat
    for i in range(6):
        dates[i] = last_date
        last_date = (datetime.datetime.strptime(last_date, "%Y-%m-%d") +
                     datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    space_iter = 0
    for key in sorted(parking):
        count = 0
        if space_iter >= len(parking_numbers):
            pno = parking_numbers[-1]
        else:
            pno = parking_numbers[space_iter]
        space_iter = space_iter + 1
        for name in parking[key]:
            cal_entry_tmpl["summary"] = pno + " " + name
            cal_entry_tmpl["start"]["date"] = dates[count]
            cal_entry_tmpl["end"]["date"] = dates[count + 1]
            count = count + 1

            try:
                service.events().insert(calendarId=cal_id,
                                        body=cal_entry_tmpl).execute()
            except Exception, err:
                print err

def get_day_selection(csv_file):
    #Get parking selections array
    reader = csv.reader(open(csv_file))
    for row in reader:
        if not row:
            continue
        row[0] = row[0].replace('_', ' ')
        if row[0].startswith('#'):
            continue
        if row[0] in parking_selection:
            print row[0] + " in parking selection file multiple times"
            return None
        parking_selection.append(row)
    return parking_selection

def print_parking(num_spaces):
    spaces_string = ["MON: ","TUE: ","WED: ","THU: ","FRI: " ]
    for n in range(len(spaces_string)):
        for i in range(int(num_spaces)):
            if i == 0:
                comma = ''
            else:
                comma = ', '
            spaces_string[n] = spaces_string[n] + comma + parking[spaces[i]][n]
        print spaces_string[n]

def main(argv):
    parser = get_command_line_option_parser()
    (opts, extra) = parser.parse_args()

    if not opts.config_file:
        print 'Config file not specified.'
        parser.print_help()
        return 1

    if not os.path.isfile(opts.config_file):
        print "Config file " + os.path.abspath(opts.config_file) + " not found."
        parser.print_help()
        return 1

    if opts.update_cal is True:
        if not opts.calendar:
            print 'No Google calendar specified.'
            parser.print_help()
            return 1
        cal_id = get_cal_id_by_name(opts.calendar)
        if not cal_id:
            print "Calendar " + opts.calendar + " not found."
            parser.print_help()
            return 1

    parking_selection = get_day_selection(opts.config_file)
    if not parking_selection:
        parser.print_help()
        return 1

    init_spaces(opts.num_spaces)

    #Build list up now top to bottom and then bottom to top
    #Try a number of times to fill the spaces up with more than one pass
    reverse = False
    for i in range(int(opts.num_spaces)):
        for n in range(1,5):
            pick_weeks_spaces(spaces[i], reverse)
        reverse = not reverse

    print_parking(opts.num_spaces)

    if opts.update_cal:
        date = datetime.datetime.strptime(opts.sdate, "%Y-%m-%d")
        if date.isoweekday() != 1:
            print "Start of week date " + opts.sdate + " not Monday."
            parser.print_help()
            return 1
        update_google_calendar(cal_id, opts.sdate)

    return 0

if __name__ == '__main__':
    main(sys.argv)
