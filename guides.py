# Buying-guide content for Cade's Liquidation.
# Pure data — rendered by build_guides() in generate_site.py.
# Each guide: slug, title, h1, meta, intro (html), sections [(heading, html)],
# category (matches a catalog category, or None), cta (bool).

GUIDES = [
    {
        "slug": "scratch-and-dent",
        "title": "What Is Scratch-and-Dent? | Cade's Liquidation",
        "h1": "What does \u201cscratch-and-dent\u201d actually mean?",
        "meta": ("What scratch-and-dent appliances are, why they cost so much less than "
                 "retail, and what to expect \u2014 from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": None,
        "intro": (
            "<p>A scratch-and-dent appliance is a <strong>brand-new unit with cosmetic "
            "damage</strong> \u2014 a dented side panel, a scratched door, a scuff from a "
            "forklift. It was never used. It works exactly like the pristine one on the "
            "showroom floor. It just can't be sold at full price anymore, so it sells "
            "for hundreds less.</p>"
            "<p>That's the entire business model behind Cade's Liquidation: buy these "
            "units by the truckload, test every one, and sell them for a fraction of "
            "retail.</p>"
        ),
        "sections": [
            ("Why is it so much cheaper?",
             "<p>When a $1,500 refrigerator gets a dent in the side during shipping, the "
             "big-box store can't put it back on the floor at full price. It goes to a "
             "liquidation sale, where buyers bid on entire truckloads. The per-unit cost "
             "ends up far below wholesale \u2014 and that discount gets passed on to you. "
             "It's common to save <strong>30% or more off retail</strong>, sometimes "
             "over half.</p>"),
            ("What does the damage actually look like?",
             "<p>Almost always, it's on the <strong>sides or back</strong> \u2014 the parts "
             "you never see once the appliance is installed. A refrigerator slides "
             "between cabinets. A washer sits in a laundry room. A range backs up to a "
             "wall. The front \u2014 the part you actually look at every day \u2014 is "
             "usually flawless.</p>"
             "<p>Every listing on this site has real photos of the actual unit, so you "
             "can see exactly what you're getting before you ever come look at it.</p>"),
            ("What's <em>not</em> wrong with them",
             "<p>Scratch-and-dent does <strong>not</strong> mean used, refurbished, or "
             "repaired. These units were never owned by anyone. Nothing was broken and "
             "fixed. The compressor, the motor, the heating element \u2014 all factory-new, "
             "all covered by the same 14-day money-back guarantee as everything else "
             "here.</p>"),
            ("How every unit gets checked",
             "<p>Before anything gets listed, it's unboxed, plugged in, and run through "
             "its paces \u2014 washers run a cycle, dryers heat up, refrigerators get "
             "cold, ovens hit temperature. If a unit doesn't work like new, it doesn't "
             "get listed. Cosmetic damage is the deal; mechanical problems are a "
             "deal-breaker.</p>"),
        ],
        "cta": True,
    },
    {
        "slug": "washers",
        "title": "Washer Buying Guide | Cade's Liquidation",
        "h1": "Washer buying guide",
        "meta": ("Top-load vs. front-load, what to check, and how to measure \u2014 a practical "
                 "washer buying guide from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": "Washers",
        "intro": (
            "<p>A washing machine is one of those purchases you live with for a decade, "
            "so it's worth spending ten minutes learning what matters. The good news: "
            "washers are simple machines, and there are only a few decisions that "
            "actually count.</p>"
        ),
        "sections": [
            ("Top-load vs. front-load",
             "<p><strong>Top-load with agitator</strong> \u2014 the classic. Fast cycles, "
             "simple to use, and you can toss in a forgotten sock mid-cycle. Harder on "
             "clothes and uses more water.</p>"
             "<p><strong>Top-load with impeller</strong> (no agitator) \u2014 gentler and "
             "roomier than agitator models, but longer cycles.</p>"
             "<p><strong>Front-load</strong> \u2014 the most efficient and gentlest on "
             "clothes, with the biggest capacities. The trade-off: you should leave the "
             "door cracked between loads so the gasket dries out.</p>"),
            ("What to check before you buy",
             "<ul>"
             "<li>Run a quick cycle \u2014 it should fill, agitate or tumble, drain, and spin without banging around.</li>"
             "<li>On front-loaders, check the door gasket for tears or mold.</li>"
             "<li>Make sure the hoses (or hookups) are included or plan to buy new ones \u2014 they're cheap insurance.</li>"
             "<li>Excessive shaking during spin usually means an unbalanced load, not a bad machine \u2014 but it shouldn't walk across the floor.</li>"
             "</ul>"),
            ("Measuring your space",
             "<p>Standard washers are about <strong>27 inches wide</strong>. Measure your "
             "laundry nook's width, then measure the <strong>doorways and hallways</strong> "
             "the machine has to travel through \u2014 that's the measurement people "
             "forget. For top-loaders, check there's clearance above to open the lid; "
             "for front-loaders, make sure the door can swing open fully.</p>"),
            ("Capacity",
             "<p>Measured in cubic feet. Around <strong>4.5 cu. ft. and up</strong> "
             "handles a family comfortably, including bulky items like comforters. "
             "Smaller households can get by with less, but bigger tubs are more "
             "forgiving \u2014 overstuffing is what wears machines out.</p>"),
        ],
        "cta": True,
    },
    {
        "slug": "dryers",
        "title": "Dryer Buying Guide: Gas vs. Electric | Cade's Liquidation",
        "h1": "Dryer buying guide",
        "meta": ("Gas vs. electric dryers, what to check, and how to measure \u2014 a practical "
                 "dryer buying guide from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": "Dryers",
        "intro": (
            "<p>Dryers are even simpler than washers \u2014 but there's one decision that "
            "matters more than everything else combined: <strong>gas or electric</strong>. "
            "Get that right and the rest is easy.</p>"
        ),
        "sections": [
            ("Gas vs. electric \u2014 the big decision",
             "<p><strong>Gas dryers</strong> cost more up front but are cheaper to run, "
             "and they heat up faster. They need a gas line in the laundry room.</p>"
             "<p><strong>Electric dryers</strong> cost less to buy but need a "
             "<strong>240-volt outlet</strong> \u2014 not a regular wall plug.</p>"
             "<p>The practical rule: <strong>buy whatever your laundry room already "
             "has</strong>. Running a new gas line or wiring a 240V circuit costs far "
             "more than any savings from switching fuel types. If you're not sure what "
             "you have, text a photo of the hookups and we'll help you figure it out.</p>"),
            ("What to check before you buy",
             "<ul>"
             "<li>It should produce real heat on every heat setting \u2014 no heat usually means a dead heating element or igniter.</li>"
             "<li>The drum should turn smoothly without grinding or squealing.</li>"
             "<li>Check the lint trap slides in and out and isn't cracked.</li>"
             "<li>Make sure the timer or electronic controls advance through a cycle.</li>"
             "</ul>"),
            ("Measuring your space",
             "<p>Like washers, standard dryers are about <strong>27 inches wide</strong>. "
             "Allow a few extra inches of depth for the vent hose behind the machine, "
             "and check the door swing. If you're buying a washer and dryer together, "
             "matching widths look right and fit the space evenly.</p>"),
            ("Venting",
             "<p>Almost every home dryer in the US is <strong>vented</strong> \u2014 it "
             "needs a duct to the outside. Keep that duct short and clean; a clogged "
             "vent is the #1 reason dryers underperform and the #1 laundry-room fire "
             "hazard.</p>"),
        ],
        "cta": True,
    },
    {
        "slug": "refrigerators",
        "title": "Refrigerator Buying Guide | Cade's Liquidation",
        "h1": "Refrigerator buying guide",
        "meta": ("French door vs. side-by-side vs. top-freezer, what to check, and how to measure "
                 "\u2014 a practical refrigerator buying guide from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": "Refrigerators",
        "intro": (
            "<p>The refrigerator is the hardest-working appliance in your home \u2014 it "
            "runs 24/7 for a decade or more. Here's how to pick the right type, check "
            "that it works, and make sure it actually fits through your front door.</p>"
        ),
        "sections": [
            ("The four types",
             "<p><strong>French door</strong> \u2014 double doors up top, freezer drawer "
             "below. The most popular style: wide shelves fit platters and pizza boxes, "
             "and you only open half the fridge at a time.</p>"
             "<p><strong>Side-by-side</strong> \u2014 fridge on one side, freezer on the "
             "other. Narrow doors are great for tight kitchens, but wide items don't fit.</p>"
             "<p><strong>Top-freezer</strong> \u2014 the classic. The most refrigerator "
             "for the money and the most reliable layout ever made.</p>"
             "<p><strong>Bottom-freezer</strong> \u2014 fresh food at eye level, freezer "
             "in a pull-out drawer below. A nice middle ground.</p>"),
            ("What to check before you buy",
             "<ul>"
             "<li>It should be genuinely cold \u2014 fridge around 37\u00b0F, freezer at 0\u00b0F. Every unit here is plugged in and tested before listing.</li>"
             "<li>If it has an ice maker or water dispenser, run both.</li>"
             "<li>Check the door seals: close the door on a dollar bill \u2014 if it slides out easily, the seal is weak.</li>"
             "<li>Look for excessive frost in the freezer, which can signal a seal or defrost issue.</li>"
             "</ul>"),
            ("Measuring your space",
             "<p>This is where most refrigerator purchases go wrong. Measure <strong>width, "
             "height (including the hinge!), and depth</strong> of the opening. Then "
             "measure your <strong>doorways and hallways</strong> \u2014 a 36-inch-wide "
             "fridge does not fit through a 32-inch door, and the doors usually come "
             "off to buy you a couple of inches. Decide between <strong>counter-depth</strong> "
             "(flush with cabinets, less capacity) and <strong>standard depth</strong> "
             "(sticks out a few inches, holds more).</p>"),
            ("Features: worth it or not?",
             "<p>Ice and water in the door are genuinely convenient \u2014 and the most "
             "common thing to need a repair down the road. Door-in-door and smart "
             "screens are nice but add cost and complexity. For pure reliability-per-dollar, "
             "a basic top-freezer is almost impossible to beat.</p>"),
        ],
        "cta": True,
    },
    {
        "slug": "ranges",
        "title": "Range Buying Guide: Gas vs. Electric | Cade's Liquidation",
        "h1": "Range buying guide",
        "meta": ("Gas vs. electric ranges, what to check, and how to measure \u2014 a practical "
                 "range buying guide from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": "Ranges",
        "intro": (
            "<p>The range is the centerpiece of the kitchen \u2014 and the appliance where "
            "the fuel question matters most, because cooks have strong opinions about "
            "it. Here's the practical version.</p>"
        ),
        "sections": [
            ("Gas vs. electric",
             "<p><strong>Gas</strong> \u2014 instant heat, instant off, visible flame. "
             "Preferred by most serious cooks. Needs a gas line behind the stove.</p>"
             "<p><strong>Electric smooth-top</strong> \u2014 sleek, easy to wipe clean, "
             "very even oven heat. Needs a 240-volt outlet.</p>"
             "<p><strong>Electric coil</strong> \u2014 the budget workhorse. Cheap, "
             "repairable, and nearly indestructible.</p>"
             "<p>Same rule as dryers: <strong>match what's already in your kitchen</strong>. "
             "Running a gas line or a 240V circuit just to switch fuels rarely pays off.</p>"),
            ("What to check before you buy",
             "<ul>"
             "<li>Every burner or element should heat \u2014 test all of them, not just one.</li>"
             "<li>The oven should reach temperature (every oven here is tested before listing).</li>"
             "<li>On gas ranges, the igniter should click and light promptly on every burner.</li>"
             "<li>Check the oven door seal and that storage drawers slide freely.</li>"
             "</ul>"),
            ("Measuring your space",
             "<p>The standard range is <strong>30 inches wide</strong>. Measure your "
             "opening, and check the depth <strong>including the handle</strong> \u2014 "
             "that's the part that sticks out into the walkway. Confirm whether you "
             "have a gas hookup or a 240V outlet before you fall in love with a unit.</p>"),
            ("Nice-to-have features",
             "<p>Convection fans cook faster and more evenly \u2014 genuinely useful. "
             "Air-fry modes are a fun bonus on newer models. Self-cleaning is convenient "
             "but hard on the oven's electronics over time; many techs quietly recommend "
             "against using it often.</p>"),
        ],
        "cta": True,
    },
    {
        "slug": "freezers",
        "title": "Freezer Buying Guide: Chest vs. Upright | Cade's Liquidation",
        "h1": "Freezer buying guide",
        "meta": ("Chest vs. upright freezers, garage-ready models, and what to check \u2014 a practical "
                 "freezer buying guide from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": "Freezers",
        "intro": (
            "<p>A second freezer is one of the best money-saving appliances there is \u2014 "
            "buy in bulk, freeze garden produce, and stop throwing food away. Here's "
            "how to pick the right one.</p>"
        ),
        "sections": [
            ("Chest vs. upright",
             "<p><strong>Chest freezers</strong> give you the most space per dollar, hold "
             "their cold better during power outages (cold air sinks and stays put when "
             "you open the lid), and are dead simple mechanically. The downside: "
             "things get buried \u2014 use bins to stay organized.</p>"
             "<p><strong>Upright freezers</strong> work like a refrigerator: shelves, "
             "easy to see everything, no digging. They cost more per cubic foot and "
             "lose more cold air when opened, but most people find them far easier to "
             "live with.</p>"),
            ("Garage-ready matters",
             "<p>Not every freezer is designed to run in an unheated garage. Standard "
             "models can struggle or shut down when ambient temperatures drop near "
             "freezing. If yours is going in the garage, look for one rated "
             "<strong>\u201cgarage ready\u201d</strong> \u2014 it's built to handle "
             "Illinois winters.</p>"),
            ("What to check before you buy",
             "<ul>"
             "<li>It should reach 0\u00b0F and hold it. Every freezer here is plugged in and tested before listing.</li>"
             "<li>Check the lid or door seal all the way around \u2014 a weak seal is the main cause of frost buildup.</li>"
             "<li>Look inside for rust or heavy staining, which can signal a hard previous life.</li>"
             "</ul>"),
            ("Where to put it",
             "<p>Freezers need a few inches of airflow around them and a level spot. "
             "Measure the space <em>and</em> the path getting it there \u2014 chest "
             "freezers are bulky and awkward to move. If you need it delivered, that's "
             "what we're here for.</p>"),
        ],
        "cta": True,
    },
    {
        "slug": "dishwashers",
        "title": "Dishwasher Buying Guide | Cade's Liquidation",
        "h1": "Dishwasher buying guide",
        "meta": ("Noise ratings, tub materials, what to check, and how to measure \u2014 a practical "
                 "dishwasher buying guide from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": "Dishwashers",
        "intro": (
            "<p>Dishwashers all <em>look</em> the same from the outside, which is why "
            "most people buy blind and hope. Don't \u2014 there are really only three "
            "things that separate a great dishwasher from a loud, damp disappointment.</p>"
        ),
        "sections": [
            ("The three things that matter",
             "<p><strong>1. Noise (dBA).</strong> This is the spec that affects your "
             "daily life most. Under 45 dBA is whisper-quiet; around 50 is normal "
             "conversation level and fine for most homes; above 55 you'll hear it from "
             "the next room.</p>"
             "<p><strong>2. Tub material.</strong> Stainless steel tubs handle higher "
             "heat, which means better drying and less odor over time. Plastic tubs "
             "cost less but leave dishes damper.</p>"
             "<p><strong>3. The third rack.</strong> That skinny top rack for utensils "
             "and lids frees up a surprising amount of room below. Once you've had "
             "one, you won't go back.</p>"),
            ("What to check before you buy",
             "<ul>"
             "<li>Run a full cycle and check for leaks underneath \u2014 this is the big one.</li>"
             "<li>Racks should slide smoothly and spray arms should spin freely.</li>"
             "<li>The door should latch firmly and the gasket should be intact all the way around.</li>"
             "</ul>"),
            ("Measuring your space",
             "<p>Standard dishwashers are <strong>24 inches wide</strong> and slide into "
             "a cabinet opening \u2014 measure the opening, not the old dishwasher. "
             "Check that you have the water line, drain hookup, and power already in "
             "place; they're usually there if a dishwasher was installed before.</p>"),
            ("A note on installation",
             "<p>Swapping a dishwasher involves water, drain, and electrical connections "
             "under your sink. If that doesn't sound like your idea of a Saturday, "
             "installation services are available \u2014 just ask for a quote.</p>"),
        ],
        "cta": True,
    },
    {
        "slug": "ovens",
        "title": "Wall Oven Buying Guide | Cade's Liquidation",
        "h1": "Wall oven buying guide",
        "meta": ("Single vs. double wall ovens, what to check, and why cutout measurements matter "
                 "\u2014 a practical wall oven buying guide from Cade's Liquidation in Bloomington-Normal, IL."),
        "category": "Ovens",
        "intro": (
            "<p>Wall ovens are the most measurement-sensitive appliance you can buy \u2014 "
            "they have to fit a precise cabinet cutout. Get the measuring right and "
            "everything else is straightforward.</p>"
        ),
        "sections": [
            ("Single vs. double",
             "<p><strong>Single ovens</strong> fit standard cutouts and handle nearly "
             "everything a home cook needs. <strong>Double ovens</strong> are a dream "
             "for holidays and big families \u2014 two temperatures at once \u2014 but "
             "they need a taller cutout and cost significantly more. Combination "
             "microwave/oven units pack both into one cutout and are worth a look "
             "during a kitchen remodel.</p>"),
            ("Gas vs. electric",
             "<p>The vast majority of wall ovens are <strong>electric</strong>, and "
             "electricity is arguably better for baking anyway \u2014 drier, more even "
             "heat. Gas wall ovens exist but are uncommon; check your hookup before "
             "assuming.</p>"),
            ("Measure twice, buy once",
             "<p>This is the whole game with wall ovens. Measure the cabinet cutout's "
             "<strong>width, height, and depth</strong> \u2014 not the old oven, the "
             "hole it sits in. Manufacturers publish exact cutout specs, and there's "
             "very little forgiveness. When in doubt, text us the measurements and "
             "we'll confirm fit before you buy.</p>"),
            ("What to check before you buy",
             "<ul>"
             "<li>The oven should reach and hold temperature \u2014 every oven here is tested before listing.</li>"
             "<li>Check the door seal and that the door closes flush.</li>"
             "<li>Test all controls and any convection fan.</li>"
             "</ul>"),
        ],
        "cta": True,
    },
    {
        "slug": "delivery",
        "title": "Delivery & Service Area | Cade's Liquidation",
        "h1": "Delivery & service area",
        "meta": ("$50 flat-rate appliance delivery to your door in Bloomington-Normal, IL. "
                 "Quotes for surrounding areas, plus installation services \u2014 Cade's Liquidation."),
        "category": None,
        "intro": (
            "<p>You found the appliance. Now let's get it to your house. Delivery is "
            "simple: <strong>$50 flat, delivered to your door anywhere in "
            "Bloomington-Normal, IL.</strong></p>"
        ),
        "sections": [
            ("How delivery works",
             "<ol>"
             "<li><strong>Pick your appliance</strong> \u2014 browse the catalog and text or call to claim it.</li>"
             "<li><strong>Schedule a time</strong> \u2014 we'll find a delivery window that works for you.</li>"
             "<li><strong>We bring it to your door</strong> \u2014 $50 flat within Bloomington-Normal, IL.</li>"
             "</ol>"),
            ("Outside Bloomington-Normal?",
             "<p>No problem \u2014 we deliver to surrounding communities all the time. "
             "Text or call for a quote; the price depends on distance. (Delivery costs "
             "move with fuel prices, so we quote each trip individually rather than "
             "posting a rate that goes stale.)</p>"),
            ("Installation services",
             "<p>Need it hooked up, not just dropped off? <strong>Installation services "
             "are available for an additional charge</strong> \u2014 dishwashers, "
             "ranges, over-the-range microwaves, and more. Text for pricing; we'll "
             "tell you straight whether your setup is simple or complicated before "
             "you commit to anything.</p>"),
            ("Prefer to pick up?",
             "<p>You're welcome to come see everything in person first \u2014 the "
             "warehouse is open <strong>by appointment</strong>. Call or text to "
             "schedule a time, and we'll have the unit pulled out and ready when you "
             "arrive.</p>"),
        ],
        "cta": True,
    },
]
