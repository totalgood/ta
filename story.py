#!/usr/bin/python
"""
A text adventure engine for willchatterr

Based on "Text Adventure Demo" by Al Sweigart (al@inventwithpython.com)
at https://github.com/totalgood/textadventuredemo
forked from https://github.com/asweigart/textadventuredemo
techniques and snippets from http://inventwithpython.com/blog/2014/12/11/
making-a-text-adventure-game-with-the-cmd-and-textwrap-python-modules/
"""
from __future__ import print_function
import os
import json
import cmd
import textwrap

FSM = 'the-magic-mission.json'

if os.path.isfile(FSM):
    f = open(FSM, 'r')
else:
    f = open(os.path.join('ta', FSM))
with f:
    world = json.load(f)
state = world['state']
    things = world['things']

"""
First, we will create some data structures for our game world.

The FSM (demo.json or the-magic-mission.json) files contain networks of states (nodes) copied, but refactored from the
textadventuredemo exmple by Al Sweigart. It may be helpful to include a 2-D "embedding" of the demo.json graph as Al did using ASCII art.
An embedding is just a projection that preserves connections and distances in a small number of dimensions, usually 2 or
3. This is 2-D embedding so it's just a flat map like you'd see in a D&D Dungeon Master's
play book.

"""


GROUND = 'GROUND'
SHOP = 'SHOP'
GROUNDDESC = 'GROUNDDESC'
SHORTDESC = 'SHORTDESC'
LONGDESC = 'LONGDESC'
TAKEABLE = 'TAKEABLE'
EDIBLE = 'EDIBLE'
DESCWORDS = 'DESCWORDS'

SCREEN_WIDTH = 80

location = 'castle tower'  # start in town square
inventory = []  # start with blank inventory
showFullExits = True


def displayLocation(loc):
    """A helper function for displaying an area's description and exits."""
    # Print the room name.
    print(loc)
    print('=' * len(loc))

    # Print the room's description (using textwrap.wrap())
    print('\n'.join(textwrap.wrap(state[loc]['DESC'], SCREEN_WIDTH)))

    # Print all the items on the ground.
    if len(state[loc][GROUND]) > 0:
        print()
        for item in state[loc][GROUND]:
            print(things[item][GROUNDDESC])

    # Print all the exits.
    exits = []
    for direction in ('north', 'south', 'east', 'west', 'up', 'down'):
        if direction in state[loc].keys():
            exits.append(direction.title())
    print()
    if showFullExits:
        for direction in ('north', 'south', 'east', 'west', 'up', 'down'):
            if direction in state[location]:
                print('%s: %s' % (direction.title(), state[location][direction]))
    else:
        print('Exits: %s' % ' '.join(exits))


def moveDirection(direction):
    """A helper function that changes the location of the player."""
    global location

    if direction in state[location]:
        print('You move to the %s.' % direction)
        location = state[location][direction]
        displayLocation(location)
    else:
        print('You cannot move in that direction')


def getAllDescWords(itemList):
    """Returns a list of "description words" for each item named in itemList."""
    itemList = list(set(itemList))  # make itemList unique
    descWords = []
    for item in itemList:
        descWords.extend(things[item][DESCWORDS])
    return list(set(descWords))

def getAllFirstDescWords(itemList):
    """Returns a list of the first "description word" in the list of
    description words for each item named in itemList."""
    itemList = list(set(itemList))  # make itemList unique
    descWords = []
    for item in itemList:
        descWords.append(things[item][DESCWORDS][0])
    return list(set(descWords))

def getFirstItemMatchingDesc(desc, itemList):
    itemList = list(set(itemList))  # make itemList unique
    for item in itemList:
        if desc in things[item][DESCWORDS]:
            return item
    return None

def getAllItemsMatchingDesc(desc, itemList):
    itemList = list(set(itemList))  # make itemList unique
    matchingItems = []
    for item in itemList:
        if desc in things[item][DESCWORDS]:
            matchingItems.append(item)
    return matchingItems


