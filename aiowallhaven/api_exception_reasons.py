
TooManyRequests = '''
    Too many requests to the server, please try again later
'''

Unauthorized = '''
    Invalid API key. Please provide a valid API key.
    You can regenerate your API key at https://wallhaven.cc/settings/account
'''

GeneralError = '''
    The request to open {session} failed with the following HTTP code:
    {status_code}
'''

ValueErrorPurity = '''
    No valid purity filter found. 
    Only 'sfw', 'sketchy', and 'nsfw' are considered to be valid purity filters.
'''

ValueErrorCategory = '''
    No valid category filter found. 
    Only 'general', 'anime', and 'people' are considered to be valid category filters.
'''

ValueErrorSorting = '''
    Invalid parameter was provided. 
    Only "date_added", "relevance", "random", "favorites", "toplist" 
    are considered to be valid arguments.
'''

ValueErrorOrder = '''
    Invalid order method was provided. 
    Only 'desc' and 'asc' are considered to be valid arguments.
'''

ValueErrorToprange = '''
    Invalid parameter was provided. 
    Only "1d", "3d", "1w", "1M", "3M", "6M", "1y" are considered to be valid arguments.
'''

ValueErrorAtleast = '''
    Invalid screen resolution was provided. 
    Valid formats: "1920x1080", "3080x2140" eg.
'''

ValueErrorResolutions = '''
    At least one of provided resolutions is incorrect.
'''

ValueErrorResolutionsFormat = '''
    The argument neither a Python list nor string. 
    Valid format: ['1920x1080', '2560x1600']. 
    Single screen ratio can be passed as a string: '1920x1080'
'''

ValueErrorRatios = '''
    The provided ratio is incorrect. 
    Example of a valid format: '16x9' or ['16x9']
'''

ValueErrorRatiosFormat = '''
    The argument neither a Python list nor string. 
    Valid format: ['16x9', '16x10']. 
    Single screen ratio can be passed as a string: '16x9'.
'''
