data = {
    "sand": {
        "name": "Sand",
        "label": "SAND",  # 4 letters
        "description": "Sand. Heavy powder.",
        "fall": 1, # 0 = solid, 1 = powder fall, 2 = liquid fall, -1 = up fall (fire), 2 = gas (float around)
        "color": (194, 178, 128),  # Color for sand
        "density": 5,
        "flammable": False,
        "flaming": False
    },
    "water": {
        "name": "Water",
        "label": "WATR",  # 4 letters
        "description": "Liquid water.",
        "fall": 2, # Liquid fall
        "color": (0, 0, 255),  # Color for water
        "density": 3,
        "flammable": True,
        "overrideburn": "steam", # When it burns, its steam, not the flaming
        "flaming": False
    },
    "fire": {
        "name": "Fire",
        "label": "FIRE",  # 4 letters
        "description": "Hot fire.",
        "fall": -1, # Up fall (fire)
        "color": (255, 0, 0),  # Color for fire
        "slife": (50, 60),
        "mlife": 50,
        "life0": ["become", "Smoke"],
        "density": 2,
        "enablefadingout": True,
        "flammable": False,
        "flaming": True,  # Fire can spread to flammable materials
        "burn": 0.04 # slow burn rate (1%)
            },
    "stone": {
        "name": "Stone",
        "label": "STNE",  # Updated to STNE
        "description": "Solid stone.",
        "fall": 1,
        "color": (128, 128, 128),  # Color for stone
        "density": 15,
        "flammable": False,
        "flaming": False
    },
    "smoke": {
        "name": "Smoke",
        "label": "SMKE",
        "description": "Smoke.",
        "fall": -1,
        "slife": (30, 40),
        "mlife": 30,
        "life0": ["die"],
        "color": (64, 64, 64),
        "density": 3,
        "enablefadingout": False,
        "flammable": False,
        "flaming": False
    },
    "wood": {
        "name": "Wood",
        "label": "WOOD",
        "description": "Wooden block. Can catch fire.",
        "fall": 0,  # Solid
        "color": (139, 69, 19),  # Brown color
        "density": 400,
        "flammable": True,  # Can catch fire
        "flaming": False,
        "burnm": 1,
    },
    "fuse": {
        "name": "Fuse",
        "label": "FUSE",
        "description": "Fuse. Can catch fire.",
        "fall": 0,  # Solid
        "color": (255, 255, 0),  # Yellow color
        "density": 200,
        "flammable": True,  # Can catch fire
        "flaming": False,
        "burnm": 500,
    },
    "oil": {
        "name": "Oil",
        "label": "OIL ",
        "description": "Flammable liquid.",
        "fall": 2,  # Liquid fall
        "color": (58, 68, 75),  # Dark oil color
        "density": 2,  # Less dense than water
        "flammable": True,
        "flaming": False,
        "burnm": 0.5
    },
    "steam": {
        "name": "Steam",
        "label": "VPOR",
        "description": "Hot water vapor.",
        "fall": -1,  # Rises like smoke
        "color": (200, 200, 255),  # Light blueish white
        "slife": (40, 50),
        "mlife": 40,
        "life0": ["become", "Water"],
        "density": 1,
        "enablefadingout": False,
        "flammable": False,
        "flaming": False
    },
    "gunpowder": {
        "name": "Gunpowder",
        "label": "GNPW",
        "description": "Explosive powder.",
        "fall": 1,  # Powder fall
        "color": (50, 50, 50),  # Dark grey
        "density": 4,
        "flammable": True,
        "flaming": False,
        "burnm": 2000  # Very explosive
    },
    "lava": {
        "name": "Lava",
        "label": "LAVA",
        "description": "Molten rock.",
        "fall": 2,  # Liquid fall
        "color": (207, 16, 32),  # Bright red
        "density": 12,  # Very dense
        "flammable": False,
        "flaming": True,  # Can ignite things
        "burn": 1, # Very igniting
        "overridemyburn": "fire", # When it burns, its fire, not lava. this is still overriden by the overrideburn
        
    },
    "wall": {
        "name": "Wall",
        "label": "WALL",
        "description": "Indestructible wall.",
        "fall": 0,  # Solid
        "color": (80, 80, 80),  # Dark grey
        "density": 999999,  # Extremely dense - nothing can displace it
        "flammable": False,
        "flaming": False
    },
    "acid": {
        "name": "Acid",
        "label": "ACID",
        "description": "Corrosive liquid.",
        "fall": 2,  # Liquid fall
        "color": (0, 255, 0),  # Bright green
        "density": 3,
        "flammable": True, # Acid can catch fire
        "flaming": False,
        "burnm": 0.5, # Acid burns slowly
        "corrode": True, # Acid can corrode other particles
        "excludecorrode": ["wall", "acid", "stone", "fire", "lava", "steam", "smoke"], # Exclude these particles from being corroded (flame starters, indestructible things, acid itself, gases)
    },
    "flamer": {
        "name": "Flamer",
        "label": "FLMR",
        "description": "Flame thrower.",
        "fall": 0,  # Solid
        "color": (255, 165, 0),  # Orange color
        "density": 599999999,
        "flammable": False,
        "flaming": False,
        "clone": "fire",  # Clones fire particles to air near it
    },
    "dynamite": {
        "name": "Dynamite",
        "label": "DYNT",
        "description": "Explosive that causes a large blast.",
        "fall": 0,  # Solid
        "color": (255, 0, 0),  # Red color
        "density": 80000000,
        "flammable": True,
        "flaming": False,
        "burnm": 3000,  # Very explosive like gunpowder
        "exploderad": 5  # Explosion radius
    },
    "rock": {
        "name": "Rock",
        "label": "ROCK",
        "description": "Solid rock that can be shattered.",
        "fall": 0,  # Solid
        "color": (100, 100, 100),  # Darker grey than stone
        "density": 2000,
        "flammable": False,
        "flaming": False,
        "shatter": "stone"  # Shatters into stone particles
    }
}

achievements = {
    "creator_bronze": {
        "name": "Creator! (Bronze)",
        "description": "Create a particle.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place", "*", "1"], # condition, which particle (* for any), amount needed (optional)
    },
    "creator_silver": {
        "name": "Creator! (Silver)",
        "description": "Create 700 particles.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place", "*", "700"], # condition, which particle (* for any), amount needed (optional)
    },
    "creator_gold": {
        "name": "Creator! (Gold)",
        "description": "Create 8000 particles.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place", "*", "8000"], # condition, which particle (* for any), amount needed (optional)
    },
    "creator_platinum": {
        "name": "Creator! (Platinum)",
        "description": "Create 50000 particles.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place", "*", "50000"], # condition, which particle (* for any), amount needed (optional)
    },
    "creator_diamond": {
        "name": "Creator! (Diamond)",
        "description": "Create 1000000 particles.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place", "*", "1000000"], # condition, which particle (* for any), amount needed (optional)
    },
    "preservation": {
        "name": "Preservation",
        "description": "Place all types of particles.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place1ofall"], # special
    },
    "firestarter": {
        "name": "Firestarter",
        "description": "Place fire.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place", "fire"], # condition, which particle (* for any), amount needed (optional)
    },
    "no": {
        "name": "NO.",
        "description": "Create a wall.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["place", "wall"], # condition, which particle (* for any), amount needed (optional)
    },
    "rain_achiev": {
        "name": "Rain Maker",
        "description": "Create a rainstorm.",
        "achieved": False,
        "type": "Achievement", # Achievement, Challenge, or SECRET
        "condit": ["liferanout", "steam", "100"], # condition, which particle (* for any), amount needed (optional)
    },
}