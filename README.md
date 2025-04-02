# Overview

`asset_explorer` is a python library which exposes a Qt widget designed to display
and allow the interaction of `asset_composition.Asset` objects in a hierarchical form.

# Quick Start

For the quickest way to get started you can simply run the example below. This
creates an empty configuration (thus no traits or discovery plugins will be
available) and launches the explorer widget. With the explorer widget open, you can
manually add plugin paths.

```python
import asset_explorer

configuration = asset_explorer.Configuration()
asset_explorer.launch(configuration=configuration)
```

# Running the Examples

The `asset_explorer` module comes with three examples:

- `examples/local_drive`: This will launch the explorer to search for files/folders
on your local disk. It will set the search root as the location of the asset_explorer
module.

- `examples/paleobio`: This example shows how traits can be used to bind to 
a REST API and represent dinosaur taxonomy as assets. This will pull data down from
paleobio.org and show the taxonomy data as assets. It is also a simple demonstration
of implementing threading support to prevent UI blocking.

- `examples/maya_assets`: This example assumes the user has Autodesk Maya 2025 (or 
higher), and is an example of how to use this library in an embedded interpreter 
environment.

### Getting Setup

In order to run the examples you **must** install the required python dependencies, 
which are :

- factories
- scribble
- xcomposite
- signalling
- qt.py
- qfactory
- qtility

All of these can be installed using `pip install <modulename>`. 

The `asset_explorer` library also has a non-pip dependency on the `asset_composition`
module. Therefore you should also download that and ensure it is placed in a 
location which is importable.

You **must** also place the `asset_composition` module in a location where your python
interpreter can import it. Typically, this is in the site-packages folder of your python
or virtual env. Alternatively you can use `sys.path.append("")` within your 
script/main.py to add the folder containing the module to the python path so that
it is importable. 

Once this is setup you can execute the `main.py` as an argument of your python 
executable, such as: `python.exe c:/my_python/examples/local_drive/main.py`

If you are wanting to try the `examples/maya_asset` example then you must install 
these using the `pip` which comes with Maya. Alternatively you can download all 
the above libraries from pypi.org directly and place them in your `user/scripts` location.

To run the maya example you should open the `main.py` file in the `maya script editor`
and execute that. 

# Configuration

The `Asset Explorer` utilises the `asset_composition` module for defining what gets
displayed and what level of interaction any given item exposes. For this reason you
need to declare a `Configuration`.

The `asset_composition` module comes with a `Configuration` class, however the
`asset_explorer` includes its own `Configuration` class which extends the one from
`asset_composition` and includes various ui settings too. Therefore, when defining
a `Configuration` for the `asset_explorer` you should use `asset_explorer.Configuration`.

To create a configuration, you can use the code below. In this case we're instancing
a `asset_explorer.Configuration` but we're adding the built in traits and discovery
mechanism's which come with `asset_composition` to serve as an example.

```python
import os
import asset_composition
import asset_explorer

# -- Create a new configuration
configuration = asset_explorer.Configuration()

# -- Add the built in traits
configuration.traits.add_path(
    os.path.join(
        os.path.dirname(asset_composition.__file__),
        "plugins",
        "filesystem",
        "traits",
    ),
)
configuration.discovery.add_path(
    os.path.join(
        os.path.dirname(asset_composition.__file__),
        "plugins",
        "filesystem",
        "discovery",
    ),
)

# -- Search roots are locations where we will look for assets from and search
# -- for assets from. The Configuration class gives us a `add_to` and `remove_from`
# -- method to interact with these.
configuration.add_to(
    "search_roots",
    "C:/",
)
asset_explorer.launch(configuration=configuration)
```

# Going Deeper

Whilst the asset explorer comes with trait, view and discovery plugins for interacting
with the users local file system out the box, its not limited to that paradigm at all.

The asset explorer will simply ask the `asset_composition.Asset` object for its children,
label, and actions. Therefore you can implement your own traits that interact with data
in completely different ways.

For instance, its entirely feasible to implement traits which interact with an online
Rest API for data, and then present the results. This can be seen in the
examples/paleobio directory.

Equally what we think of as an asset could be an object within an application instance
or a file, or a piece of text. What we want to define as an asset simply comes down
to the traits being implemented - the `Asset Explorer` will then simply visualise those.

# Implementing Custom Views

It is critical to understand that `Traits`, `Discovery` mechanisms and `Views` are all
implemented as discreet plugins into the framework. It is this pattern which allows the
library to be so flexible in what it shows.

You can read about implementing `Trait` and `Discovery` plugins within the
`asset_composition` documentation. However, with the `asset_explorer` you can also
`View` plugins. This allow you to tailor what is visible to the user.

By default the tool has three views:

    * Folder View
    * Search View
    * Favourites View

The `Folder View` shows a hierarchy view starting from the project roots. The `Search View`
will allow you to only see the items that match the given search criteria (which are the
results of `Discovery` plugins). The `Favourites` view allows you to see any items
marked as a favourite - which is done through a `Favourites Trait` provided by the
`asset_explorer`.

To implement you're own view is just a case of inheriting from `asset_explorer.View` and
implementing the populate method.

```python
import typing
import asset_explorer
import asset_composition


# noinspection PyUnresolvedReferences
class SceneView(asset_explorer.View):
    """
    This view will present the user with any items which have been marked
    as favourites.
    """
    identifier = "Scene View"

    def __init__(self, *args, **kwargs):
        super(SceneView, self).__init__(*args, **kwargs)
        self.populate()

    def populate(self, filter_value: typing.AnyStr | None = None):

        # -- Clear the current contents before we start repopulating
        self.clear()

        # -- Ensure we're always working with a string
        # -- filter
        filter_value = filter_value or ""

        # -- Cycle the favourites we have stored
        for asset in asset_composition.search(filter_value or "*", trait_factory=self.app.trait_factory, discovery_factory=self.app.discovery_factory):

            # -- Now that we know we need to display this item we
            # -- can instance the item object and add it as a top
            # -- level item
            item = asset_explorer.AssetItem(asset, app=self.app)
            self.addTopLevelItem(item)

            # -- Ensure we populate its children. This is important
            # -- as it will show a chevron if it has children.
            item.populate_children()
```

The `asset_explorer.View` is a QTreeWidget which has a `.app` property which gives
access to the `Explorer` widget it is part of. From the explorer widget you have
direct access to the config (`.app.config`) as well as the three factories:

    * view.app.config.traits
    * view.app.config.discoveries
    * view.app.views

When adding items to the custom view, you should always add `asset_explorer.AssetItem`
objects and not native `QTreeWidgetItem` items. The `AssetItem` will store a weak
reference to the asset its operating on and manage the data in readiness for the view
delegate to draw.

# Examples

## filesystem

This is intended to be the most simplistic example and it does nothing more than
instances the Explorer widget, adds a search root and shows the window. This uses
all the built-in plugins.

## paleobio

This is a demonstration of an asset type that is drastically different to files
present on disk. Instead this interacts with the paleobiodb.org RestAPI and queries
taxonomy data. Its a good example of a completely different expectation of what an
asset might be.

It also demonstrates a very simplistic approach to managing threading when traits
might take time to resolve data and you need to keep the ui feeling snappy.

## maya_assets

This example will only run within the scope of Autodesk Maya and shows how the tool
can be utilised within an embedded interpreter and interact with application specific
data through its own python api.
