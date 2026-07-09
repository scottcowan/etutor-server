"""
Curriculum — English National Curriculum (KS1–KS3) + Vocational Topics
=======================================================================
Structured reference used by the tutor, planner, and recommender to:
  - Select age-appropriate topics for a child
  - Map a topic to its key stage, subject, and Bloom's entry level
  - Find prerequisite topics before introducing a new one
  - Suggest vocational/interest-led extensions alongside core curriculum

Structure:
  CURRICULUM: list[Topic]
  Topic fields:
    id          — machine-readable slug
    name        — display name
    subject     — broad category
    key_stages  — list of KS integers (1=Y1-2, 2=Y3-6, 3=Y7-9)
    year_groups — list of year group integers (1-9)
    bloom_entry — lowest Bloom level appropriate at introduction (1-6)
    bloom_target — Bloom level to aim for once topic is established
    prerequisites — list of topic ids that should come first
    tags        — free tags for interest-matching (e.g. "animals", "hands-on")
    vocational  — True if this is a vocational/life-skills topic (not NC core)

Age → Year group: age 6=Y2, 7=Y3... roughly age-5=year group.
Key Stage → Year: KS1=Y1-2, KS2=Y3-6, KS3=Y7-9.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Topic:
    id: str
    name: str
    subject: str
    key_stages: list[int]
    year_groups: list[int]
    bloom_entry: int        # Bloom level at first introduction
    bloom_target: int       # Bloom level to reach before moving on
    prerequisites: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    vocational: bool = False
    accelerated_ok: bool = True  # Can a child study this ahead of their year group?
    # Most topics are fine to accelerate into if the child is interested and
    # prerequisites are met. Set False for topics with hard developmental gates
    # (e.g. abstract algebra before concrete number sense is solid).


# ---------------------------------------------------------------------------
# English National Curriculum — Core Subjects
# ---------------------------------------------------------------------------

_ENGLISH = [
    Topic("phonics_phase1", "Phonics — Environmental and Instrumental Sounds",
          "English", [1], [1], 1, 2, [],
          ["reading", "listening", "sounds"]),
    Topic("phonics_phase2", "Phonics — Letter Sounds and Blending",
          "English", [1], [1, 2], 1, 2, ["phonics_phase1"],
          ["reading", "letters", "sounds"]),
    Topic("phonics_phase3", "Phonics — Digraphs and Trigraphs",
          "English", [1], [1, 2], 1, 2, ["phonics_phase2"],
          ["reading", "letters"]),
    Topic("phonics_phase5", "Phonics — Alternative Spellings and Sounds",
          "English", [1], [2], 2, 3, ["phonics_phase3"],
          ["reading", "spelling"]),
    Topic("reading_comprehension_ks1", "Reading Comprehension — Fiction and Non-fiction",
          "English", [1], [1, 2], 2, 3, ["phonics_phase2"],
          ["reading", "stories"]),
    Topic("reading_comprehension_ks2", "Reading Comprehension — Inference and Deduction",
          "English", [2], [3, 4, 5, 6], 3, 4, ["reading_comprehension_ks1"],
          ["reading", "stories", "inference"]),
    Topic("reading_comprehension_ks3", "Reading Comprehension — Analysis and Evaluation",
          "English", [3], [7, 8, 9], 4, 5, ["reading_comprehension_ks2"],
          ["reading", "analysis", "literature"]),
    Topic("creative_writing_ks1", "Creative Writing — Stories and Sentences",
          "English", [1], [1, 2], 2, 3, ["phonics_phase2"],
          ["writing", "stories", "imagination"]),
    Topic("creative_writing_ks2", "Creative Writing — Structure, Style, and Voice",
          "English", [2], [3, 4, 5, 6], 3, 4, ["creative_writing_ks1"],
          ["writing", "stories", "imagination"]),
    Topic("poetry_ks2", "Poetry — Rhyme, Rhythm, and Figurative Language",
          "English", [2], [4, 5, 6], 3, 5, ["reading_comprehension_ks1"],
          ["writing", "poetry", "language"]),
    Topic("grammar_punctuation_ks1", "Grammar — Sentences, Capital Letters, and Full Stops",
          "English", [1], [1, 2], 1, 2, ["phonics_phase2"],
          ["grammar", "writing"]),
    Topic("grammar_punctuation_ks2", "Grammar — Clauses, Tenses, and Punctuation",
          "English", [2], [3, 4, 5, 6], 2, 3, ["grammar_punctuation_ks1"],
          ["grammar", "writing"]),
    Topic("spelling_ks2", "Spelling — Prefixes, Suffixes, and Word Families",
          "English", [2], [3, 4, 5, 6], 1, 2, ["phonics_phase5"],
          ["spelling", "vocabulary"]),
    Topic("vocabulary_ks2", "Vocabulary — Word Meaning in Context",
          "English", [2], [4, 5, 6], 2, 3, ["reading_comprehension_ks1"],
          ["vocabulary", "language"]),
    Topic("shakespeare_ks3", "Shakespeare — Plays and Language",
          "English", [3], [7, 8, 9], 3, 5, ["reading_comprehension_ks2"],
          ["literature", "drama", "history"]),
    Topic("media_literacy_ks3", "Media Literacy — Analysing Texts and Bias",
          "English", [3], [8, 9], 4, 5, ["reading_comprehension_ks3"],
          ["media", "critical thinking", "language"]),

    # --- Exam-preparation topics ---
    Topic("literary_terminology", "Literary Terminology — Writers' Craft and Language Analysis",
          "English", [2, 3], [5, 6, 7, 8, 9], 3, 5, ["reading_comprehension_ks2"],
          ["literary terms", "analysis", "11 plus", "common entrance", "language", "poetry"],
          # Simile, metaphor, personification, alliteration, onomatopoeia, imagery,
          # tone, connotation, juxtaposition, volta, structure, narrative voice.
          # Essential for KS2 SATs Q2d, 11+, and CE 13+. Often assumed but never taught.
    ),
    Topic("verbal_reasoning_11plus", "Verbal Reasoning — 11-Plus Question Types",
          "English", [2], [5, 6], 2, 3, ["vocabulary_ks2", "spelling_ks2"],
          ["11 plus", "verbal reasoning", "GL assessment", "word patterns", "analogies",
           "exam prep", "entrance exam"],
          # GL Assessment 11+ VR types: word codes, letter sequences, word analogies
          # (hot:cold::big:?), odd word out, hidden words, compound words, anagram
          # completion, word sequences. Not taught in NC — requires dedicated practice.
    ),
    Topic("directed_writing", "Directed Writing — Letters, Articles, Speeches, and Reports",
          "English", [2, 3], [6, 7, 8, 9], 3, 5, ["creative_writing_ks2"],
          ["writing", "non-fiction", "letters", "persuasion", "common entrance",
           "forms", "audience", "purpose"],
          # CE 13+ and KS3 writing tests expect form-specific non-fiction writing
          # alongside imaginative writing. Register, audience, and purpose are key.
    ),
]

_MATHS = [
    Topic("counting_numbers", "Counting and Number Recognition",
          "Maths", [1], [1, 2], 1, 2, [],
          ["numbers", "counting"]),
    Topic("addition_subtraction_ks1", "Addition and Subtraction to 20",
          "Maths", [1], [1, 2], 1, 2, ["counting_numbers"],
          ["arithmetic", "numbers"]),
    Topic("multiplication_tables", "Times Tables (2, 5, 10 then all to 12)",
          "Maths", [1, 2], [2, 3, 4], 1, 2, ["addition_subtraction_ks1"],
          ["arithmetic", "multiplication", "patterns"]),
    Topic("division_basics", "Division — Sharing and Grouping",
          "Maths", [2], [3, 4], 2, 3, ["multiplication_tables"],
          ["arithmetic", "division"]),
    Topic("fractions_ks2", "Fractions — Halves, Quarters, and Equivalence",
          "Maths", [2], [3, 4, 5], 2, 3, ["division_basics"],
          ["fractions", "numbers"]),
    Topic("decimals_percentages", "Decimals and Percentages",
          "Maths", [2], [5, 6], 2, 3, ["fractions_ks2"],
          ["fractions", "decimals", "percentages"]),
    Topic("place_value", "Place Value — Tens, Hundreds, Thousands",
          "Maths", [1, 2], [2, 3, 4], 1, 2, ["counting_numbers"],
          ["numbers", "place value"]),
    Topic("measurement_ks1", "Measurement — Length, Mass, and Capacity",
          "Maths", [1], [1, 2], 1, 2, ["counting_numbers"],
          ["measurement", "practical", "hands-on"]),
    Topic("measurement_ks2", "Measurement — Area, Perimeter, and Volume",
          "Maths", [2], [4, 5, 6], 2, 3, ["measurement_ks1", "multiplication_tables"],
          ["measurement", "geometry"]),
    Topic("geometry_shapes_ks1", "Geometry — 2D and 3D Shapes",
          "Maths", [1], [1, 2], 1, 2, [],
          ["geometry", "shapes", "patterns"]),
    Topic("geometry_ks2", "Geometry — Angles, Coordinates, and Symmetry",
          "Maths", [2], [4, 5, 6], 2, 3, ["geometry_shapes_ks1"],
          ["geometry", "shapes"]),
    Topic("statistics_ks2", "Statistics — Charts, Graphs, and Tables",
          "Maths", [2], [4, 5, 6], 2, 3, ["multiplication_tables"],
          ["data", "charts", "statistics"]),
    Topic("algebra_ks3", "Algebra — Expressions, Equations, and Formulae",
          "Maths", [3], [7, 8, 9], 3, 4, ["decimals_percentages"],
          ["algebra", "equations", "patterns"],
          accelerated_ok=False),  # requires solid concrete number sense first
    Topic("ratio_proportion", "Ratio and Proportion",
          "Maths", [2, 3], [6, 7], 3, 4, ["fractions_ks2"],
          ["fractions", "ratio", "practical"]),
    Topic("probability_ks3", "Probability — Chance and Likelihood",
          "Maths", [3], [8, 9], 3, 4, ["statistics_ks2"],
          ["statistics", "probability", "prediction"]),
    Topic("negative_numbers", "Negative Numbers and the Number Line",
          "Maths", [2, 3], [5, 6, 7], 2, 3, ["addition_subtraction_ks1"],
          ["numbers", "temperature", "practical"]),
]

_SCIENCE = [
    Topic("living_things_ks1", "Living Things — Animals and Plants",
          "Science", [1], [1, 2], 1, 2, [],
          ["animals", "plants", "nature", "biology"]),
    Topic("human_body_ks1", "The Human Body — Senses and Basic Biology",
          "Science", [1], [1, 2], 1, 2, [],
          ["human body", "health", "biology"]),
    Topic("materials_ks1", "Everyday Materials — Properties and Uses",
          "Science", [1], [1, 2], 1, 2, [],
          ["materials", "properties", "hands-on"]),
    Topic("seasons_weather", "Seasons, Weather, and the Sun",
          "Science", [1], [1, 2], 1, 2, [],
          ["weather", "seasons", "earth", "nature"]),
    Topic("plants_ks2", "Plants — Life Cycles and Photosynthesis",
          "Science", [2], [3, 4], 2, 3, ["living_things_ks1"],
          ["plants", "nature", "biology", "photosynthesis"]),
    Topic("animals_habitats", "Animals — Habitats, Adaptation, and Food Chains",
          "Science", [2], [4, 5], 2, 3, ["living_things_ks1"],
          ["animals", "ecosystems", "nature", "food chains"]),
    Topic("human_body_ks2", "The Human Body — Organs, Digestion, and Nutrition",
          "Science", [2], [4, 5, 6], 2, 3, ["human_body_ks1"],
          ["human body", "health", "biology", "nutrition"]),
    Topic("rocks_soils", "Rocks, Fossils, and Soils",
          "Science", [2], [3], 1, 3, [],
          ["geology", "fossils", "earth science", "dinosaurs"]),
    Topic("light_shadows", "Light — Sources, Reflection, and Shadows",
          "Science", [2], [3], 2, 3, [],
          ["light", "physics", "practical"]),
    Topic("forces_magnets", "Forces and Magnets",
          "Science", [2], [3], 2, 3, [],
          ["forces", "physics", "magnets", "hands-on"]),
    Topic("electricity_ks2", "Electricity — Circuits and Components",
          "Science", [2], [4], 2, 3, [],
          ["electricity", "circuits", "physics", "practical", "hands-on"]),
    Topic("sound_ks2", "Sound — Vibrations and Pitch",
          "Science", [2], [4], 2, 3, [],
          ["sound", "music", "physics"]),
    Topic("earth_space_ks2", "Earth and Space — Planets, the Moon, and the Solar System",
          "Science", [2], [5], 2, 3, ["seasons_weather"],
          ["space", "planets", "astronomy"]),
    Topic("properties_materials_ks2", "Properties and Changes of Materials",
          "Science", [2], [5], 2, 3, ["materials_ks1"],
          ["materials", "chemistry", "practical"]),
    Topic("evolution_adaptation", "Evolution, Inheritance, and Adaptation",
          "Science", [2], [6], 3, 4, ["animals_habitats", "plants_ks2"],
          ["evolution", "biology", "darwin", "nature"]),
    Topic("cells_ks3", "Cells — Structure and Function",
          "Science", [3], [7], 2, 3, ["living_things_ks1"],
          ["biology", "cells", "microscope"]),
    Topic("particle_model", "The Particle Model — States of Matter",
          "Science", [3], [7], 3, 4, ["properties_materials_ks2"],
          ["chemistry", "particles", "states of matter"]),
    Topic("chemical_reactions", "Chemical Reactions and the Periodic Table",
          "Science", [3], [8, 9], 3, 4, ["particle_model"],
          ["chemistry", "reactions", "elements"]),
    Topic("forces_motion_ks3", "Forces, Motion, and Speed",
          "Science", [3], [8], 3, 4, ["forces_magnets"],
          ["physics", "forces", "motion", "speed"]),
    Topic("waves_ks3", "Waves — Light, Sound, and the Electromagnetic Spectrum",
          "Science", [3], [8, 9], 3, 4, ["light_shadows", "sound_ks2"],
          ["physics", "waves", "light", "sound"]),
    Topic("genetics_ks3", "Genetics and Reproduction",
          "Science", [3], [9], 3, 4, ["evolution_adaptation", "cells_ks3"],
          ["biology", "genetics", "reproduction"]),
    Topic("ecosystems_ks3", "Ecosystems — Interdependence and Human Impact",
          "Science", [3], [9], 4, 5, ["animals_habitats", "evolution_adaptation"],
          ["ecosystems", "environment", "sustainability", "animals"]),
]

_HISTORY = [
    # --- KS1: Foundations ---
    Topic("history_significant_people", "Significant People — Local Heroes and Historical Figures",
          "History", [1], [1, 2], 1, 2, [],
          ["history", "people", "stories", "britain"]),
    Topic("history_changes_living", "Changes in Living Memory — How Britain Has Changed",
          "History", [1], [1, 2], 1, 2, [],
          ["history", "living memory", "technology", "britain"]),
    Topic("great_fire_london", "The Great Fire of London (1666)",
          "History", [1], [2], 1, 2, [],
          ["history", "london", "britain", "fire", "stories"]),

    # --- KS2: Ancient and Medieval Britain ---
    Topic("stone_bronze_iron_age", "Stone Age, Bronze Age, and Iron Age Britain",
          "History", [2], [3], 2, 3, [],
          ["ancient history", "prehistory", "britain", "archaeology", "tools"]),
    Topic("romans_britain", "Romans in Britain — Conquest, Roads, and Culture",
          "History", [2], [3], 2, 3, ["stone_bronze_iron_age"],
          ["romans", "britain", "ancient history", "conquest", "roads"]),
    Topic("vikings_saxons", "Vikings and Anglo-Saxons — Raids, Kingdoms, and Laws",
          "History", [2], [4], 2, 3, ["romans_britain"],
          ["vikings", "saxons", "britain", "medieval", "raids"]),
    Topic("norman_conquest", "The Norman Conquest and Medieval Britain",
          "History", [2], [4], 2, 3, ["vikings_saxons"],
          ["normans", "medieval", "britain", "castles", "feudal system"]),

    # --- KS2: World Civilisations (context for empire) ---
    Topic("ancient_egypt", "Ancient Egypt — Pharaohs, Trade, and the Nile",
          "History", [2], [3, 4], 2, 3, [],
          ["ancient history", "egypt", "pyramids", "africa", "trade", "nile"]),
    Topic("ancient_greece", "Ancient Greece — Democracy, Philosophy, and Influence",
          "History", [2], [4], 2, 3, [],
          ["ancient history", "greece", "democracy", "philosophy", "culture"]),
    Topic("ancient_benin", "The Kingdom of Benin — Art, Trade, and Power in West Africa",
          "History", [2], [5], 2, 3, [],
          ["africa", "west africa", "benin", "trade", "art", "empire"]),
    Topic("mayan_civilisation", "The Mayan Civilisation — Astronomy, Writing, and Cities",
          "History", [2], [5], 2, 3, [],
          ["maya", "americas", "astronomy", "ancient history", "civilisation"]),
    Topic("mughal_empire", "The Mughal Empire — India Before British Rule",
          "History", [2, 3], [6, 7], 3, 4, [],
          ["mughal", "india", "empire", "trade", "art", "islam"]),

    # --- KS2–3: Medieval Britain (Plantagenets to Wars of the Roses) ---
    Topic("magna_carta_barons", "Magna Carta and the Barons — Limits on Royal Power",
          "History", [2, 3], [5, 6, 7], 3, 4, ["norman_conquest"],
          ["magna carta", "medieval", "britain", "law", "rights", "parliament"]),
    Topic("black_death", "The Black Death — Plague, Death, and Social Change",
          "History", [2, 3], [5, 6], 2, 4, ["norman_conquest"],
          ["black death", "plague", "medieval", "disease", "social change"]),
    Topic("hundred_years_war", "The Hundred Years War and Joan of Arc",
          "History", [2, 3], [5, 6, 7], 3, 4, ["norman_conquest"],
          ["hundred years war", "france", "medieval", "joan of arc", "war"]),
    Topic("wars_of_the_roses", "Wars of the Roses — Lancaster, York, and Tudor Rise",
          "History", [3], [7], 3, 4, ["magna_carta_barons"],
          ["wars of the roses", "medieval", "tudor", "britain", "monarchy"]),

    # --- KS2–3: Tudors ---
    Topic("henry_viii_reformation", "Henry VIII and the English Reformation",
          "History", [2, 3], [6, 7], 3, 4, ["wars_of_the_roses"],
          ["tudor", "henry viii", "reformation", "church", "britain", "religion"]),
    Topic("elizabethan_era", "Elizabethan England — Exploration, Theatre, and the Armada",
          "History", [2, 3], [6, 7], 3, 4, ["henry_viii_reformation"],
          ["tudor", "elizabeth i", "armada", "shakespeare", "exploration", "britain"]),

    # --- KS2–3: Stuarts and the Road to Empire ---
    Topic("english_civil_war", "The English Civil War — King vs Parliament",
          "History", [3], [7, 8], 3, 5, ["elizabethan_era"],
          ["civil war", "charles i", "cromwell", "parliament", "rights", "britain"]),
    Topic("glorious_revolution", "The Glorious Revolution and the Bill of Rights (1688)",
          "History", [3], [7, 8], 3, 5, ["english_civil_war"],
          ["glorious revolution", "bill of rights", "parliament", "democracy", "britain"]),
    Topic("union_of_britain", "The Acts of Union — Creating Great Britain",
          "History", [3], [7, 8], 3, 4, ["glorious_revolution"],
          ["union", "scotland", "wales", "ireland", "britain", "parliament"]),

    # --- KS3: Hanoverians, America, and the French Revolution ---
    Topic("american_revolution", "The American Revolution — Colonies, Taxation, and Independence",
          "History", [3], [8], 4, 5, ["glorious_revolution", "british_empire_expansion"],
          ["american revolution", "usa", "empire", "independence", "taxation", "rights"]),
    Topic("french_revolution_napoleon", "The French Revolution and Napoleon",
          "History", [3], [8], 4, 5, ["american_revolution"],
          ["french revolution", "napoleon", "europe", "rights", "war", "modern history"]),
    Topic("abolition_movement", "Abolition — The Fight to End the Slave Trade",
          "History", [2, 3], [6, 7, 8], 3, 5, ["transatlantic_slave_trade"],
          ["abolition", "wilberforce", "equiano", "civil rights", "empire", "resistance"]),

    # --- KS2–3: The British Empire — core arc ---
    Topic("age_of_exploration", "The Age of Exploration — Trade, Navigation, and First Contact",
          "History", [2, 3], [5, 6, 7], 3, 4, ["elizabethan_era"],
          ["exploration", "trade", "navigation", "empire", "columbus", "africa", "americas"]),
    Topic("transatlantic_slave_trade", "The Transatlantic Slave Trade — Causes, Experience, and Resistance",
          "History", [2, 3], [6, 7, 8], 3, 5, ["age_of_exploration"],
          ["slave trade", "africa", "empire", "resistance", "abolition", "history"]),
    Topic("british_empire_expansion", "The British Empire — How and Why It Grew",
          "History", [2, 3], [6, 7, 8], 3, 4, ["age_of_exploration"],
          ["empire", "colonialism", "india", "africa", "trade", "britain", "power"]),
    Topic("empire_everyday_life", "Life Under the British Empire — Perspectives from Colonised Peoples",
          "History", [3], [7, 8, 9], 4, 5, ["british_empire_expansion"],
          ["empire", "colonialism", "india", "africa", "caribbean", "perspectives", "resistance"]),
    Topic("empire_trade_economy", "How the British Empire Shaped the World Economy",
          "History", [3], [7, 8, 9], 4, 5, ["british_empire_expansion", "industrial_revolution"],
          ["empire", "trade", "economy", "cotton", "sugar", "india", "globalisation"]),

    # --- KS2–3: Industrial Revolution (linked to Empire) ---
    Topic("industrial_revolution", "The Industrial Revolution — Factories, Cities, and Child Labour",
          "History", [2, 3], [6, 7, 8], 3, 4, ["union_of_britain"],
          ["industrial revolution", "factories", "cities", "technology", "britain", "change"]),
    Topic("victorian_britain", "Victorian Britain — Society, Reform, and the Height of Empire",
          "History", [2, 3], [6, 7, 8], 3, 4, ["industrial_revolution", "british_empire_expansion"],
          ["victorian", "britain", "reform", "empire", "poverty", "technology"]),

    # --- KS3: World Wars and Decolonisation ---
    Topic("ww1_causes_consequences", "World War One — Causes, Trenches, and the End of Empires",
          "History", [3], [7, 8], 3, 4, ["victorian_britain"],
          ["world war one", "ww1", "trenches", "empire", "europe", "modern history"]),
    Topic("ww2_global_conflict", "World War Two — Global Conflict, the Holocaust, and Allied Forces",
          "History", [3], [8, 9], 3, 5, ["ww1_causes_consequences"],
          ["world war two", "ww2", "holocaust", "empire", "commonwealth", "resistance", "modern history"]),
    Topic("decolonisation", "Decolonisation — Independence Movements and the End of Empire",
          "History", [3], [8, 9], 4, 5, ["empire_everyday_life", "ww2_global_conflict"],
          ["decolonisation", "independence", "india", "africa", "empire", "gandhi", "modern history"]),
    Topic("civil_rights_global", "Civil Rights — Struggles for Equality Around the World",
          "History", [3], [8, 9], 4, 5, ["abolition_movement", "decolonisation"],
          ["civil rights", "equality", "mlk", "mandela", "rosa parks", "empire", "modern history"]),
    Topic("cold_war_context", "The Cold War and Britain's Place in the World",
          "History", [3], [9], 4, 5, ["ww2_global_conflict"],
          ["cold war", "usa", "ussr", "nuclear", "modern history", "geopolitics"]),
    Topic("windrush_immigration", "Windrush and Post-War Immigration — Building Modern Britain",
          "History", [3], [8, 9], 3, 5, ["decolonisation"],
          ["windrush", "immigration", "caribbean", "empire", "identity", "modern britain"]),

    # --- KS3: Britain in Global Context ---
    Topic("history_of_democracy_britain", "Democracy in Britain — From Magna Carta to Today",
          "History", [2, 3], [6, 7, 8, 9], 3, 5, ["glorious_revolution"],
          ["democracy", "magna carta", "parliament", "rights", "britain", "citizenship"]),
    Topic("empire_legacy_today", "The Legacy of Empire — How History Shapes the World Today",
          "History", [3], [9], 5, 6, ["decolonisation", "empire_trade_economy"],
          ["empire", "legacy", "globalisation", "identity", "modern world", "critical thinking"]),
]

_GEOGRAPHY = [
    Topic("geography_local_ks1", "My Local Area — Maps and Places",
          "Geography", [1], [1, 2], 1, 2, [],
          ["geography", "maps", "local", "community"]),
    Topic("continents_oceans", "Continents and Oceans of the World",
          "Geography", [1, 2], [2, 3], 1, 2, [],
          ["geography", "world", "oceans", "maps"]),
    Topic("weather_climate", "Weather Patterns and Climate Zones",
          "Geography", [2], [3, 4], 2, 3, ["seasons_weather"],
          ["weather", "climate", "environment"]),
    Topic("rivers_mountains", "Rivers, Mountains, and Physical Landforms",
          "Geography", [2], [4, 5], 2, 3, [],
          ["rivers", "mountains", "earth science", "geography"]),
    Topic("biomes_habitats", "Biomes — Rainforests, Deserts, and Polar Regions",
          "Geography", [2], [5, 6], 3, 4, ["weather_climate", "animals_habitats"],
          ["biomes", "habitats", "climate", "animals"]),
    Topic("human_geography_ks2", "Human Geography — Settlements, Trade, and Land Use",
          "Geography", [2], [5, 6], 2, 3, ["geography_local_ks1"],
          ["human geography", "trade", "cities", "community"]),
    Topic("plate_tectonics", "Plate Tectonics — Volcanoes and Earthquakes",
          "Geography", [2, 3], [6, 7], 3, 4, ["rivers_mountains"],
          ["volcanoes", "earthquakes", "earth science", "geology"]),
    Topic("globalisation_ks3", "Globalisation — Trade, Migration, and Interdependence",
          "Geography", [3], [8, 9], 4, 5, ["human_geography_ks2"],
          ["globalisation", "trade", "migration", "society"]),
    Topic("climate_change_ks3", "Climate Change — Causes, Evidence, and Responses",
          "Geography", [3], [8, 9], 4, 5, ["weather_climate", "biomes_habitats"],
          ["climate change", "environment", "sustainability", "science"]),
]

_COMPUTING = [
    Topic("algorithms_ks1", "Algorithms — Giving Instructions and Sequences",
          "Computing", [1], [1, 2], 1, 2, [],
          ["coding", "algorithms", "computing", "logic"]),
    Topic("programming_scratch_ks2", "Programming — Scratch and Block-based Coding",
          "Computing", [2], [3, 4, 5], 2, 3, ["algorithms_ks1"],
          ["coding", "programming", "scratch", "games"]),
    Topic("networks_internet_ks2", "How the Internet Works",
          "Computing", [2], [5, 6], 2, 3, [],
          ["internet", "networks", "computing", "digital literacy"]),
    Topic("data_representation", "Data — Binary, Files, and Databases",
          "Computing", [3], [7, 8], 3, 4, ["networks_internet_ks2"],
          ["data", "binary", "computing"]),
    Topic("programming_python_ks3", "Programming — Python and Text-based Coding",
          "Computing", [3], [7, 8, 9], 3, 4, ["programming_scratch_ks2"],
          ["coding", "python", "programming", "text"]),
    Topic("cyber_security", "Cyber Security and Online Safety",
          "Computing", [2, 3], [5, 6, 7, 8, 9], 2, 4, [],
          ["safety", "internet", "digital literacy", "privacy"]),
    Topic("digital_literacy", "Digital Literacy — Evaluating Sources and Digital Wellbeing",
          "Computing", [2, 3], [4, 5, 6, 7], 3, 4, ["networks_internet_ks2"],
          ["internet", "media", "critical thinking", "wellbeing"]),
]

_ART_MUSIC = [
    Topic("art_drawing_ks1", "Art — Drawing, Painting, and Colour",
          "Art", [1], [1, 2], 1, 3, [],
          ["art", "drawing", "painting", "colour", "creative"]),
    Topic("art_ks2", "Art — Sculpture, Printing, and Famous Artists",
          "Art", [2], [3, 4, 5, 6], 2, 4, ["art_drawing_ks1"],
          ["art", "sculpture", "artists", "creative"]),
    Topic("music_rhythm_ks1", "Music — Pulse, Rhythm, and Singing",
          "Music", [1], [1, 2], 1, 3, [],
          ["music", "rhythm", "singing", "creative"]),
    Topic("music_notation_ks2", "Music — Reading Notation and Playing Instruments",
          "Music", [2], [3, 4, 5, 6], 2, 3, ["music_rhythm_ks1"],
          ["music", "notation", "instruments", "creative"]),
]

_PSHE = [
    Topic("health_wellbeing_ks1", "Health and Wellbeing — Feelings and Healthy Choices",
          "PSHE", [1], [1, 2], 1, 3, [],
          ["health", "emotions", "wellbeing", "feelings"]),
    Topic("relationships_ks2", "Relationships — Friendships, Family, and Respect",
          "PSHE", [2], [3, 4, 5, 6], 2, 3, ["health_wellbeing_ks1"],
          ["relationships", "friendship", "respect", "community"]),
    Topic("online_safety_pshe", "Online Safety — Safe Internet Use and Privacy",
          "PSHE", [2, 3], [4, 5, 6, 7, 8], 2, 4, [],
          ["internet safety", "privacy", "digital literacy"]),
    Topic("money_finance_ks2", "Money — Earning, Saving, and Spending",
          "PSHE", [2], [5, 6], 2, 3, [],
          ["money", "finance", "practical", "life skills"]),
]


# ---------------------------------------------------------------------------
# Grand Narratives — Montessori "Cosmic Curriculum" style big-picture arcs
# These are the overarching stories that give all other topics their context.
# Introduced at the cosmic level first, then zoomed into for detail.
# Not part of the NC core but deeply enriching and developmentally appropriate
# for ages 6-12 (Montessori's "second plane" — reason, imagination, big questions).
# ---------------------------------------------------------------------------

_GRAND_NARRATIVES = [
    # --- Story of the Universe ---
    Topic("universe_origin", "The Big Bang — How the Universe Began",
          "Grand Narrative", [1, 2], [2, 3, 4], 2, 4, [],
          ["universe", "big bang", "space", "origins", "science", "cosmology"]),
    Topic("stars_and_elements", "How Stars Were Born and Made the Elements",
          "Grand Narrative", [2], [4, 5, 6], 3, 4, ["universe_origin"],
          ["stars", "elements", "space", "nuclear fusion", "chemistry", "science"]),
    Topic("solar_system_formation", "How Our Solar System Formed",
          "Grand Narrative", [2], [4, 5], 2, 3, ["stars_and_elements"],
          ["solar system", "planets", "space", "origins", "earth science"]),
    Topic("earth_formation", "How the Earth Formed and Changed",
          "Grand Narrative", [2], [4, 5, 6], 3, 4, ["solar_system_formation"],
          ["earth", "geology", "volcanoes", "plate tectonics", "origins"]),
    Topic("cosmic_time_scale", "Deep Time — Understanding Billions of Years",
          "Grand Narrative", [2, 3], [5, 6, 7], 3, 5, ["universe_origin", "earth_formation"],
          ["time", "deep time", "geology", "evolution", "universe", "scale"]),

    # --- Story of Life on Earth ---
    Topic("origin_of_life", "How Life Began — From Chemicals to the First Cell",
          "Grand Narrative", [2], [5, 6], 3, 4, ["earth_formation"],
          ["life", "origins", "cells", "chemistry", "biology", "evolution"]),
    Topic("age_of_single_cells", "Billions of Years of Single-Celled Life",
          "Grand Narrative", [2], [5, 6], 3, 4, ["origin_of_life"],
          ["bacteria", "evolution", "oxygen", "life", "biology", "deep time"]),
    Topic("cambrian_explosion", "The Cambrian Explosion — Life Gets Complex",
          "Grand Narrative", [2], [5, 6], 3, 4, ["age_of_single_cells"],
          ["cambrian", "fossils", "evolution", "animals", "oceans", "biology"]),
    Topic("age_of_fish", "The Age of Fish — Life Conquers the Seas",
          "Grand Narrative", [2], [5, 6], 2, 3, ["cambrian_explosion"],
          ["fish", "oceans", "evolution", "fossils", "prehistoric life"]),
    Topic("life_onto_land", "Life Comes Ashore — From Sea to Land",
          "Grand Narrative", [2], [5, 6], 3, 4, ["age_of_fish"],
          ["amphibians", "evolution", "land", "plants", "prehistoric life"]),
    Topic("age_of_dinosaurs", "The Age of Dinosaurs — Rise and Fall",
          "Grand Narrative", [1, 2], [2, 3, 4, 5, 6], 2, 4, ["life_onto_land"],
          ["dinosaurs", "prehistoric life", "extinction", "fossils", "evolution",
           "cretaceous", "jurassic"]),
    Topic("age_of_mammals", "The Rise of Mammals After the Extinction",
          "Grand Narrative", [2], [5, 6], 3, 4, ["age_of_dinosaurs"],
          ["mammals", "extinction", "evolution", "prehistoric life", "ice age"]),
    Topic("human_evolution", "The Story of Human Evolution",
          "Grand Narrative", [2, 3], [6, 7, 8], 3, 5,
          ["age_of_mammals"],
          ["human evolution", "prehistoric humans", "africa", "homo sapiens",
           "tools", "fire", "language"]),

    # --- Story of Human Civilisation ---
    Topic("human_migration_out_of_africa", "Humans Spread Across the Earth",
          "Grand Narrative", [2, 3], [5, 6, 7], 3, 4, ["human_evolution"],
          ["migration", "prehistoric humans", "africa", "ice age", "exploration",
           "australians", "americas"]),
    Topic("agricultural_revolution_story", "The Agricultural Revolution — From Hunter to Farmer",
          "Grand Narrative", [2], [5, 6], 3, 4, ["human_migration_out_of_africa"],
          ["farming", "neolithic", "revolution", "civilisation", "food", "trade"]),
    Topic("first_civilisations", "The First Cities and Writing",
          "Grand Narrative", [2], [5, 6], 3, 4, ["agricultural_revolution_story"],
          ["mesopotamia", "sumer", "writing", "cities", "trade", "civilisation",
           "egypt", "indus valley"]),
    Topic("story_of_trade_and_empire", "How Trade and Empire Shaped the World",
          "Grand Narrative", [2, 3], [6, 7, 8, 9], 4, 5,
          ["first_civilisations"],
          ["trade", "empire", "silk road", "colonialism", "globalisation",
           "power", "history"]),
    Topic("story_of_science", "The Story of Science — How Humans Learned to Understand the World",
          "Grand Narrative", [2, 3], [6, 7, 8, 9], 4, 5,
          ["first_civilisations"],
          ["science", "history of science", "newton", "galileo", "darwin",
           "einstein", "discovery"]),
    Topic("story_of_language", "The Story of Language — How Humans Learned to Communicate",
          "Grand Narrative", [2, 3], [5, 6, 7], 3, 5,
          ["human_evolution"],
          ["language", "writing", "communication", "linguistics", "stories",
           "babel", "culture"]),
]


# ---------------------------------------------------------------------------
# Vocational and Interest-Led Topics (beyond core NC)
# ---------------------------------------------------------------------------

_VOCATIONAL = [

    # =========================================================================
    # COOKING AND FOOD
    # Project arc: safety → techniques → recipes → nutrition → cuisine
    # =========================================================================
    Topic("cooking_safety_basics", "Kitchen Safety — Equipment, Heat, and Hygiene",
          "Vocational", [1, 2], [2, 3, 4], 1, 2, [],
          ["cooking", "safety", "kitchen", "hygiene", "practical", "hands-on"],
          vocational=True),
    Topic("cooking_techniques_ks1", "Basic Cooking Techniques — Mixing, Cutting, and Measuring",
          "Vocational", [1, 2], [2, 3, 4], 1, 3, ["cooking_safety_basics"],
          ["cooking", "techniques", "measuring", "practical", "hands-on", "maths"],
          vocational=True),
    Topic("cooking_eggs_dairy", "Cooking with Eggs and Dairy — Scrambled Eggs to Simple Sauces",
          "Vocational", [2], [3, 4, 5], 2, 3, ["cooking_techniques_ks1"],
          ["cooking", "eggs", "dairy", "sauces", "practical", "food"],
          vocational=True),
    Topic("baking_bread_pastry", "Baking — Bread, Pastry, and How Yeast Works",
          "Vocational", [2], [4, 5, 6], 2, 4, ["cooking_techniques_ks1"],
          ["baking", "bread", "yeast", "chemistry", "practical", "food"],
          vocational=True),
    Topic("cooking_vegetables", "Cooking Vegetables — Seasonal, Roasted, and from the Garden",
          "Vocational", [2], [3, 4, 5, 6], 2, 3, ["cooking_safety_basics"],
          ["cooking", "vegetables", "seasonal", "nutrition", "practical", "gardening"],
          vocational=True),
    Topic("nutrition_food_science", "Nutrition — What Food Does in Your Body",
          "Vocational", [2], [4, 5, 6, 7], 2, 4, ["cooking_safety_basics"],
          ["nutrition", "food", "health", "biology", "science", "practical"],
          vocational=True),
    Topic("cooking_world_cuisines", "World Cuisines — Recipes from Different Cultures",
          "Vocational", [2, 3], [5, 6, 7, 8], 3, 4, ["cooking_vegetables"],
          ["cooking", "culture", "world food", "geography", "creative", "food"],
          vocational=True),
    Topic("fermentation_preservation", "Fermentation and Preserving — Yoghurt, Pickles, and Jam",
          "Vocational", [2, 3], [6, 7, 8], 3, 5, ["cooking_eggs_dairy"],
          ["fermentation", "food science", "chemistry", "biology", "practical"],
          vocational=True),
    Topic("meal_planning_budgeting", "Meal Planning — Feeding People on a Budget",
          "Vocational", [3], [7, 8, 9], 3, 5, ["nutrition_food_science", "cooking_vegetables"],
          ["cooking", "planning", "budget", "life skills", "maths", "nutrition"],
          vocational=True),

    # =========================================================================
    # GROWING FOOD AND GARDENING
    # Project arc: soil → seeds → growing → harvest → seasons
    # =========================================================================
    Topic("soil_and_compost", "Soil — What It Is, What Lives in It, and How to Make Compost",
          "Vocational", [1, 2], [2, 3, 4], 1, 3, [],
          ["soil", "gardening", "worms", "compost", "nature", "biology", "hands-on"],
          vocational=True),
    Topic("seeds_germination", "Seeds — How They Sprout and What They Need",
          "Vocational", [1, 2], [2, 3, 4], 1, 2, ["soil_and_compost"],
          ["seeds", "germination", "gardening", "biology", "plants", "hands-on"],
          vocational=True),
    Topic("growing_salad_herbs", "Growing Salad and Herbs — Your First Crops",
          "Vocational", [1, 2], [2, 3, 4, 5], 1, 3, ["seeds_germination"],
          ["gardening", "salad", "herbs", "growing", "practical", "food", "hands-on"],
          vocational=True),
    Topic("growing_vegetables", "Growing Vegetables — From Seed to Plate",
          "Vocational", [2], [3, 4, 5, 6], 2, 3, ["growing_salad_herbs"],
          ["gardening", "vegetables", "growing", "seasonal", "practical", "food"],
          vocational=True),
    Topic("fruit_trees_soft_fruit", "Fruit — Trees, Bushes, and How Fruit Forms",
          "Vocational", [2], [4, 5, 6], 2, 3, ["growing_vegetables"],
          ["fruit", "trees", "gardening", "biology", "pollination", "food"],
          vocational=True),
    Topic("garden_pests_wildlife", "Pests, Predators, and Wildlife in the Garden",
          "Vocational", [2], [4, 5, 6], 2, 4, ["growing_vegetables"],
          ["pests", "wildlife", "ecosystems", "gardening", "nature", "biology"],
          vocational=True),
    Topic("seasonal_growing_calendar", "The Seasonal Growing Calendar — What to Plant When",
          "Vocational", [2], [5, 6, 7], 3, 4, ["growing_vegetables"],
          ["seasons", "gardening", "planning", "calendar", "practical", "food"],
          vocational=True),
    Topic("allotment_project", "Running an Allotment — Planning, Rotating Crops, and Harvesting",
          "Vocational", [2, 3], [6, 7, 8], 3, 5, ["seasonal_growing_calendar"],
          ["allotment", "project", "planning", "crops", "gardening", "practical"],
          vocational=True),

    # =========================================================================
    # WOODWORK AND MAKING
    # Project arc: safety → measuring → hand tools → joining → finishing → projects
    # =========================================================================
    Topic("woodwork_safety", "Workshop Safety — Tools, Rules, and Protective Equipment",
          "Vocational", [2], [4, 5, 6], 1, 2, [],
          ["woodwork", "safety", "tools", "making", "workshop", "practical"],
          vocational=True),
    Topic("woodwork_measuring_marking", "Measuring and Marking — Accuracy in Making",
          "Vocational", [2], [4, 5, 6], 2, 3, ["woodwork_safety", "measurement_ks1"],
          ["woodwork", "measuring", "marking", "maths", "precision", "practical"],
          vocational=True),
    Topic("woodwork_hand_tools", "Hand Tools — Saw, Plane, Chisel, and Mallet",
          "Vocational", [2], [5, 6, 7], 2, 3, ["woodwork_measuring_marking"],
          ["woodwork", "hand tools", "saw", "chisel", "making", "practical", "hands-on"],
          vocational=True),
    Topic("woodwork_joining", "Joining Wood — Nails, Screws, Glue, and Simple Joints",
          "Vocational", [2, 3], [5, 6, 7, 8], 2, 3, ["woodwork_hand_tools"],
          ["woodwork", "joining", "screws", "joints", "making", "practical"],
          vocational=True),
    Topic("woodwork_finishing", "Finishing — Sanding, Painting, and Protecting Wood",
          "Vocational", [2, 3], [5, 6, 7, 8], 2, 3, ["woodwork_joining"],
          ["woodwork", "finishing", "sanding", "painting", "making", "practical"],
          vocational=True),
    Topic("woodwork_project_box", "Project: Build a Wooden Box",
          "Vocational", [2, 3], [5, 6, 7], 3, 4, ["woodwork_joining"],
          ["woodwork", "project", "box", "making", "practical", "hands-on"],
          vocational=True),
    Topic("woodwork_project_shelf", "Project: Build a Simple Shelf",
          "Vocational", [3], [7, 8, 9], 3, 4, ["woodwork_finishing"],
          ["woodwork", "project", "shelf", "making", "practical", "engineering"],
          vocational=True),
    Topic("woodwork_design_process", "Design — Sketching, Prototyping, and Iterating",
          "Vocational", [2, 3], [6, 7, 8, 9], 3, 5, ["woodwork_joining"],
          ["design", "woodwork", "sketching", "prototyping", "engineering", "making"],
          vocational=True),

    # =========================================================================
    # ELECTRONICS AND ROBOTICS
    # Project arc: circuits → components → Arduino/micro:bit → sensors → robotics
    # =========================================================================
    Topic("electronics_circuits_basics", "Circuits — Batteries, Bulbs, and Simple Connections",
          "Vocational", [2], [4, 5], 1, 3, ["electricity_ks2"],
          ["electronics", "circuits", "electricity", "practical", "hands-on", "physics"],
          vocational=True),
    Topic("electronics_components", "Components — LEDs, Resistors, Buzzers, and Switches",
          "Vocational", [2], [5, 6], 2, 3, ["electronics_circuits_basics"],
          ["electronics", "components", "LED", "resistors", "making", "practical"],
          vocational=True),
    Topic("electronics_breadboard", "Breadboards — Prototyping Without Soldering",
          "Vocational", [2, 3], [5, 6, 7], 2, 3, ["electronics_components"],
          ["electronics", "breadboard", "prototyping", "making", "practical", "engineering"],
          vocational=True),
    Topic("microbit_intro", "BBC micro:bit — Your First Programmable Device",
          "Vocational", [2], [5, 6], 2, 3, ["electronics_circuits_basics", "algorithms_ks1"],
          ["micro:bit", "microcontroller", "coding", "electronics", "practical", "making"],
          vocational=True),
    Topic("microbit_sensors", "micro:bit Sensors — Light, Temperature, Motion, and Compass",
          "Vocational", [2, 3], [5, 6, 7], 3, 4, ["microbit_intro"],
          ["micro:bit", "sensors", "data", "science", "coding", "electronics"],
          vocational=True),
    Topic("arduino_intro", "Arduino — Microcontrollers and Physical Computing",
          "Vocational", [3], [7, 8, 9], 3, 4, ["electronics_breadboard", "programming_python_ks3"],
          ["arduino", "microcontroller", "C++", "physical computing", "electronics", "making"],
          vocational=True),
    Topic("robotics_building", "Robotics — Building a Moving Robot",
          "Vocational", [2, 3], [6, 7, 8, 9], 3, 5,
          ["microbit_intro"],
          ["robotics", "motors", "making", "engineering", "coding", "electronics", "practical"],
          vocational=True),
    Topic("robotics_sensors_autonomy", "Robotics — Sensors, Feedback, and Autonomous Behaviour",
          "Vocational", [3], [8, 9], 4, 5, ["robotics_building"],
          ["robotics", "sensors", "autonomy", "AI", "engineering", "coding"],
          vocational=True),
    Topic("electronics_soldering", "Soldering — Permanent Connections and PCB Assembly",
          "Vocational", [3], [8, 9], 2, 3, ["electronics_breadboard"],
          ["soldering", "PCB", "electronics", "making", "practical", "hands-on"],
          vocational=True),

    # =========================================================================
    # PROGRAMMING
    # Project arc: blocks → Scratch games → Python basics → projects → web/data
    # =========================================================================
    Topic("programming_unplugged", "Unplugged Computing — Algorithms Without a Screen",
          "Vocational", [1, 2], [2, 3, 4], 1, 2, [],
          ["coding", "algorithms", "unplugged", "logic", "computing", "hands-on"],
          vocational=True),
    Topic("scratch_first_project", "Scratch — Animating a Character",
          "Vocational", [2], [3, 4], 1, 3, ["algorithms_ks1"],
          ["scratch", "coding", "animation", "blocks", "computing", "creative"],
          vocational=True),
    Topic("scratch_game_platformer", "Scratch — Building a Platform Game",
          "Vocational", [2], [4, 5], 2, 4, ["scratch_first_project"],
          ["scratch", "game", "coding", "loops", "conditions", "computing", "creative"],
          vocational=True),
    Topic("scratch_variables_score", "Scratch — Variables, Score, and Lives",
          "Vocational", [2], [4, 5, 6], 2, 3, ["scratch_game_platformer"],
          ["scratch", "variables", "coding", "game", "computing", "maths"],
          vocational=True),
    Topic("python_first_steps", "Python — Your First Lines of Code",
          "Vocational", [2, 3], [5, 6, 7], 2, 3, ["scratch_variables_score"],
          ["python", "coding", "text", "programming", "computing", "variables"],
          vocational=True),
    Topic("python_loops_functions", "Python — Loops, Functions, and Making Code Reusable",
          "Vocational", [3], [6, 7, 8], 3, 4, ["python_first_steps"],
          ["python", "loops", "functions", "coding", "programming", "computing"],
          vocational=True),
    Topic("python_turtle_art", "Python Turtle — Drawing Patterns and Shapes with Code",
          "Vocational", [2, 3], [6, 7, 8], 2, 4, ["python_first_steps"],
          ["python", "turtle", "art", "geometry", "maths", "coding", "creative"],
          vocational=True),
    Topic("python_text_games", "Python — Build a Text Adventure Game",
          "Vocational", [3], [7, 8, 9], 3, 5, ["python_loops_functions"],
          ["python", "game", "text", "story", "coding", "creative", "programming"],
          vocational=True),
    Topic("python_data_files", "Python — Reading Files and Working with Data",
          "Vocational", [3], [8, 9], 3, 4, ["python_loops_functions"],
          ["python", "data", "files", "csv", "coding", "computing", "maths"],
          vocational=True),
    Topic("web_html_css", "Web — HTML, CSS, and Building a Web Page",
          "Vocational", [3], [7, 8, 9], 3, 4, ["python_first_steps"],
          ["html", "css", "web", "design", "coding", "computing", "creative"],
          vocational=True),
    Topic("programming_project_own", "Personal Coding Project — Build Something You Want to Exist",
          "Vocational", [3], [8, 9], 4, 6, ["python_loops_functions"],
          ["coding", "project", "creative", "computing", "programming", "making"],
          vocational=True),

    # =========================================================================
    # OTHER PRACTICAL SKILLS (retained from before, tidied)
    # =========================================================================
    Topic("first_aid_ks2", "First Aid — Basic Safety and Emergency Response",
          "Vocational", [2, 3], [5, 6, 7, 8], 2, 3, [],
          ["first aid", "safety", "health", "life skills", "practical"],
          vocational=True),
    Topic("sewing_basics", "Sewing — Hand Stitches, Buttons, and Repairs",
          "Vocational", [2], [4, 5, 6], 1, 2, [],
          ["sewing", "textiles", "making", "practical", "life skills", "hands-on"],
          vocational=True),
    Topic("sewing_project", "Sewing Project — Make a Bag or a Cushion",
          "Vocational", [2, 3], [5, 6, 7, 8], 2, 3, ["sewing_basics"],
          ["sewing", "project", "textiles", "making", "creative", "hands-on"],
          vocational=True),
    Topic("budgeting_life_skills", "Budgeting and Personal Finance",
          "Vocational", [2, 3], [6, 7, 8, 9], 3, 4, ["money_finance_ks2"],
          ["money", "budgeting", "finance", "life skills", "practical"],
          vocational=True),
    Topic("map_navigation", "Map Reading and Navigation",
          "Vocational", [2, 3], [4, 5, 6, 7, 8], 2, 3, ["geography_local_ks1"],
          ["maps", "navigation", "geography", "outdoor", "practical"],
          vocational=True),

    # --- Society and Enterprise ---
    Topic("entrepreneurship", "Entrepreneurship — Ideas, Products, and Business Plans",
          "Vocational", [3], [7, 8, 9], 4, 6, ["budgeting_life_skills"],
          ["business", "enterprise", "money", "planning", "design"],
          vocational=True),
    Topic("volunteering_community", "Community — Volunteering, Rights, and Responsibilities",
          "Vocational", [2, 3], [5, 6, 7, 8, 9], 3, 5, ["relationships_ks2"],
          ["community", "volunteering", "citizenship", "values"],
          vocational=True),
    Topic("journalism_news", "Journalism — Writing News, Opinion, and Fact-Checking",
          "Vocational", [3], [7, 8, 9], 4, 5, ["media_literacy_ks3"],
          ["journalism", "writing", "media", "critical thinking", "news"],
          vocational=True),
    Topic("debate_public_speaking", "Debate and Public Speaking",
          "Vocational", [2, 3], [5, 6, 7, 8, 9], 4, 6, ["reading_comprehension_ks2"],
          ["debate", "speaking", "argument", "confidence", "critical thinking"],
          vocational=True),

    # --- Wellbeing and Sport ---
    Topic("mindfulness_ks2", "Mindfulness and Mental Wellbeing",
          "Vocational", [2, 3], [4, 5, 6, 7, 8, 9], 2, 4, ["health_wellbeing_ks1"],
          ["mindfulness", "wellbeing", "mental health", "emotional"],
          vocational=True),
    Topic("sport_teamwork", "Sport, Games, and Teamwork",
          "Vocational", [1, 2, 3], [1, 2, 3, 4, 5, 6, 7, 8, 9], 1, 3, [],
          ["sport", "teamwork", "health", "physical", "games"],
          vocational=True),

    # --- Language and Culture ---
    Topic("sign_language_bsl", "British Sign Language — Basic Signs and Communication",
          "Vocational", [1, 2, 3], [2, 3, 4, 5, 6, 7, 8, 9], 1, 3, [],
          ["sign language", "BSL", "communication", "inclusion"],
          vocational=True),
    Topic("mythology_stories", "Myths and Legends from Around the World",
          "Vocational", [1, 2], [3, 4, 5, 6], 2, 4, ["reading_comprehension_ks1"],
          ["myths", "stories", "culture", "history", "dragons", "heroes"],
          vocational=True),
    Topic("philosophy_for_children", "Philosophy for Children — Big Questions and Thinking",
          "Vocational", [2, 3], [5, 6, 7, 8, 9], 4, 6, ["reading_comprehension_ks2"],
          ["philosophy", "thinking", "ethics", "big questions", "critical thinking"],
          vocational=True),
]


# ---------------------------------------------------------------------------
# Full curriculum registry
# ---------------------------------------------------------------------------

CURRICULUM: list[Topic] = (
    _ENGLISH + _MATHS + _SCIENCE + _HISTORY + _GEOGRAPHY +
    _COMPUTING + _ART_MUSIC + _PSHE + _VOCATIONAL + _GRAND_NARRATIVES
)

_by_id: dict[str, Topic] = {t.id: t for t in CURRICULUM}


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_topic(topic_id: str) -> Optional[Topic]:
    return _by_id.get(topic_id)


def topics_for_age(age: int, include_vocational: bool = True) -> list[Topic]:
    """Return all topics appropriate for a given age."""
    year = max(1, age - 5)
    return [
        t for t in CURRICULUM
        if year in t.year_groups and (include_vocational or not t.vocational)
    ]


def topics_for_subject(subject: str, age: Optional[int] = None) -> list[Topic]:
    results = [t for t in CURRICULUM if t.subject.lower() == subject.lower()]
    if age is not None:
        year = max(1, age - 5)
        results = [t for t in results if year in t.year_groups]
    return results


def topics_by_interest(tags: list[str], age: Optional[int] = None) -> list[Topic]:
    """Return topics matching any of the given interest tags, sorted by match count."""
    tag_set = {t.lower() for t in tags}
    scored = []
    for topic in CURRICULUM:
        if age is not None:
            year = max(1, age - 5)
            if year not in topic.year_groups:
                continue
        matches = len(tag_set & {t.lower() for t in topic.tags})
        if matches:
            scored.append((matches, topic))
    scored.sort(key=lambda x: -x[0])
    return [t for _, t in scored]


def prerequisites_met(topic_id: str, mastered_ids: list[str]) -> bool:
    """Check whether all prerequisites for a topic have been mastered."""
    topic = _by_id.get(topic_id)
    if not topic:
        return False
    mastered = set(mastered_ids)
    return all(p in mastered for p in topic.prerequisites)


def next_topics(age: int, mastered_ids: list[str],
                interests: Optional[list[str]] = None,
                allow_ahead: bool = True) -> list[Topic]:
    """
    Return topics that have prerequisites met and haven't been mastered yet.

    By default (allow_ahead=True) includes topics above the child's year group
    if they have matching interests and prerequisites met — a child passionate
    about astronomy shouldn't be blocked from learning about the solar system
    just because they're in Year 3.

    Topics with accelerated_ok=False are never surfaced above year group,
    regardless of interest — these have hard developmental prerequisites that
    can't be shortcut (e.g. algebra before solid concrete number sense).
    """
    mastered = set(mastered_ids)
    year = max(1, age - 5)

    # Base: age-appropriate topics with prerequisites met
    candidates = [
        t for t in CURRICULUM
        if t.id not in mastered
        and year in t.year_groups
        and prerequisites_met(t.id, mastered_ids)
    ]

    # Accelerated: topics one key stage ahead if interests match and accelerated_ok
    if allow_ahead and interests:
        interest_set = {i.lower() for i in interests}
        for t in CURRICULUM:
            if (t.id not in mastered
                    and t.accelerated_ok
                    and year not in t.year_groups
                    and min(t.year_groups) <= year + 3  # max 3 years ahead
                    and prerequisites_met(t.id, mastered_ids)
                    and len(interest_set & {tag.lower() for tag in t.tags}) >= 2):
                candidates.append(t)

    if interests:
        interest_set = {i.lower() for i in interests}
        candidates.sort(
            key=lambda t: (
                # Deprioritise above-year topics slightly so they don't crowd out
                # age-appropriate ones, but a strong interest match can override
                -(len(interest_set & {tag.lower() for tag in t.tags}) * 2
                  - (0 if year in t.year_groups else 1))
            )
        )
    return candidates


def subjects() -> list[str]:
    return sorted(set(t.subject for t in CURRICULUM))