class TextAdventureCmd(cmd.Cmd):
    prompt = '\n>>> '

    # The default() method is called when none of the other do_*() command methods match.
    def default(self, arg):
        print('I do not understand that command. Type "help" for a list of commands.')

    # A very simple "quit" command to terminate the program:
    def do_quit(self, arg):
        """Quit the game."""
        return True  # this exits the Cmd application loop in TextAdventureCmd.cmdloop()

    def help_combat(self):
        print('Combat is not implemented in this program.')

    # These direction commands have a long (i.e. north) and short (i.e. n) form.
    def do_north(self, arg):
        """Go to the area to the north, if possible."""
        moveDirection('north')

    def do_south(self, arg):
        """Go to the area to the south, if possible."""
        moveDirection('south')

    def do_east(self, arg):
        """Go to the area to the east, if possible."""
        moveDirection('east')

    def do_west(self, arg):
        """Go to the area to the west, if possible."""
        moveDirection('west')

    def do_up(self, arg):
        """Go to the area upwards, if possible."""
        moveDirection('up')

    def do_down(self, arg):
        """Go to the area downwards, if possible."""
        moveDirection('down')

    # Since the code is the exact same, we can just copy the
    # methods with shortened names:
    do_n = do_north
    do_s = do_south
    do_e = do_east
    do_w = do_west
    do_u = do_up
    do_d = do_down

    def do_exits(self, arg):
        """Toggle showing full exit descriptions or brief exit descriptions."""
        global showFullExits
        showFullExits = not showFullExits
        if showFullExits:
            print('Showing full exit descriptions.')
        else:
            print('Showing brief exit descriptions.')

    def do_inventory(self, arg):
        """Display a list of the items in your possession."""

        if len(inventory) == 0:
            print('Inventory:\n  (nothing)')
            return

        # first get a count of each distinct item in the inventory
        itemCount = {}
        for item in inventory:
            if item in itemCount.keys():
                itemCount[item] += 1
            else:
                itemCount[item] = 1

        # get a list of inventory items with duplicates removed:
        print('Inventory:')
        for item in set(inventory):
            if itemCount[item] > 1:
                print('  %s (%s)' % (item, itemCount[item]))
            else:
                print('  ' + item)

    do_inv = do_inventory

    def do_take(self, arg):
        """"take <item> - Take an item on the ground."""

        # put this value in a more suitably named variable
        itemToTake = arg.lower()

        if itemToTake == '':
            print('Take what? Type "look" the items on the ground here.')
            return

        cantTake = False

        # get the item name that the player's command describes
        for item in getAllItemsMatchingDesc(itemToTake, state[location][GROUND]):
            if things[item].get(TAKEABLE, True) == False:
                cantTake = True
                continue  # there may be other items named this that you can take, so we continue checking
            print('You take %s.' % (things[item][SHORTDESC]))
            state[location][GROUND].remove(item)  # remove from the ground
            inventory.append(item)  # add to inventory
            return

        if cantTake:
            print('You cannot take "%s".' % (itemToTake))
        else:
            print('That is not on the ground.')

    def do_drop(self, arg):
        """"drop <item> - Drop an item from your inventory onto the ground."""

        # put this value in a more suitably named variable
        itemToDrop = arg.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)

        # find out if the player doesn't have that item
        if itemToDrop not in invDescWords:
            print('You do not have "%s" in your inventory.' % (itemToDrop))
            return

        # get the item name that the player's command describes
        item = getFirstItemMatchingDesc(itemToDrop, inventory)
        if item is not None:
            print('You drop %s.' % (things[item][SHORTDESC]))
            inventory.remove(item)  # remove from inventory
            state[location][GROUND].append(item)  # add to the ground

    def complete_take(self, text, line, begidx, endidx):
        possibleItems = []
        text = text.lower()

        # if the user has only typed "take" but no item name:
        if not text:
            return getAllFirstDescWords(state[location][GROUND])

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for item in list(set(state[location][GROUND])):
            for descWord in things[item][DESCWORDS]:
                if descWord.startswith(text) and things[item].get(TAKEABLE, True):
                    possibleItems.append(descWord)

        return list(set(possibleItems))  # make list unique

    def complete_drop(self, text, line, begidx, endidx):
        possibleItems = []
        itemToDrop = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)

        for descWord in invDescWords:
            if line.startswith('drop %s' % (descWord)):
                return []  # command is complete

        # if the user has only typed "drop" but no item name:
        if itemToDrop == '':
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(text):
                possibleItems.append(descWord)
        return list(set(possibleItems))  # make list unique

    def do_look(self, arg):
        """Look at an item, direction, or the area:
        "look" - display the current area's description
        "look <direction>" - display the description of the area in that direction
        "look exits" - display the description of all adjacent areas
        "look <item>" - display the description of an item on the ground or in your inventory"""

        lookingAt = arg.lower()
        if lookingAt == '':
            # "look" will re-print the area description
            displayLocation(location)
            return

        if lookingAt == 'exits':
            for direction in ('north', 'south', 'east', 'west', 'up', 'down'):
                if direction in state[location]:
                    print('%s: %s' % (direction.title(), state[location][direction]))
            return

        if lookingAt in ('north', 'west', 'east', 'south', 'up', 'down', 'n', 'w', 'e', 's', 'u', 'd'):
            if lookingAt.startswith('n') and 'north' in state[location]:
                print(state[location]['north'])
            elif lookingAt.startswith('w') and 'west' in state[location]:
                print(state[location]['west'])
            elif lookingAt.startswith('e') and 'east' in state[location]:
                print(state[location]['east'])
            elif lookingAt.startswith('s') and 'south' in state[location]:
                print(state[location]['south'])
            elif lookingAt.startswith('u') and 'up' in state[location]:
                print(state[location]['up'])
            elif lookingAt.startswith('d') and 'down' in state[location]:
                print(state[location]['down'])
            else:
                # FIXME: Use dict associating regexes with canonical spellings, which should be used here
                print('There is nothing to the {}.'.format(lookingAt))
            return

        # see if the item being looked at is on the ground at this location
        item = getFirstItemMatchingDesc(lookingAt, state[location][GROUND])
        if item is not None:
            print('\n'.join(textwrap.wrap(things[item][LONGDESC], SCREEN_WIDTH)))
            return

        # see if the item being looked at is in the inventory
        item = getFirstItemMatchingDesc(lookingAt, inventory)
        if item is not None:
            print('\n'.join(textwrap.wrap(things[item][LONGDESC], SCREEN_WIDTH)))
            return

        print("You do not see '{}' on the ground nearby and you aren't carrying it with you.".format(lookingAt))

    def complete_look(self, text, line, begidx, endidx):
        possibleItems = []
        lookingAt = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)
        groundDescWords = getAllDescWords(state[location][GROUND])
        shopDescWords = getAllDescWords(state[location].get(SHOP, []))

        for descWord in invDescWords + groundDescWords + shopDescWords + [
                'north', 'south', 'east', 'west', 'up', 'down']:
            if line.startswith('look %s' % (descWord)):
                return []  # command is complete

        # if the user has only typed "look" but no item name, show all items on ground, shop and directions:
        if lookingAt == '':
            possibleItems.extend(getAllFirstDescWords(state[location][GROUND]))
            possibleItems.extend(getAllFirstDescWords(state[location].get(SHOP, [])))
            for direction in ('north', 'south', 'east', 'west', 'up', 'down'):
                if direction in state[location]:
                    possibleItems.append(direction)
            return list(set(possibleItems))  # make list unique

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for descWord in groundDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        # otherwise, get a list of all "description words" for items for sale at the shop (if this is one):
        for descWord in shopDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        # check for matching directions
        for direction in ('north', 'south', 'east', 'west', 'up', 'down'):
            if direction.startswith(lookingAt):
                possibleItems.append(direction)

        # get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        return list(set(possibleItems))  # make list unique

    def do_talk_to(self, arg):
        """Start a conversation with an element of the game."""
        if "characters" not in state[location]:
            print("You can only talk to animate objects!")
            return

        arg = arg.lower()

        for item in state[location]["characters"]:
            if arg == 'item':
                print('\n'.join(textwrap.wrap(things[item][LONGDESC], SCREEN_WIDTH)))

    def do_list(self, arg):
        """List the items for sale at the current location's shop. "list full" will show details of the items."""
        if SHOP not in state[location]:
            print("You can only list items for sale in a shop, but this isn't a shop.")
            return

        arg = arg.lower()

        print('For sale:')
        for item in state[location][SHOP]:
            print('  - %s' % (item))
            if arg == 'full':
                print('\n'.join(textwrap.wrap(things[item][LONGDESC], SCREEN_WIDTH)))


    def do_buy(self, arg):
        """"buy <item>" - buy an item at the current location's shop."""
        if SHOP not in state[location]:
            print('This is not a shop.')
            return

        itemToBuy = arg.lower()

        if itemToBuy == '':
            print('Buy what? Type "list" or "list full" to see a list of items for sale.')
            return

        item = getFirstItemMatchingDesc(itemToBuy, state[location][SHOP])
        if item is not None:
            # NOTE - If you wanted to implement money, here is where you would add
            # code that checks if the player has enough, then deducts the price
            # from their money.
            print('You have purchased %s' % (things[item][SHORTDESC]))
            inventory.append(item)
            return

        print('"%s" is not sold here. Type "list" or "list full" to see a list of items for sale.' % (itemToBuy))

    def complete_buy(self, text, line, begidx, endidx):
        if SHOP not in state[location]:
            return []

        itemToBuy = text.lower()
        possibleItems = []

        # if the user has only typed "buy" but no item name:
        if not itemToBuy:
            return getAllFirstDescWords(state[location][SHOP])

        # otherwise, get a list of all "description words" for shop items matching the command text so far:
        for item in list(set(state[location][SHOP])):
            for descWord in things[item][DESCWORDS]:
                if descWord.startswith(text):
                    possibleItems.append(descWord)

        return list(set(possibleItems))  # make list unique


    def do_sell(self, arg):
        """"sell <item>" - sell an item at the current location's shop."""
        if SHOP not in state[location]:
            print('This is not a shop.')
            return

        itemToSell = arg.lower()

        if itemToSell == '':
            print('Sell what? Type "inventory" or "inv" to see your inventory.')
            return

        for item in inventory:
            if itemToSell in things[item][DESCWORDS]:
                # NOTE - If you wanted to implement money, here is where you would add
                # code that gives the player money for selling the item.
                print('You have sold %s' % (things[item][SHORTDESC]))
                inventory.remove(item)
                return

        print('You do not have "%s". Type "inventory" or "inv" to see your inventory.' % (itemToSell))


    def complete_sell(self, text, line, begidx, endidx):
        if SHOP not in state[location]:
            return []

        itemToSell = text.lower()
        possibleItems = []

        # if the user has only typed "sell" but no item name:
        if not itemToSell:
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for inventory items matching the command text so far:
        for item in list(set(inventory)):
            for descWord in things[item][DESCWORDS]:
                if descWord.startswith(text):
                    possibleItems.append(descWord)

        return list(set(possibleItems))  # make list unique


    def do_eat(self, arg):
        """"eat <item>" - eat an item in your inventory."""
        itemToEat = arg.lower()

        if itemToEat == '':
            print('Eat what? Type "inventory" or "inv" to see your inventory.')
            return

        cantEat = False

        for item in getAllItemsMatchingDesc(itemToEat, inventory):
            if things[item].get(EDIBLE, False) == False:
                cantEat = True
                continue  # there may be other items named this that you can eat, so we continue checking
            # NOTE - If you wanted to implement hunger levels, here is where
            # you would add code that changes the player's hunger level.
            print('You eat %s' % (things[item][SHORTDESC]))
            inventory.remove(item)
            return

        if cantEat:
            print('You cannot eat that.')
        else:
            print('You do not have "%s". Type "inventory" or "inv" to see your inventory.' % (itemToEat))


    def complete_eat(self, text, line, begidx, endidx):
        itemToEat = text.lower()
        possibleItems = []

        # if the user has only typed "eat" but no item name:
        if itemToEat == '':
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for edible inventory items matching the command text so far:
        for item in list(set(inventory)):
            for descWord in things[item][DESCWORDS]:
                if descWord.startswith(text) and things[item].get(EDIBLE, False):
                    possibleItems.append(descWord)

        return list(set(possibleItems))  # make list unique


if __name__ == '__main__':
    print(FSM.split('.')[0].upper().replace('-', ' ').replace('_', ' '))
    print('==================')
    print()
    displayLocation(location)
    TextAdventureCmd().cmdloop()

