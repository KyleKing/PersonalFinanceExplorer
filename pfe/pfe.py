"""Personal Finance Application.

Run with:

```
from pfe.pfe import PFEApp

if __name__ == '__main__':
    PFEApp().run(debug=True)
```

"""

from dash_charts import appUtils

from .profile import TabProfile


class PFEApp(appUtils.TabbedDashApp):
    """Personal Finance Explorer Application."""

    def defineTABS(self):
        """Define the tabs."""
        return [
            TabProfile(self.app),
        ]
