# Deck - a django card drawing project

Sometimes you want to draw a card from a deck in a group of people online. This project aims to provide a backend for that.

## Dependencies

* django
* djangorestframework 
* django-searchable-select (for the admin panel)
* django-braces (for permissions)

> Still not a full release

# API

The api is found at [host api path]/v2/[object]/ in the example.

##### Import into your project with with ease
```python
from django.conf.urls import include, url
#...
from deck import api_urls

urlpatterns = [
   # Rename "deck" with your desired location
   url(r'^deck/api/', include(api_urls)),
   #...
]
```

## Card object /cards/ lookup field 'pk'

Returns a list of cards like so

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "text": "Foo",
            "flavor_text": "Bar",
            "slug": "foo",
            "pk": 1,
            "user_created": 1,
            "date_edited": "2017-07-25T14:09:01.227000",
            "date_created": "2017-07-25T14:09:01.227000"
        }
    ]
}
```

#### Use /cards/[pk]/ to return a specific card. 

```json
{
    "text": "Xen",
    "flavor_text": "Hello world!",
    "slug": "xen",
    "pk": 2,
    "user_created": 1,
    "date_edited": "2017-07-25T14:11:49.311000",
    "date_created": "2017-07-25T14:11:49.311000"
}
```

##### Permissions
* Must be authenticated
* If not owner readonly is applied

##### Queries 
* ?since="%Y-%m-%d %H:%M:%S", check date_edited. Default not applied.
* ?search=[text], searchs card text. Default not applied.
* ?own=[true/false], check if requesting user created the card. Default True.

### Actions

#### Create Card
> 'POST' on /cards/ returns the created card

Looks for an object with 'text' and 'flavor_text' strings.

#### Delete Card
> 'DELETE' on /cards/[pk]

#### Update Card
> 'PUT' on /cards/[pk]/ returns the updated card

Looks for an object with 'text' and 'flavor_text' strings.

#### Copy Card
> 'GET' on /cards/[pk]/copy/ returns the copied card

This copies a card and sets the new cards 'user' as the request's user. Used to 'store' or 'favorite' cards.
Copying is preferred so card text will not change suprisingly on a user.

## Deck object /decks/ lookup field 'slug'

returns a list of decks like so

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "name": "Deck A",
            "slug": "deck-a",
            "cards": [
                1,
                2
            ],
            "cards_in_deck": [],
            "cards_in_discard": [],
            "card_displayed": null,
            "in_play": false,
            "user_created": 1
        }
    ]
}
```

#### Use /decks/[slug] to return a specific deck
> This will use an expanded serializer, where cards (Cards In Deck object type) are expanded into 'card' and 'count' objects
> Note: 'cards' and 'cards_indeck/discard' are different object types.

```json
{
    "name": "Deck B",
    "slug": "deck-b",
    "pk": 2,
    "cards_in_deck": [],
    "card_count": {
        "count__sum": 3
    },
    "cards": [
        {
            "card": {
                "text": "Foo",
                "flavor_text": "Bar",
                "pk": 1
            },
            "count": 2
        },
        {
            "card": {
                "text": "Xen",
                "flavor_text": "Hello world!",
                "pk": 2
            },
            "count": 1
        }
    ],
    "cards_in_discard": [],
    "card_displayed": null,
    "in_play": false,
    "date_edited": "2017-07-25T14:12:27.128000",
    "date_created": "2017-07-25T14:12:27.128000",
    "user_created": 1
}
```

##### Permissions
* Must be authenticated
* If not owner readonly is applied

##### Queries 
* ?since="%Y-%m-%d %H:%M:%S", check date_edited. Default not applied.
* ?search=[text], searchs deck names. Default not applied.
* ?own=[true/false], check if requesting user created the deck. Default True.
* ?in_play=[true/false], check if deck is being played. Default False. Only works for staff users.

### Actions

#### Add Cards
> 'POST' on /decks/[slug]/add_cards/ returns the deck in simple format.

Looks for a list of Card In Deck objects like so
```json
[
    { "card": {
        "text":"", 
        "flavor_text":"", 
        "pk":0
      }, 
      "count": 2
    } ...
]
```

If pk is invalid (send a -1 or a 0), this will preform a create on those cards. 
If you know pk, do not need to transmit text or flavor_text, just the pk.

#### Remove Cards 
> 'POST' on /decks/[slug]/remove_cards/ returns the deck in simple format.

Looks for a list of texts and cards, where it will delete all cards in the deck that match texts or pks
```json
{
	"texts": [
	    "Example text 1", 
	    "Example text 2"
	    ], 
	"cards": [1,2,4]
}
```

#### Change Card Count
> 'POST' on /decks/[slug]/change_count/ returns the deck in simple format.

Looks for a list of Card In Deck simple objects like so
```json
[
    { "card": 3, 
      "count": 2
    } ...
]
```

