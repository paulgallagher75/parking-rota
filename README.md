# Car parking rota systems
Group of scripts utilizing google services to share a limited number of car parking spaces fairly among a group of people.

## Allocation system
The rota is driven by a CSV list of names and choice of days in order of preference example :

```
Dave,Mon,Tue,Fri
Mark,Mon,Tue,Thur,Fri
John,Mon,Tue,Wed,Fri
Sarah,Mon,Tue,Wed,Fri
```

The output is displayed on the console and written to a google calandar of choice that can be shared with all the individuals.

The rota is decided on a top down then bottom up. so running the allocator like this, with the list of name above with only 3 spaces to pick from,

```sh
./allocate.py -c example_choices.txt -d 2017-02-27 -s 3
```

results in this list below as the outcome, so MON has 4 people wanting it as first choice, as Dave is at the top of the list he gets Monday for Space 1 first, Mark is next on the list however as Space 1 has already gone for the Monday he gets his sencond choice which is Tuesday for Space 1, next is John who wanted Monday then Tuesday which have both already gone do he gets Thursday for Space 1, then Sarah gets Friday as all other choices for Space 1 are gone.

The system then move onto Space 2 however starts at the bottom of the list, so Sarah gets Monday, and so on from bottom to top. After allocating Space 2 we move to the next Space 3 which is worked out from top to bottom and so on.

After the intial pass over to fill up the spaces the system runs back over from the start 4 more time filling up any spaces it con with choices, which is why Mark has been allocated Thursday as well as Tuesday in Space 1

```
MON: Dave, Sarah, Mark
TUE: Mark, John, Dave
WED: John, Sarah, Free
THU: Mark, Free, Free
FRI: Sarah, Mark, John
```

The system is only fair if each week it is generated the list the rotated from bottom to top so Sarah would move to the top of the list next time we allocated.

### Options
```
--config-file          CSV file with ordered list of names and days selected
--add-calendar-entries Automatically add the entries to the specified calendar
--google-calendar      Name of the Google Calendar to update
--date-of-monday       Date (YYYY-MM-DD) that the Monday starts on for this week
--number-of-spaces     Number os car park spaces there are
```

## Email notification system

TODO

## Future plans
- Upgrade to use web based choice so users can update the day preferences.
- Automation of list rotation i.e. moving the person from the botton to top.
- Automate email notification of new allocation.
