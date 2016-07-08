name = 'ebaychecker'
version = '2.0.1b'


"""
Version Notes:

1.0.1b:
    Initial installed beta.
2.0.1b:
    This is our first real guy out the door.
    Super proud of this and happy to see it go.
    Can't wait to see what it becomes.


Completed:

    -Created and sorted entries into a second table when they have less than 3 ebay item returns



"""

"""
TODO:

    -Implement ajax calls for individual items

    -Add date sold

    -Determine how often an item sells

    -Reset price and shipping when 'reset' is clicked

    -Rebuild HTML so that extra tables can load (make it more elegant)

    -Reorder sub columns to match upper items

    -Grab bid price and time remaining from tech liquidators? -- Ajax

    -Remove hyphens from titles

    -Remove shipping column, add it to price.

    -Split Price into three prices, New Price, Used Price, and New other Price.
    This can be found from ['condition']['conditionDisplayName'][0]

    -Also Add max min values for all three prices

    -When modifications are made to an item, save for all future item searches of the same kind.
    This will require database work or a cache. Preferably both?

    -Rewrite buttons to call added function so we can have different actions without all the forms
"""