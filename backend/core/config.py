# Build Queue Categories
BUILD_CATEGORIES = {
    "app": {"id": "app", "name": "Application", "icon": "app-window", "color": "blue", "description": "Desktop/mobile applications"},
    "webpage": {"id": "webpage", "name": "Webpage", "icon": "globe", "color": "cyan", "description": "Websites and web apps"},
    "game": {"id": "game", "name": "Game", "icon": "gamepad-2", "color": "purple", "description": "Games for any platform"},
    "api": {"id": "api", "name": "API", "icon": "server", "color": "emerald", "description": "Backend APIs and services"},
    "mobile": {"id": "mobile", "name": "Mobile", "icon": "smartphone", "color": "amber", "description": "iOS and Android apps"}
}

# Blueprint Node Templates
BLUEPRINT_NODE_TEMPLATES = {
    "event_begin_play": {"type": "event", "name": "Event Begin Play", "color": "red", "outputs": [{"name": "exec", "type": "exec"}]},
    "event_tick": {"type": "event", "name": "Event Tick", "color": "red", "outputs": [{"name": "exec", "type": "exec"}, {"name": "delta_time", "type": "float"}]},
    "event_input": {"type": "event", "name": "Input Event", "color": "red", "properties": {"key": "Space"}, "outputs": [{"name": "pressed", "type": "exec"}, {"name": "released", "type": "exec"}]},
    "branch": {"type": "flow", "name": "Branch", "color": "zinc", "inputs": [{"name": "exec", "type": "exec"}, {"name": "condition", "type": "bool"}], "outputs": [{"name": "true", "type": "exec"}, {"name": "false", "type": "exec"}]},
    "sequence": {"type": "flow", "name": "Sequence", "color": "zinc", "inputs": [{"name": "exec", "type": "exec"}], "outputs": [{"name": "then_0", "type": "exec"}, {"name": "then_1", "type": "exec"}, {"name": "then_2", "type": "exec"}]},
    "for_loop": {"type": "flow", "name": "For Loop", "color": "zinc", "inputs": [{"name": "exec", "type": "exec"}, {"name": "start", "type": "int"}, {"name": "end", "type": "int"}], "outputs": [{"name": "loop_body", "type": "exec"}, {"name": "index", "type": "int"}, {"name": "completed", "type": "exec"}]},
    "delay": {"type": "flow", "name": "Delay", "color": "cyan", "inputs": [{"name": "exec", "type": "exec"}, {"name": "duration", "type": "float"}], "outputs": [{"name": "completed", "type": "exec"}]},
    "print_string": {"type": "function", "name": "Print String", "color": "blue", "inputs": [{"name": "exec", "type": "exec"}, {"name": "string", "type": "string"}], "outputs": [{"name": "exec", "type": "exec"}]},
    "spawn_actor": {"type": "function", "name": "Spawn Actor", "color": "emerald", "inputs": [{"name": "exec", "type": "exec"}, {"name": "class", "type": "class"}, {"name": "location", "type": "vector"}, {"name": "rotation", "type": "rotator"}], "outputs": [{"name": "exec", "type": "exec"}, {"name": "actor", "type": "actor"}]},
    "destroy_actor": {"type": "function", "name": "Destroy Actor", "color": "red", "inputs": [{"name": "exec", "type": "exec"}, {"name": "target", "type": "actor"}], "outputs": [{"name": "exec", "type": "exec"}]},
    "get_player": {"type": "function", "name": "Get Player Character", "color": "emerald", "inputs": [], "outputs": [{"name": "character", "type": "character"}]},
    "get_location": {"type": "function", "name": "Get Actor Location", "color": "amber", "inputs": [{"name": "target", "type": "actor"}], "outputs": [{"name": "location", "type": "vector"}]},
    "set_location": {"type": "function", "name": "Set Actor Location", "color": "amber", "inputs": [{"name": "exec", "type": "exec"}, {"name": "target", "type": "actor"}, {"name": "location", "type": "vector"}], "outputs": [{"name": "exec", "type": "exec"}]},
}