This ignore invalid card pks. If a count is < 1, the card will be totally removed from the deck.

#### Get a random card
> 'GET' on /decks/[slug]/get_random_card/

Gives a random card from the deck without altering anything

#### Play View
> 'GET' on /decks/[slug]/play_view/

Returns the deck in a semi-compressed view of only detail relevant for play.
```json
{
    "name": "Deck B",
    "slug": "deck-b",
    "cards_in_deck": [
        {
            "text": "Foo",
            "flavor_text": "Bar",
            "pk": 15
        }
    ],
    "cards_in_discard": [
        {
            "text": "Xen",
            "flavor_text": "Hello world!",
            "pk": 17
        }
    ],
    "card_displayed": {
        "text": "Foo",
        "flavor_text": "Bar",
        "pk": 16
    },
    "in_play": true,
    "user_created": 1
}
```

## Game Room object /rooms/ lookup field 'slug'

Returns a list of game rooms like so

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "name": "Game Room Alpha",
            "slug": "game-room-alpha",
            "user_created": 1,
            "players": [
                1
            ],
            "deck": 2,
            "open_draw": true
        }
    ]
}
```

#### Use /rooms/[slug]/ to return a specific game room 
> This will use an expanded serializer, where decks and cards are expanded into their full definitions.

```json
{
    "name": "Game Room Alpha",
    "slug": "game-room-alpha",
    "pk": 1,
    "user_created": 1,
    "players": [
        1
    ],
    "deck": {
        "name": "Deck B",
        "slug": "deck-b",
        "pk": 2,
        "cards_in_deck": [],
        "card_count": {
            "count__sum": 3
        },
        "cards": [
            {
                "card": {
                    "text": "Foo",
                    "flavor_text": "Bar",
                    "pk": 1
                },
                "count": 2
            },
            {
                "card": {
                    "text": "Xen",
                    "flavor_text": "Hello world!",
                    "pk": 2
                },
                "count": 1
            }
        ],
        "cards_in_discard": [],
        "card_displayed": null,
        "in_play": false,
        "date_edited": "2017-07-25T14:12:27.128000",
        "date_created": "2017-07-25T14:12:27.128000",
        "user_created": 1
    },
    "open_draw": true,
    "date_edited": "2017-07-25T14:14:27.706000",
    "date_created": "2017-07-25T14:14:23.112000"
}
```

##### Permissions
* Must be a player of the room (or pass the key in the query)
* If not owner readonly is applied

##### Queries 
* ?since="%Y-%m-%d %H:%M:%S", check date_edited. Default not applied.
* ?key=[text], key to the room. If user is authenticated and the key matches, they are added as a player to the room. If the user is anon, then access is checked against the allow_guests field of the room.
* ?own=[true/false], check if requesting user created the card. Default True.

### Actions

#### Get Current Displayed Card 
> 'GET' on /rooms/[slug]/get_current_card/

Returns the current displayed card from the deck

#### Draw Card 
> 'GET' on /rooms/[slug]/draw_card/

Discards the current card, draws a random card from the deck and sets is as the current displayed card, removes it from the deck, and returns the card.

> Permissions: Checks if user is a player of the room (including the key as described above) AND if they can draw. This is set in the room object, with open_draw. If this is false, only the owner can draw a card.

#### Start Game 
> 'GET' on /rooms/[slug]/start_game/

Sets the deck in play. Clears cards_in_deck, cards_in_discard, and card displaed. Explodes all cards (the ones with counts) in the deck, and inserts a temp card for each that it needs for the defined count.

Returns the deck in the 'in game' view.

> Permissions: User must be owner of room.

#### Stop Game 
> 'GET' on /rooms/[slug]/stop_game/

Clears cards_in_deck, cards_in_discard, and card displaed. Sets deck as not in play. Returns the game room. 

> Permissions: User must be owner of room.

#### Close Room 
> 'GET' on /rooms/[slug]/close_room/

Deletes the room.

> Permissions: User must be owner of room.

#### Reset Deck 
> 'GET' on /rooms/[slug]/reset_deck/

Keeps the deck in play. Moves all cards back to cards_in_deck.

Returns the deck in the 'in game' view.

> Permissions: User must be owner of room.

#### Play View
> 'GET' on /rooms/[slug]/play_view/

Returns the deck in a semi-compressed view of only detail relevant for play.
Same as is found in the 'decks' objects

## Settings
> Include in your settings.py file


#### Limit amount of objects a user can own
* MAX_ALLOWED_CARDS (default 2500)
* MAX_ALLOWED_DECKS (default 5)
* MAX_ALLOWED_ROOMS (default 2)

### We include a normal views.py file 
* This returns normal html
* You can include the urls.py by adding "from deck import urls as deck_urls" to your urls.py and including it
* Check our main project for the html file names it is looking for, and build your frontend
