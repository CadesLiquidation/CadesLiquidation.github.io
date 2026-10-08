# Your site settings

This website reads your business details from one file: **`config.json`**
(sitting next to this guide in the repository). It's already filled in —
your name, phone number, and links appear all over the site automatically.
If anything changes, edit the file as described below.

## How to edit it on GitHub.com

1. Go to your repository on GitHub.com and click the **`config.json`** file.
2. Click the **pencil icon** (Edit) in the top-right of the file view.
3. Change the values on the right-hand side of each line. Keep the
   quotation marks around your text.
4. Scroll down and click **Commit changes**. The live site updates in a
   minute or two.

## What each field does

| Field | Where it shows up |
|---|---|
| `businessName` | Top of every page, page titles, footer |
| `tagline` | Under the store name on the home page |
| `ratingText` | Under the tagline on the home page |
| `phone` | The number buyers see on "Call or text" buttons |
| `phoneHref` | Makes the call buttons actually dial on phones (format: `tel:+1` + number, no spaces or dashes) |
| `facebookGroupUrl` | "Facebook group" buttons — your group's web address |
| `facebookGroupName` | Next to the Facebook buttons |
| `aboutText` | The About page |
| `serviceArea` | Home page and About page |

## Tips

- Leave a field as `""` (empty quotes) to hide that button. For example,
  if `phone` is empty, no call buttons appear on the site.
- `phone` is what people *see*; `phoneHref` is what makes it *work* when
  tapped on a phone. Fill in both.
- Don't touch anything else in the file — just the text between the quotes.
- The appliance listings themselves update automatically from the
  inventory file; you don't need to edit them by hand.
- Each listing's "View this listing on Facebook Marketplace" button comes
  from the inventory data and updates automatically.