# Audio generation categories
AUDIO_CATEGORIES = {
    "sfx": {
        "explosion": "Powerful explosion sound effect, rumbling bass with debris",
        "footstep_grass": "Footstep on grass, soft rustling sound",
        "footstep_stone": "Footstep on stone, hard clicking impact",
        "sword_swing": "Sword swing whoosh, metal cutting through air",
        "sword_hit": "Sword hitting metal armor, clang and ring",
        "pickup_item": "Item pickup sound, magical sparkle chime",
        "ui_click": "UI button click, soft satisfying pop",
        "ui_hover": "UI hover sound, subtle whoosh",
        "door_open": "Wooden door opening, creaking hinges",
        "chest_open": "Treasure chest opening, wood and metal",
        "level_up": "Level up fanfare, triumphant ascending notes",
        "damage_hit": "Taking damage, impact thud with grunt",
        "heal": "Healing sound, gentle magical restoration",
        "jump": "Character jump, effort grunt with air movement",
        "land": "Landing on ground, impact thud"
    },
    "music": {
        "menu_ambient": "Calm ambient menu music, gentle synth pads",
        "battle_epic": "Epic battle music, orchestral with drums",
        "exploration": "Exploration music, wonder and discovery theme",
        "boss_fight": "Intense boss fight music, dramatic and urgent",
        "victory": "Victory fanfare, triumphant celebration",
        "defeat": "Defeat music, somber and reflective",
        "shop": "Shop music, cheerful and welcoming",
        "dungeon": "Dungeon ambience, dark and mysterious",
        "village": "Village theme, peaceful and friendly",
        "night": "Nighttime ambient, calm with cricket sounds"
    },
    "voice": {
        "narrator_intro": "Epic narrator voice for game intro",
        "npc_greeting": "Friendly NPC greeting the player",
        "npc_merchant": "Merchant voice offering wares",
        "enemy_taunt": "Enemy taunting the player",
        "tutorial_guide": "Helpful tutorial guide voice",
        "quest_giver": "Quest giver explaining a mission"
    }
}

# Deployment platform configs
DEPLOYMENT_PLATFORMS = {
    "vercel": {
        "id": "vercel",
        "name": "Vercel",
        "icon": "triangle",
        "color": "zinc",
        "description": "Best for web apps and static sites",
        "supports": ["web_app", "webpage", "static"],
        "requires": ["VERCEL_TOKEN"]
    },
    "railway": {
        "id": "railway",
        "name": "Railway",
        "icon": "train",
        "color": "purple",
        "description": "Full-stack apps with databases",
        "supports": ["web_app", "api", "fullstack"],
        "requires": ["RAILWAY_TOKEN"]
    },
    "itch": {
        "id": "itch",
        "name": "Itch.io",
        "icon": "gamepad-2",
        "color": "red",
        "description": "Game distribution platform",
        "supports": ["game", "web_game"],
        "requires": ["ITCH_API_KEY", "ITCH_USERNAME"]
    }
}

# Asset type configurations
ASSET_TYPES = {
    "image": {"formats": ["png", "jpg", "jpeg", "webp", "gif", "svg"], "icon": "image", "color": "blue"},
    "audio": {"formats": ["mp3", "wav", "ogg", "flac", "aac"], "icon": "volume-2", "color": "purple"},
    "texture": {"formats": ["png", "jpg", "tga", "dds", "exr"], "icon": "grid", "color": "amber"},
    "sprite": {"formats": ["png", "gif", "webp"], "icon": "layers", "color": "cyan"},
    "model_3d": {"formats": ["fbx", "obj", "gltf", "glb", "blend"], "icon": "box", "color": "emerald"},
    "material": {"formats": ["mat", "json", "uasset"], "icon": "palette", "color": "pink"},
    "animation": {"formats": ["fbx", "anim", "json"], "icon": "play", "color": "orange"},
    "font": {"formats": ["ttf", "otf", "woff", "woff2"], "icon": "type", "color": "zinc"},
    "video": {"formats": ["mp4", "webm", "mov", "avi"], "icon": "film", "color": "red"},
    "script": {"formats": ["js", "ts", "py", "cs", "cpp", "lua", "gd"], "icon": "code", "color": "green"}
}

ASSET_CATEGORIES = [
    {"id": "ui", "name": "UI/HUD", "description": "User interface elements"},
    {"id": "character", "name": "Characters", "description": "Player, NPCs, enemies"},
    {"id": "environment", "name": "Environment", "description": "World, props, terrain"},
    {"id": "vfx", "name": "VFX/Particles", "description": "Visual effects"},
    {"id": "audio", "name": "Audio", "description": "Sound effects and music"},
    {"id": "animation", "name": "Animations", "description": "Character and object animations"},
    {"id": "misc", "name": "Miscellaneous", "description": "Other assets"}
]

PROJECT_THUMBNAILS = {
    "unreal": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=300&fit=crop",
    "unity": "https://images.unsplash.com/photo-1556438064-2d7646166914?w=400&h=300&fit=crop",
    "godot": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&h=300&fit=crop",
    "web_game": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&h=300&fit=crop",
    "web_app": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop",
    "mobile_app": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop"
}

# Delegation keywords for auto-routing
DELEGATION_KEYWORDS = {
    "architecture": "architect",
    "design pattern": "architect",
    "system design": "architect",
    "code": "developer",
    "implement": "developer",
    "build": "developer",
    "create function": "developer",
    "review": "reviewer",
    "check": "reviewer",
    "test": "tester",
    "bug": "tester",
    "art": "artist",
    "ui": "artist",
    "visual": "artist",
}
