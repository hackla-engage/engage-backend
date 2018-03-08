import calendar

def time_check(datetime_to_check_against, unixtime, direction):
    '''
    Checks to see if a timestamp is either before or after 
    another timestamp. Returns a boolean
    ''' 

    unixtime_to_check_against = calendar.timegm(datetime_to_check_against.utctimetuple())
    if direction == "before":
        return unixtime < unixtime_to_check_against
    elif direction == "after":
        return unixtime > unixtime_to_check_against
    else:
        raise Exception("Direction can only be 'before' or 'after'")
