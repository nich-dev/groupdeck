# Deck - a django card drawing project

Sometimes you want to draw a card from a deck in a group of people online. This project aims to provide a backend for that.

## Dependencies

* django
* djangorestframwork
* django-searchable-select

> django-rest-auth is required right now as the user object is in the app. This will be removed.

## Major bugs/TODOs/Road Maps :camel:

* Remove the User object from this app
* Do CREATE and UPDATE statements on objects
* Further refine and expand the Card object
* Build views

# API

The api is found at [host]/deck/v2/[object]/

> Creates and Updates are all broken at the moment, objects must be built through the admin panel

## Card object /cards/ lookup field 'pk'

Returns a list of cards like so

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "text": "Foo",
            "slug": "foo",
            "pk": 1,
            "date_edited": "2017-07-24T22:20:37.029488Z",
            "date_created": "2017-07-24T22:20:37.029583Z"
        }
    ]
}
```

> use /cards/[pk]/ to return a specific card. 

> Permissions: must be authenticated

> Queries: ?since="%Y-%m-%d %H:%M:%S", check date_edited. ?search=[text], searchs card text.

## Deck object /decks/ lookup field 'slug'

returns a list of cards like so

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "name": "Test Deck A",
            "slug": "test-deck-a",
            "cards": [
                1,
                2,
                3,
                4
            ],
            "cards_in_discard": [],
            "card_displayed": null,
            "in_play": false,
            "user_created": 1
        }
    ]
}
```

> use /decks/[slug] to return a specific deck, this will use an expanded serializer, where cards are expanded into 'text' and 'pk' objects

> Permissions: Must be authenticated, If not owner of deck it will be read-only. Applies to actions. 

> Queries: ?since="%Y-%m-%d %H:%M:%S", check date_edited. ?in_play=[true/false], checks if in_play. Must be staff user. ?search=[text], searchs deck names. ?owned=[true/false], checks if user is owner.

### Actions

#### Add Cards /decks/[slug]/add_cards/

Adds cards using a POST with list of text and count of cards

```json
[
{"text": "Example card 1", "count": 2}, 
{"text": "Example card 2", "count": 1}
]
```
#### Remove Cards /decks/[slug]/remove_cards/

Removes cards using a POST with on field "texts", which is a list of texts you want removed
> This will remove all cards with this name in the deck

```json
{"texts": [
    "Example text 1", 
    "Example text 2"]
}
```

### Get a random card /decks/[slug]/get_random_card/

Gives a random card from the deck without altering anything

## Game Room object /rooms/ lookup field 'slug'

Returns a list of game rooms like so

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "name": "Test Game Room 1",
            "slug": "test-game-room-1",
            "user_created": 1,
            "players": [
                1
            ],
            "deck": null,
            "deck_parent": 1,
            "open_draw": true
        }
    ]
}
```

> use /rooms/[slug]/ to return a specific game room. This will use an expanded serializer, where decks and cards are expanded into their full definitions.

> Permissions: If not owner of deck it will be read-only. If user is not a player in the game room, no access is allowed. You can use the ?key=[secret] query to allow a guest through (if allow_guests is set) or to have a authenticated player join the room.

> Queries: ?since="%Y-%m-%d %H:%M:%S", check date_edited. 

### Actions

#### Get current displayed card /rooms/[slug]/get_current_card/

Returns the current displayed card from the deck

#### Draw card from deck /rooms/[slug]/draw_card/

Discards the current card, draws a random card from the deck and sets is as the current displayed card, removes it from the deck, and returns the card.

> Permissions: Checks if user is a player of the room (including the key as described above) AND if they can draw. This is set in the room object, with open_draw. If this is false, only the owner can draw a card.

#### Start game /rooms/[slug]/start_game/

Deep copies the room's deck_parent to deck, and sets it as in play. Returns the game room. Allows the above actions.

> Permissions: User must be owner of room.

#### Stop game /rooms/[slug]/stop_game/

Removes the room's in play deck. Returns the game room. 

> Permissions: User must be owner of room.

#### Close room /rooms/[slug]/close_room/

Delete's the room.

> Permissions: User must be owner of room.

#### Reset deck /rooms/[slug]/reset_deck/

Removes current deck and deep copies the room's deck_parent to deck, and sets it as in play. Returns the game room.

> Permissions: User must be owner of room.

## User object /users/ lookup field 'username'

> Will be removed, given to your app to manage