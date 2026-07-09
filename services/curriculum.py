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

    # Model progression — the "lies to children" principle.
    # Many topics teach an intentionally simplified model that is useful and
    # approximately true, but will be refined later. When a child has mastered
    # the prerequisite topic deeply enough, the refined model unlocks.
    #
    # model_level: int — 1=introductory simplification, 2=refined model,
    #                     3=full/graduate-level model. Default 1.
    # supersedes: str — topic id of the simpler model this topic corrects.
    #   When a child has mastered `supersedes` to bloom_target, the tutor
    #   can introduce the refinement naturally: "Remember how we said X?
    #   That's mostly true, but here's the fuller picture..."
    model_level: int = 1
    supersedes: Optional[str] = None


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

    # --- Number Theory ---
    Topic("primes_factors", "Primes, Factors, and Multiples",
          "Maths", [2, 3], [4, 5, 6, 7], 2, 4, ["multiplication_tables"],
          ["number theory", "primes", "factors", "multiples", "HCF", "LCM",
           "sieve of eratosthenes"]),
    Topic("powers_roots", "Square Numbers, Cube Numbers, and Powers",
          "Maths", [2, 3], [5, 6, 7, 8], 2, 4, ["multiplication_tables"],
          ["powers", "square numbers", "cube numbers", "indices", "square roots"]),

    # --- Number Sense ---
    Topic("mental_maths_strategies", "Mental Maths — Tricks, Shortcuts, and Number Sense",
          "Maths", [1, 2], [2, 3, 4, 5], 1, 3, ["addition_subtraction_ks1"],
          ["mental maths", "number bonds", "compensation", "partitioning",
           "near doubles", "arithmetic strategies"]),
    Topic("estimation_rounding", "Estimation, Rounding, and Fermi Problems",
          "Maths", [2, 3], [4, 5, 6, 7, 8], 2, 4, ["place_value"],
          ["estimation", "rounding", "significant figures", "Fermi problems",
           "order of magnitude", "approximation"]),
    Topic("time_calendars", "Time — Clocks, Calendars, and Time Zones",
          "Maths", [1, 2], [2, 3, 4, 5], 1, 3, ["counting_numbers"],
          ["time", "clocks", "calendars", "24-hour clock", "time zones", "duration"]),

    # --- Sequences, Functions, and Geometry ---
    Topic("sequences_patterns", "Sequences and Patterns — Arithmetic, Geometric, and Fibonacci",
          "Maths", [2, 3], [4, 5, 6, 7, 8], 2, 4, ["multiplication_tables"],
          ["sequences", "patterns", "Fibonacci", "arithmetic sequences",
           "geometric sequences", "nth term", "Pascal's triangle"]),
    Topic("functions_graphs", "Functions and Graphs — Input, Output, and Straight Lines",
          "Maths", [3], [7, 8, 9], 3, 4, ["algebra_ks3"],
          ["functions", "graphs", "y=mx+c", "gradient", "intercept",
           "coordinates", "linear"]),
    Topic("pythagoras_theorem", "Pythagoras' Theorem — Right Triangles and the Most Famous Proof",
          "Maths", [3], [8, 9], 3, 5, ["geometry_ks2", "powers_roots"],
          ["Pythagoras", "right triangles", "hypotenuse", "proof",
           "geometry", "distance", "theorem"]),

    # --- Logic and Discrete Maths ---
    Topic("logic_sets", "Logic and Sets — Venn Diagrams, AND, OR, and NOT",
          "Maths", [2, 3], [5, 6, 7, 8], 3, 5, ["statistics_ks2"],
          ["logic", "sets", "Venn diagrams", "AND", "OR", "NOT",
           "intersection", "union", "set theory"]),
    Topic("combinatorics", "Combinatorics — Counting, Permutations, and Combinations",
          "Maths", [2, 3], [6, 7, 8, 9], 3, 5,
          ["multiplication_tables", "probability_ks3"],
          ["combinatorics", "counting", "permutations", "combinations",
           "multiplication principle", "arrangements"]),

    # --- Mathematical Reasoning and Culture ---
    Topic("mathematical_reasoning", "Mathematical Reasoning — Proof, Conjectures, and Counterexamples",
          "Maths", [2, 3], [6, 7, 8, 9], 4, 6, ["algebra_ks3"],
          ["proof", "reasoning", "conjecture", "counterexample",
           "always sometimes never", "deduction", "logic"],
          accelerated_ok=False),
    Topic("problem_solving_strategies", "Problem-Solving Strategies — How to Attack Hard Maths",
          "Maths", [2, 3], [5, 6, 7, 8, 9], 3, 5,
          ["addition_subtraction_ks1"],
          ["problem solving", "heuristics", "working backwards", "systematic listing",
           "draw a diagram", "trial and improvement", "pattern finding"]),
    Topic("history_of_maths", "The History of Mathematics — Mathematicians and Big Ideas",
          "Maths", [2, 3], [5, 6, 7, 8, 9], 2, 4, [],
          ["history of maths", "Euclid", "Al-Khwarizmi", "Newton", "Euler",
           "Gauss", "Ramanujan", "Ada Lovelace", "mathematicians"]),
    Topic("mathematical_beauty", "Mathematical Beauty — Pi, Phi, Fractals, and Patterns in Nature",
          "Maths", [2, 3], [5, 6, 7, 8, 9], 2, 5, ["sequences_patterns"],
          ["pi", "golden ratio", "phi", "Fibonacci", "fractals",
           "mathematical beauty", "infinity", "patterns in nature", "spirals"]),
    Topic("financial_maths", "Financial Maths — Interest, Percentage Change, and Real Money",
          "Maths", [2, 3], [6, 7, 8, 9], 3, 5,
          ["decimals_percentages", "ratio_proportion"],
          ["finance", "interest", "compound interest", "percentage change",
           "VAT", "tax", "inflation", "depreciation"]),
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

    # --- Science gaps added from audit ---
    Topic("astronomy_ks3", "Advanced Astronomy — Stars, Black Holes, and the Expanding Universe",
          "Science", [3], [7, 8, 9], 3, 5, ["earth_space_ks2"],
          ["astronomy", "stars", "black holes", "exoplanets", "universe",
           "stellar evolution", "space", "JWST"]),
    Topic("nervous_system", "Brain and Nervous System — Neurons, Reflexes, and the Mind",
          "Science", [2, 3], [5, 6, 7, 8], 2, 4, ["human_body_ks2", "cells_ks3"],
          ["nervous system", "brain", "neurons", "synapses", "reflex",
           "human body", "neuroscience", "biology"]),
    Topic("immune_system", "Immune System — Pathogens, Vaccination, and Antibiotic Resistance",
          "Science", [2, 3], [6, 7, 8], 2, 4, ["living_things_ks1", "cells_ks3"],
          ["immune system", "vaccination", "antibiotics", "bacteria", "virus",
           "pathogen", "health", "biology", "resistance"]),
    Topic("reproductive_biology", "Reproduction — Plants, Animals, and Human Development",
          "Science", [2, 3], [5, 6, 7, 8], 2, 4,
          ["plants_ks2", "animals_habitats", "human_body_ks2"],
          ["reproduction", "puberty", "fertilisation", "life cycle",
           "biology", "variation", "human body"]),
    Topic("carbon_cycle", "The Carbon Cycle — Photosynthesis, Respiration, and Climate",
          "Science", [3], [6, 7, 8, 9], 3, 5,
          ["plants_ks2", "ecosystems_ks3", "chemical_reactions"],
          ["carbon cycle", "photosynthesis", "respiration", "decomposition",
           "fossil fuels", "climate", "chemistry", "biology"]),
    Topic("nitrogen_cycle", "The Nitrogen Cycle — Fixation, Nitrification, and Farming",
          "Science", [3], [8, 9], 3, 5,
          ["plants_ks2", "ecosystems_ks3", "carbon_cycle"],
          ["nitrogen cycle", "fixation", "bacteria", "fertiliser", "farming",
           "eutrophication", "chemistry", "biology"]),
    Topic("food_webs_energy_flow", "Food Webs and Energy Flow — Trophic Levels and Biomass",
          "Science", [2, 3], [5, 6, 7, 8], 2, 4,
          ["animals_habitats", "biomes_habitats"],
          ["food webs", "trophic levels", "energy flow", "biomass", "ecology",
           "producer", "consumer", "keystone species"]),
    Topic("pressure_buoyancy", "Pressure, Buoyancy, and Archimedes",
          "Science", [2], [5, 6, 7], 2, 4,
          ["forces_magnets", "particle_model"],
          ["pressure", "buoyancy", "Archimedes", "upthrust", "floating",
           "sinking", "physics", "fluid mechanics"]),
    Topic("simple_machines", "Simple Machines — Levers, Pulleys, Gears, and Mechanical Advantage",
          "Science", [2], [3, 4, 5, 6], 1, 3, ["forces_magnets"],
          ["levers", "pulleys", "gears", "mechanical advantage", "simple machines",
           "forces", "physics", "engineering", "hands-on"]),
    Topic("heat_thermal_energy", "Heat Transfer — Conduction, Convection, and Radiation",
          "Science", [2], [4, 5, 6, 7], 2, 4,
          ["materials_ks1", "particle_model"],
          ["heat transfer", "conduction", "convection", "radiation",
           "insulation", "thermal energy", "physics"]),
    Topic("electricity_ks3", "Electricity at KS3 — Voltage, Current, Resistance, and Ohm's Law",
          "Science", [3], [7, 8, 9], 3, 5,
          ["electricity_ks2"],
          ["electricity", "voltage", "current", "resistance", "Ohm's law",
           "power", "series", "parallel", "physics", "quantitative"]),
    Topic("periodic_table", "The Periodic Table — Elements, Groups, and Atomic Structure",
          "Science", [3], [7, 8, 9], 2, 4,
          ["particle_model", "chemical_reactions"],
          ["periodic table", "elements", "groups", "periods", "atomic structure",
           "proton", "electron", "Mendeleev", "chemistry"]),
    Topic("acids_bases_ph", "Acids, Bases, and pH — Neutralisation and Everyday Chemistry",
          "Science", [3], [7, 8, 9], 3, 4,
          ["chemical_reactions", "particle_model"],
          ["acids", "bases", "pH", "neutralisation", "indicators",
           "chemistry", "ions", "salt", "quantitative"]),
    Topic("oxidation_combustion", "Oxidation and Combustion — Fire, Rusting, and Energy Release",
          "Science", [2, 3], [5, 6, 7, 8], 2, 4,
          ["properties_materials_ks2", "chemical_reactions"],
          ["oxidation", "combustion", "rusting", "fire triangle",
           "chemistry", "energy", "carbon cycle", "fire safety"]),
    Topic("rates_of_reaction", "Rates of Reaction — Concentration, Temperature, and Catalysts",
          "Science", [3], [8, 9], 3, 5,
          ["chemical_reactions", "particle_model", "acids_bases_ph"],
          ["rates of reaction", "concentration", "temperature", "surface area",
           "catalyst", "collision theory", "chemistry", "kinetics"]),
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

    # --- Geography gaps from audit ---
    Topic("map_skills_ks2", "Map Skills — Grid References, Contour Lines, and OS Maps",
          "Geography", [2], [3, 4, 5, 6, 7], 1, 3,
          ["geography_local_ks1", "continents_oceans"],
          ["maps", "grid references", "contour lines", "OS maps", "GIS",
           "spatial reasoning", "fieldwork", "geography"]),
    Topic("water_cycle_depth", "The Water Cycle in Depth — Groundwater, Aquifers, and Human Impact",
          "Geography", [2], [4, 5, 6, 7], 2, 4,
          ["weather_climate", "rivers_mountains", "plants_ks2"],
          ["water cycle", "groundwater", "aquifer", "transpiration",
           "hydrology", "flooding", "drought", "geography"]),
    Topic("uk_geography", "UK Geography — Regions, Rivers, National Parks, and Industrial Places",
          "Geography", [1, 2], [1, 2, 3, 4, 5, 6], 1, 3,
          ["geography_local_ks1"],
          ["UK", "Britain", "regions", "rivers", "national parks",
           "industrial heritage", "place knowledge", "geography"]),
    Topic("place_studies", "Place Studies — Comparing a UK Locality with the Wider World",
          "Geography", [2], [2, 3, 4, 5, 6], 1, 4,
          ["continents_oceans", "human_geography_ks2"],
          ["place study", "locality", "comparison", "Europe", "global",
           "quality of life", "geography"]),
    Topic("ocean_currents_tides", "Ocean Currents, Tides, and the Deep Ocean",
          "Geography", [2], [5, 6, 7, 8], 2, 4,
          ["continents_oceans", "weather_climate"],
          ["ocean currents", "tides", "thermohaline", "Gulf Stream",
           "climate", "marine ecosystems", "physical geography"]),
    Topic("coastal_geography", "Coastal Geography — Erosion, Deposition, and Coastal Management",
          "Geography", [2], [4, 5, 6, 7], 2, 4,
          ["rivers_mountains", "map_skills_ks2"],
          ["coastal erosion", "deposition", "cliff", "bay", "headland",
           "coastal management", "physical geography", "Jurassic Coast"]),
    Topic("urbanisation", "Urbanisation — Growth of Cities, Megacities, and Urban Change",
          "Geography", [2, 3], [5, 6, 7, 8], 2, 4,
          ["human_geography_ks2"],
          ["urbanisation", "megacities", "urban growth", "slums",
           "human geography", "development", "population"]),
    Topic("migration", "Migration — Causes, Patterns, and Impacts",
          "Geography", [3], [7, 8, 9], 3, 5,
          ["human_geography_ks2", "urbanisation"],
          ["migration", "refugees", "economic migrants", "push pull factors",
           "human geography", "global", "ethics"]),
    Topic("development_inequality_geo", "Development and Global Inequality — HDI and the North-South Divide",
          "Geography", [3], [7, 8, 9], 3, 5,
          ["human_geography_ks2", "globalisation_ks3"],
          ["development", "HDI", "inequality", "north-south", "GDP",
           "human geography", "global", "data literacy"]),
    Topic("resource_distribution", "Resource Distribution — Water, Energy, and Food Security",
          "Geography", [3], [7, 8, 9], 4, 5,
          ["water_cycle_depth", "biomes_habitats", "globalisation_ks3"],
          ["resources", "water security", "food security", "energy",
           "human geography", "sustainability", "geopolitics"]),
    Topic("deforestation_rewilding", "Deforestation, Rewilding, and Biodiversity Loss",
          "Geography", [2], [4, 5, 6, 7, 8], 2, 5,
          ["biomes_habitats", "human_geography_ks2"],
          ["deforestation", "rainforest", "rewilding", "biodiversity",
           "Amazon", "Borneo", "environment", "sustainability", "geography"]),
    Topic("plastic_ocean_pollution", "Plastic Pollution and Ocean Health",
          "Geography", [2], [3, 4, 5, 6, 7], 1, 4,
          ["continents_oceans", "biomes_habitats"],
          ["plastic pollution", "ocean", "microplastics", "food webs",
           "environment", "sustainability", "citizenship", "geography"]),
    Topic("soil_types_desertification", "Soil Types, Fertility, and Desertification",
          "Geography", [2], [4, 5, 6, 7], 2, 4,
          ["biomes_habitats", "rocks_soils"],
          ["soil", "desertification", "land degradation", "farming",
           "food security", "physical geography", "environment"]),
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

    # --- Computing gaps from audit ---
    Topic("history_of_computing", "The History of Computing — From Lovelace to the Internet",
          "Computing", [2, 3], [5, 6, 7, 8, 9], 2, 4, [],
          ["history", "Ada Lovelace", "Alan Turing", "transistor", "Moore's law",
           "internet history", "computing", "Enigma"]),
    Topic("how_computers_work", "How Computers Work — CPU, Memory, and the Fetch-Execute Cycle",
          "Computing", [3], [7, 8, 9], 3, 5, ["data_representation"],
          ["CPU", "memory", "RAM", "fetch-decode-execute", "von Neumann",
           "hardware", "processor", "computing"]),
    Topic("binary_arithmetic", "Binary Arithmetic — Adding in Binary and Hexadecimal",
          "Computing", [3], [7, 8, 9], 3, 5,
          ["data_representation", "powers_roots"],
          ["binary", "binary arithmetic", "hexadecimal", "two's complement",
           "number bases", "computing"]),
    Topic("algorithms_complexity", "Algorithms and Complexity — Sorting, Searching, and Efficiency",
          "Computing", [2, 3], [6, 7, 8, 9], 3, 5, ["algorithms_ks1"],
          ["algorithms", "sorting", "bubble sort", "merge sort", "binary search",
           "Big O", "complexity", "efficiency", "computing"]),
    Topic("cryptography", "Cryptography — Codes, Ciphers, and the Maths of Secrets",
          "Computing", [2, 3], [5, 6, 7, 8, 9], 2, 5, ["algorithms_ks1"],
          ["cryptography", "Caesar cipher", "substitution", "frequency analysis",
           "public key", "RSA", "Turing", "Enigma", "encryption", "codes"]),
    Topic("compression_encoding", "Compression and Encoding — How Computers Store Less",
          "Computing", [3], [7, 8, 9], 3, 5, ["data_representation"],
          ["compression", "run-length encoding", "Huffman", "lossy", "lossless",
           "JPEG", "MP3", "ZIP", "encoding", "computing"]),
    Topic("artificial_intelligence_basics", "Artificial Intelligence — How Machines Learn",
          "Computing", [3], [7, 8, 9], 3, 5,
          ["data_representation", "algorithms_complexity"],
          ["AI", "machine learning", "training data", "neural networks",
           "bias in AI", "ethics", "generative AI", "classification", "computing"]),
    Topic("data_science_concepts", "Data Science — Patterns, Correlation, and Decisions from Data",
          "Computing", [3], [8, 9], 3, 5,
          ["statistics_ks2", "data_representation"],
          ["data science", "correlation", "causation", "bias in data",
           "visualisation", "Simpson's paradox", "statistics", "computing"]),
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

    # --- Art gaps ---
    Topic("art_colour_theory_ks2", "Colour Theory — The Language of Colour",
          "Art", [2], [3, 4], 1, 4, ["art_drawing_ks1"],
          ["colour", "colour theory", "complementary", "warm", "cool",
           "tonal value", "perception", "art", "design"]),
    Topic("art_appreciation_visual_literacy", "Reading Images — Visual Literacy and Art Appreciation",
          "Art", [2], [4, 5, 6], 2, 5, ["art_drawing_ks1"],
          ["visual literacy", "art appreciation", "analysis", "symbolism",
           "iconography", "critical thinking", "Vermeer", "Turner", "Kahlo"]),
    Topic("art_composition_perspective", "Composition and Perspective — How Artists Organise Space",
          "Art", [2], [4, 5, 6], 2, 4,
          ["art_drawing_ks1", "art_colour_theory_ks2"],
          ["composition", "perspective", "rule of thirds", "foreground",
           "visual language", "Raphael", "Hopper", "art", "design"]),
    Topic("art_history_ancient_renaissance", "Art History I — From Cave Paintings to the Renaissance",
          "Art", [2], [5, 6], 2, 4,
          ["art_appreciation_visual_literacy", "art_ks2"],
          ["art history", "Renaissance", "Leonardo", "Michelangelo",
           "ancient world", "medieval", "cave paintings", "art"]),
    Topic("art_movements_modern", "Art History II — Impressionism to the Modern World",
          "Art", [3], [7, 8], 3, 5,
          ["art_history_ancient_renaissance", "art_appreciation_visual_literacy"],
          ["art history", "Impressionism", "Cubism", "Surrealism", "Modernism",
           "Monet", "Picasso", "Dali", "Warhol", "movements", "art"]),
    Topic("art_world_traditions", "Art Beyond Europe — World Art Traditions",
          "Art", [3], [7, 8], 3, 5,
          ["art_history_ancient_renaissance", "art_appreciation_visual_literacy"],
          ["world art", "Islamic art", "Japanese art", "Benin Bronzes",
           "Aboriginal", "African art", "cultural context", "decolonisation"]),
    Topic("art_design_visual_persuasion", "Design, Advertising, and Visual Persuasion",
          "Art", [3], [7, 8, 9], 3, 5,
          ["art_appreciation_visual_literacy", "art_movements_modern"],
          ["design", "advertising", "propaganda", "typography", "visual communication",
           "media literacy", "posters", "brand", "art"]),
    Topic("art_digital_contemporary", "Art in the Digital Age — Photography, Street Art, and AI",
          "Art", [3], [8, 9], 3, 5,
          ["art_movements_modern", "art_design_visual_persuasion"],
          ["digital art", "photography", "street art", "Banksy", "AI art",
           "contemporary", "authorship", "aesthetics", "what is art"]),

    # --- Music gaps ---
    Topic("music_listening_vocabulary", "How Does Music Make You Feel? Listening and Describing",
          "Music", [1], [1, 2], 1, 3, ["music_rhythm_ks1"],
          ["music", "listening", "vocabulary", "timbre", "dynamics",
           "tempo", "mood", "describing"]),
    Topic("music_theory_melody_harmony", "Music Theory — Melody, Scales, and How Chords Work",
          "Music", [2], [4, 5, 6], 2, 4, ["music_notation_ks2"],
          ["music theory", "scales", "melody", "harmony", "chords",
           "major", "minor", "keys", "intervals"]),
    Topic("music_physics_sound", "The Science of Sound — Why Music Works",
          "Music", [2], [5, 6], 2, 4, ["music_rhythm_ks1", "sound_ks2"],
          ["music", "physics", "acoustics", "frequency", "pitch",
           "timbre", "resonance", "overtones", "Doppler", "science"]),
    Topic("music_history_baroque", "Music Through Time I — Ancient World to the Baroque",
          "Music", [2], [5, 6], 2, 3, ["music_notation_ks2"],
          ["music history", "Baroque", "Bach", "Handel", "Vivaldi",
           "plainchant", "Renaissance polyphony", "timeline"]),
    Topic("music_classical_romantic", "Music Through Time II — Classical and Romantic Periods",
          "Music", [3], [7, 8], 2, 4,
          ["music_history_baroque", "music_theory_melody_harmony"],
          ["music history", "Classical", "Romantic", "Mozart", "Beethoven",
           "Tchaikovsky", "symphony", "opera", "nationalism"]),
    Topic("music_twentieth_century", "Music Through Time III — Jazz, Blues, Rock, and Hip Hop",
          "Music", [3], [8, 9], 3, 5, ["music_classical_romantic"],
          ["music history", "jazz", "blues", "rock", "hip hop",
           "African American", "civil rights", "20th century", "culture"]),
    Topic("music_world_traditions", "Music of the World — Traditions Beyond the Western Canon",
          "Music", [3], [7, 8], 2, 4, ["music_rhythm_ks1"],
          ["world music", "Indian classical", "gamelan", "African drumming",
           "Arabic", "Celtic", "global", "culture", "diversity"]),
    Topic("music_composition_songwriting", "How Songs Are Made — Composition and Songwriting",
          "Music", [3], [7, 8, 9], 3, 6, ["music_theory_melody_harmony"],
          ["composition", "songwriting", "structure", "lyrics", "verse",
           "chorus", "prosody", "creativity", "music"]),
    Topic("music_technology", "Music Technology — From Wax Cylinders to Streaming",
          "Music", [3], [8, 9], 3, 4,
          ["music_twentieth_century", "music_physics_sound"],
          ["music technology", "recording", "production", "sampling",
           "synthesis", "DAW", "streaming", "history", "computing"]),
    Topic("music_society_culture", "Music, Power, and Identity",
          "Music", [3], [8, 9], 4, 5, ["music_twentieth_century"],
          ["music and society", "protest songs", "propaganda", "national anthems",
           "film music", "identity", "censorship", "culture", "politics"]),
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
# How Things Are Made — Manufacturing, Materials, and Industrial Processes
# The journey from raw material to finished object. Connects science,
# history, economics, and the made world. Every topic follows the pattern:
# what is the thing → where does the raw material come from → how is it made
# → what happens to it afterwards. Inspired by "The Way Things Work" (Macaulay)
# and the tradition of industrial curiosity.
# ---------------------------------------------------------------------------

_HOW_THINGS_ARE_MADE = [

    # --- Food and Farming ---
    Topic("how_bread_is_made", "How Bread Is Made — From Wheat Field to Loaf",
          "How Things Are Made", [1, 2], [2, 3, 4, 5], 2, 4,
          ["seeds_germination"],
          ["bread", "wheat", "farming", "factory", "food", "yeast", "chemistry",
           "how things work"]),
    Topic("how_chocolate_is_made", "How Chocolate Is Made — Cacao to Bar",
          "How Things Are Made", [2], [3, 4, 5, 6], 2, 4,
          [],
          ["chocolate", "cacao", "trade", "africa", "food", "factory", "history",
           "how things work"]),
    Topic("how_milk_dairy_made", "How Dairy Works — From Cow to Cheese, Butter, and Yoghurt",
          "How Things Are Made", [1, 2], [2, 3, 4, 5], 1, 3,
          [],
          ["dairy", "milk", "cheese", "farming", "food", "biology", "how things work"]),
    Topic("how_sugar_is_made", "How Sugar Is Made — Cane, Beet, and Refining",
          "How Things Are Made", [2], [4, 5, 6], 3, 4,
          ["transatlantic_slave_trade"],
          ["sugar", "cane", "refining", "trade", "history", "empire", "food",
           "how things work"]),
    Topic("how_beer_wine_made", "How Fermented Drinks Are Made — Brewing and Fermentation",
          "How Things Are Made", [3], [7, 8, 9], 3, 4,
          ["fermentation_preservation"],
          ["brewing", "fermentation", "chemistry", "biology", "history", "food",
           "how things work"]),

    # --- Materials and Textiles ---
    Topic("how_cotton_is_made", "How Cotton Becomes Cloth — Field to Fabric",
          "How Things Are Made", [2], [4, 5, 6], 2, 4,
          ["transatlantic_slave_trade"],
          ["cotton", "textiles", "farming", "weaving", "industrial revolution",
           "trade", "history", "how things work"]),
    Topic("how_wool_is_made", "How Wool Is Made — Sheep to Jumper",
          "How Things Are Made", [1, 2], [3, 4, 5], 1, 3,
          [],
          ["wool", "sheep", "knitting", "weaving", "textiles", "farming",
           "how things work"]),
    Topic("how_paper_is_made", "How Paper Is Made — Pulp, Pressing, and Drying",
          "How Things Are Made", [1, 2], [3, 4, 5], 2, 3,
          ["plants_ks2"],
          ["paper", "wood", "pulp", "trees", "recycling", "factory",
           "how things work"]),
    Topic("how_glass_is_made", "How Glass Is Made — Sand, Heat, and Shaping",
          "How Things Are Made", [2], [4, 5, 6], 2, 4,
          ["properties_materials_ks2"],
          ["glass", "sand", "heat", "manufacturing", "materials", "chemistry",
           "how things work"]),
    Topic("how_plastic_is_made", "How Plastic Is Made — Oil, Polymers, and the Problem of Waste",
          "How Things Are Made", [2], [5, 6, 7], 3, 5,
          ["properties_materials_ks2"],
          ["plastic", "oil", "polymers", "chemistry", "environment", "recycling",
           "pollution", "how things work"]),
    Topic("how_concrete_steel_made", "How Concrete and Steel Are Made — Building the Modern World",
          "How Things Are Made", [2, 3], [6, 7, 8], 3, 4,
          ["particle_model"],
          ["concrete", "steel", "iron", "construction", "engineering", "materials",
           "industrial revolution", "how things work"]),

    # --- Machines and Technology ---
    Topic("how_engines_work", "How Engines Work — Steam, Internal Combustion, and Jets",
          "How Things Are Made", [2, 3], [5, 6, 7, 8], 3, 5,
          ["forces_motion_ks3"],
          ["engines", "steam", "combustion", "jets", "physics", "industrial revolution",
           "transport", "how things work"]),
    Topic("how_electricity_generated", "How Electricity Is Generated — Power Stations and the Grid",
          "How Things Are Made", [2, 3], [5, 6, 7, 8], 3, 5,
          ["electricity_ks2"],
          ["electricity", "power stations", "coal", "wind", "solar", "nuclear",
           "energy", "environment", "how things work"]),
    Topic("how_computers_made", "How Computers Are Made — Silicon, Chips, and Factories",
          "How Things Are Made", [3], [7, 8, 9], 4, 5,
          ["data_representation"],
          ["computers", "silicon", "chips", "semiconductors", "manufacturing",
           "mining", "environment", "how things work"]),
    Topic("how_phones_made", "How Smartphones Are Made — Rare Metals and Global Supply Chains",
          "How Things Are Made", [3], [8, 9], 4, 5,
          ["how_computers_made"],
          ["smartphones", "rare earth", "mining", "supply chain", "globalisation",
           "environment", "trade", "how things work"]),
    Topic("how_cars_made", "How Cars Are Made — Design, Assembly, and the Factory Line",
          "How Things Are Made", [2, 3], [6, 7, 8], 3, 4,
          ["how_engines_work"],
          ["cars", "factory", "assembly", "design", "steel", "engineering",
           "industrial revolution", "how things work"]),
    Topic("how_medicine_made", "How Medicine Is Made — From Plant to Pill",
          "How Things Are Made", [2, 3], [6, 7, 8, 9], 4, 5,
          ["chemical_reactions"],
          ["medicine", "drugs", "chemistry", "biology", "pharmaceutical",
           "plants", "testing", "how things work"]),

    # --- Building and Infrastructure ---
    Topic("how_buildings_made", "How Buildings Are Made — Foundations to Roof",
          "How Things Are Made", [2], [4, 5, 6], 2, 4,
          ["how_concrete_steel_made"],
          ["buildings", "construction", "architecture", "engineering", "design",
           "materials", "how things work"]),
    Topic("how_bridges_made", "How Bridges Are Built — Forces, Materials, and Span",
          "How Things Are Made", [2, 3], [5, 6, 7], 3, 5,
          ["forces_magnets"],
          ["bridges", "engineering", "forces", "design", "materials", "maths",
           "how things work"]),
    Topic("how_roads_railways_made", "How Roads and Railways Are Built",
          "How Things Are Made", [2, 3], [6, 7, 8], 3, 4,
          ["romans_britain"],
          ["roads", "railways", "engineering", "industrial revolution", "history",
           "transport", "how things work"]),
    Topic("how_water_reaches_home", "How Water Reaches Your Tap — Reservoirs to Pipes",
          "How Things Are Made", [2], [4, 5, 6], 2, 4,
          ["rivers_mountains"],
          ["water", "pipes", "reservoirs", "filtration", "engineering",
           "environment", "how things work"]),

    # --- Energy and the Environment ---
    Topic("how_wind_turbines_work", "How Wind Turbines Work — Catching Wind and Making Power",
          "How Things Are Made", [2], [5, 6, 7], 2, 4,
          ["electricity_ks2", "forces_magnets"],
          ["wind", "turbines", "renewable energy", "electricity", "environment",
           "engineering", "how things work"]),
    Topic("how_solar_panels_work", "How Solar Panels Work — Light into Electricity",
          "How Things Are Made", [2, 3], [6, 7, 8], 3, 5,
          ["electricity_ks2", "waves_ks3"],
          ["solar", "photovoltaic", "energy", "electricity", "environment",
           "physics", "how things work"]),
    Topic("how_recycling_works", "How Recycling Works — Sorting, Melting, and Making Again",
          "How Things Are Made", [2], [4, 5, 6], 2, 4,
          ["how_plastic_is_made"],
          ["recycling", "environment", "materials", "plastic", "paper", "glass",
           "sustainability", "how things work"]),
    Topic("how_internet_works_deep", "How the Internet Actually Works — Cables, Servers, and Data",
          "How Things Are Made", [3], [7, 8, 9], 3, 5,
          ["networks_internet_ks2"],
          ["internet", "cables", "servers", "data", "computing", "infrastructure",
           "how things work"]),

    # --- Food Systems and Global Chains ---
    Topic("where_food_comes_from", "Where Our Food Comes From — Tracing a Meal Around the World",
          "How Things Are Made", [2], [4, 5, 6], 3, 5,
          [],
          ["food", "farming", "globalisation", "trade", "environment",
           "geography", "supply chain", "how things work"]),
    Topic("how_supermarket_works", "How a Supermarket Works — Supply Chains and Cold Storage",
          "How Things Are Made", [2, 3], [6, 7, 8], 3, 4,
          ["where_food_comes_from"],
          ["supermarket", "supply chain", "logistics", "trade", "food",
           "business", "how things work"]),

    # --- Build It Yourself — Understanding by Making ---
    # These topics go beyond "how it works" to "now build one".
    # Each pairs the theory with an achievable hands-on project.
    Topic("build_a_radio", "Build a Crystal Radio — How Radio Waves Become Sound",
          "How Things Are Made", [3], [7, 8, 9], 3, 5,
          ["waves_ks3", "electronics_components"],
          ["radio", "crystal radio", "electronics", "waves", "physics", "making",
           "hands-on", "build it", "how things work"]),
    Topic("build_an_electric_motor", "Build an Electric Motor — Magnets, Coils, and Rotation",
          "How Things Are Made", [2, 3], [6, 7, 8], 3, 5,
          ["electricity_ks2", "forces_magnets"],
          ["motor", "electromagnetism", "coil", "magnet", "physics", "making",
           "hands-on", "build it", "how things work", "engineering"]),
    Topic("build_a_generator", "Build a Generator — Turning Motion into Electricity",
          "How Things Are Made", [3], [7, 8, 9], 4, 5,
          ["build_an_electric_motor", "how_electricity_generated"],
          ["generator", "electromagnetism", "energy", "physics", "making",
           "hands-on", "build it", "how things work", "engineering"]),
    Topic("build_a_battery", "Build a Battery — How Chemical Energy Becomes Electricity",
          "How Things Are Made", [2, 3], [6, 7, 8], 3, 5,
          ["chemical_reactions", "electricity_ks2"],
          ["battery", "electrochemistry", "zinc", "copper", "lemon battery",
           "chemistry", "making", "hands-on", "build it", "how things work"]),
    Topic("build_a_speaker", "Build a Speaker — How Electricity Becomes Sound",
          "How Things Are Made", [3], [7, 8, 9], 3, 5,
          ["sound_ks2", "build_an_electric_motor"],
          ["speaker", "electromagnet", "sound", "vibration", "physics", "making",
           "hands-on", "build it", "how things work"]),
    Topic("build_a_periscope", "Build a Periscope — How Mirrors Bend Light",
          "How Things Are Made", [2], [5, 6, 7], 2, 4,
          ["light_shadows"],
          ["periscope", "mirrors", "light", "reflection", "optics", "making",
           "hands-on", "build it", "how things work", "physics"]),
    Topic("build_a_water_filter", "Build a Water Filter — How Filtration and Purification Work",
          "How Things Are Made", [2], [5, 6, 7], 2, 4,
          ["how_water_reaches_home"],
          ["water filter", "filtration", "purification", "sand", "charcoal",
           "science", "making", "hands-on", "build it", "how things work"]),
    Topic("build_a_trebuchet", "Build a Trebuchet — Medieval Siege Engines and Physics",
          "How Things Are Made", [2, 3], [5, 6, 7, 8], 3, 5,
          ["forces_magnets", "norman_conquest"],
          ["trebuchet", "catapult", "medieval", "forces", "physics", "making",
           "hands-on", "build it", "engineering", "history"]),
    Topic("nuclear_reactor_how_it_works", "How a Nuclear Reactor Works — Fission, Fuel, and Safety",
          "How Things Are Made", [3], [8, 9], 4, 5,
          ["particle_model", "how_electricity_generated"],
          ["nuclear", "reactor", "fission", "uranium", "energy", "physics",
           "safety", "environment", "how things work"]),
    # Note: no "build a nuclear reactor" project for obvious reasons —
    # but the physics and history (Manhattan Project, Chernobyl, climate debate)
    # is some of the most interesting and morally complex material in the curriculum.
    Topic("nuclear_history_debate", "Nuclear Power — History, Accidents, and the Climate Debate",
          "How Things Are Made", [3], [8, 9], 4, 6,
          ["nuclear_reactor_how_it_works", "climate_change_ks3"],
          ["nuclear", "chernobyl", "fukushima", "climate", "energy", "debate",
           "evaluate", "morality", "history", "how things work"]),
]


# ---------------------------------------------------------------------------
# Materials — From Earth to Object to Waste
# Each topic follows: what is this material → where does it come from →
# how is it extracted/processed → what is it used for → what happens at end of life.
# Grouped by material family. Connects science, geography, history, and environment.
# ---------------------------------------------------------------------------

_MATERIALS = [

    # --- Metals ---
    Topic("iron_and_steel", "Iron and Steel — From Ore to the Modern World",
          "Materials", [2, 3], [5, 6, 7, 8], 3, 5,
          ["particle_model"],
          ["iron", "steel", "smelting", "ore", "industrial revolution", "materials",
           "mining", "engineering", "how things work"]),
    Topic("aluminium", "Aluminium — The Metal That Comes From Clay",
          "Materials", [2, 3], [6, 7, 8], 3, 5,
          ["particle_model", "how_electricity_generated"],
          ["aluminium", "bauxite", "electrolysis", "smelting", "recycling",
           "energy", "materials", "how things work"]),
    Topic("copper", "Copper — The First Metal and How We Still Use It",
          "Materials", [2, 3], [5, 6, 7], 3, 4,
          ["particle_model"],
          ["copper", "mining", "electricity", "wiring", "bronze age", "materials",
           "history", "how things work"]),
    Topic("gold_silver", "Gold and Silver — Why Rare Metals Matter",
          "Materials", [2, 3], [6, 7, 8], 3, 4,
          ["particle_model"],
          ["gold", "silver", "mining", "trade", "jewellery", "history",
           "empire", "materials", "how things work"]),
    Topic("rare_earth_metals", "Rare Earth Metals — Inside Every Modern Device",
          "Materials", [3], [8, 9], 4, 5,
          ["how_phones_made"],
          ["rare earth", "lithium", "cobalt", "mining", "environment",
           "electronics", "trade", "globalisation", "how things work"]),
    Topic("alloys", "Alloys — Why We Mix Metals",
          "Materials", [3], [7, 8, 9], 3, 5,
          ["iron_and_steel", "copper"],
          ["alloys", "bronze", "brass", "stainless steel", "materials science",
           "chemistry", "engineering", "how things work"]),

    # --- Textiles and Natural Fibres ---
    Topic("wool_production", "Wool — From Sheep to Yarn to Cloth",
          "Materials", [1, 2], [3, 4, 5], 1, 3,
          [],
          ["wool", "sheep", "shearing", "spinning", "weaving", "textiles",
           "farming", "materials", "how things work"]),
    Topic("cotton_production", "Cotton — Field, Gin, Mill, and the World It Made",
          "Materials", [2], [5, 6, 7], 3, 5,
          ["transatlantic_slave_trade"],
          ["cotton", "slavery", "industrial revolution", "textiles", "trade",
           "empire", "materials", "history", "how things work"]),
    Topic("silk_production", "Silk — The Secret of the Silkworm and the Silk Road",
          "Materials", [2, 3], [5, 6, 7], 3, 4,
          [],
          ["silk", "silkworm", "china", "trade", "silk road", "textiles",
           "history", "materials", "how things work"]),
    Topic("linen_flax", "Linen — From Flax Plant to Fabric",
          "Materials", [2], [5, 6], 2, 3,
          ["plants_ks2"],
          ["linen", "flax", "textiles", "plant fibres", "materials",
           "farming", "how things work"]),
    Topic("synthetic_fibres", "Synthetic Fibres — Nylon, Polyester, and Oil-Based Fabric",
          "Materials", [2, 3], [6, 7, 8], 3, 5,
          ["how_plastic_is_made", "cotton_production"],
          ["nylon", "polyester", "synthetic", "plastic", "textiles", "environment",
           "materials", "how things work"]),
    Topic("leather_production", "Leather — From Animal Hide to Shoe and Belt",
          "Materials", [2, 3], [5, 6, 7], 2, 4,
          [],
          ["leather", "tanning", "hide", "animals", "ethics", "materials",
           "history", "how things work"]),
    Topic("rubber_production", "Rubber — Natural and Synthetic, From Tree to Tyre",
          "Materials", [2, 3], [6, 7, 8], 3, 4,
          ["how_plastic_is_made"],
          ["rubber", "latex", "vulcanisation", "tyres", "south america",
           "empire", "materials", "history", "how things work"]),

    # --- Stone, Clay, and Ceramics ---
    Topic("stone_materials", "Stone — Granite, Limestone, Marble, and How We Shape It",
          "Materials", [2], [4, 5, 6], 2, 4,
          ["rocks_soils"],
          ["stone", "granite", "limestone", "marble", "quarrying", "building",
           "history", "materials", "how things work"]),
    Topic("clay_ceramics", "Clay and Ceramics — From Mud to Pottery to Porcelain",
          "Materials", [2], [4, 5, 6], 2, 4,
          ["rocks_soils"],
          ["clay", "pottery", "ceramics", "kiln", "china", "history",
           "materials", "art", "how things work"]),
    Topic("glass_production", "Glass — Sand, Heat, and the Art of Glassblowing",
          "Materials", [2], [5, 6, 7], 2, 4,
          ["properties_materials_ks2"],
          ["glass", "sand", "silica", "glassblowing", "windows", "optics",
           "materials", "history", "how things work"]),
    Topic("cement_concrete", "Cement and Concrete — The Material That Built Civilisation",
          "Materials", [2, 3], [6, 7, 8], 3, 4,
          ["chemical_reactions"],
          ["cement", "concrete", "limestone", "romans", "construction",
           "materials", "engineering", "how things work"]),

    # --- Wood and Plant Materials ---
    Topic("timber_production", "Timber — From Forest to Plank to Building",
          "Materials", [2], [4, 5, 6], 2, 3,
          ["plants_ks2"],
          ["timber", "wood", "forestry", "sawmill", "construction", "furniture",
           "materials", "environment", "how things work"]),
    Topic("paper_production", "Paper — Pulp, Pressing, and the Story of Writing",
          "Materials", [2], [4, 5, 6], 2, 3,
          ["timber_production"],
          ["paper", "pulp", "wood", "recycling", "printing", "history",
           "materials", "how things work"]),
    Topic("bamboo_materials", "Bamboo — The World's Fastest-Growing Material",
          "Materials", [2], [5, 6, 7], 2, 4,
          ["plants_ks2"],
          ["bamboo", "sustainable", "construction", "textiles", "asia",
           "materials", "environment", "how things work"]),
    Topic("cork_natural_materials", "Cork, Hemp, and Other Natural Materials",
          "Materials", [2, 3], [6, 7, 8], 3, 4,
          ["plants_ks2"],
          ["cork", "hemp", "natural materials", "sustainable", "portugal",
           "materials", "environment", "how things work"]),

    # --- Plastics and Modern Materials ---
    Topic("plastics_types", "Types of Plastic — PET, HDPE, PVC, and What They're For",
          "Materials", [2, 3], [6, 7, 8], 3, 4,
          ["how_plastic_is_made"],
          ["plastic", "PET", "polymer", "recycling", "materials science",
           "environment", "chemistry", "how things work"]),
    Topic("composites", "Composite Materials — Carbon Fibre, Fibreglass, and Plywood",
          "Materials", [3], [7, 8, 9], 3, 5,
          ["alloys", "plastics_types"],
          ["composite", "carbon fibre", "fibreglass", "aerospace", "engineering",
           "materials science", "how things work"]),
    Topic("smart_materials", "Smart Materials — Shape Memory, Self-Healing, and Piezoelectrics",
          "Materials", [3], [8, 9], 4, 5,
          ["composites"],
          ["smart materials", "shape memory alloy", "piezoelectric", "future",
           "materials science", "engineering", "how things work"]),

    # --- Fuels and Energy Materials ---
    Topic("coal_fossil_fuels", "Coal — How It Formed, How We Burned It, and What It Cost",
          "Materials", [2, 3], [6, 7, 8], 3, 5,
          ["cosmic_time_scale", "industrial_revolution"],
          ["coal", "fossil fuels", "industrial revolution", "environment",
           "climate change", "energy", "materials", "how things work"]),
    Topic("oil_petroleum", "Oil and Petroleum — Fossil Fuel to Fuel, Plastic, and Medicine",
          "Materials", [2, 3], [7, 8, 9], 3, 5,
          ["coal_fossil_fuels"],
          ["oil", "petroleum", "refining", "plastic", "petrol", "environment",
           "trade", "geopolitics", "materials", "how things work"]),
    Topic("lithium_batteries", "Lithium and Batteries — How We Store Energy",
          "Materials", [3], [8, 9], 3, 5,
          ["rare_earth_metals", "build_a_battery"],
          ["lithium", "battery", "energy storage", "electric vehicles", "mining",
           "environment", "materials", "how things work"]),

    # --- Materials Science and Design ---
    Topic("materials_properties", "Materials Properties — Hardness, Conductivity, and Strength",
          "Materials", [2, 3], [6, 7, 8], 3, 4,
          ["properties_materials_ks2"],
          ["materials properties", "hardness", "conductivity", "strength",
           "materials science", "engineering", "design", "how things work"]),
    Topic("materials_and_design", "Choosing Materials — Why We Use What We Use",
          "Materials", [3], [7, 8, 9], 4, 5,
          ["materials_properties"],
          ["materials", "design", "engineering", "sustainability", "choice",
           "environment", "how things work"]),
    Topic("materials_recycling_lifecycle", "The Life of a Material — Extraction to Landfill",
          "Materials", [3], [7, 8, 9], 4, 6,
          ["materials_and_design", "how_recycling_works"],
          ["recycling", "lifecycle", "sustainability", "environment",
           "materials", "ethics", "how things work"]),
]


# ---------------------------------------------------------------------------
# Connections — James Burke style unexpected chains between ideas
# How one discovery leads to another across centuries and disciplines.
# These are cross-curricular topics that exist to show children that
# knowledge is not siloed — everything connects to everything else.
# Each topic traces one surprising chain: A → B → C → D → modern world.
# ---------------------------------------------------------------------------

_CONNECTIONS = [
    Topic("connection_stirrup_feudalism", "The Stirrup and Feudalism — How a Horse Accessory Made Medieval Europe",
          "Connections", [2, 3], [6, 7, 8], 4, 5,
          ["norman_conquest"],
          ["stirrup", "medieval", "feudalism", "cavalry", "connections", "history",
           "james burke", "unexpected"]),
    Topic("connection_plough_university", "The Heavy Plough to the University — How Farming Made Scholars",
          "Connections", [2, 3], [6, 7, 8], 4, 5,
          ["agricultural_revolution_story"],
          ["plough", "medieval", "university", "surplus", "connections", "history",
           "james burke", "unexpected"]),
    Topic("connection_spice_trade_chemistry", "Spice Trade to Modern Chemistry — How Preserving Food Made Science",
          "Connections", [2, 3], [6, 7, 8], 4, 5,
          ["age_of_exploration", "chemical_reactions"],
          ["spice trade", "chemistry", "distillation", "connections", "history",
           "james burke", "unexpected", "trade"]),
    Topic("connection_printing_revolution", "Gutenberg's Press and the Scientific Revolution — How Cheap Books Changed Everything",
          "Connections", [2, 3], [6, 7, 8], 4, 5,
          ["how_paper_is_made", "henry_viii_reformation"],
          ["printing press", "gutenberg", "reformation", "scientific revolution",
           "connections", "history", "james burke", "unexpected"]),
    Topic("connection_clock_navigation_capitalism", "The Clock, Navigation, and Modern Capitalism",
          "Connections", [3], [7, 8, 9], 4, 5,
          ["age_of_exploration", "industrial_revolution"],
          ["clock", "navigation", "longitude", "capitalism", "connections",
           "history", "james burke", "unexpected", "trade"]),
    Topic("connection_steam_computer", "Steam Engine to Computer — How Controlling Machines Led to Thinking Machines",
          "Connections", [3], [7, 8, 9], 4, 5,
          ["how_engines_work", "data_representation"],
          ["steam engine", "babbage", "lovelace", "computer", "connections",
           "history", "james burke", "unexpected", "industrial revolution"]),
    Topic("connection_dye_medicine", "Purple Dye to Penicillin — How Colour Made Modern Medicine",
          "Connections", [3], [7, 8, 9], 4, 5,
          ["how_medicine_made", "chemical_reactions"],
          ["dye", "chemistry", "penicillin", "medicine", "connections",
           "history", "james burke", "unexpected"]),
    Topic("connection_cannon_calculus", "The Cannon and Calculus — How Warfare Made Mathematics",
          "Connections", [3], [8, 9], 4, 5,
          ["algebra_ks3", "elizabethan_era"],
          ["cannon", "ballistics", "calculus", "newton", "leibniz", "connections",
           "maths", "history", "james burke", "unexpected"]),
    Topic("connection_glass_telescope_microscope", "Glass, Telescopes, and Germs — How Windows Led to Germ Theory",
          "Connections", [2, 3], [6, 7, 8], 4, 5,
          ["glass_production", "light_shadows"],
          ["glass", "telescope", "microscope", "germs", "leeuwenhoek",
           "connections", "science", "history", "james burke", "unexpected"]),
    Topic("connection_sugar_slavery_industry", "Sugar, Slavery, and the Industrial Revolution — The Dark Chain",
          "Connections", [3], [7, 8, 9], 4, 6,
          ["how_sugar_is_made", "transatlantic_slave_trade", "industrial_revolution"],
          ["sugar", "slavery", "industrial revolution", "capitalism", "connections",
           "history", "james burke", "unexpected", "empire"]),
    Topic("connection_nitrogen_war_food", "Nitrogen, Explosives, and the Green Revolution — How Bombs Feed the World",
          "Connections", [3], [8, 9], 4, 5,
          ["chemical_reactions", "ww1_causes_consequences"],
          ["nitrogen", "haber process", "explosives", "fertiliser", "food",
           "connections", "chemistry", "history", "james burke", "unexpected"]),
    Topic("connection_telegraph_internet", "The Telegraph to the Internet — One Wire, Many Messages",
          "Connections", [3], [7, 8, 9], 4, 5,
          ["how_electricity_generated", "how_internet_works_deep"],
          ["telegraph", "morse code", "internet", "cables", "connections",
           "history", "james burke", "unexpected", "computing"]),
]


# ---------------------------------------------------------------------------
# Full curriculum registry
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Social Patterns — Recurring structures in human societies across time.
# The goal: teach children to recognise a pattern when it appears in a new
# context. A child who has studied scapegoating in 1930s Germany should
# recognise the same structure when they see it elsewhere — in history,
# in the news, in their own school. These topics are explicitly taught as
# patterns, not just as historical events.
# ---------------------------------------------------------------------------

_SOCIAL_PATTERNS = [

    # --- Power and Control ---
    Topic("pattern_scapegoating", "Scapegoating — Blaming a Group When Things Go Wrong",
          "Social Patterns", [2, 3], [6, 7, 8, 9], 4, 6,
          ["ww2_global_conflict"],
          ["scapegoating", "prejudice", "nazis", "witch trials", "blame",
           "pattern", "critical thinking", "history", "social"]),
    Topic("pattern_propaganda", "Propaganda — How Governments and Groups Control Information",
          "Social Patterns", [2, 3], [6, 7, 8, 9], 4, 6,
          ["ww1_causes_consequences"],
          ["propaganda", "persuasion", "posters", "media", "control",
           "pattern", "critical thinking", "history", "social"]),
    Topic("pattern_authoritarian_rise", "How Authoritarians Come to Power — The Same Steps, Every Time",
          "Social Patterns", [3], [8, 9], 4, 6,
          ["history_of_democracy_britain", "ww2_global_conflict"],
          ["authoritarianism", "fascism", "dictatorship", "pattern",
           "critical thinking", "history", "democracy", "social"]),
    Topic("pattern_revolution", "Revolution — Why They Happen and What Comes Next",
          "Social Patterns", [3], [8, 9], 4, 6,
          ["french_revolution_napoleon", "english_civil_war"],
          ["revolution", "pattern", "france", "russia", "inequality",
           "change", "history", "social", "critical thinking"]),
    Topic("pattern_empire_collapse", "How Empires Fall — The Recurring Pattern of Overreach",
          "Social Patterns", [3], [8, 9], 4, 5,
          ["decolonisation", "romans_britain"],
          ["empire", "collapse", "overreach", "pattern", "history",
           "rome", "british empire", "social", "critical thinking"]),
    Topic("pattern_moral_panic", "Moral Panics — When Society Decides Something Is a Threat",
          "Social Patterns", [3], [8, 9], 4, 6,
          ["media_literacy_ks3"],
          ["moral panic", "media", "fear", "pattern", "critical thinking",
           "social", "psychology", "witches", "video games"]),
    Topic("pattern_ingroup_outgroup", "Us and Them — How Humans Form Groups and Exclude Others",
          "Social Patterns", [2, 3], [7, 8, 9], 4, 5,
          ["civil_rights_global"],
          ["in-group", "out-group", "tribalism", "pattern", "psychology",
           "prejudice", "social", "critical thinking"]),
    Topic("pattern_protest_reform", "Protest and Reform — How Ordinary People Change Society",
          "Social Patterns", [2, 3], [7, 8, 9], 4, 5,
          ["abolition_movement", "civil_rights_global"],
          ["protest", "reform", "suffrage", "civil rights", "pattern",
           "change", "history", "social", "activism"]),
    Topic("pattern_wealth_inequality", "Wealth and Inequality — Why the Gap Keeps Growing",
          "Social Patterns", [3], [8, 9], 4, 6,
          ["industrial_revolution", "empire_trade_economy"],
          ["inequality", "wealth", "poverty", "pattern", "economics",
           "history", "social", "critical thinking"]),
    Topic("pattern_pandemic_response", "Pandemics and Society — How Outbreaks Change the World",
          "Social Patterns", [2, 3], [7, 8, 9], 4, 5,
          ["black_death", "human_body_ks2"],
          ["pandemic", "disease", "pattern", "black death", "covid",
           "history", "society", "science", "critical thinking"]),

    # --- Economics and Markets ---
    Topic("pattern_boom_bust", "Boom and Bust — Why Economies Keep Crashing",
          "Social Patterns", [3], [8, 9], 4, 5,
          ["industrial_revolution", "entrepreneurship"],
          ["boom", "bust", "crash", "economics", "pattern",
           "1929", "2008", "history", "social", "money"]),
    Topic("pattern_tragedy_commons", "The Tragedy of the Commons — Why We Overuse Shared Resources",
          "Social Patterns", [3], [8, 9], 4, 6,
          ["ecosystems_ks3", "climate_change_ks3"],
          ["tragedy of the commons", "economics", "environment", "pattern",
           "fishing", "climate", "shared resources", "critical thinking"]),
]


# ---------------------------------------------------------------------------
# Critical Thinking — How to Think, Not What to Think
# Explicit teaching of reasoning skills, logical fallacies, evidence
# evaluation, and how to be an informed person in a world designed to
# manipulate. These are the meta-skills that protect everything else.
# ---------------------------------------------------------------------------

_CRITICAL_THINKING = [

    # --- Logic and Reasoning ---
    Topic("argument_structure", "What Makes a Good Argument — Claims, Evidence, and Reasoning",
          "Critical Thinking", [2, 3], [6, 7, 8, 9], 3, 5,
          ["reading_comprehension_ks2"],
          ["argument", "evidence", "reasoning", "critical thinking", "logic",
           "debate", "persuasion"]),
    Topic("logical_fallacies", "Logical Fallacies — The Most Common Tricks Bad Arguments Use",
          "Critical Thinking", [3], [7, 8, 9], 4, 5,
          ["argument_structure"],
          ["logical fallacies", "ad hominem", "straw man", "slippery slope",
           "critical thinking", "logic", "rhetoric", "debate"]),
    Topic("correlation_causation", "Correlation Is Not Causation — Why Numbers Lie",
          "Critical Thinking", [2, 3], [7, 8, 9], 4, 5,
          ["statistics_ks2"],
          ["correlation", "causation", "statistics", "critical thinking",
           "science", "data", "maths", "evidence"]),
    Topic("statistical_thinking", "How to Read Statistics — Averages, Percentages, and Misleading Graphs",
          "Critical Thinking", [2, 3], [6, 7, 8, 9], 3, 5,
          ["statistics_ks2"],
          ["statistics", "averages", "graphs", "misleading", "data",
           "critical thinking", "maths", "media"]),
    Topic("confirmation_bias", "Confirmation Bias — Why We Believe What We Already Think",
          "Critical Thinking", [3], [7, 8, 9], 4, 5,
          ["argument_structure"],
          ["confirmation bias", "bias", "psychology", "critical thinking",
           "belief", "evidence", "social media"]),
    Topic("cognitive_biases", "Cognitive Biases — How Our Brains Trick Us",
          "Critical Thinking", [3], [8, 9], 4, 5,
          ["confirmation_bias"],
          ["cognitive bias", "psychology", "anchoring", "heuristics",
           "decision making", "critical thinking", "behaviour"]),

    # --- Evidence and Information ---
    Topic("primary_secondary_sources", "Primary and Secondary Sources — How We Know What We Know",
          "Critical Thinking", [2], [5, 6, 7], 3, 4,
          ["reading_comprehension_ks2"],
          ["primary source", "secondary source", "evidence", "history",
           "critical thinking", "research", "truth"]),
    Topic("evaluating_sources", "How to Evaluate a Source — Who Made This and Why?",
          "Critical Thinking", [2, 3], [6, 7, 8, 9], 3, 5,
          ["primary_secondary_sources", "media_literacy_ks3"],
          ["sources", "credibility", "bias", "critical thinking", "media",
           "internet", "research", "CRAAP test"]),
    Topic("misinformation_disinformation", "Misinformation — How False Information Spreads and Why",
          "Critical Thinking", [3], [7, 8, 9], 4, 5,
          ["evaluating_sources", "pattern_propaganda"],
          ["misinformation", "fake news", "disinformation", "social media",
           "critical thinking", "media", "internet", "manipulation"]),
    Topic("how_to_fact_check", "How to Fact-Check — Tools and Techniques for Finding the Truth",
          "Critical Thinking", [2, 3], [6, 7, 8, 9], 3, 4,
          ["evaluating_sources"],
          ["fact checking", "snopes", "reverse image search", "critical thinking",
           "media", "internet", "journalism", "truth"]),
    Topic("scientific_method", "The Scientific Method — How We Find Out What's Actually True",
          "Critical Thinking", [2], [5, 6, 7], 3, 5,
          ["argument_structure"],
          ["scientific method", "hypothesis", "experiment", "evidence",
           "critical thinking", "science", "peer review", "falsifiability"]),
    Topic("peer_review_consensus", "Peer Review and Scientific Consensus — Why Science Isn't Just Opinion",
          "Critical Thinking", [3], [8, 9], 4, 5,
          ["scientific_method"],
          ["peer review", "consensus", "climate science", "vaccines",
           "critical thinking", "science", "authority", "evidence"]),

    # --- Media and Information Literacy ---
    Topic("how_news_works", "How News Works — Editors, Owners, Deadlines, and Incentives",
          "Critical Thinking", [3], [7, 8, 9], 4, 5,
          ["journalism_news"],
          ["news", "media", "editors", "bias", "incentives", "critical thinking",
           "journalism", "democracy", "how things work"]),
    Topic("advertising_persuasion", "Advertising — How Companies Change What You Want",
          "Critical Thinking", [2, 3], [6, 7, 8, 9], 3, 5,
          ["media_literacy_ks3"],
          ["advertising", "persuasion", "manipulation", "psychology",
           "critical thinking", "media", "consumption", "marketing"]),
    Topic("social_media_algorithms", "Social Media Algorithms — Why You See What You See",
          "Critical Thinking", [3], [7, 8, 9], 4, 5,
          ["how_internet_works_deep", "misinformation_disinformation"],
          ["algorithms", "filter bubble", "social media", "manipulation",
           "critical thinking", "internet", "wellbeing", "radicalisation"]),
    Topic("echo_chambers", "Echo Chambers and Filter Bubbles — How the Internet Divides Us",
          "Critical Thinking", [3], [8, 9], 4, 6,
          ["social_media_algorithms", "confirmation_bias"],
          ["echo chamber", "filter bubble", "radicalisation", "social media",
           "critical thinking", "democracy", "polarisation"]),

    # --- Ethics and Decision Making ---
    Topic("ethics_dilemmas", "Ethical Dilemmas — How to Think Through Hard Choices",
          "Critical Thinking", [2, 3], [6, 7, 8, 9], 4, 6,
          ["philosophy_for_children"],
          ["ethics", "dilemmas", "trolley problem", "critical thinking",
           "philosophy", "decision making", "values", "morality"]),
    Topic("rights_responsibilities", "Rights and Responsibilities — Where Freedom Ends",
          "Critical Thinking", [2, 3], [6, 7, 8, 9], 4, 5,
          ["history_of_democracy_britain"],
          ["rights", "responsibilities", "freedom", "law", "democracy",
           "critical thinking", "ethics", "citizenship"]),
    Topic("how_to_disagree", "How to Disagree Well — Steel-Manning and Charitable Interpretation",
          "Critical Thinking", [3], [7, 8, 9], 4, 5,
          ["logical_fallacies", "debate_public_speaking"],
          ["disagreement", "steel man", "charity", "debate", "listening",
           "critical thinking", "rhetoric", "respect"]),
    Topic("how_to_change_your_mind", "How to Change Your Mind — Why Updating Beliefs Is a Strength",
          "Critical Thinking", [3], [8, 9], 5, 6,
          ["confirmation_bias", "how_to_disagree"],
          ["belief change", "epistemics", "humility", "critical thinking",
           "growth mindset", "evidence", "rationality"]),
]


# ---------------------------------------------------------------------------
# Social Intelligence — The skills that determine how well a person
# moves through the world with other people. Not "soft skills" — these
# are some of the hardest skills to learn and among the most consequential.
# Explicitly taught rather than assumed to develop naturally.
# Covers: reading people, communication, persuasion, leadership, empathy,
# conflict, negotiation, relationships.
# ---------------------------------------------------------------------------

_SOCIAL_INTELLIGENCE = [

    # --- Self-Awareness ---
    Topic("understanding_emotions", "Understanding Your Emotions — What They Are and What They're For",
          "Social Intelligence", [1, 2], [2, 3, 4, 5, 6], 2, 4,
          ["health_wellbeing_ks1"],
          ["emotions", "feelings", "self-awareness", "psychology",
           "social skills", "wellbeing", "empathy"]),
    Topic("emotional_regulation", "Managing Strong Emotions — What to Do When You're Overwhelmed",
          "Social Intelligence", [1, 2], [3, 4, 5, 6, 7], 2, 4,
          ["understanding_emotions"],
          ["emotional regulation", "anger", "anxiety", "calm", "self-control",
           "social skills", "wellbeing", "psychology"]),
    Topic("self_awareness_strengths", "Knowing Yourself — Strengths, Weaknesses, and How You Come Across",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 4, 5,
          ["understanding_emotions"],
          ["self-awareness", "strengths", "feedback", "identity",
           "social skills", "leadership", "growth"]),
    Topic("growth_mindset", "Growth Mindset — The Belief That You Can Get Better at Things",
          "Social Intelligence", [1, 2], [3, 4, 5, 6, 7], 2, 4,
          [],
          ["growth mindset", "effort", "resilience", "failure", "learning",
           "psychology", "social skills", "wellbeing"]),

    # --- Reading People ---
    Topic("reading_body_language", "Body Language — What People Say Without Words",
          "Social Intelligence", [2], [5, 6, 7, 8], 3, 4,
          ["understanding_emotions"],
          ["body language", "nonverbal", "communication", "reading people",
           "social skills", "empathy", "psychology"]),
    Topic("active_listening", "Active Listening — How to Really Hear What Someone Is Saying",
          "Social Intelligence", [1, 2], [3, 4, 5, 6, 7, 8], 2, 4,
          [],
          ["listening", "communication", "empathy", "social skills",
           "relationships", "understanding", "attention"]),
    Topic("perspective_taking", "Perspective Taking — Seeing the World Through Someone Else's Eyes",
          "Social Intelligence", [1, 2], [3, 4, 5, 6, 7], 3, 5,
          ["active_listening"],
          ["perspective", "empathy", "theory of mind", "social skills",
           "understanding", "relationships", "psychology"]),
    Topic("empathy_compassion", "Empathy and Compassion — The Difference, and Why Both Matter",
          "Social Intelligence", [2, 3], [5, 6, 7, 8, 9], 3, 5,
          ["perspective_taking"],
          ["empathy", "compassion", "kindness", "social skills",
           "relationships", "wellbeing", "ethics", "psychology"]),

    # --- Communication ---
    Topic("clear_communication", "Communicating Clearly — Saying What You Mean and Being Understood",
          "Social Intelligence", [1, 2], [3, 4, 5, 6, 7], 2, 4,
          ["active_listening"],
          ["communication", "clarity", "language", "social skills",
           "speaking", "listening", "relationships"]),
    Topic("asking_good_questions", "Asking Good Questions — The Most Underrated Social Skill",
          "Social Intelligence", [2], [4, 5, 6, 7, 8], 3, 5,
          ["clear_communication"],
          ["questions", "curiosity", "communication", "social skills",
           "interviews", "relationships", "learning"]),
    Topic("giving_receiving_feedback", "Giving and Receiving Feedback — Without Crushing or Being Crushed",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 3, 5,
          ["clear_communication", "emotional_regulation"],
          ["feedback", "criticism", "communication", "social skills",
           "growth", "leadership", "relationships"]),
    Topic("difficult_conversations", "Having Difficult Conversations — How to Talk About Hard Things",
          "Social Intelligence", [3], [7, 8, 9], 4, 5,
          ["emotional_regulation", "clear_communication"],
          ["difficult conversations", "conflict", "communication",
           "social skills", "relationships", "courage", "honesty"]),

    # --- Persuasion and Influence ---
    Topic("rhetoric_persuasion", "Rhetoric — The Art of Speaking Persuasively",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 3, 5,
          ["argument_structure"],
          ["rhetoric", "persuasion", "ethos", "pathos", "logos", "speaking",
           "social skills", "debate", "influence", "aristotle"]),
    Topic("negotiation_basics", "Negotiation — How to Get What You Want Without Losing the Relationship",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 3, 5,
          ["clear_communication", "perspective_taking"],
          ["negotiation", "compromise", "win-win", "conflict", "social skills",
           "relationships", "business", "life skills"]),
    Topic("debate_skills", "Debate — How to Argue a Position Well, Even One You Don't Hold",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 4, 6,
          ["rhetoric_persuasion", "how_to_disagree"],
          ["debate", "argument", "evidence", "social skills", "speaking",
           "critical thinking", "confidence", "logic"]),
    Topic("public_speaking_confidence", "Public Speaking — How to Speak to a Group Without Freezing",
          "Social Intelligence", [2, 3], [5, 6, 7, 8, 9], 3, 4,
          ["clear_communication"],
          ["public speaking", "confidence", "speaking", "social skills",
           "presentations", "performance", "anxiety"]),
    Topic("storytelling_social", "Storytelling — How Stories Change Minds and Move People",
          "Social Intelligence", [2, 3], [5, 6, 7, 8, 9], 3, 5,
          ["creative_writing_ks2", "rhetoric_persuasion"],
          ["storytelling", "narrative", "persuasion", "social skills",
           "communication", "influence", "memory", "culture"]),

    # --- Working With Others ---
    Topic("teamwork_collaboration", "Teamwork — How Groups Work Well Together (and Why They Often Don't)",
          "Social Intelligence", [1, 2], [3, 4, 5, 6, 7], 2, 4,
          [],
          ["teamwork", "collaboration", "groups", "social skills",
           "leadership", "communication", "conflict", "sport"]),
    Topic("managing_conflict", "Managing Conflict — Turning Arguments into Resolutions",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 3, 5,
          ["emotional_regulation", "negotiation_basics"],
          ["conflict", "resolution", "mediation", "social skills",
           "relationships", "communication", "leadership"]),
    Topic("leadership_basics", "Leadership — What It Is, What It Isn't, and How to Do It",
          "Social Intelligence", [2, 3], [7, 8, 9], 4, 5,
          ["self_awareness_strengths", "teamwork_collaboration"],
          ["leadership", "responsibility", "motivation", "social skills",
           "management", "teams", "influence", "service"]),
    Topic("managing_up", "Managing Up — How to Work Well with People Who Have Power Over You",
          "Social Intelligence", [3], [8, 9], 4, 5,
          ["leadership_basics", "clear_communication"],
          ["managing up", "workplace", "authority", "social skills",
           "communication", "relationships", "professional"]),
    Topic("building_trust", "Building Trust — Why It Matters and How You Earn It",
          "Social Intelligence", [2, 3], [7, 8, 9], 3, 5,
          ["empathy_compassion", "giving_receiving_feedback"],
          ["trust", "reliability", "honesty", "social skills",
           "relationships", "leadership", "character"]),
    Topic("reading_rooms_social", "Reading the Room — How to Adapt to Different Social Contexts",
          "Social Intelligence", [3], [8, 9], 4, 5,
          ["reading_body_language", "self_awareness_strengths"],
          ["social awareness", "context", "adapt", "social skills",
           "professional", "relationships", "intelligence"]),

    # --- Relationships ---
    Topic("making_keeping_friends", "Making and Keeping Friends — What Friendship Actually Requires",
          "Social Intelligence", [1, 2], [2, 3, 4, 5, 6], 2, 4,
          ["understanding_emotions"],
          ["friendship", "relationships", "social skills", "kindness",
           "loyalty", "social", "wellbeing"]),
    Topic("handling_rejection", "Handling Rejection — How to Deal with Disappointment and Move On",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 3, 5,
          ["emotional_regulation", "growth_mindset"],
          ["rejection", "resilience", "disappointment", "social skills",
           "wellbeing", "psychology", "relationships"]),
    Topic("peer_pressure", "Peer Pressure — How Groups Change Individual Behaviour",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 3, 5,
          ["pattern_ingroup_outgroup", "emotional_regulation"],
          ["peer pressure", "conformity", "identity", "social skills",
           "psychology", "wellbeing", "social patterns", "resilience"]),
    Topic("healthy_unhealthy_relationships", "Healthy and Unhealthy Relationships — Knowing the Difference",
          "Social Intelligence", [2, 3], [6, 7, 8, 9], 3, 5,
          ["relationships_ks2", "empathy_compassion"],
          ["relationships", "healthy", "red flags", "social skills",
           "wellbeing", "safety", "boundaries", "trust"]),
]


# ---------------------------------------------------------------------------
# Growing Up — The Inner Life
# The emotional and psychological curriculum for children understanding
# themselves and others. Covers the experience of growing up, how the
# mind works, human diversity, and why people are the way they are.
# Not therapy — just the knowledge that makes life less confusing.
# Age-gated carefully: some topics only land when a child is actually
# experiencing them.
# ---------------------------------------------------------------------------

_GROWING_UP = [

    # --- The Emotional Landscape ---
    Topic("emotions_map", "The Emotions Map — Naming Every Feeling You Have",
          "Growing Up", [1, 2], [2, 3, 4, 5], 1, 3,
          [],
          ["emotions", "feelings", "vocabulary", "self-awareness",
           "wellbeing", "growing up", "psychology"]),
    Topic("why_we_feel", "Why We Feel — What Emotions Are Actually For",
          "Growing Up", [2], [5, 6, 7], 3, 4,
          ["emotions_map"],
          ["emotions", "evolution", "psychology", "fear", "anger", "joy",
           "wellbeing", "growing up", "science"]),
    Topic("grief_and_loss", "Grief and Loss — How to Go Through It",
          "Growing Up", [1, 2, 3], [3, 4, 5, 6, 7, 8, 9], 2, 4,
          ["understanding_emotions"],
          ["grief", "loss", "death", "change", "emotions", "wellbeing",
           "growing up", "relationships", "resilience"]),
    Topic("loneliness", "Loneliness — Why It Hurts and What Helps",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 4,
          ["understanding_emotions"],
          ["loneliness", "connection", "wellbeing", "emotions",
           "growing up", "psychology", "relationships"]),
    Topic("jealousy_envy", "Jealousy and Envy — Understanding the Green-Eyed Monster",
          "Growing Up", [2], [5, 6, 7, 8], 3, 4,
          ["emotions_map"],
          ["jealousy", "envy", "emotions", "relationships", "growing up",
           "psychology", "wellbeing", "social"]),
    Topic("shame_guilt", "Shame and Guilt — The Difference and Why It Matters",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 5,
          ["understanding_emotions"],
          ["shame", "guilt", "emotions", "psychology", "wellbeing",
           "growing up", "morality", "self-compassion"]),
    Topic("anxiety_worry", "Anxiety and Worry — What It Is, Why It Happens, and What Helps",
          "Growing Up", [2, 3], [5, 6, 7, 8, 9], 2, 4,
          ["emotional_regulation"],
          ["anxiety", "worry", "mental health", "wellbeing", "emotions",
           "growing up", "psychology", "coping"]),
    Topic("happiness_what_it_is", "What Is Happiness — And Why Chasing It Often Backfires",
          "Growing Up", [3], [7, 8, 9], 4, 5,
          ["why_we_feel"],
          ["happiness", "wellbeing", "psychology", "meaning", "growing up",
           "stoicism", "philosophy", "hedonic treadmill"]),
    Topic("boredom_meaning", "Boredom — Why It Exists and What It's Trying to Tell You",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 4,
          ["emotions_map"],
          ["boredom", "meaning", "purpose", "emotions", "growing up",
           "creativity", "psychology", "attention"]),

    # --- Growing Up and the Body ---
    Topic("puberty_bodies_changing", "Puberty — What Happens and Why",
          "Growing Up", [2, 3], [5, 6, 7, 8], 2, 4,
          ["human_body_ks2"],
          ["puberty", "body", "growing up", "biology", "hormones",
           "changes", "health", "wellbeing"],
          accelerated_ok=False),  # age-gated: only relevant when approaching/in puberty
    Topic("sleep_and_the_brain", "Sleep — Why You Need It and What Happens When You Don't Get It",
          "Growing Up", [2, 3], [5, 6, 7, 8, 9], 2, 4,
          ["human_body_ks2"],
          ["sleep", "brain", "memory", "wellbeing", "health", "growing up",
           "biology", "teenagers"]),
    Topic("food_mood_brain", "Food and Your Brain — How What You Eat Affects How You Feel",
          "Growing Up", [2], [5, 6, 7], 3, 4,
          ["nutrition_food_science"],
          ["food", "mood", "brain", "sugar", "gut", "wellbeing",
           "biology", "growing up", "health"]),
    Topic("exercise_mental_health", "Exercise and the Mind — Why Moving Makes You Feel Better",
          "Growing Up", [2], [5, 6, 7], 2, 4,
          [],
          ["exercise", "mental health", "wellbeing", "biology",
           "endorphins", "growing up", "sport", "health"]),
    Topic("addiction_habits", "Habits and Addiction — How Behaviour Gets Locked In",
          "Growing Up", [3], [7, 8, 9], 4, 5,
          ["emotional_regulation"],
          ["habits", "addiction", "dopamine", "psychology", "wellbeing",
           "growing up", "screens", "substances", "neuroscience"]),

    # --- Identity and Growing Up ---
    Topic("identity_who_am_i", "Identity — Who Am I and How Do I Know?",
          "Growing Up", [3], [7, 8, 9], 4, 6,
          ["self_awareness_strengths"],
          ["identity", "who am i", "growing up", "psychology", "culture",
           "values", "philosophy", "self", "belonging"]),
    Topic("values_what_matters", "Values — Figuring Out What Actually Matters to You",
          "Growing Up", [2, 3], [7, 8, 9], 4, 5,
          ["ethics_dilemmas"],
          ["values", "morality", "identity", "growing up", "philosophy",
           "choices", "meaning", "character"]),
    Topic("gender_identity", "Gender — What It Is, How It Works, and Why It's Complicated",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 5,
          ["puberty_bodies_changing"],
          ["gender", "identity", "biology", "culture", "growing up",
           "equality", "diversity", "wellbeing"]),
    Topic("sexuality_relationships", "Attraction and Relationships — How They Work and Why They're Different for Everyone",
          "Growing Up", [3], [8, 9], 3, 5,
          ["healthy_unhealthy_relationships", "gender_identity"],
          ["attraction", "relationships", "sexuality", "growing up", "love",
           "identity", "diversity", "wellbeing"],
          accelerated_ok=False),
    Topic("family_structures", "Families — All the Different Shapes a Family Can Take",
          "Growing Up", [1, 2], [2, 3, 4, 5, 6], 1, 3,
          [],
          ["family", "diversity", "relationships", "growing up",
           "belonging", "culture", "social", "wellbeing"]),
    Topic("culture_and_identity", "Culture and Where You Come From — How Background Shapes Who You Are",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 5,
          ["identity_who_am_i"],
          ["culture", "identity", "heritage", "diversity", "belonging",
           "growing up", "history", "values"]),

    # --- Understanding Other People ---
    Topic("personality_types", "Personality — Why People Are So Different from Each Other",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 4,
          ["perspective_taking"],
          ["personality", "introvert", "extrovert", "psychology",
           "growing up", "types", "diversity", "relationships"]),
    Topic("neurodiversity_explainer", "Neurodiversity — Different Kinds of Minds",
          "Growing Up", [2], [5, 6, 7, 8], 3, 4,
          ["perspective_taking"],
          ["neurodiversity", "autism", "ADHD", "dyslexia", "minds",
           "diversity", "growing up", "empathy", "inclusion"]),
    Topic("mental_health_basics", "Mental Health — What It Is, Why It Matters, How to Talk About It",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 4,
          ["anxiety_worry", "grief_and_loss"],
          ["mental health", "wellbeing", "stigma", "depression", "anxiety",
           "growing up", "help", "psychology"]),
    Topic("where_beliefs_come_from", "Where Our Beliefs Come From — Family, Culture, and Experience",
          "Growing Up", [3], [8, 9], 4, 5,
          ["culture_and_identity", "confirmation_bias"],
          ["beliefs", "psychology", "culture", "family", "growing up",
           "critical thinking", "identity", "religion"]),
    Topic("power_of_narrative", "The Stories We Tell About Ourselves",
          "Growing Up", [3], [8, 9], 4, 6,
          ["identity_who_am_i", "storytelling_social"],
          ["narrative", "self-story", "identity", "psychology", "growing up",
           "meaning", "change", "resilience"]),

    # --- The Practical Stuff Nobody Teaches ---
    Topic("how_to_ask_for_help", "How to Ask for Help — Why It's Hard and How to Do It",
          "Growing Up", [2, 3], [6, 7, 8, 9], 3, 4,
          ["difficult_conversations"],
          ["help", "vulnerability", "growing up", "wellbeing",
           "social skills", "resilience", "communication"]),
    Topic("failure_and_resilience", "Failing and Getting Back Up — What Resilience Actually Is",
          "Growing Up", [2, 3], [5, 6, 7, 8, 9], 3, 5,
          ["growth_mindset", "emotional_regulation"],
          ["failure", "resilience", "growing up", "wellbeing",
           "psychology", "effort", "setbacks", "character"]),
    Topic("making_decisions", "How to Make Decisions — When You Don't Know What to Do",
          "Growing Up", [2, 3], [7, 8, 9], 4, 5,
          ["values_what_matters", "cognitive_biases"],
          ["decisions", "choice", "growing up", "psychology", "values",
           "uncertainty", "life skills", "thinking"]),
    Topic("future_and_uncertainty", "Living With Uncertainty — Nobody Knows What's Going to Happen",
          "Growing Up", [3], [8, 9], 4, 5,
          ["anxiety_worry", "making_decisions"],
          ["uncertainty", "future", "anxiety", "growing up", "philosophy",
           "wellbeing", "stoicism", "acceptance"]),
]


# ---------------------------------------------------------------------------
# Vocabulary and Language — Words as Power
# Explicit vocabulary teaching beyond the NC word lists. Etymology,
# word roots, the history of English, registers, precision, and the
# pleasure of finding the right word. Vocabulary is the single strongest
# predictor of reading comprehension — and it compounds. Children with
# large vocabularies read more; reading builds vocabulary; the gap grows.
# ---------------------------------------------------------------------------

_VOCABULARY = [

    # --- The Architecture of Words ---
    Topic("vocab_roots_latin_greek", "Word Roots — Latin and Greek Building Blocks",
          "Vocabulary", [2, 3], [5, 6, 7, 8, 9], 3, 5,
          ["spelling_ks2"],
          ["word roots", "latin", "greek", "etymology", "vocabulary",
           "prefixes", "suffixes", "language", "English"]),
    Topic("vocab_prefixes_suffixes", "Prefixes and Suffixes — How Words Are Built",
          "Vocabulary", [2], [4, 5, 6, 7], 2, 4,
          ["spelling_ks2"],
          ["prefixes", "suffixes", "word building", "vocabulary",
           "spelling", "language", "English"]),
    Topic("vocab_etymology", "Etymology — Where Words Come From",
          "Vocabulary", [2, 3], [6, 7, 8, 9], 3, 5,
          ["vocab_roots_latin_greek"],
          ["etymology", "word history", "language", "vocabulary",
           "Latin", "French", "Old English", "interesting words"]),
    Topic("vocab_word_families", "Word Families — How One Root Spawns Many Words",
          "Vocabulary", [2], [5, 6, 7], 3, 4,
          ["vocab_roots_latin_greek"],
          ["word families", "vocabulary", "roots", "spelling",
           "language", "patterns", "English"]),
    Topic("vocab_synonyms_precision", "Synonyms and Precision — Why 'Said' is Never Enough",
          "Vocabulary", [2, 3], [5, 6, 7, 8, 9], 3, 5,
          ["vocabulary_ks2"],
          ["synonyms", "precision", "vocabulary", "writing",
           "word choice", "language", "English", "nuance"]),
    Topic("vocab_connotation_denotation", "Connotation and Denotation — What Words Mean vs What They Suggest",
          "Vocabulary", [3], [7, 8, 9], 4, 5,
          ["vocab_synonyms_precision"],
          ["connotation", "denotation", "vocabulary", "language",
           "meaning", "rhetoric", "literary analysis", "nuance"]),
    Topic("vocab_register_formality", "Register — How We Change Language for Different Audiences",
          "Vocabulary", [2, 3], [6, 7, 8, 9], 3, 5,
          ["grammar_punctuation_ks2"],
          ["register", "formal", "informal", "audience", "vocabulary",
           "language", "communication", "writing"]),

    # --- The History of English ---
    Topic("history_of_english_ks2", "Where English Comes From — Anglo-Saxon, Norman French, and Latin",
          "Vocabulary", [2, 3], [6, 7, 8], 3, 4,
          ["vikings_saxons", "norman_conquest"],
          ["history of English", "Anglo-Saxon", "Norman French", "Latin",
           "language", "vocabulary", "etymology", "history"]),
    Topic("history_of_english_ks3", "How English Conquered the World — and What It Borrowed Back",
          "Vocabulary", [3], [8, 9], 4, 5,
          ["history_of_english_ks2", "british_empire_expansion"],
          ["history of English", "empire", "loan words", "global English",
           "language", "vocabulary", "history", "culture"]),
    Topic("dialects_accents", "Dialects and Accents — Why English Varies Across the World",
          "Vocabulary", [2, 3], [6, 7, 8, 9], 3, 4,
          ["history_of_english_ks2"],
          ["dialects", "accents", "variation", "language", "vocabulary",
           "culture", "identity", "English", "linguistics"]),
    Topic("slang_and_language_change", "Slang and How Language Changes — Why Dictionaries Are Always Behind",
          "Vocabulary", [3], [7, 8, 9], 3, 5,
          ["history_of_english_ks2"],
          ["slang", "language change", "vocabulary", "linguistics",
           "culture", "youth", "English", "dictionaries"]),

    # --- Specific Vocabulary Domains ---
    Topic("vocab_science_latin_greek", "Science Vocabulary — Why Scientists Use Latin and Greek",
          "Vocabulary", [2, 3], [6, 7, 8, 9], 3, 4,
          ["vocab_roots_latin_greek"],
          ["science vocabulary", "Latin", "Greek", "naming", "taxonomy",
           "vocabulary", "biology", "chemistry", "language"]),
    Topic("vocab_emotions_granular", "Granular Emotion Vocabulary — From Happy to Sanguine to Ebullient",
          "Vocabulary", [2, 3], [6, 7, 8, 9], 3, 5,
          ["emotions_map", "vocab_synonyms_precision"],
          ["emotions vocabulary", "feelings", "precision", "vocabulary",
           "wellbeing", "language", "nuance", "self-awareness"]),
    Topic("vocab_describing_people", "Words for People — Character, Personality, and Appearance",
          "Vocabulary", [2], [5, 6, 7], 3, 4,
          ["vocab_synonyms_precision"],
          ["describing people", "character", "vocabulary", "writing",
           "adjectives", "language", "social", "English"]),
    Topic("vocab_argument_discourse", "Vocabulary for Arguments — The Words That Carry Ideas",
          "Vocabulary", [3], [7, 8, 9], 4, 5,
          ["argument_structure", "vocab_connotation_denotation"],
          ["argument vocabulary", "discourse markers", "rhetoric",
           "academic language", "vocabulary", "writing", "debate"]),
    Topic("vocab_power_of_words", "The Power of Words — How Language Shapes Thought",
          "Vocabulary", [3], [8, 9], 5, 6,
          ["vocab_connotation_denotation", "pattern_propaganda"],
          ["power of words", "Sapir-Whorf", "framing", "language",
           "vocabulary", "critical thinking", "philosophy", "thought"]),
]


# ---------------------------------------------------------------------------
# Manipulation and Influence — How Power Shapes What You Believe
# The applied curriculum for understanding institutional deception, influence
# operations, manufactured consent, and the techniques used to make people
# believe things that serve someone else's interests.
# This is not conspiracy theory — it is documented history and technique.
# Sources: declassified documents, court records, academic research.
# Every topic here has an evidence base; it is taught as history and
# critical analysis, not as paranoia.
# ---------------------------------------------------------------------------

_MANIPULATION = [

    # --- Corporate Deception — The Tobacco Playbook ---
    Topic("tobacco_industry_lies", "Big Tobacco — How an Industry Lied for Fifty Years and Got Away With It",
          "Manipulation", [3], [8, 9], 4, 6,
          ["scientific_method", "peer_review_consensus"],
          ["tobacco", "big tobacco", "corporate deception", "manufactured doubt",
           "lobbying", "manipulation", "health", "history", "critical thinking"]),
    Topic("manufactured_doubt", "Manufactured Doubt — How Industries Buy Time by Faking Uncertainty",
          "Manipulation", [3], [8, 9], 4, 6,
          ["tobacco_industry_lies", "peer_review_consensus"],
          ["manufactured doubt", "tobacco", "climate denial", "asbestos",
           "think tanks", "manipulation", "corporate", "science", "critical thinking"]),
    Topic("merchants_of_doubt", "The Same Playbook — From Tobacco to Climate to Opioids",
          "Manipulation", [3], [9], 5, 6,
          ["manufactured_doubt"],
          ["merchants of doubt", "tobacco", "climate", "opioids", "corporate",
           "playbook", "manipulation", "history", "critical thinking"]),
    Topic("food_industry_manipulation", "Big Food — How the Food Industry Shaped What We Eat and Think",
          "Manipulation", [3], [8, 9], 4, 5,
          ["nutrition_food_science", "advertising_persuasion"],
          ["food industry", "sugar", "fat", "lobbying", "nutrition science",
           "manipulation", "health", "corporate", "critical thinking"]),
    Topic("pharmaceutical_marketing", "How Pharmaceutical Companies Market Diseases",
          "Manipulation", [3], [9], 4, 5,
          ["how_medicine_made", "advertising_persuasion"],
          ["pharmaceutical", "marketing", "disease", "opioids", "FDA",
           "manipulation", "health", "corporate", "critical thinking"]),

    # --- Government and State Influence Operations ---
    Topic("propaganda_techniques", "Propaganda Techniques — The Specific Methods, Named",
          "Manipulation", [3], [8, 9], 4, 5,
          ["pattern_propaganda", "rhetorical_devices"],
          ["propaganda", "techniques", "bandwagon", "glittering generality",
           "transfer", "plain folks", "fear appeal", "manipulation",
           "critical thinking", "history"]),
    Topic("psyops_history", "Psychological Operations — How Governments Manipulate Populations",
          "Manipulation", [3], [8, 9], 4, 5,
          ["propaganda_techniques", "ww2_global_conflict"],
          ["psyops", "psychological operations", "CIA", "MKULTRA", "cold war",
           "manipulation", "history", "government", "critical thinking"]),
    Topic("cia_covert_history", "Covert Operations — What Governments Do in Secret (and How We Know)",
          "Manipulation", [3], [9], 4, 6,
          ["cold_war_context", "psyops_history"],
          ["CIA", "covert", "declassified", "Iran", "Chile", "Guatemala",
           "history", "government", "manipulation", "critical thinking"]),
    Topic("censorship_history", "Censorship — What Governments Have Suppressed and Why",
          "Manipulation", [3], [8, 9], 4, 5,
          ["history_of_democracy_britain", "pattern_propaganda"],
          ["censorship", "banned books", "press freedom", "history",
           "government", "manipulation", "democracy", "critical thinking"]),
    Topic("political_spin", "Political Spin — How Politicians Frame Reality",
          "Manipulation", [3], [8, 9], 4, 5,
          ["propaganda_techniques", "how_news_works"],
          ["spin", "framing", "politics", "PR", "language", "manipulation",
           "media", "critical thinking", "democracy"]),

    # --- Media and Attention ---
    Topic("attention_economy", "The Attention Economy — You Are the Product",
          "Manipulation", [3], [7, 8, 9], 4, 5,
          ["social_media_algorithms", "advertising_persuasion"],
          ["attention economy", "social media", "advertising", "product",
           "manipulation", "psychology", "technology", "critical thinking"]),
    Topic("media_ownership", "Who Owns the Media — And Why It Matters",
          "Manipulation", [3], [8, 9], 4, 5,
          ["how_news_works", "pattern_wealth_inequality"],
          ["media ownership", "Murdoch", "newspapers", "bias", "power",
           "manipulation", "democracy", "critical thinking", "press"]),
    Topic("astroturfing_fake_grassroots", "Astroturfing — Fake Grassroots Movements",
          "Manipulation", [3], [8, 9], 4, 5,
          ["misinformation_disinformation", "manufactured_doubt"],
          ["astroturfing", "fake grassroots", "lobbying", "corporate",
           "manipulation", "critical thinking", "social media", "PR"]),
    Topic("dark_patterns_ux", "Dark Patterns — How Apps and Websites Are Designed to Trick You",
          "Manipulation", [3], [7, 8, 9], 3, 5,
          ["attention_economy", "advertising_persuasion"],
          ["dark patterns", "UX", "design", "apps", "manipulation",
           "technology", "critical thinking", "subscriptions", "tricks"]),

    # --- Psychological Techniques ---
    Topic("nudge_theory", "Nudge Theory — How Environments Shape Choices Without You Noticing",
          "Manipulation", [3], [8, 9], 4, 5,
          ["cognitive_biases", "advertising_persuasion"],
          ["nudge", "choice architecture", "Thaler", "Sunstein", "defaults",
           "psychology", "manipulation", "policy", "critical thinking"]),
    Topic("social_proof_manipulation", "Social Proof and Authority — How We're Manipulated by 'Everyone Else'",
          "Manipulation", [3], [8, 9], 4, 5,
          ["cognitive_biases", "pattern_ingroup_outgroup"],
          ["social proof", "authority", "Cialdini", "persuasion",
           "manipulation", "psychology", "conformity", "critical thinking"]),
    Topic("cult_techniques", "Cult Techniques — How Groups Capture and Control Members",
          "Manipulation", [3], [9], 4, 6,
          ["pattern_authoritarian_rise", "social_proof_manipulation"],
          ["cults", "thought reform", "love bombing", "isolation",
           "manipulation", "psychology", "critical thinking", "coercion"]),
    Topic("radicalization_pipeline", "Radicalisation — How People Are Drawn to Extreme Ideas",
          "Manipulation", [3], [9], 4, 6,
          ["echo_chambers", "cult_techniques"],
          ["radicalisation", "extremism", "pipeline", "online", "manipulation",
           "critical thinking", "psychology", "social media", "prevention"]),

    # --- Being Inoculated ---
    Topic("inoculation_theory", "Inoculation — How Forewarning Protects Against Manipulation",
          "Manipulation", [3], [8, 9], 4, 5,
          ["misinformation_disinformation", "propaganda_techniques"],
          ["inoculation", "prebunking", "manipulation", "critical thinking",
           "psychology", "research", "media literacy", "protection"]),
    Topic("recognising_manipulation", "How to Spot When You're Being Manipulated",
          "Manipulation", [3], [7, 8, 9], 4, 5,
          ["propaganda_techniques", "advertising_persuasion"],
          ["manipulation", "recognition", "critical thinking", "media literacy",
           "protection", "psychology", "awareness", "independence"]),
    Topic("information_hygiene", "Information Hygiene — How to Build a Healthy Information Diet",
          "Manipulation", [3], [8, 9], 4, 5,
          ["recognising_manipulation", "how_to_fact_check"],
          ["information hygiene", "news", "sources", "diet", "manipulation",
           "critical thinking", "media literacy", "independence"]),
]


# ---------------------------------------------------------------------------
# Political Systems — How Power Is Organised
# Covers the full range of political systems humans have tried, how specific
# institutions actually work (not just in theory), and the CGP Grey track:
# concrete, specific "how does this actually work" deep-dives on real
# institutions. Named after CGP Grey's YouTube approach — start with a
# curious question ("how do you become the Pope?"), follow the mechanics,
# end with something surprising about how the world is organised.
# ---------------------------------------------------------------------------

_POLITICAL_SYSTEMS = [

    # --- Political Systems Overview ---
    Topic("what_is_government", "What Is Government — Why Humans Organise Power at All",
          "Political Systems", [2], [5, 6, 7], 2, 4,
          [],
          ["government", "power", "political systems", "civics",
           "history", "organisation", "society"]),
    Topic("democracy_types", "Types of Democracy — Direct, Representative, and Everything Between",
          "Political Systems", [2, 3], [6, 7, 8, 9], 3, 5,
          ["history_of_democracy_britain", "ancient_greece"],
          ["democracy", "representative", "direct", "political systems",
           "voting", "parliament", "civics"]),
    Topic("monarchy_types", "Monarchy — Absolute, Constitutional, and Ceremonial",
          "Political Systems", [2, 3], [6, 7, 8, 9], 3, 4,
          ["norman_conquest", "glorious_revolution"],
          ["monarchy", "absolute", "constitutional", "ceremonial", "king",
           "queen", "political systems", "history", "Britain"]),
    Topic("republic_vs_monarchy", "Republics vs Monarchies — What's the Actual Difference",
          "Political Systems", [3], [7, 8, 9], 3, 5,
          ["democracy_types", "monarchy_types"],
          ["republic", "monarchy", "president", "head of state",
           "political systems", "civics", "comparison"]),
    Topic("authoritarianism_types", "Authoritarianism — Dictatorships, Oligarchies, and Theocracies",
          "Political Systems", [3], [8, 9], 4, 5,
          ["pattern_authoritarian_rise"],
          ["authoritarianism", "dictatorship", "oligarchy", "theocracy",
           "political systems", "history", "power", "critical thinking"]),
    Topic("federalism_devolution", "Federalism and Devolution — How Power Is Shared Between Levels",
          "Political Systems", [3], [8, 9], 4, 5,
          ["union_of_britain"],
          ["federalism", "devolution", "USA", "Scotland", "Wales",
           "political systems", "government", "power"]),
    Topic("left_right_political_spectrum", "Left, Right, and Why the Spectrum Is Misleading",
          "Political Systems", [3], [8, 9], 4, 5,
          ["democracy_types"],
          ["left", "right", "political spectrum", "ideology",
           "political systems", "socialism", "conservatism", "critical thinking"]),
    Topic("political_ideologies", "Political Ideologies — Liberalism, Conservatism, Socialism, and More",
          "Political Systems", [3], [8, 9], 4, 5,
          ["left_right_political_spectrum"],
          ["ideology", "liberalism", "conservatism", "socialism", "fascism",
           "political systems", "history", "critical thinking"]),
    Topic("electoral_systems", "Electoral Systems — First Past the Post, PR, and Why It Matters",
          "Political Systems", [3], [7, 8, 9], 4, 5,
          ["democracy_types"],
          ["electoral systems", "FPTP", "proportional representation",
           "voting", "elections", "political systems", "civics"]),
    Topic("separation_of_powers", "Separation of Powers — Legislature, Executive, and Judiciary",
          "Political Systems", [3], [7, 8, 9], 4, 5,
          ["history_of_democracy_britain"],
          ["separation of powers", "legislature", "executive", "judiciary",
           "checks and balances", "political systems", "law", "democracy"]),
    Topic("international_organisations", "International Organisations — UN, NATO, WTO, and What They Do",
          "Political Systems", [3], [8, 9], 4, 5,
          ["decolonisation", "ww2_global_conflict"],
          ["UN", "NATO", "WTO", "international", "political systems",
           "globalisation", "power", "diplomacy"]),

    # --- CGP Grey Track: How It Actually Works ---
    Topic("how_british_parliament_works", "How British Parliament Actually Works — Commons, Lords, and the Crown",
          "Political Systems", [2, 3], [6, 7, 8, 9], 3, 5,
          ["glorious_revolution", "history_of_democracy_britain"],
          ["parliament", "commons", "lords", "crown", "how it works",
           "Britain", "civics", "CGP Grey", "political systems"]),
    Topic("how_become_prime_minister", "How Do You Become Prime Minister?",
          "Political Systems", [3], [7, 8, 9], 4, 5,
          ["how_british_parliament_works"],
          ["prime minister", "how it works", "elections", "party",
           "Britain", "civics", "CGP Grey", "political systems", "power"]),
    Topic("how_become_pope", "How Do You Become the Pope? — The Conclave and the Papacy",
          "Political Systems", [3], [7, 8, 9], 3, 5,
          ["what_is_government"],
          ["pope", "conclave", "Vatican", "Catholic Church", "how it works",
           "religion", "power", "history", "CGP Grey", "political systems"]),
    Topic("what_is_the_city_of_london", "The City of London — A Medieval Corporation Inside a Modern City",
          "Political Systems", [3], [8, 9], 4, 6,
          ["how_british_parliament_works", "industrial_revolution"],
          ["City of London", "Lord Mayor", "corporation", "finance",
           "how it works", "history", "power", "Britain", "CGP Grey"]),
    Topic("how_become_lord_mayor", "How Do You Become the Lord Mayor of London?",
          "Political Systems", [3], [8, 9], 4, 5,
          ["what_is_the_city_of_london"],
          ["Lord Mayor", "City of London", "how it works", "guilds",
           "livery companies", "history", "Britain", "CGP Grey", "ceremony"]),
    Topic("what_is_the_commonwealth", "What Is the Commonwealth — and What Does It Actually Do?",
          "Political Systems", [3], [7, 8, 9], 3, 5,
          ["decolonisation", "british_empire_expansion"],
          ["Commonwealth", "British Empire", "monarchy", "how it works",
           "history", "decolonisation", "Britain", "CGP Grey", "political systems"]),
    Topic("how_laws_made_britain", "How Laws Are Made in Britain — From Idea to Act of Parliament",
          "Political Systems", [3], [7, 8, 9], 3, 5,
          ["how_british_parliament_works"],
          ["laws", "parliament", "bills", "acts", "how it works",
           "Britain", "civics", "CGP Grey", "political systems", "democracy"]),
    Topic("how_supreme_court_works", "How the Supreme Court Works — and Why Judges Matter",
          "Political Systems", [3], [8, 9], 4, 5,
          ["separation_of_powers"],
          ["supreme court", "judiciary", "judges", "law", "how it works",
           "Britain", "USA", "civics", "CGP Grey", "political systems"]),
    Topic("how_un_security_council_works", "The UN Security Council — Why Five Countries Have a Veto",
          "Political Systems", [3], [8, 9], 4, 6,
          ["international_organisations", "ww2_global_conflict"],
          ["UN", "security council", "veto", "P5", "how it works",
           "power", "international", "CGP Grey", "political systems", "history"]),
    Topic("how_eu_works", "How the EU Works — and Why Britain Left",
          "Political Systems", [3], [8, 9], 4, 5,
          ["federalism_devolution", "international_organisations"],
          ["EU", "European Union", "Brexit", "how it works",
           "political systems", "Britain", "Europe", "civics", "CGP Grey"]),
    Topic("how_taxes_work", "How Taxes Work — Where Money Comes From and Where It Goes",
          "Political Systems", [3], [7, 8, 9], 3, 5,
          ["budgeting_life_skills", "what_is_government"],
          ["taxes", "income tax", "VAT", "government spending", "how it works",
           "money", "civics", "CGP Grey", "political systems", "economics"]),
    Topic("how_central_banks_work", "Central Banks — How Governments Control Money",
          "Political Systems", [3], [9], 4, 5,
          ["how_taxes_work", "pattern_boom_bust"],
          ["central bank", "Bank of England", "interest rates", "inflation",
           "how it works", "money", "economics", "CGP Grey", "political systems"]),
    Topic("what_is_the_civil_service", "What Is the Civil Service — The Permanent Government",
          "Political Systems", [3], [8, 9], 4, 5,
          ["how_british_parliament_works"],
          ["civil service", "bureaucracy", "permanent government",
           "how it works", "Britain", "civics", "CGP Grey", "political systems"]),
    Topic("how_local_government_works", "How Local Government Works — Councils, Mayors, and What They Control",
          "Political Systems", [2, 3], [7, 8, 9], 3, 4,
          ["what_is_government"],
          ["local government", "council", "mayor", "planning", "how it works",
           "civics", "Britain", "CGP Grey", "political systems", "community"]),

    # --- Geopolitics ---
    Topic("what_is_geopolitics", "Geopolitics — How Geography Shapes Power",
          "Political Systems", [3], [8, 9], 4, 5,
          ["international_organisations", "rivers_mountains"],
          ["geopolitics", "power", "geography", "resources", "influence",
           "political systems", "history", "critical thinking"]),
    Topic("how_empires_work", "How Empires Work — Hard Power, Soft Power, and Economic Control",
          "Political Systems", [3], [8, 9], 4, 6,
          ["empire_legacy_today", "what_is_geopolitics"],
          ["empire", "hard power", "soft power", "economic control",
           "political systems", "history", "critical thinking", "geopolitics"]),
    Topic("what_is_nato", "What Is NATO — An Alliance, Not an Army",
          "Political Systems", [3], [8, 9], 4, 5,
          ["cold_war_context", "international_organisations"],
          ["NATO", "alliance", "collective defence", "how it works",
           "geopolitics", "political systems", "military", "CGP Grey"]),
]


# ---------------------------------------------------------------------------
# Science Experiments — Hands-On Science at Home or School
# Each topic is a doable experiment with household or easily sourced
# materials. Structure per topic: the question to investigate → what you
# need → what to do → what to observe → what it shows → what to wonder next.
# The tutor walks the child through the experiment conversationally, asks
# predictive questions before ("what do you think will happen?"), and
# Socratic questions after ("why do you think that happened?").
# Grouped by discipline: Chemistry, Biology, Physics.
# ---------------------------------------------------------------------------

_EXPERIMENTS = [

    # ==========================================================================
    # CHEMISTRY EXPERIMENTS
    # ==========================================================================

    # --- Acids, Bases, and Indicators ---
    Topic("exp_red_cabbage_indicator", "Red Cabbage pH Indicator — Make Your Own Acid-Base Test",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["properties_materials_ks2"],
          ["chemistry", "experiment", "acids", "bases", "pH", "indicator",
           "red cabbage", "household", "hands-on", "science"]),
    Topic("exp_volcano_baking_soda", "Baking Soda Volcano — Acid-Base Reaction",
          "Experiment", [1, 2], [2, 3, 4], 1, 3,
          [],
          ["chemistry", "experiment", "acids", "bases", "reaction",
           "baking soda", "vinegar", "household", "hands-on", "science"]),
    Topic("exp_elephant_toothpaste", "Elephant Toothpaste — Catalytic Decomposition",
          "Experiment", [2, 3], [6, 7, 8], 3, 5,
          ["chemical_reactions"],
          ["chemistry", "experiment", "catalyst", "hydrogen peroxide",
           "decomposition", "exothermic", "hands-on", "science"]),
    Topic("exp_crystal_growing", "Growing Crystals — Supersaturation and Crystallisation",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["particle_model"],
          ["chemistry", "experiment", "crystals", "salt", "sugar", "alum",
           "crystallisation", "supersaturation", "hands-on", "science"]),
    Topic("exp_chromatography", "Chromatography — Separating Colours in Ink",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["properties_materials_ks2"],
          ["chemistry", "experiment", "chromatography", "separation",
           "ink", "paper", "household", "hands-on", "science"]),
    Topic("exp_slime", "Making Slime — Polymer Chemistry",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["properties_materials_ks2"],
          ["chemistry", "experiment", "slime", "polymer", "PVA", "borax",
           "non-Newtonian", "hands-on", "science", "materials"]),
    Topic("exp_electroplating", "Electroplating — Depositing Metal Using Electricity",
          "Experiment", [3], [7, 8, 9], 3, 5,
          ["build_a_battery", "copper"],
          ["chemistry", "experiment", "electroplating", "electrolysis",
           "copper", "electrochemistry", "hands-on", "science", "metals"]),
    Topic("exp_soap_making", "Making Soap — Saponification",
          "Experiment", [3], [7, 8, 9], 3, 5,
          ["chemical_reactions", "cooking_nutrition"],
          ["chemistry", "experiment", "soap", "saponification", "alkali",
           "fat", "hands-on", "science", "household"]),
    Topic("exp_invisible_ink", "Invisible Ink — Chemistry of Oxidation and Heat",
          "Experiment", [2], [4, 5, 6], 2, 3,
          ["chemical_reactions"],
          ["chemistry", "experiment", "invisible ink", "oxidation", "lemon",
           "household", "hands-on", "science", "spy"]),
    Topic("exp_density_tower", "Density Tower — Liquids That Won't Mix",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["particle_model"],
          ["chemistry", "experiment", "density", "liquids", "honey",
           "oil", "water", "household", "hands-on", "science", "physics"]),
    Topic("exp_milk_plastic", "Milk Plastic — Making Casein Plastic",
          "Experiment", [2, 3], [6, 7, 8], 3, 5,
          ["how_plastic_is_made", "chemical_reactions"],
          ["chemistry", "experiment", "plastic", "casein", "milk",
           "polymer", "hands-on", "science", "materials"]),
    Topic("exp_fermentation_yeast", "Yeast Fermentation — Feeding Yeast and Catching CO2",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["baking_bread_pastry"],
          ["chemistry", "experiment", "fermentation", "yeast", "CO2",
           "biology", "bread", "hands-on", "science", "food"]),

    # --- Applied Chemistry: Water and Pools ---
    Topic("exp_pool_chemistry", "Pool Chemistry — Testing and Balancing Water",
          "Experiment", [2, 3], [6, 7, 8, 9], 3, 5,
          ["exp_red_cabbage_indicator", "chemical_reactions"],
          ["chemistry", "experiment", "pool", "water chemistry", "pH",
           "chlorine", "alkalinity", "test kit", "applied chemistry",
           "hands-on", "science", "real world"]),
    Topic("exp_water_hardness", "Water Hardness — Why Soap Doesn't Lather the Same Everywhere",
          "Experiment", [2, 3], [6, 7, 8], 3, 4,
          ["particle_model", "exp_red_cabbage_indicator"],
          ["chemistry", "experiment", "water hardness", "calcium", "magnesium",
           "soap", "limescale", "ions", "hands-on", "science"]),
    Topic("exp_drinking_water_testing", "Testing Drinking Water — What's Actually in Your Tap Water",
          "Experiment", [2, 3], [6, 7, 8], 3, 5,
          ["how_water_reaches_home", "exp_pool_chemistry"],
          ["chemistry", "experiment", "drinking water", "testing", "chlorine",
           "pH", "nitrates", "tap water", "hands-on", "science", "real world"]),
    Topic("exp_water_filtration_build", "Building a Water Filter — From Muddy to Clear",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["how_water_reaches_home"],
          ["chemistry", "experiment", "water filter", "filtration", "sand",
           "gravel", "charcoal", "build it", "hands-on", "science", "practical"]),
    Topic("exp_electrolysis_water", "Electrolysis of Water — Splitting H2O into Hydrogen and Oxygen",
          "Experiment", [3], [7, 8, 9], 3, 5,
          ["build_a_battery", "chemical_reactions"],
          ["chemistry", "experiment", "electrolysis", "water", "hydrogen",
           "oxygen", "fuel cell", "electricity", "hands-on", "science"]),

    # ==========================================================================
    # BIOLOGY EXPERIMENTS
    # ==========================================================================

    # --- Plants and Growth ---
    Topic("exp_seed_germination", "Germination Experiment — What Do Seeds Need to Sprout?",
          "Experiment", [1, 2], [2, 3, 4], 1, 3,
          ["seeds_germination"],
          ["biology", "experiment", "seeds", "germination", "conditions",
           "light", "water", "temperature", "hands-on", "science", "plants"]),
    Topic("exp_photosynthesis_oxygen", "Photosynthesis — Watching Plants Produce Oxygen",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["plants_ks2"],
          ["biology", "experiment", "photosynthesis", "oxygen", "pondweed",
           "light", "bubbles", "hands-on", "science", "plants"]),
    Topic("exp_osmosis_potato", "Osmosis — Why Potatoes Shrink in Salt Water",
          "Experiment", [2, 3], [6, 7, 8], 3, 5,
          ["cells_ks3"],
          ["biology", "experiment", "osmosis", "potato", "salt", "water",
           "cells", "membrane", "hands-on", "science"]),
    Topic("exp_dissection_flower", "Dissecting a Flower — Parts and Their Functions",
          "Experiment", [2], [4, 5, 6], 2, 3,
          ["plants_ks2"],
          ["biology", "experiment", "flower", "dissection", "stamen",
           "pistil", "petals", "pollination", "hands-on", "science"]),
    Topic("exp_yeast_bread_rise", "Bread Rising — Yeast, CO2, and Gluten",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["baking_bread_pastry", "exp_fermentation_yeast"],
          ["biology", "experiment", "yeast", "bread", "CO2", "gluten",
           "rising", "hands-on", "science", "food", "chemistry"]),
    Topic("exp_microscope_pond_water", "Pond Water Under a Microscope — A World in a Drop",
          "Experiment", [2, 3], [5, 6, 7], 2, 4,
          ["cells_ks3", "age_of_single_cells"],
          ["biology", "experiment", "microscope", "pond water", "protozoa",
           "microorganisms", "cells", "hands-on", "science"]),
    Topic("exp_mould_growth", "Growing Mould — What Conditions Does Mould Prefer?",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["cells_ks3"],
          ["biology", "experiment", "mould", "fungus", "conditions",
           "bread", "growth", "hands-on", "science", "decay"]),
    Topic("exp_dna_extraction", "Extracting DNA — From Strawberry to Visible Thread",
          "Experiment", [2, 3], [7, 8, 9], 3, 5,
          ["genetics_ks3"],
          ["biology", "experiment", "DNA", "extraction", "strawberry",
           "genetics", "hands-on", "science", "cells"]),
    Topic("exp_enzyme_activity", "Enzymes — Testing How Temperature Affects Reaction Speed",
          "Experiment", [3], [8, 9], 4, 5,
          ["chemical_reactions", "human_body_ks2"],
          ["biology", "experiment", "enzymes", "temperature", "liver",
           "hydrogen peroxide", "catalase", "hands-on", "science"]),
    Topic("exp_food_testing", "Food Testing — Detecting Starch, Glucose, and Protein",
          "Experiment", [2, 3], [6, 7, 8], 3, 4,
          ["nutrition_food_science", "chemical_reactions"],
          ["biology", "experiment", "food testing", "iodine", "Benedict's",
           "Biuret", "nutrients", "hands-on", "science", "food"]),
    Topic("exp_reaction_time", "Reaction Time — Testing Your Nervous System",
          "Experiment", [2], [5, 6, 7], 2, 3,
          ["human_body_ks2"],
          ["biology", "experiment", "reaction time", "nervous system",
           "ruler drop", "brain", "hands-on", "science", "body"]),
    Topic("exp_heart_rate_exercise", "Heart Rate and Exercise — Your Cardiovascular System",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["human_body_ks2"],
          ["biology", "experiment", "heart rate", "exercise", "pulse",
           "cardiovascular", "recovery", "hands-on", "science", "body"]),

    # ==========================================================================
    # PHYSICS EXPERIMENTS
    # ==========================================================================

    # --- Forces and Motion ---
    Topic("exp_pendulum", "The Pendulum — Does Weight Affect Swing Time?",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["forces_magnets"],
          ["physics", "experiment", "pendulum", "gravity", "period",
           "forces", "timing", "hands-on", "science", "maths"]),
    Topic("exp_egg_drop", "The Egg Drop — Protecting an Egg from a Height",
          "Experiment", [2, 3], [5, 6, 7], 3, 5,
          ["forces_motion_ks3"],
          ["physics", "experiment", "egg drop", "forces", "impact",
           "design", "engineering", "hands-on", "science", "challenge"]),
    Topic("exp_paper_bridges", "Paper Bridge — How Much Weight Can Paper Hold?",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["forces_magnets"],
          ["physics", "experiment", "bridge", "forces", "structure",
           "compression", "tension", "design", "hands-on", "science"]),
    Topic("exp_air_resistance", "Air Resistance — Parachutes and Falling",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["forces_magnets"],
          ["physics", "experiment", "air resistance", "parachute",
           "falling", "forces", "drag", "hands-on", "science"]),
    Topic("exp_centre_of_gravity", "Centre of Gravity — Balancing Impossibly",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["forces_magnets"],
          ["physics", "experiment", "centre of gravity", "balance",
           "stability", "forks", "household", "hands-on", "science"]),

    # --- Electricity and Magnetism ---
    Topic("exp_static_electricity", "Static Electricity — Bending Water with a Comb",
          "Experiment", [2], [4, 5, 6], 2, 3,
          ["electricity_ks2"],
          ["physics", "experiment", "static electricity", "charges",
           "comb", "water", "attraction", "household", "hands-on", "science"]),
    Topic("exp_electromagnet", "Build an Electromagnet — Coils, Current, and Iron",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["build_an_electric_motor", "forces_magnets"],
          ["physics", "experiment", "electromagnet", "coil", "iron",
           "current", "magnetism", "hands-on", "science", "build it"]),
    Topic("exp_circuit_challenge", "Circuit Challenge — Build a Working Alarm or Light",
          "Experiment", [2], [4, 5, 6], 2, 3,
          ["electronics_circuits_basics"],
          ["physics", "experiment", "circuit", "electricity", "LED",
           "buzzer", "build it", "hands-on", "science", "practical"]),

    # --- Light and Sound ---
    Topic("exp_light_spectrum_prism", "Light Through a Prism — Splitting White Light",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["light_shadows", "waves_ks3"],
          ["physics", "experiment", "light", "prism", "spectrum", "rainbow",
           "refraction", "colour", "hands-on", "science"]),
    Topic("exp_shadows_sundial", "Shadows and a Sundial — Tracking the Sun",
          "Experiment", [1, 2], [2, 3, 4], 1, 3,
          ["light_shadows", "seasons_weather"],
          ["physics", "experiment", "shadows", "sundial", "sun",
           "time", "light", "outdoor", "hands-on", "science"]),
    Topic("exp_sound_vibrations", "Seeing Sound — Vibrations and Standing Waves",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["sound_ks2"],
          ["physics", "experiment", "sound", "vibrations", "salt",
           "speaker", "Chladni", "waves", "hands-on", "science"]),
    Topic("exp_echo_speed_sound", "Measuring the Speed of Sound — Echoes and Timing",
          "Experiment", [3], [7, 8, 9], 3, 5,
          ["waves_ks3"],
          ["physics", "experiment", "sound", "speed", "echo", "timing",
           "distance", "maths", "hands-on", "science"]),

    # --- Heat and Energy ---
    Topic("exp_insulation_contest", "Insulation Contest — Which Material Keeps Ice Longest?",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["materials_properties"],
          ["physics", "experiment", "insulation", "heat", "temperature",
           "materials", "energy", "household", "hands-on", "science"]),
    Topic("exp_convection_currents", "Convection Currents — Watching Heat Move Through Water",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["particle_model"],
          ["physics", "experiment", "convection", "heat", "temperature",
           "water", "dye", "currents", "hands-on", "science"]),
    Topic("exp_solar_oven", "Build a Solar Oven — Concentrating Sunlight",
          "Experiment", [2, 3], [6, 7, 8], 3, 5,
          ["how_solar_panels_work", "how_electricity_generated"],
          ["physics", "experiment", "solar", "energy", "oven", "reflection",
           "build it", "hands-on", "science", "environment"]),
    Topic("exp_trebuchet_physics", "Trebuchet Physics — Measuring Projectile Motion",
          "Experiment", [3], [7, 8, 9], 3, 5,
          ["build_a_trebuchet", "forces_motion_ks3"],
          ["physics", "experiment", "projectile", "trebuchet", "motion",
           "forces", "maths", "measurement", "hands-on", "science"]),

    # --- Film science experiments ---
    Topic("exp_pinhole_camera", "Build a Pinhole Camera — How Film and Photography Work",
          "Experiment", [2], [5, 6, 7], 2, 4,
          ["light_shadows"],
          ["physics", "experiment", "pinhole camera", "optics", "light",
           "photography", "film", "build it", "hands-on", "science"]),
    Topic("exp_persistence_of_vision", "Persistence of Vision — Why Movies Move",
          "Experiment", [2], [4, 5, 6], 2, 4,
          ["light_shadows"],
          ["physics", "experiment", "persistence of vision", "animation",
           "thaumatrope", "zoetrope", "film", "brain", "hands-on", "science"]),

    # --- New experiments from audit ---
    Topic("exp_candle_combustion", "Candle Science — The Fire Triangle and Combustion Products",
          "Experiment", [2], [5, 6, 7, 8], 2, 4,
          ["oxidation_combustion"],
          ["chemistry", "experiment", "combustion", "fire triangle", "candle",
           "CO2", "water", "carbon cycle", "hands-on", "science", "safety"]),
    Topic("exp_lemon_battery", "Lemon Battery — Making Electricity from Fruit",
          "Experiment", [2, 3], [5, 6, 7, 8], 2, 4,
          ["build_a_battery", "chemical_reactions"],
          ["chemistry", "experiment", "battery", "lemon", "zinc", "copper",
           "redox", "electrochemistry", "electricity", "Volta", "hands-on", "science"]),
    Topic("exp_magnetic_field_mapping", "Magnetic Field Mapping — Seeing Invisible Forces",
          "Experiment", [2], [4, 5, 6, 7], 2, 4,
          ["forces_magnets"],
          ["physics", "experiment", "magnets", "field lines", "compass",
           "poles", "Earth's field", "magnetism", "hands-on", "science"]),
    Topic("exp_bernoulli_flight", "Bernoulli and Flight — Why Wings Lift",
          "Experiment", [2], [5, 6, 7, 8], 2, 4,
          ["forces_magnets", "air_resistance"],
          ["physics", "experiment", "Bernoulli", "flight", "lift", "aerofoil",
           "air pressure", "Wright Brothers", "hands-on", "science"]),
    Topic("exp_bread_baking_science", "Bread Baking Science — Gluten, Yeast, and the Maillard Reaction",
          "Experiment", [2], [5, 6, 7, 8], 2, 5,
          ["baking_bread_pastry", "exp_fermentation_yeast"],
          ["biology", "chemistry", "experiment", "bread", "gluten", "yeast",
           "Maillard reaction", "oven spring", "hands-on", "science", "food"]),
]


# ---------------------------------------------------------------------------
# Film — The Art and Technology of Moving Pictures
# How movies are made, how VFX evolved era by era, the grammar of cinema,
# and the stories behind the tricks. Connects art, physics, computing,
# history, and social patterns. The James Burke approach applied to film:
# every technique has an origin story that is more interesting than the trick.
# ---------------------------------------------------------------------------

_FILM = [
    # --- Origins and Silent Era ---
    Topic("film_origins", "How Cinema Was Invented — Persistence of Vision to the Lumière Brothers",
          "Film", [2], [5, 6, 7], 2, 4, ["light_shadows"],
          ["film", "cinema history", "Lumière", "Edison", "persistence of vision",
           "zoetrope", "photography", "how things work"]),
    Topic("film_silent_era", "Silent Films — Acting Without Words and the Grammar of Editing",
          "Film", [2, 3], [6, 7, 8], 3, 4, ["film_origins"],
          ["film", "silent film", "Chaplin", "Buster Keaton", "editing",
           "cinema history", "storytelling", "visual language"]),
    Topic("film_sound_arrives", "When Sound Arrived — The Jazz Singer and the End of the Silent Era",
          "Film", [3], [7, 8], 3, 4, ["film_silent_era"],
          ["film", "sound", "talkies", "The Jazz Singer", "cinema history",
           "technology", "how things work", "music"]),

    # --- The Grammar of Cinema ---
    Topic("film_grammar", "The Grammar of Film — Shots, Cuts, and How Cinema Tells Stories",
          "Film", [2, 3], [6, 7, 8, 9], 3, 5, ["film_origins"],
          ["film", "cinematography", "shots", "editing", "close-up", "montage",
           "storytelling", "visual language", "Eisenstein"]),
    Topic("film_directors_auteurs", "Directors as Authors — Hitchcock, Kubrick, and the Auteur Theory",
          "Film", [3], [8, 9], 4, 5, ["film_grammar"],
          ["film", "directors", "auteur", "Hitchcock", "Kubrick", "Spielberg",
           "cinema history", "storytelling", "art"]),
    Topic("film_genres_conventions", "Film Genres — Conventions, Expectations, and Subversions",
          "Film", [2, 3], [6, 7, 8, 9], 3, 5, ["film_grammar"],
          ["film", "genres", "western", "horror", "science fiction", "noir",
           "conventions", "storytelling", "critical thinking"]),
    Topic("film_music_scores", "Film Music — How Scores Manipulate Emotion",
          "Film", [2, 3], [6, 7, 8], 3, 4, ["film_grammar", "music_society_culture"],
          ["film music", "score", "Jaws", "Star Wars", "leitmotif",
           "emotion", "manipulation", "John Williams", "music"]),

    # --- VFX Through the Eras ---
    Topic("vfx_practical_effects", "Practical Effects — How Films Faked It Before Computers",
          "Film", [2, 3], [6, 7, 8], 3, 5, ["film_origins"],
          ["VFX", "practical effects", "miniatures", "matte painting", "stop motion",
           "King Kong", "2001", "Star Wars", "how things work", "film"]),
    Topic("vfx_optical_tricks", "Optical Tricks — Double Exposure, Rear Projection, and Glass Mattes",
          "Film", [3], [7, 8, 9], 3, 5, ["vfx_practical_effects", "light_shadows"],
          ["VFX", "optical effects", "rear projection", "matte painting",
           "double exposure", "light", "optics", "film", "how things work"]),
    Topic("vfx_stop_motion", "Stop Motion Animation — Ray Harryhausen and the Frame-by-Frame Art",
          "Film", [2, 3], [5, 6, 7, 8], 2, 4, ["film_origins"],
          ["VFX", "stop motion", "Harryhausen", "animation", "puppets",
           "Clash of the Titans", "Wallace and Gromit", "film", "art", "patience"]),
    Topic("vfx_first_cgi", "The Birth of CGI — Tron, The Abyss, and Terminator 2",
          "Film", [3], [7, 8, 9], 3, 5,
          ["vfx_practical_effects", "programming_scratch_ks2"],
          ["VFX", "CGI", "computer graphics", "Tron", "Terminator 2",
           "ILM", "computing", "film", "how things work"]),
    Topic("vfx_jurassic_park_revolution", "Jurassic Park — The Revolution That Changed Everything (1993)",
          "Film", [3], [7, 8, 9], 3, 5, ["vfx_first_cgi"],
          ["VFX", "Jurassic Park", "CGI", "ILM", "dinosaurs", "revolution",
           "computing", "film", "how things work", "science"]),
    Topic("vfx_motion_capture", "Motion Capture — Turning Actors Into Digital Characters",
          "Film", [3], [7, 8, 9], 3, 5, ["vfx_jurassic_park_revolution"],
          ["VFX", "motion capture", "Gollum", "Avatar", "performance capture",
           "computing", "film", "how things work", "acting"]),
    Topic("vfx_modern_pipeline", "Modern VFX — How Blockbusters Are Made Today",
          "Film", [3], [8, 9], 4, 5, ["vfx_motion_capture"],
          ["VFX", "modern VFX", "compositing", "previz", "green screen",
           "rendering", "computing", "film", "pipeline", "how things work"]),
    Topic("vfx_deepfakes_ai", "Deepfakes and AI — When You Can't Trust What You See",
          "Film", [3], [8, 9], 4, 6,
          ["vfx_modern_pipeline", "artificial_intelligence_basics"],
          ["VFX", "deepfakes", "AI", "synthetic media", "trust", "media literacy",
           "manipulation", "film", "critical thinking", "ethics"]),

    # --- Film and Society ---
    Topic("film_propaganda_history", "Film as Propaganda — Triumph of the Will to Today",
          "Film", [3], [8, 9], 4, 6,
          ["film_grammar", "pattern_propaganda"],
          ["film", "propaganda", "Riefenstahl", "Triumph of the Will",
           "Soviet cinema", "manipulation", "history", "critical thinking"]),
    Topic("film_censorship_ratings", "Censorship and Ratings — Who Decides What We Can Watch",
          "Film", [3], [8, 9], 4, 5,
          ["censorship_history", "film_grammar"],
          ["film", "censorship", "ratings", "Hays Code", "BBFC", "classification",
           "history", "political systems", "media", "critical thinking"]),
    Topic("film_representation", "Representation in Film — Who Gets to Tell the Story",
          "Film", [3], [8, 9], 4, 6,
          ["film_directors_auteurs", "civil_rights_global"],
          ["film", "representation", "diversity", "Bechdel test", "Hollywood",
           "identity", "critical thinking", "media", "social patterns"]),
    Topic("film_documentary", "Documentary Film — Fact, Point of View, and the Ethics of Truth",
          "Film", [3], [8, 9], 4, 5,
          ["film_grammar", "evaluating_sources"],
          ["documentary", "film", "truth", "bias", "ethics", "journalism",
           "critical thinking", "media literacy", "storytelling"]),
    Topic("film_how_to_watch", "How to Watch a Film — Active Viewing and Film Analysis",
          "Film", [2, 3], [6, 7, 8, 9], 3, 5,
          ["film_grammar", "art_appreciation_visual_literacy"],
          ["film", "analysis", "active viewing", "visual literacy",
           "critical thinking", "storytelling", "art", "media"]),
]


# ---------------------------------------------------------------------------
# Music Theory and Production — Deep Tracks
# The extended music curriculum for children who want to go further.
# Two parallel arcs that cross-reference each other:
#   1. Music Theory — piano keyboard as the model, intervals, chords,
#      harmony, voice leading, modes, composition
#   2. Music Production — signal chain, effects, synthesis, sampling,
#      mixing, mastering — how studio music is actually made
# The piano is the best instrument for teaching theory because every note
# is visible and laid out spatially. These topics are for voice+e-ink:
# the tutor describes, the child reasons — no instrument needed to learn
# the theory, though having a keyboard available enriches every session.
# ---------------------------------------------------------------------------

_MUSIC_DEEP = [

    # ==========================================================================
    # MUSIC THEORY — The Piano as Model
    # ==========================================================================

    Topic("piano_keyboard_layout", "The Piano Keyboard — The Map of All Western Music",
          "Music", [2], [4, 5, 6], 1, 3, [],
          ["piano", "keyboard", "notes", "octaves", "white keys", "black keys",
           "music theory", "ABCDEFG", "visual"]),
    # The keyboard as a spatial representation of pitch. White and black keys,
    # naming notes A-G, the pattern that repeats every octave, middle C as anchor,
    # why the black keys are where they are (the chromatic scale structure).
    # No instrument needed — describe the layout verbally. "Count up from C..."

    Topic("semitones_tones", "Semitones and Tones — The Building Blocks of Scales",
          "Music", [2], [5, 6, 7], 2, 4, ["piano_keyboard_layout"],
          ["music theory", "semitone", "tone", "half step", "whole step",
           "intervals", "chromatic scale", "piano"]),
    # A semitone is one key to the very next (white or black). A tone is two semitones.
    # The chromatic scale is 12 semitones. This is the foundation for understanding
    # why scales sound the way they do — they're patterns of tones and semitones.

    Topic("major_scale_construction", "Building a Major Scale — The TTSTTTS Pattern",
          "Music", [2], [5, 6, 7], 2, 4, ["semitones_tones"],
          ["music theory", "major scale", "TTSTTTS", "C major", "key",
           "scales", "piano", "pattern"]),
    # Tone-Tone-Semitone-Tone-Tone-Tone-Semitone. Why C major uses only white keys.
    # Build a G major scale — one black key needed. This is the moment students
    # understand why key signatures exist. Perfect for voice: "Start on D, go up
    # using TTSTTTS — what note do you land on?"

    Topic("minor_scales", "Minor Scales — Natural, Harmonic, and Melodic",
          "Music", [3], [6, 7, 8], 3, 4, ["major_scale_construction"],
          ["music theory", "minor scale", "natural minor", "harmonic minor",
           "melodic minor", "sad", "mood", "scales", "piano"]),
    # Why minor sounds different (sad/tense) — the third is lowered by a semitone.
    # Natural minor (Aeolian mode), harmonic minor (raised 7th for the leading tone),
    # melodic minor (different ascending and descending). The tutor can demonstrate
    # by humming or describing: "Imagine a scale that goes up but comes back differently."

    Topic("intervals_ear_training", "Intervals — Naming the Distance Between Any Two Notes",
          "Music", [2, 3], [5, 6, 7, 8], 3, 4, ["semitones_tones"],
          ["music theory", "intervals", "unison", "third", "fifth", "octave",
           "perfect", "major", "minor", "ear training", "recognition"]),
    # Unison, minor 2nd, major 2nd, minor 3rd... through to the octave.
    # The classic trick: each interval has a famous melody that starts with it.
    # Major 2nd = first two notes of Happy Birthday. Perfect 5th = Star Wars theme.
    # Minor 3rd = Smoke on the Water. Voice-teachable as recognition exercises.

    Topic("triads_chord_construction", "Triads — Building Chords from Three Notes",
          "Music", [2, 3], [5, 6, 7, 8], 3, 4, ["intervals_ear_training"],
          ["music theory", "chords", "triads", "major chord", "minor chord",
           "diminished", "augmented", "root", "third", "fifth", "piano"]),
    # Root + major third + perfect fifth = major chord (happy).
    # Root + minor third + perfect fifth = minor chord (sad).
    # Root + minor third + diminished fifth = diminished chord (tense/unstable).
    # Every chord in Western music is built from intervals stacked on a root.

    Topic("chord_progressions", "Chord Progressions — The Patterns Behind Every Song",
          "Music", [2, 3], [6, 7, 8, 9], 3, 5, ["triads_chord_construction"],
          ["music theory", "chord progressions", "I IV V", "ii V I", "twelve bar blues",
           "pop progression", "jazz", "harmony", "piano", "songwriting"]),
    # I-IV-V: the foundation of blues, rock, and country.
    # I-V-vi-IV: the four-chord pop progression (Pachelbel → Axis of Awesome).
    # ii-V-I: the jazz turnaround.
    # Twelve bar blues as a complete harmonic system.
    # Voice exercise: "Name three famous songs that use I-V-vi-IV."

    Topic("seventh_chords", "Seventh Chords — Adding the Fourth Note",
          "Music", [3], [7, 8, 9], 3, 5, ["chord_progressions"],
          ["music theory", "seventh chords", "dominant seventh", "major seventh",
           "minor seventh", "jazz", "blues", "tension", "piano", "harmony"]),
    # Dominant seventh (C7) = the chord that most wants to resolve — foundation of blues.
    # Major seventh (Cmaj7) = jazzy, sophisticated, floaty.
    # Minor seventh (Cm7) = mellow, soulful.
    # Why sevenths create tension and how resolution works.

    Topic("modes_introduction", "Modes — The Seven Flavours of the Major Scale",
          "Music", [3], [8, 9], 4, 5, ["major_scale_construction"],
          ["music theory", "modes", "Dorian", "Mixolydian", "Lydian", "Phrygian",
           "modal", "jazz", "folk", "colour", "piano", "advanced"]),
    # Starting a major scale on a different degree gives a mode with a distinct colour.
    # Dorian (D to D on white keys) = minor but with a raised 6th — used in folk and jazz.
    # Mixolydian (G to G) = major but with a flat 7th — used in rock and blues.
    # Lydian (F to F) = dreamy, film music.
    # Phrygian (E to E) = Spanish/flamenco sound.

    Topic("counterpoint_voice_leading", "Counterpoint and Voice Leading — How Notes Move Together",
          "Music", [3], [8, 9], 4, 6, ["chord_progressions", "intervals_ear_training"],
          ["music theory", "counterpoint", "voice leading", "Bach", "polyphony",
           "part writing", "dissonance", "resolution", "advanced", "composition"]),
    # Why some note movements sound smooth and others jarring.
    # The rules of classical counterpoint (parallel fifths are forbidden, why?).
    # Bach's chorales as examples of perfect voice leading.
    # How this connects to jazz chord voicings and smooth progressions.

    Topic("rhythm_advanced", "Rhythm in Depth — Polyrhythm, Syncopation, and Odd Time Signatures",
          "Music", [2, 3], [6, 7, 8, 9], 3, 5, ["music_rhythm_ks1"],
          ["music theory", "rhythm", "polyrhythm", "syncopation", "3/4", "5/4", "7/8",
           "odd time", "jazz", "African music", "groove", "advanced"]),
    # Syncopation: the beat lands where you don't expect it — the engine of jazz and funk.
    # Polyrhythm: two different rhythms simultaneously (3 against 2).
    # Odd time signatures: Brubeck's Take Five (5/4), Pink Floyd's Money (7/4).
    # Voice exercise: "Count 1-2-3-4-5 to yourself while I speak the rhythm..."

    # ==========================================================================
    # MUSIC PRODUCTION — The Studio as Instrument
    # ==========================================================================

    Topic("signal_chain", "The Signal Chain — From Instrument to Speaker",
          "Music", [3], [7, 8, 9], 3, 4, ["music_physics_sound"],
          ["music production", "signal chain", "instrument", "amplifier",
           "speaker", "gain", "decibels", "audio", "electronics", "how things work"]),
    # Every sound travels: instrument → pickup/microphone → preamp → amplifier → speaker.
    # What gain is and why it matters.
    # Decibels as a logarithmic scale (0dB, +3dB doubles perceived volume).
    # Why the order of effects in the chain matters.

    Topic("microphones_how_they_work", "Microphones — How Sound Becomes Electricity",
          "Music", [3], [7, 8, 9], 3, 4, ["signal_chain", "sound_ks2"],
          ["music production", "microphones", "condenser", "dynamic", "ribbon",
           "polar patterns", "cardioid", "phantom power", "recording", "how things work"]),
    # Dynamic (moving coil — robust, live), condenser (capacitor — sensitive, studio),
    # ribbon (warm, vintage). Polar patterns: cardioid captures what's in front,
    # omni captures everything, figure-8 captures front and back.
    # Why you can't plug a condenser mic into a guitar amp.

    Topic("effects_distortion_overdrive", "Distortion and Overdrive — Clipping, Harmonics, and Grit",
          "Music", [3], [7, 8, 9], 3, 5,
          ["signal_chain", "music_physics_sound"],
          ["music production", "effects", "distortion", "overdrive", "fuzz",
           "clipping", "harmonics", "guitar", "electric guitar", "pedals", "tone"]),
    # What actually happens electrically when you overdrive a signal (clipping).
    # How clipping generates harmonic overtones — why distortion sounds musical.
    # The difference: overdrive (soft clipping, warm) → distortion (hard clipping, aggressive)
    # → fuzz (extreme clipping, sustain, octave effects).
    # History: the Kinks cutting their speaker cone, the Tone Bender, the Big Muff.

    Topic("effects_time_based", "Reverb, Delay, and Chorus — Time-Based Effects",
          "Music", [3], [7, 8, 9], 3, 5,
          ["signal_chain", "sound_ks2"],
          ["music production", "effects", "reverb", "delay", "chorus", "flanger",
           "phaser", "time", "echo", "space", "pedals", "atmosphere"]),
    # Reverb: simulates a space (room, hall, plate, spring). The physics — reflections.
    # Delay: discrete echo. Slap-back (Rockabilly), dotted-eighth (The Edge, U2).
    # Chorus: multiple slightly detuned and delayed copies = perceived fullness.
    # Flanger: extreme chorus with feedback — the jet-plane sound.
    # Phaser: all-pass filter swept in frequency — sweeping, psychedelic.

    Topic("effects_dynamic_processing", "Compression and EQ — Shaping Dynamics and Tone",
          "Music", [3], [8, 9], 4, 5,
          ["signal_chain", "music_physics_sound"],
          ["music production", "compression", "EQ", "equalisation", "threshold",
           "ratio", "attack", "release", "frequency", "mixing", "mastering"]),
    # EQ: boost or cut frequency bands. Low-pass, high-pass, shelf, parametric.
    # Why vocals need high-pass filtering (removes room rumble).
    # Compression: turns down the loudest parts, turns up the average level.
    # Threshold, ratio, attack, release as parameters.
    # Why over-compressed music sounds flat and exhausting (the loudness war).

    Topic("synthesis_basics", "Synthesis — Making Sound from Electricity",
          "Music", [3], [7, 8, 9], 3, 5,
          ["signal_chain", "music_physics_sound"],
          ["music production", "synthesis", "oscillator", "filter", "envelope",
           "ADSR", "LFO", "subtractive synthesis", "Moog", "analogue", "synth"]),
    # Subtractive synthesis: start with a harmonically rich waveform, filter out what
    # you don't want. Oscillator (generates waveform) → Filter (shapes tone) →
    # Amplifier (shapes volume) → controlled by envelope and LFO.
    # ADSR: Attack, Decay, Sustain, Release — the shape of a sound over time.
    # LFO: Low Frequency Oscillator — creates vibrato, tremolo, filter wobble.
    # History: Moog synthesiser (1964), Minimoog, the ARP, Kraftwerk.

    Topic("synthesis_modern", "Modern Synthesis — FM, Wavetable, and Granular",
          "Music", [3], [9], 4, 5,
          ["synthesis_basics"],
          ["music production", "synthesis", "FM synthesis", "wavetable",
           "granular", "Yamaha DX7", "Serum", "advanced", "digital synth"]),
    # FM synthesis: two oscillators where one modulates the frequency of the other.
    # Creates metallic, bell-like, electric piano sounds. The DX7 sound (1983).
    # Wavetable: scanning through a table of waveforms in real time — modern digital sound.
    # Granular: slicing audio into tiny grains and reassembling them — stretching, morphing.

    Topic("sampling_basics", "Sampling — Using Recordings as Instruments",
          "Music", [3], [7, 8, 9], 3, 5,
          ["music_technology"],
          ["music production", "sampling", "sampler", "loop", "chop", "hip hop",
           "Akai MPC", "SP-404", "copyright", "creative", "how things work"]),
    # What a sampler is — it records a sound and plays it back at different pitches.
    # Crate digging: finding the break-beat. James Brown's "Funky Drummer."
    # The Amen break — used in thousands of tracks.
    # Chopping: slicing a sample into pieces and rearranging them.
    # Copyright and sampling (the Biz Markie case, Bridgeport v. Dimension Films).
    # Hardware samplers: Akai MPC, E-mu SP-1200, Roland SP-404.

    Topic("sampling_advanced", "Advanced Sampling — Flip, Chop, and Replay",
          "Music", [3], [9], 4, 6,
          ["sampling_basics", "chord_progressions"],
          ["music production", "sampling", "flip", "chop", "pitch shift",
           "time stretch", "replay", "interpolation", "hip hop", "production"]),
    # The flip: taking a sample and making it unrecognisable through transposition, chopping,
    # filtering, and reversing.
    # Replay: recreating a sample note-for-note on a keyboard to avoid copyright.
    # Interpolation: quoting a melody without the original recording.
    # Beatmaking workflow: MPC workflow, DAW workflow, hardware vs software.

    Topic("mixing_basics", "Mixing — Balancing Sounds in 3D Space",
          "Music", [3], [8, 9], 3, 5,
          ["effects_dynamic_processing", "signal_chain"],
          ["music production", "mixing", "panning", "levels", "frequency",
           "stereo field", "EQ", "compression", "arrangement", "balance"]),
    # The three dimensions of a mix: volume (up/down), pan (left/right),
    # frequency (front/back — high frequencies feel closer).
    # Why you EQ different instruments to occupy different frequency ranges.
    # Why the kick and bass need to share the low end carefully.
    # Listening on different systems: headphones vs speakers vs phone speaker.

    Topic("mastering_concepts", "Mastering — The Final Step Before Release",
          "Music", [3], [9], 4, 5,
          ["mixing_basics", "effects_dynamic_processing"],
          ["music production", "mastering", "loudness", "LUFS", "limiting",
           "stereo width", "distribution", "Spotify", "streaming", "final"]),
    # What mastering is (optimising a stereo mix for distribution).
    # Loudness normalisation: why Spotify sets everything to -14 LUFS and what
    # that did to the loudness war.
    # The limiter: the final brick wall that stops clipping on playback.
    # Stereo width and how to check mono compatibility.

    Topic("daw_workflow", "DAW Workflow — How a Track Is Built in a Digital Audio Workstation",
          "Music", [3], [7, 8, 9], 3, 4,
          ["signal_chain", "sampling_basics"],
          ["music production", "DAW", "Ableton", "Logic", "GarageBand", "FL Studio",
           "workflow", "arrangement", "MIDI", "audio", "production"]),
    # What a DAW does: records audio, plays MIDI, hosts plugins, arranges tracks.
    # MIDI vs audio: MIDI is instructions (play note C4 at velocity 80 for 0.5s);
    # audio is recorded sound.
    # The arrangement view: intro, verse, chorus, bridge, outro.
    # Budget options: GarageBand (free on Mac/iPad), LMMS (free, Windows/Linux).

    Topic("music_production_genres", "Genre DNA — How Different Genres Use Production Differently",
          "Music", [3], [8, 9], 4, 5,
          ["daw_workflow", "music_twentieth_century"],
          ["music production", "genres", "hip hop", "electronic", "rock", "jazz",
           "trap", "house", "techno", "drum and bass", "production techniques"]),

    # ==========================================================================
    # INSTRUMENT FAMILIES — How They Work and Why They Sound Different
    # ==========================================================================

    Topic("strings_how_they_work", "Strings — Violin, Cello, Guitar, and How Vibrating Strings Make Sound",
          "Music", [2], [4, 5, 6, 7], 2, 4,
          ["music_physics_sound"],
          ["music", "strings", "violin", "cello", "guitar", "vibration",
           "harmonics", "overtones", "resonance", "orchestral", "how things work"]),
    # A string vibrates — its fundamental frequency gives the pitch, but it also
    # vibrates at 2×, 3×, 4× the frequency (harmonics). Different harmonics give
    # each instrument its timbre. Why a violin and a guitar playing the same note
    # sound different (the body shape, wood type, and bow vs pluck change which
    # harmonics are amplified). The physics of the bow (stick-slip friction).
    # The orchestra: violin family from highest to lowest (violin, viola, cello, bass).
    # Guitar family: nylon-string (classical), steel-string (folk), electric (amplified).

    Topic("strings_playing_techniques", "String Playing Techniques — Bowing, Plucking, and Extended Techniques",
          "Music", [3], [6, 7, 8, 9], 3, 4,
          ["strings_how_they_work"],
          ["music", "strings", "arco", "pizzicato", "col legno", "sul ponticello",
           "harmonics", "tremolo", "vibrato", "techniques", "orchestral", "notation"]),
    # Arco (bowing) vs pizzicato (plucking). Col legno (hit with the bow stick — Holst).
    # Natural and artificial harmonics — producing those ghostly high notes.
    # Sul ponticello (near the bridge) for glassy, eerie tone.
    # Tremolo: rapid back-and-forth bowing for tension.
    # Vibrato: oscillating the finger to vary pitch slightly for warmth and expression.

    Topic("woodwind_how_they_work", "Woodwind — Flute, Clarinet, Oboe, and Making Sound with Air",
          "Music", [2], [4, 5, 6, 7], 2, 4,
          ["music_physics_sound"],
          ["music", "woodwind", "flute", "clarinet", "oboe", "saxophone", "recorder",
           "air column", "reed", "embouchure", "harmonics", "how things work"]),
    # Three mechanisms: edge tone (flute — air splits across an edge, creating turbulence),
    # single reed (clarinet, saxophone — reed vibrates against the mouthpiece),
    # double reed (oboe, bassoon — two reeds vibrate against each other).
    # The air column inside the tube vibrates at different frequencies depending on
    # which holes are covered. Opening a hole shortens the vibrating air column →
    # raises the pitch. Why the clarinet overblows to a twelfth and the flute to an octave.
    # The recorder as the most accessible starting point for understanding all of this.

    Topic("woodwind_extended_techniques", "Woodwind Techniques — Multiphonics, Circular Breathing, and Tonguing",
          "Music", [3], [7, 8, 9], 3, 5,
          ["woodwind_how_they_work"],
          ["music", "woodwind", "multiphonics", "circular breathing", "flutter tongue",
           "extended techniques", "jazz", "contemporary", "advanced"]),
    # Circular breathing: inhaling through the nose while exhaling through the mouth —
    # allows continuous sound. Used by throat singers, didgeridoo players, jazz soloists.
    # Multiphonics: producing two or more simultaneous pitches on a single reed instrument
    # by fingering and embouchure manipulation — creates eerie, complex tones.
    # Flutter tongue: rolling the tongue rapidly while playing — used in Stravinsky.
    # Altissimo register on saxophone: playing above the normal range.

    Topic("brass_how_they_work", "Brass — Trumpet, Trombone, Horn, and Standing Waves in Tubes",
          "Music", [2], [5, 6, 7], 2, 4,
          ["music_physics_sound"],
          ["music", "brass", "trumpet", "trombone", "French horn", "tuba",
           "valve", "slide", "harmonic series", "embouchure", "how things work"]),
    # The player's lips vibrate, setting the air column in the tube vibrating.
    # The harmonic series: a tube can only produce specific pitches naturally —
    # the fundamental and its overtones. Early natural horns could only play these.
    # Valves (trumpet, horn) add extra tubing to change the fundamental pitch.
    # Slide (trombone) continuously varies the tube length.
    # Why brass players warm up by buzzing their lips on the mouthpiece.
    # The harmonic series as the origin of the chord — the first five harmonics
    # naturally spell out a major chord.

    Topic("percussion_how_it_works", "Percussion — Drums, Pitched and Unpitched, and Why Membranes Ring",
          "Music", [2], [3, 4, 5, 6], 1, 4,
          ["music_rhythm_ks1", "music_physics_sound"],
          ["music", "percussion", "drums", "snare", "timpani", "xylophone",
           "vibraphone", "membrane", "resonance", "kit", "tuning", "how things work"]),
    # Two families: pitched (timpani, marimba, vibraphone, xylophone) and unpitched
    # (snare, bass drum, cymbals).
    # How a drum membrane vibrates in 2D — circular standing waves — and why
    # you can tune a drum by tightening the skin.
    # The drum kit as a single player's orchestration of the percussion section.
    # Cymbal acoustics: why cymbals are inharmonic (their complex shape means
    # the overtones don't follow a neat harmonic series — hence the "crash" rather
    # than a clear pitch).
    # Marimba vs xylophone: wood resonator length and bar thickness differences.

    Topic("percussion_drumming_styles", "Drum Techniques — Rudiments, Grooves, and World Drumming",
          "Music", [2, 3], [5, 6, 7, 8], 3, 4,
          ["percussion_how_it_works", "rhythm_advanced"],
          ["music", "drums", "rudiments", "paradiddle", "flam", "groove",
           "jazz drumming", "rock drumming", "African drumming", "Brazilian",
           "polyrhythm", "techniques"]),
    # The 40 drum rudiments — foundational sticking patterns.
    # The paradiddle (RLRR LRLL) and why it's used for fills and transitions.
    # Rock vs jazz kick placement (four-on-the-floor vs more fluid jazz feel).
    # African drumming as ensemble polyrhythm vs Western drumming as timekeeping.
    # Brazilian rhythms: the samba pattern, baião, bossa nova.
    # How trap-style hi-hat patterns evolved from jazz brushwork.

    Topic("voice_as_instrument", "The Voice — How Humans Make Every Sound in Music",
          "Music", [2], [4, 5, 6, 7], 2, 4,
          ["music_physics_sound"],
          ["music", "voice", "vocal cords", "resonance", "register", "chest voice",
           "head voice", "falsetto", "vowels", "formants", "singing", "how things work"]),
    # Vocal cords (folds) vibrate when air passes — the fundamental pitch.
    # Resonating chambers (chest, throat, mouth, nasal) amplify different harmonics —
    # why different vowel sounds have different timbres.
    # Chest voice vs head voice vs falsetto — different vibratory modes.
    # Why singers warm up (the voice is a muscle).
    # Formants: the resonant peaks that let us distinguish vowel sounds even at the
    # same pitch — the acoustic basis of language and singing.
    # Throat singing (Tuvan): producing multiple simultaneous pitches by
    # strongly amplifying a specific overtone through mouth-shaping.

    Topic("orchestra_layout_instruments", "The Orchestra — Its Instruments, Layout, and Why It's Arranged That Way",
          "Music", [2], [5, 6, 7], 2, 3,
          ["strings_how_they_work", "woodwind_how_they_work", "brass_how_they_work",
           "percussion_how_it_works"],
          ["music", "orchestra", "layout", "sections", "conductor", "strings",
           "woodwind", "brass", "percussion", "balance", "acoustics"]),
    # Why strings sit at the front (they project forward best from that position).
    # Why the conductor faces the orchestra (cuing entries).
    # How the layout evolved over time (the classical orchestra is smaller than
    # the Romantic orchestra).
    # The balance problem: a single horn player can easily drown out twelve violinists
    # at full volume — how orchestration manages this.
]


# ---------------------------------------------------------------------------
# Performing Arts — Dance, Drama, and Movement
# ---------------------------------------------------------------------------

_PERFORMING_ARTS = [
    Topic("dance_styles_history", "Dance Styles Through History — From Court Dance to Street",
          "Performing Arts", [2, 3], [5, 6, 7, 8, 9], 2, 4, [],
          ["dance", "ballet", "jazz dance", "hip hop dance", "contemporary",
           "breakdancing", "history", "culture", "performing arts"]),
    Topic("ballet_basics", "Ballet — Technique, Vocabulary, and Its Classical Tradition",
          "Performing Arts", [2], [4, 5, 6, 7], 2, 3,
          ["dance_styles_history"],
          ["ballet", "classical dance", "positions", "vocabulary", "Swan Lake",
           "Nutcracker", "Tchaikovsky", "performing arts"]),
    Topic("contemporary_dance", "Contemporary Dance — Exploring Movement and Expression",
          "Performing Arts", [2, 3], [6, 7, 8, 9], 3, 5,
          ["dance_styles_history"],
          ["contemporary dance", "modern dance", "improvisation", "Martha Graham",
           "expression", "choreography", "performing arts"]),
    Topic("hip_hop_dance", "Hip Hop Dance — Breaking, Popping, Locking, and Freestyle",
          "Performing Arts", [2, 3], [5, 6, 7, 8, 9], 2, 4,
          ["dance_styles_history", "music_twentieth_century"],
          ["hip hop", "breakdancing", "b-boy", "popping", "locking", "freestyle",
           "culture", "performing arts", "street dance"]),
    Topic("dance_choreography", "Choreography — How Dances Are Designed and Structured",
          "Performing Arts", [3], [7, 8, 9], 4, 6,
          ["dance_styles_history"],
          ["choreography", "dance", "structure", "motif", "development",
           "space", "time", "dynamics", "performing arts", "creative"]),
    Topic("drama_improv", "Improvisation — Making Theatre Without a Script",
          "Performing Arts", [2], [3, 4, 5, 6, 7], 2, 4, [],
          ["drama", "improvisation", "yes and", "theatre games", "comedy",
           "confidence", "performing arts", "social skills"]),
    Topic("drama_characterisation", "Characterisation — How to Be Someone Else Believably",
          "Performing Arts", [2, 3], [5, 6, 7, 8], 3, 5,
          ["drama_improv"],
          ["drama", "character", "Stanislavski", "method acting", "emotion memory",
           "physicality", "voice", "performing arts"]),
    Topic("theatre_history", "The Story of Theatre — From Ancient Greece to the West End",
          "Performing Arts", [2, 3], [6, 7, 8], 3, 4, [],
          ["theatre", "history", "Greek theatre", "Shakespeare", "commedia dell arte",
           "Brecht", "musical theatre", "performing arts"]),
    Topic("stagecraft", "Stagecraft — Sets, Lighting, Sound, and How Theatre Is Made",
          "Performing Arts", [3], [7, 8, 9], 3, 4, ["theatre_history"],
          ["stagecraft", "set design", "lighting", "sound design", "stage management",
           "production", "performing arts", "how things work"]),
    Topic("musical_theatre", "Musical Theatre — Song, Dance, and Story Combined",
          "Performing Arts", [2, 3], [6, 7, 8, 9], 2, 4,
          ["theatre_history", "music_composition_songwriting"],
          ["musical theatre", "Broadway", "West End", "Sondheim", "Rodgers Hammerstein",
           "Hamilton", "story", "music", "performing arts"]),
]


# ---------------------------------------------------------------------------
# Sport, Physical Training, and the Body
# ---------------------------------------------------------------------------

_SPORT = [

    # --- Sport Theory and Tactics ---
    Topic("sport_how_to_learn", "How to Learn a Sport — Deliberate Practice and Skill Acquisition",
          "Sport", [2, 3], [5, 6, 7, 8, 9], 3, 4, ["growth_mindset"],
          ["sport", "deliberate practice", "skill", "learning", "feedback",
           "motor learning", "training", "improvement"]),
    Topic("football_tactics_basics", "Football Tactics — Formations, Roles, and Pressing",
          "Sport", [2, 3], [5, 6, 7, 8, 9], 2, 5,
          ["teamwork_collaboration"],
          ["football", "tactics", "4-4-2", "4-3-3", "pressing", "formation",
           "position", "strategy", "coaching", "sport"]),
    Topic("football_tactics_advanced", "Advanced Football Tactics — High Press, Gegenpressing, and Pep's Positional Play",
          "Sport", [3], [8, 9], 4, 6,
          ["football_tactics_basics"],
          ["football", "tactics", "gegenpressing", "positional play", "Guardiola",
           "Klopp", "tiki-taka", "transitions", "advanced", "coaching"]),
    Topic("sport_rules_major", "Rules of the Game — Football, Cricket, Rugby, Tennis, and Athletics",
          "Sport", [1, 2], [2, 3, 4, 5, 6, 7], 1, 3, [],
          ["sport", "rules", "football", "cricket", "rugby", "tennis",
           "athletics", "fair play", "offside", "LBW"]),
    Topic("sport_coaching_principles", "Coaching — How to Help Others Improve",
          "Sport", [3], [7, 8, 9], 4, 5,
          ["sport_how_to_learn", "leadership_basics"],
          ["coaching", "feedback", "sport", "motivation", "drills",
           "session planning", "communication", "leadership"]),
    Topic("sport_drills_design", "Designing Drills — How Coaches Build Skills Progressively",
          "Sport", [3], [8, 9], 4, 5,
          ["sport_coaching_principles"],
          ["drills", "coaching", "progression", "sport", "skill building",
           "overload", "practice", "design"]),
    Topic("sports_psychology", "Sports Psychology — Mind, Performance, and Pressure",
          "Sport", [3], [7, 8, 9], 4, 5,
          ["growth_mindset", "emotional_regulation"],
          ["sports psychology", "performance", "anxiety", "flow", "confidence",
           "visualisation", "choking", "sport", "mental skills"]),
    Topic("olympic_history", "The Olympics — History, Politics, and the Meaning of Competition",
          "Sport", [2, 3], [5, 6, 7, 8], 2, 5,
          ["ancient_greece"],
          ["Olympics", "history", "politics", "sport", "Jesse Owens",
           "Mexico 1968", "Munich 1972", "fair play", "doping"]),

    # --- Martial Arts ---
    Topic("martial_arts_overview", "Martial Arts — Origins, Philosophy, and the Major Traditions",
          "Sport", [2, 3], [5, 6, 7, 8, 9], 2, 4, [],
          ["martial arts", "judo", "karate", "kung fu", "Brazilian jiu-jitsu",
           "boxing", "philosophy", "discipline", "self-defence", "history"]),
    Topic("martial_arts_striking", "Striking Arts — Boxing, Muay Thai, Karate, and the Science of Impact",
          "Sport", [3], [7, 8, 9], 3, 5,
          ["martial_arts_overview", "forces_motion_ks3"],
          ["boxing", "Muay Thai", "karate", "striking", "footwork", "distance",
           "physics", "force", "sport", "self-defence"]),
    Topic("martial_arts_grappling", "Grappling Arts — Judo, Wrestling, and Brazilian Jiu-Jitsu",
          "Sport", [3], [7, 8, 9], 3, 5,
          ["martial_arts_overview"],
          ["judo", "wrestling", "Brazilian jiu-jitsu", "BJJ", "throws",
           "ground fighting", "leverage", "sport", "self-defence", "physics"]),
    Topic("self_defence_awareness", "Self-Defence — Awareness, De-escalation, and Knowing When to Leave",
          "Sport", [2, 3], [6, 7, 8, 9], 3, 5,
          ["martial_arts_overview", "emotional_regulation"],
          ["self-defence", "awareness", "de-escalation", "safety", "martial arts",
           "boundaries", "sport", "real world", "confidence"]),

    # --- Physical Training and Health ---
    Topic("fitness_components", "Fitness Components — Strength, Endurance, Flexibility, and Speed",
          "Sport", [2], [5, 6, 7], 2, 3, [],
          ["fitness", "strength", "endurance", "flexibility", "speed",
           "agility", "coordination", "health", "sport", "training"]),
    Topic("training_principles", "Training Principles — Progressive Overload, Rest, and Adaptation",
          "Sport", [3], [7, 8, 9], 3, 5,
          ["fitness_components", "human_body_ks2"],
          ["training", "progressive overload", "SAID principle", "supercompensation",
           "rest", "recovery", "adaptation", "sport", "strength training"]),
    Topic("weight_training_basics", "Weight Training — How Lifting Makes You Stronger",
          "Sport", [3], [8, 9], 3, 5,
          ["training_principles", "human_body_ks2"],
          ["weight training", "strength", "hypertrophy", "reps", "sets",
           "compound lifts", "squat", "deadlift", "bench press", "sport", "health"]),
    Topic("yoga_movement", "Yoga — Breath, Movement, and the Mind-Body Connection",
          "Sport", [2, 3], [6, 7, 8, 9], 2, 4, [],
          ["yoga", "flexibility", "breath", "mindfulness", "movement",
           "balance", "wellbeing", "sport", "health", "mental health"]),
    Topic("sports_nutrition", "Sports Nutrition — What to Eat and When for Performance",
          "Sport", [3], [7, 8, 9], 3, 5,
          ["nutrition_food_science", "training_principles"],
          ["nutrition", "sport", "carbohydrates", "protein", "fat", "hydration",
           "timing", "energy", "performance", "health"]),
    Topic("supplements_evidence", "Supplements — What the Evidence Actually Says",
          "Sport", [3], [8, 9], 4, 5,
          ["sports_nutrition", "peer_review_consensus"],
          ["supplements", "protein powder", "creatine", "caffeine", "evidence",
           "sport", "health", "critical thinking", "marketing", "placebo"]),
    Topic("recovery_sleep_sport", "Recovery — Why Rest Is Part of Training",
          "Sport", [3], [7, 8, 9], 3, 4,
          ["training_principles", "sleep_and_the_brain"],
          ["recovery", "sleep", "DOMS", "active recovery", "nutrition",
           "sport", "training", "health", "adaptation"]),
    Topic("sports_biomechanics", "Sports Biomechanics — The Physics of Movement",
          "Sport", [3], [8, 9], 4, 5,
          ["forces_motion_ks3", "fitness_components"],
          ["biomechanics", "sport", "forces", "lever", "torque", "efficiency",
           "technique", "physics", "injury prevention", "movement"]),
]


# ---------------------------------------------------------------------------
# Sports Medicine and Exercise Science — University-Level Topics
# Made accessible from age 12+ for any child who wants to go deeper.
# Design principle: no ceiling. A curious child should be able to follow
# any interest as far as it goes — up to and including the content of a
# first-year BSc Sports Science or Sports Medicine course — without
# hitting an artificial age wall or being told "that's for university."
# The stigma of higher education is the idea that deep knowledge
# requires institutional permission. It doesn't. If you want to understand
# why your hamstring keeps tearing, the anatomy, histology, biomechanics,
# and rehabilitation science are all accessible through conversation.
# ---------------------------------------------------------------------------

_SPORTS_MEDICINE = [

    # --- Anatomy and Musculoskeletal System ---
    Topic("skeletal_system_sport", "The Skeletal System — Bones, Joints, and Movement",
          "Sports Medicine", [2, 3], [6, 7, 8, 9], 3, 5,
          ["human_body_ks2"],
          ["anatomy", "bones", "joints", "skeleton", "cartilage", "ligament",
           "sport", "injury", "sports medicine", "university level"]),
    Topic("muscular_system", "The Muscular System — Muscles, Fibres, and Contraction",
          "Sports Medicine", [3], [7, 8, 9], 3, 5,
          ["human_body_ks2", "cells_ks3"],
          ["anatomy", "muscles", "muscle fibres", "slow twitch", "fast twitch",
           "contraction", "sarcomere", "sport", "sports medicine", "university level"]),
    Topic("muscle_fibre_types", "Muscle Fibre Types — Slow vs Fast Twitch and Training Adaptation",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["muscular_system", "training_principles"],
          ["muscle fibres", "Type I", "Type II", "slow twitch", "fast twitch",
           "endurance", "power", "training", "adaptation", "sports medicine"]),
    Topic("connective_tissue", "Tendons, Ligaments, and Cartilage — The Connective Tissues",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["skeletal_system_sport", "muscular_system"],
          ["tendons", "ligaments", "cartilage", "collagen", "connective tissue",
           "injury", "ACL", "Achilles", "sports medicine", "anatomy"]),
    Topic("joint_mechanics", "Joint Mechanics — Types of Joints and How They Move",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["skeletal_system_sport", "sports_biomechanics"],
          ["joints", "ball and socket", "hinge", "pivot", "range of motion",
           "synovial fluid", "biomechanics", "sport", "sports medicine", "anatomy"]),

    # --- Physiology ---
    Topic("cardiovascular_physiology", "The Heart and Exercise — Cardiac Output, VO2 max, and Adaptation",
          "Sports Medicine", [3], [7, 8, 9], 3, 5,
          ["human_body_ks2", "exercise_mental_health"],
          ["cardiovascular", "heart rate", "stroke volume", "cardiac output",
           "VO2 max", "aerobic", "adaptation", "sport", "sports medicine", "physiology"]),
    Topic("respiratory_physiology", "The Lungs and Exercise — Oxygen Transport and the Ventilatory System",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["cardiovascular_physiology"],
          ["lungs", "oxygen", "CO2", "breathing", "tidal volume",
           "respiratory rate", "altitude", "sport", "sports medicine", "physiology"]),
    Topic("energy_systems", "Energy Systems — ATP, Anaerobic, and Aerobic Pathways",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["cardiovascular_physiology", "nutrition_food_science"],
          ["energy systems", "ATP", "creatine phosphate", "glycolysis",
           "aerobic", "anaerobic", "lactate", "sport", "sports medicine", "physiology"]),
    Topic("thermoregulation", "Thermoregulation — How the Body Controls Temperature During Exercise",
          "Sports Medicine", [3], [8, 9], 3, 5,
          ["human_body_ks2", "heat_thermal_energy"],
          ["thermoregulation", "sweating", "heat stroke", "hypothermia",
           "hydration", "core temperature", "sport", "sports medicine", "physiology"]),
    Topic("hormones_exercise", "Hormones and Exercise — Cortisol, Testosterone, and Adrenaline",
          "Sports Medicine", [3], [9], 4, 5,
          ["nervous_system", "energy_systems"],
          ["hormones", "cortisol", "adrenaline", "testosterone", "endorphins",
           "stress response", "sport", "sports medicine", "physiology", "endocrinology"]),

    # --- Injury — Mechanisms and Classification ---
    Topic("injury_types", "Types of Sports Injury — Acute vs Chronic, Sprains vs Strains",
          "Sports Medicine", [3], [7, 8, 9], 3, 4,
          ["connective_tissue", "muscular_system"],
          ["injury", "sprain", "strain", "fracture", "contusion", "acute",
           "chronic", "overuse", "sport", "sports medicine", "first aid"]),
    Topic("common_injuries_lower_limb", "Lower Limb Injuries — Knee, Ankle, and Hamstring",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["injury_types", "joint_mechanics"],
          ["knee", "ACL", "MCL", "meniscus", "ankle sprain", "hamstring",
           "shin splints", "Achilles tendinopathy", "sport", "sports medicine"]),
    Topic("common_injuries_upper_limb", "Upper Limb and Back Injuries — Shoulder, Elbow, and Spine",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["injury_types", "joint_mechanics"],
          ["shoulder", "rotator cuff", "SLAP tear", "tennis elbow",
           "back pain", "disc herniation", "sport", "sports medicine", "anatomy"]),
    Topic("concussion_head_injury", "Concussion — Brain Injury in Sport and Return-to-Play Protocols",
          "Sports Medicine", [3], [8, 9], 4, 6,
          ["nervous_system", "injury_types"],
          ["concussion", "traumatic brain injury", "CTE", "return to play",
           "sport", "safety", "sports medicine", "neuroscience", "ethics"]),
    Topic("overtraining_syndrome", "Overtraining — When More Training Makes You Worse",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["training_principles", "recovery_sleep_sport"],
          ["overtraining", "fatigue", "performance decline", "burnout",
           "recovery", "sport", "sports medicine", "physiology"]),

    # --- Treatment and Rehabilitation ---
    Topic("rice_police_protocol", "PRICE/POLICE — First Response to Acute Injury",
          "Sports Medicine", [2, 3], [6, 7, 8, 9], 2, 3,
          ["injury_types", "first_aid_cpr_choking"],
          ["PRICE", "POLICE", "ice", "compression", "elevation", "load",
           "acute injury", "first aid", "sport", "sports medicine"]),
    Topic("inflammation_healing", "Inflammation and Tissue Healing — The Four Stages",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["immune_system", "injury_types"],
          ["inflammation", "healing", "tissue repair", "collagen remodelling",
           "haematoma", "fibrosis", "sport", "sports medicine", "physiology"]),
    Topic("rehabilitation_principles", "Rehabilitation — How Injured Athletes Get Back to Sport",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["inflammation_healing", "training_principles"],
          ["rehabilitation", "physiotherapy", "progressive loading",
           "return to sport", "function", "sport", "sports medicine", "recovery"]),
    Topic("physiotherapy_massage", "Manual Therapy — Physiotherapy, Massage, and Soft Tissue Work",
          "Sports Medicine", [3], [9], 4, 5,
          ["rehabilitation_principles", "muscular_system"],
          ["physiotherapy", "massage", "soft tissue", "mobilisation",
           "manipulation", "trigger points", "sport", "sports medicine"]),
    Topic("taping_bracing", "Taping and Bracing — Supporting Joints in Sport",
          "Sports Medicine", [3], [8, 9], 3, 4,
          ["injury_types", "joint_mechanics"],
          ["taping", "strapping", "bracing", "kinesiology tape", "support",
           "proprioception", "sport", "sports medicine", "prevention"]),

    # --- Performance and Prevention ---
    Topic("warm_up_cool_down", "Warm-Up and Cool-Down — The Physiology Behind the Ritual",
          "Sports Medicine", [2, 3], [6, 7, 8, 9], 2, 4,
          ["muscular_system", "cardiovascular_physiology"],
          ["warm up", "cool down", "flexibility", "injury prevention",
           "performance", "sport", "sports medicine", "physiology"]),
    Topic("flexibility_stretching", "Flexibility and Stretching — Static, Dynamic, and PNF",
          "Sports Medicine", [3], [7, 8, 9], 3, 4,
          ["muscular_system", "joint_mechanics"],
          ["flexibility", "stretching", "static stretch", "dynamic stretch",
           "PNF", "range of motion", "injury prevention", "sport", "sports medicine"]),
    Topic("strength_conditioning", "Strength and Conditioning — Programming for Athletes",
          "Sports Medicine", [3], [8, 9], 4, 6,
          ["weight_training_basics", "training_principles", "energy_systems"],
          ["strength and conditioning", "periodisation", "S&C", "programming",
           "power", "speed", "agility", "sport", "sports medicine", "university level"]),
    Topic("periodisation", "Periodisation — Planning a Season of Training",
          "Sports Medicine", [3], [9], 4, 6,
          ["strength_conditioning", "overtraining_syndrome"],
          ["periodisation", "macrocycle", "mesocycle", "microcycle",
           "peaking", "tapering", "sport", "sports medicine", "university level"]),
    Topic("sports_nutrition_science", "Sports Nutrition Science — Macros, Timing, and the Evidence",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["sports_nutrition", "energy_systems"],
          ["sports nutrition", "macronutrients", "carbohydrate loading",
           "protein synthesis", "fuelling", "hydration", "sport", "university level"]),
    Topic("doping_anti_doping", "Doping — Performance-Enhancing Drugs and Why They're Banned",
          "Sports Medicine", [3], [8, 9], 4, 6,
          ["hormones_exercise", "supplements_evidence"],
          ["doping", "steroids", "EPO", "WADA", "USADA", "ethics", "sport",
           "sports medicine", "fairness", "health", "critical thinking"]),

    # --- Psychology and Mental Performance ---
    Topic("goal_setting_sport", "Goal Setting in Sport — SMART Goals and Self-Determination",
          "Sports Medicine", [3], [7, 8, 9], 3, 4,
          ["sports_psychology", "self_awareness_strengths"],
          ["goal setting", "SMART", "motivation", "self-determination",
           "sport", "sports medicine", "psychology", "performance"]),
    Topic("mental_imagery_sport", "Mental Imagery and Visualisation — Practising Without Moving",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["sports_psychology"],
          ["mental imagery", "visualisation", "internal imagery", "external imagery",
           "motor learning", "sport", "sports medicine", "psychology"]),
    Topic("team_dynamics_sport", "Team Dynamics — Cohesion, Roles, and Group Performance",
          "Sports Medicine", [3], [8, 9], 4, 5,
          ["sports_psychology", "teamwork_collaboration"],
          ["team dynamics", "cohesion", "social loafing", "group norms",
           "leadership", "sport", "sports medicine", "psychology", "social"]),
]


# ---------------------------------------------------------------------------
# Model Progressions — "Lies to Children" Unlocked by Mastery
#
# Each topic here is a Level 2 or 3 refinement of a simpler model taught
# earlier. The simpler model is *correct enough* to be useful — it's not
# wrong, it's incomplete. When a child has mastered the prerequisite deeply
# (bloom_target reached), the tutor introduces the correction:
# "Remember how we said X? That's a good model, and it works for most
# purposes. Here's the fuller picture..."
#
# The supersedes field points to the topic being refined.
# This list is not exhaustive — it seeds the pattern. Tutors should
# spontaneously offer refinements when a child asks "but wait, why?"
# after mastering a simplified model.
# ---------------------------------------------------------------------------

_MODEL_PROGRESSIONS = [

    # --- Physics ---
    Topic("atom_bohr_to_quantum", "From the Bohr Atom to Quantum Mechanics",
          "Science", [3], [9], 4, 6,
          ["particle_model", "periodic_table"],
          ["quantum mechanics", "electron orbitals", "probability cloud",
           "Schrödinger", "Bohr model", "atomic structure", "physics", "refined model"],
          model_level=2, supersedes="particle_model",
          accelerated_ok=False),
    # The Bohr model (electrons orbit like planets) is useful but wrong.
    # Electrons exist in probability clouds described by wave functions.
    # You can't know both position and momentum (Heisenberg uncertainty).
    # The periodic table's structure *requires* quantum mechanics to explain
    # why elements in the same group have similar properties.

    Topic("newtonian_to_relativity", "From Newton's Gravity to Einstein's Spacetime",
          "Science", [3], [9], 5, 6,
          ["forces_motion_ks3"],
          ["general relativity", "spacetime", "curved spacetime", "GPS",
           "gravity waves", "Newton", "Einstein", "physics", "refined model"],
          model_level=2, supersedes="forces_motion_ks3",
          accelerated_ok=False),
    # Newtonian gravity works for everyday speeds and masses.
    # At high velocities or near massive objects, spacetime curves — that
    # IS gravity, not a force acting at a distance.
    # GPS satellites require relativistic corrections to work.
    # Gravitational waves: ripples in spacetime detected by LIGO in 2015.

    Topic("light_wave_particle_duality", "Light Is Both a Wave and a Particle — Wave-Particle Duality",
          "Science", [3], [9], 4, 6,
          ["waves_ks3", "light_shadows"],
          ["wave-particle duality", "photon", "double slit", "quantum",
           "photoelectric effect", "Einstein", "physics", "refined model"],
          model_level=2, supersedes="waves_ks3"),
    # Light behaves as a wave (diffraction, interference) AND as a particle
    # (photoelectric effect — Einstein's Nobel prize). The double-slit
    # experiment: a single photon passes through both slits simultaneously
    # and interferes with itself. Observation collapses the wave function.

    Topic("classical_to_statistical_thermodynamics", "From Heat Transfer to Statistical Mechanics",
          "Science", [3], [9], 5, 6,
          ["heat_thermal_energy", "particle_model"],
          ["thermodynamics", "entropy", "statistical mechanics", "Boltzmann",
           "second law", "disorder", "physics", "refined model"],
          model_level=2, supersedes="heat_thermal_energy"),
    # Heat transfer rules (conduction, convection, radiation) are useful
    # engineering approximations. The deeper picture: temperature IS the
    # average kinetic energy of particles. Entropy is a statistical concept —
    # disorder increases not because of a rule, but because there are far
    # more disordered states than ordered ones.

    # --- Chemistry ---
    Topic("combustion_to_redox", "From Burning to Redox — Electron Transfer Is Everything",
          "Science", [3], [8, 9], 4, 5,
          ["oxidation_combustion", "chemical_reactions"],
          ["redox", "oxidation", "reduction", "electron transfer", "electrochemistry",
           "half equations", "chemistry", "refined model"],
          model_level=2, supersedes="oxidation_combustion"),
    # "Burning" is a useful first model. The deeper picture: oxidation is
    # electron loss, reduction is electron gain (OIL RIG). Every combustion
    # reaction is a redox reaction. This framework unifies combustion,
    # corrosion, photosynthesis, cellular respiration, and batteries.

    Topic("acid_base_to_proton_transfer", "From pH to Brønsted-Lowry Acid-Base Theory",
          "Science", [3], [9], 4, 5,
          ["acids_bases_ph"],
          ["Brønsted-Lowry", "proton transfer", "conjugate acid", "conjugate base",
           "buffer", "chemistry", "refined model"],
          model_level=2, supersedes="acids_bases_ph"),
    # pH and H⁺/OH⁻ ions is the Level 1 model. Brønsted-Lowry: an acid is
    # a proton donor, a base is a proton acceptor. This explains why ammonia
    # (no OH⁻) is a base, and why CO2 dissolved in water is acidic.
    # Buffer chemistry: why blood maintains pH 7.4 despite metabolic acids.

    # --- Biology ---
    Topic("cells_to_molecular_biology", "From Cells to Molecular Biology — DNA, Proteins, and Gene Expression",
          "Science", [3], [9], 4, 6,
          ["cells_ks3", "genetics_ks3"],
          ["molecular biology", "transcription", "translation", "mRNA",
           "protein synthesis", "gene expression", "epigenetics", "refined model"],
          model_level=2, supersedes="cells_ks3",
          accelerated_ok=False),
    # The cell as a bag of chemicals with a nucleus is Level 1.
    # Level 2: DNA → RNA → protein (the central dogma). Transcription
    # (DNA copied to mRNA in the nucleus) → translation (ribosomes read
    # mRNA and build proteins). Gene expression is regulated — not all
    # genes are active in all cells. Epigenetics: gene expression can be
    # changed by environment without changing the DNA sequence.

    Topic("evolution_to_evo_devo", "From Natural Selection to Evolutionary Developmental Biology",
          "Science", [3], [9], 5, 6,
          ["evolution_adaptation", "genetics_ks3"],
          ["evo-devo", "Hox genes", "regulatory genes", "development",
           "body plans", "Cambrian explosion", "evolution", "refined model"],
          model_level=2, supersedes="evolution_adaptation"),
    # Natural selection + variation + inheritance is the Level 1 model.
    # Evo-devo explains how large morphological changes can arise quickly:
    # Hox genes (master regulatory genes) control body plan. A single
    # mutation in a Hox gene can add or remove a body segment. This explains
    # the Cambrian explosion — not slow accumulation but rapid regulatory change.

    Topic("food_chains_to_ecosystem_dynamics", "From Food Chains to Ecosystem Dynamics and Tipping Points",
          "Science", [3], [8, 9], 4, 6,
          ["food_webs_energy_flow", "ecosystems_ks3"],
          ["ecosystem dynamics", "tipping points", "regime shifts", "resilience",
           "keystone species", "alternative stable states", "ecology", "refined model"],
          model_level=2, supersedes="food_webs_energy_flow"),
    # Food chains and food webs are useful simplifications. The deeper model:
    # ecosystems have non-linear dynamics. Small changes can push a system
    # past a tipping point into a completely different stable state
    # (regime shift). Kelp forest ↔ urchin barren. Coral reef ↔ algae mat.
    # Hysteresis: it takes more effort to restore a system than it took to
    # degrade it. This is the science behind why climate change is so dangerous.

    # --- Maths ---
    Topic("euclidean_to_non_euclidean", "Beyond Flat Space — Non-Euclidean Geometry",
          "Maths", [3], [9], 4, 6,
          ["geometry_ks2", "pythagoras_theorem"],
          ["non-Euclidean geometry", "spherical geometry", "hyperbolic geometry",
           "parallel postulate", "Riemann", "spacetime", "maths", "refined model"],
          model_level=2, supersedes="geometry_ks2"),
    # Euclidean geometry (flat plane) is the Level 1 model. On a sphere,
    # the angles of a triangle add up to MORE than 180°. Parallel lines
    # meet (all lines of longitude meet at the poles). Non-Euclidean geometry
    # was thought to be pure abstraction until Einstein used it to describe
    # spacetime. Navigation on Earth requires spherical geometry.

    Topic("statistics_to_bayesian", "From Frequency Statistics to Bayesian Thinking",
          "Maths", [3], [9], 5, 6,
          ["statistics_ks2", "probability_ks3"],
          ["Bayesian statistics", "prior", "posterior", "likelihood",
           "Bayes theorem", "updating beliefs", "maths", "refined model"],
          model_level=2, supersedes="probability_ks3"),
    # Classical statistics: frequency of outcomes in repeated experiments.
    # Bayesian: probability as degree of belief, updated by evidence.
    # Bayes' theorem: how to rationally update your confidence in a hypothesis
    # when you get new information. Direct connection to `how_to_change_your_mind`
    # and to medical diagnosis (false positives, base rate neglect).

    # --- History and Social Science ---
    Topic("great_man_to_structural_history", "From Great Men to Structural Forces — How History Actually Works",
          "History", [3], [8, 9], 5, 6,
          ["story_of_science", "empire_legacy_today"],
          ["historiography", "structural history", "contingency", "great man theory",
           "Annales school", "long run", "history", "refined model"],
          model_level=2, supersedes="history_significant_people"),
    # The Level 1 model: great individuals (Napoleon, Churchill, Gandhi)
    # make history. The Level 2 model: structural forces (climate, disease,
    # geography, economics, technology) create the conditions; individuals
    # act within them. Jared Diamond's Guns, Germs, and Steel argument.
    # The Annales school: history should study long-term patterns, not events.
    # Both models are useful; the tension between them is the discipline.

    Topic("free_market_to_market_failure", "From the Free Market Model to Market Failure and Institutional Economics",
          "Political Systems", [3], [9], 5, 6,
          ["supply_demand_prices", "market_failure_externalities"],
          ["market failure", "externalities", "public goods", "information asymmetry",
           "institutional economics", "behavioural economics", "refined model"],
          model_level=2, supersedes="supply_demand_prices"),
    # Level 1: supply and demand, prices as signals, markets allocate efficiently.
    # Level 2: markets fail systematically — externalities (pollution not priced),
    # public goods (can't be sold), information asymmetry (seller knows more than buyer),
    # behavioural biases (humans aren't rational). The policy debate isn't
    # "markets vs government" but "which market failures are worst and what are
    # the cheapest fixes?"

    # --- Music ---
    Topic("equal_temperament_to_just_intonation", "Why Pianos Are Slightly Out of Tune — Equal Temperament vs Just Intonation",
          "Music", [3], [8, 9], 4, 6,
          ["semitones_tones", "music_physics_sound"],
          ["equal temperament", "just intonation", "Pythagorean tuning",
           "overtone series", "wolf interval", "tuning", "music theory", "refined model"],
          model_level=2, supersedes="semitones_tones"),
    # The Level 1 model: an octave is divided into 12 equal semitones.
    # The Level 2 model: this is a mathematical compromise. Pure intervals
    # (5th = 3:2 frequency ratio) don't stack up perfectly to fill an octave.
    # Equal temperament slightly detunes every interval so you can play in
    # all keys on one instrument. Before 1700, instruments were tuned to
    # different systems that sounded pure in some keys but terrible in others.
    # Bach's Well-Tempered Clavier was written to demonstrate a new tuning
    # system that worked in all keys.
]


# ---------------------------------------------------------------------------
# World Religions and Belief Systems
# Taught as history, culture, and comparative worldviews — not as doctrine.
# The goal is cultural literacy and empathy: a child should understand what
# adherents actually believe, why, and what it means to them — without being
# told what to believe themselves.
# Scope: the six major living traditions with global significance.
# Not included: modern syncretic movements, new religious movements,
# or traditions primarily significant as historical curiosities.
# Approach: "Many people believe X. Here is why they find it meaningful.
# Here is the history of how this tradition developed. Here is what it asks
# of its followers. What questions does it raise for you?"
# ---------------------------------------------------------------------------

_WORLD_RELIGIONS = [

    # --- Overview and Comparison ---
    Topic("world_religions_overview", "The World's Major Religions — Who Believes What and Why",
          "Religion", [2], [5, 6, 7], 2, 4, [],
          ["religion", "world religions", "Christianity", "Islam", "Hinduism",
           "Buddhism", "Judaism", "Sikhism", "belief", "culture", "overview"]),
    Topic("how_religions_spread", "How Religions Spread — Trade, Conquest, and Conversion",
          "Religion", [2, 3], [6, 7, 8], 3, 5,
          ["world_religions_overview", "age_of_exploration"],
          ["religion", "spread", "trade", "missionary", "conversion", "history",
           "Silk Road", "empire", "culture", "how things work"]),
    Topic("religion_and_science", "Religion and Science — Conflict, Dialogue, and What the Question Actually Is",
          "Religion", [3], [8, 9], 4, 6,
          ["world_religions_overview", "scientific_method"],
          ["religion", "science", "conflict thesis", "Galileo", "Darwin",
           "evolution", "cosmology", "philosophy", "critical thinking"]),
    Topic("comparative_ethics", "How Religions Think About Right and Wrong",
          "Religion", [3], [7, 8, 9], 4, 5,
          ["world_religions_overview", "ethics_dilemmas"],
          ["religion", "ethics", "Golden Rule", "karma", "dharma", "sin",
           "commandments", "compassion", "comparison", "moral philosophy"]),
    Topic("religion_and_politics", "Religion and Political Power — Theocracy, Secularism, and the Separation of Church and State",
          "Religion", [3], [8, 9], 4, 6,
          ["world_religions_overview", "history_of_democracy_britain"],
          ["religion", "politics", "theocracy", "secularism", "church and state",
           "Reformation", "Iran", "Israel", "history", "political systems"]),

    # --- Christianity ---
    Topic("christianity_origins", "Christianity — The Life of Jesus, Paul, and the Early Church",
          "Religion", [2], [5, 6, 7], 2, 4, [],
          ["Christianity", "Jesus", "Paul", "early church", "Bible",
           "gospels", "apostles", "history", "religion"]),
    Topic("christianity_history", "Christian History — From Rome to the Reformation to Today",
          "Religion", [2, 3], [6, 7, 8], 3, 5,
          ["christianity_origins", "romans_britain"],
          ["Christianity", "Roman Empire", "Catholic Church", "Reformation",
           "Luther", "Protestant", "history", "religion", "politics"]),
    Topic("christianity_denominations", "Christian Denominations — Catholic, Orthodox, Protestant, and the Differences",
          "Religion", [3], [7, 8, 9], 3, 4,
          ["christianity_history"],
          ["Christianity", "Catholic", "Protestant", "Orthodox", "Anglican",
           "Baptist", "denominations", "history", "religion", "comparison"]),

    # --- Church History as Political History ---
    Topic("church_as_political_power", "The Church as a State — How the Papacy Became a Political Institution",
          "Religion", [3], [7, 8, 9], 4, 6,
          ["christianity_history", "norman_conquest"],
          ["Catholic Church", "papacy", "pope", "papal states", "political power",
           "Constantine", "Donation of Constantine", "Christendom", "history",
           "religion", "politics"]),
    # Constantine's conversion (312 AD) turned a persecuted sect into the
    # Roman Empire's official religion. Within a century, emperors were
    # calling church councils and exiling bishops. The Donation of Constantine
    # (a forged document, exposed by Lorenzo Valla in 1440) was used to
    # justify the Pope's claim to rule central Italy. By the 11th century,
    # the Pope could crown and depose emperors. The Papal States were a
    # physical territory the Pope ruled as a monarch until 1870.
    # The key question: was this a corruption of Christianity, or an
    # inevitable consequence of any institution acquiring wealth and influence?

    Topic("indulgences_simony", "Indulgences, Simony, and the Church as a Business",
          "Religion", [3], [8, 9], 4, 6,
          ["church_as_political_power"],
          ["indulgences", "simony", "Church corruption", "selling salvation",
           "purgatory", "Johann Tetzel", "nepotism", "Reformation",
           "religion", "history", "money", "corruption"]),
    # An indulgence was a certificate reducing time in purgatory, sold for
    # cash. Johann Tetzel's sales pitch: "As soon as the coin in the coffer
    # rings, the soul from purgatory springs." This was one direct cause of
    # Luther's 95 Theses. Simony: selling church offices (bishoprics, priest
    # positions) to the highest bidder — named after Simon Magus who tried
    # to buy the Holy Spirit in Acts 8. Nepotism: popes appointing relatives
    # as cardinals (the word comes from Italian "nipote" — nephew, a
    # euphemism for illegitimate sons). The Borgia popes as the extreme case.
    # This is the Church as a feudal revenue system, not just a spiritual one.

    Topic("crusades_as_geopolitics", "The Crusades — Holy War, Land Grab, and the Politics of Salvation",
          "Religion", [3], [7, 8, 9], 4, 6,
          ["church_as_political_power", "islamic_civilisation_golden_age",
           "norman_conquest"],
          ["Crusades", "Jerusalem", "holy war", "Pope Urban II", "Saladin",
           "Richard I", "sacking of Constantinople", "geopolitics", "religion",
           "history", "violence", "colonialism"]),
    # Pope Urban II launched the First Crusade in 1095 offering full
    # indulgence (cancellation of all sins) to those who fought. The actual
    # motivations: land hunger among younger sons with no inheritance,
    # Byzantine Emperor asking for help against the Seljuk Turks, papal
    # desire to reunite Eastern and Western churches, and genuine religious
    # fervour all at once. The Fourth Crusade (1204) never reached the Holy
    # Land — Crusaders sacked Constantinople, a Christian city, instead.
    # Saladin's recapture of Jerusalem (1187) was more merciful than the
    # Christian capture (1099) in which chroniclers described the streets
    # running with blood. What does this tell us about how religious
    # motivation combines with other interests?

    Topic("inquisition", "The Inquisition — Church Courts, Heresy, and the Machinery of Conformity",
          "Religion", [3], [8, 9], 4, 6,
          ["church_as_political_power", "pattern_authoritarian_rise"],
          ["Inquisition", "heresy", "torture", "Spanish Inquisition", "Cathars",
           "Albigensians", "witchcraft", "confession", "surveillance",
           "religion", "history", "power", "conformity"]),
    # The Inquisition was a formal legal process, not mob violence.
    # The Medieval Inquisition (1184) targeted the Cathars in southern France —
    # a Christian sect the Church declared heretical. The Spanish Inquisition
    # (1478) was run by the Spanish Crown to enforce religious unity after
    # the Reconquista (converting or expelling Jews and Muslims). Torture
    # was permitted but regulated. Execution was carried out by civil
    # authorities (the Church handed over the convicted — "relaxed to the
    # secular arm" — a bureaucratic euphemism). The popular image (nobody
    # expects it) exaggerates the terror; the scholarly debate is about
    # whether it was more or less violent than secular justice of the time.
    # The core question: what does it mean when an institution that claims
    # spiritual authority uses physical coercion?

    Topic("great_schism_east_west", "The Great Schism — When Christianity Split in Two (1054)",
          "Religion", [3], [7, 8, 9], 3, 5,
          ["christianity_history", "church_as_political_power"],
          ["Great Schism", "East-West Schism", "Orthodox", "Catholic",
           "Pope", "Patriarch", "filioque", "Constantinople", "Rome",
           "religion", "history", "politics"]),
    # The split of 1054 had been building for centuries: theological dispute
    # (the filioque — whether the Holy Spirit proceeds "from the Father"
    # or "from the Father and the Son"), political dispute (who has supreme
    # authority — the Pope in Rome or the Patriarch in Constantinople?),
    # cultural divide (Latin West vs Greek East), and the practical reality
    # that Rome and Constantinople had been growing apart for 700 years.
    # The mutual excommunications of 1054 were formally lifted in 1965.

    Topic("avignon_papacy", "The Avignon Papacy — When France Controlled the Church",
          "Religion", [3], [8, 9], 4, 5,
          ["church_as_political_power", "hundred_years_war"],
          ["Avignon", "Avignon papacy", "Babylonian captivity", "French papacy",
           "papal court", "corruption", "Petrarch", "history", "religion",
           "politics", "France"]),
    # From 1309–1377, seven popes lived not in Rome but in Avignon, France,
    # under effective French royal control. Petrarch called it the "Babylonian
    # Captivity of the Church." When the papacy returned to Rome, there were
    # briefly two — then three — simultaneous popes each excommunicating the
    # others (the Western Schism, 1378–1417). The Council of Constance (1414)
    # ended it by deposing all three and electing a new one. This episode
    # permanently damaged the papacy's claim to spiritual independence from
    # political power.

    Topic("reformation_causes", "The Reformation — Why Luther's 95 Theses Changed the World",
          "Religion", [2, 3], [7, 8, 9], 4, 6,
          ["indulgences_simony", "printing_revolution"],
          ["Reformation", "Luther", "95 Theses", "Calvin", "Henry VIII",
           "Protestant", "printing press", "Bible in vernacular", "sola scriptura",
           "religion", "history", "politics", "revolution"]),
    # The Reformation only succeeded where previous reform movements (Wycliffe,
    # Hus) failed because of one technology: the printing press. Luther's
    # 95 Theses were printed and distributed across Germany within weeks.
    # The Reformation was inseparable from political power: German princes
    # who converted to Protestantism could seize Church lands. Henry VIII's
    # "Reformation" in England was explicitly a political act (divorce) that
    # created a national church under royal control. Calvin's Geneva was a
    # theocracy. The Peace of Augsburg (1555): "cuius regio, eius religio"
    # — whoever rules determines the religion of their territory.

    Topic("counter_reformation", "The Counter-Reformation — How the Catholic Church Fought Back",
          "Religion", [3], [8, 9], 4, 5,
          ["reformation_causes"],
          ["Counter-Reformation", "Council of Trent", "Jesuits", "Inquisition",
           "Index Librorum Prohibitorum", "baroque art", "Catholic revival",
           "religion", "history", "politics"]),
    # The Council of Trent (1545–63) defined Catholic doctrine in response
    # to Protestant challenges. The Jesuits (Society of Jesus, founded 1540)
    # became the Church's intellectual and missionary vanguard — establishing
    # universities across Europe and Asia. The Index Librorum Prohibitorum
    # (list of banned books) ran until 1966. The Baroque art movement was
    # partly a Counter-Reformation tool — overwhelming emotional experience
    # to compete with Protestant austerity. The Thirty Years War (1618–48)
    # was the military conclusion: eight million dead, ending with a compromise
    # that permanently fractured Christendom.

    Topic("religion_empire_missions", "Missions and Empire — How Christianity Spread Through Colonialism",
          "Religion", [3], [8, 9], 4, 6,
          ["reformation_causes", "british_empire_expansion",
           "transatlantic_slave_trade"],
          ["missions", "missionaries", "colonialism", "conversion", "forced conversion",
           "cultural destruction", "indigenous", "religion", "empire", "history",
           "ethics", "decolonisation"]),
    # The Spanish Requirement (1513): conquistadors were legally required to
    # read a document to indigenous people (often in Latin, through an interpreter
    # they didn't understand) stating that the Pope had given Spain authority
    # over their lands. If they didn't submit, war was justified. Missions in
    # the Americas combined genuine belief, cultural imperialism, and political
    # control. Residential schools in Canada and Australia (children removed
    # from families to be "civilised") ran into the 20th century.
    # The question isn't whether individual missionaries believed sincerely —
    # many did. The question is what happens when sincere belief is backed
    # by imperial power.

    Topic("liberation_theology", "Liberation Theology — When the Church Sided with the Poor",
          "Religion", [3], [9], 4, 6,
          ["religion_empire_missions", "civil_rights_global"],
          ["liberation theology", "Oscar Romero", "Latin America", "poverty",
           "social justice", "Marxism", "Vatican", "religion", "politics",
           "20th century", "history"]),
    # Liberation theology (1960s-70s, Latin America): God has a "preferential
    # option for the poor." The Church's mission is not otherworldly salvation
    # but earthly justice. Archbishop Oscar Romero of El Salvador spoke against
    # the US-backed military government and was assassinated at the altar in
    # 1980. The Vatican under John Paul II actively suppressed liberation
    # theology, seeing its Marxist analysis as incompatible with Christianity.
    # A genuine theological and political argument, still ongoing.
    # Pope Francis (elected 2013) is the first Latin American pope and has
    # rehabilitated much of liberation theology's language.

    # --- Islam ---
    Topic("islam_origins", "Islam — Muhammad, the Quran, and the First Community",
          "Religion", [2], [5, 6, 7], 2, 4, [],
          ["Islam", "Muhammad", "Quran", "Mecca", "Medina", "Arabia",
           "five pillars", "religion", "history"]),
    Topic("islam_history_civilisation", "Islamic Civilisation — The Golden Age of Science, Art, and Philosophy",
          "Religion", [2, 3], [6, 7, 8], 3, 5,
          ["islam_origins", "ancient_egypt"],
          ["Islam", "Islamic civilisation", "Golden Age", "algebra", "astronomy",
           "medicine", "Baghdad", "Cordoba", "history", "science", "religion"]),
    Topic("islam_sunni_shia", "Sunni and Shia — The Split That Shaped Islam",
          "Religion", [3], [7, 8, 9], 3, 5,
          ["islam_origins"],
          ["Islam", "Sunni", "Shia", "Ali", "succession", "split",
           "history", "religion", "politics", "conflict"]),
    Topic("islam_practice_today", "Islam Today — Salah, Ramadan, Hajj, and What It Means to Be Muslim",
          "Religion", [2, 3], [6, 7, 8], 2, 4,
          ["islam_origins"],
          ["Islam", "five pillars", "Ramadan", "Hajj", "Salah", "Zakat",
           "Shahadah", "practice", "religion", "culture", "daily life"]),

    # --- Judaism ---
    Topic("judaism_origins", "Judaism — Abraham, Moses, and the Covenant",
          "Religion", [2], [5, 6, 7], 2, 4, [],
          ["Judaism", "Abraham", "Moses", "covenant", "Torah", "Exodus",
           "Sinai", "Israel", "religion", "history", "Bible"]),
    Topic("judaism_diaspora_history", "Jewish History — Exile, Diaspora, and Survival",
          "Religion", [2, 3], [6, 7, 8, 9], 3, 5,
          ["judaism_origins", "romans_britain"],
          ["Judaism", "diaspora", "Babylon", "Rome", "persecution", "Holocaust",
           "Israel", "Zionism", "history", "religion", "identity"]),
    Topic("judaism_practice", "Jewish Practice — Shabbat, Torah, and the Jewish Year",
          "Religion", [2, 3], [6, 7, 8], 2, 4,
          ["judaism_origins"],
          ["Judaism", "Shabbat", "Torah", "synagogue", "rabbi", "Passover",
           "Yom Kippur", "bar mitzvah", "practice", "religion", "culture"]),
    Topic("judaism_denominations", "Orthodox, Conservative, and Reform Judaism",
          "Religion", [3], [8, 9], 3, 4,
          ["judaism_practice"],
          ["Judaism", "Orthodox", "Conservative", "Reform", "denominations",
           "modernity", "religion", "identity", "culture"]),

    # --- Hinduism ---
    Topic("hinduism_overview", "Hinduism — The World's Oldest Living Religion",
          "Religion", [2], [5, 6, 7], 2, 4, [],
          ["Hinduism", "Brahman", "dharma", "karma", "moksha", "Vedas",
           "India", "religion", "philosophy", "history"]),
    Topic("hinduism_gods_stories", "Hindu Gods and Stories — Brahma, Vishnu, Shiva, and the Great Epics",
          "Religion", [2, 3], [5, 6, 7, 8], 2, 4,
          ["hinduism_overview"],
          ["Hinduism", "Brahma", "Vishnu", "Shiva", "Devi", "Ramayana",
           "Mahabharata", "Krishna", "myths", "religion", "stories"]),
    Topic("hinduism_philosophy", "Hindu Philosophy — The Upanishads, Atman, and Non-Duality",
          "Religion", [3], [8, 9], 4, 6,
          ["hinduism_overview"],
          ["Hinduism", "Upanishads", "Atman", "Brahman", "Advaita",
           "non-duality", "philosophy", "consciousness", "religion", "university level"]),
    Topic("hinduism_practice", "Hindu Practice — Puja, Festivals, and the Caste System",
          "Religion", [2, 3], [6, 7, 8], 2, 4,
          ["hinduism_overview"],
          ["Hinduism", "puja", "Diwali", "Holi", "caste", "varna",
           "temple", "practice", "religion", "culture", "social"]),

    # --- Buddhism ---
    Topic("buddhism_origins", "Buddhism — Siddhartha Gautama, the Four Noble Truths, and the Eightfold Path",
          "Religion", [2], [5, 6, 7], 2, 4, [],
          ["Buddhism", "Buddha", "Siddhartha", "Four Noble Truths", "Eightfold Path",
           "suffering", "nirvana", "India", "religion", "philosophy"]),
    Topic("buddhism_traditions", "Buddhist Traditions — Theravada, Mahayana, and Zen",
          "Religion", [3], [7, 8, 9], 3, 5,
          ["buddhism_origins"],
          ["Buddhism", "Theravada", "Mahayana", "Zen", "Tibetan Buddhism",
           "bodhisattva", "meditation", "traditions", "religion"]),
    Topic("buddhism_spread_asia", "How Buddhism Spread Across Asia",
          "Religion", [2, 3], [6, 7, 8], 3, 4,
          ["buddhism_origins", "how_religions_spread"],
          ["Buddhism", "Asia", "China", "Japan", "Tibet", "Southeast Asia",
           "spread", "history", "Silk Road", "religion", "culture"]),
    Topic("buddhism_meditation_practice", "Buddhist Practice — Meditation, Mindfulness, and the Sangha",
          "Religion", [2, 3], [6, 7, 8], 2, 4,
          ["buddhism_origins"],
          ["Buddhism", "meditation", "mindfulness", "sangha", "monastery",
           "practice", "religion", "wellbeing", "psychology"]),

    # --- Sikhism ---
    Topic("sikhism_origins", "Sikhism — Guru Nanak, the Ten Gurus, and the Khalsa",
          "Religion", [2], [5, 6, 7], 2, 4, [],
          ["Sikhism", "Guru Nanak", "Ten Gurus", "Khalsa", "Punjab",
           "Guru Granth Sahib", "religion", "history", "India"]),
    Topic("sikhism_practice", "Sikh Practice — The Five Ks, the Gurdwara, and Seva",
          "Religion", [2, 3], [6, 7, 8], 2, 4,
          ["sikhism_origins"],
          ["Sikhism", "Five Ks", "kara", "turban", "gurdwara", "langar",
           "seva", "practice", "religion", "culture", "service"]),
    Topic("sikhism_values", "Sikh Values — Equality, Service, and Standing Against Injustice",
          "Religion", [2, 3], [6, 7, 8, 9], 3, 5,
          ["sikhism_origins"],
          ["Sikhism", "equality", "seva", "justice", "Waheguru",
           "saint-soldier", "values", "religion", "ethics", "social"]),

    # --- Ancient and Extinct Religions ---
    Topic("zoroastrianism", "Zoroastrianism — The Oldest Monotheism and Its Influence on Everything",
          "Religion", [3], [7, 8, 9], 4, 6,
          ["world_religions_overview", "ancient_egypt"],
          ["Zoroastrianism", "Zoroaster", "Zarathustra", "Ahura Mazda", "Ahriman",
           "Persia", "monotheism", "afterlife", "heaven", "hell", "angels",
           "apocalypse", "religion", "history", "influence"]),
    # Possibly the most influential religion you've never heard of.
    # Founded by Zarathustra (Zoroaster) in ancient Persia (~1500-1000 BCE).
    # First religion to teach: one supreme God, cosmic battle between good and evil,
    # individual judgment after death, heaven and hell, a final apocalypse,
    # angels, and a saviour figure. These ideas entered Judaism during the
    # Babylonian exile, and from there into Christianity and Islam.
    # Still practised by Parsis in India and Iran (~100,000 worldwide).

    Topic("ancient_greek_religion", "Ancient Greek Religion — Gods, Myths, and the Sacred",
          "Religion", [2], [5, 6, 7], 2, 4,
          ["ancient_greece", "greek_mythology_olympians"],
          ["Greek religion", "Olympian gods", "sacrifice", "oracle", "Delphi",
           "mystery cults", "afterlife", "Hades", "ancient history", "religion"]),
    # Greek religion wasn't just mythology — it was a living practice.
    # Animal sacrifice, oracles (Delphi), temple rituals, mystery cults
    # (Eleusinian Mysteries promised initiates a better afterlife).
    # The Greeks had no word for "religion" — it was simply how life was lived.
    # Connects Greek mythology to its actual religious function.

    Topic("ancient_egyptian_religion", "Ancient Egyptian Religion — Ra, Osiris, and the Journey After Death",
          "Religion", [2], [4, 5, 6], 2, 4,
          ["ancient_egypt"],
          ["Egyptian religion", "Ra", "Osiris", "Isis", "Horus", "Set",
           "mummification", "Book of the Dead", "afterlife", "pharaoh",
           "religion", "ancient history"]),
    # 3,000 years of continuous religious tradition. The pharaoh as a god.
    # The elaborate afterlife — mummification to preserve the body, the
    # weighing of the heart against a feather (Ma'at), the Field of Reeds.
    # How Egyptian religion influenced Greek mystery cults and early Christianity
    # (Osiris's death and resurrection, the Madonna and child in Isis and Horus).

    Topic("norse_religion", "Norse Religion — Odin, the Nine Worlds, and Ragnarök",
          "Religion", [2], [5, 6, 7], 2, 4,
          ["vikings_saxons", "norse_mythology"],
          ["Norse religion", "Odin", "Thor", "Freya", "Yggdrasil", "Ragnarök",
           "Valhalla", "Norns", "fate", "Viking", "religion", "history", "myths"]),
    # Norse religion was a living belief system, not just entertaining stories.
    # Odin sacrificed his eye for wisdom, hung on the World Tree for knowledge.
    # Fate (the Norns) was central — even the gods would die at Ragnarök.
    # The concept of an honourable death in battle to reach Valhalla shaped
    # Viking culture. How it blended with Christianity in Scandinavia.

    Topic("mesopotamian_religion", "Mesopotamian Religion — The Gods of Babylon and the World's First Stories",
          "Religion", [2, 3], [6, 7, 8], 3, 5,
          ["first_civilisations", "ancient_egypt"],
          ["Mesopotamia", "Babylon", "Sumerian religion", "Gilgamesh", "Enkidu",
           "flood myth", "Marduk", "ziggurat", "religion", "ancient history",
           "myths", "connections"]),
    # The Epic of Gilgamesh (2100 BCE) contains a flood story older than Genesis.
    # Mesopotamian religion gave us the first written myths, the first concept
    # of fate controlled by gods, and many narrative templates (the flood,
    # the hero's journey) that recur across later religions.
    # The seven-day week comes from Babylonian astrology.

    Topic("roman_religion", "Roman Religion — From Jupiter to the Fall of the Gods",
          "Religion", [2, 3], [5, 6, 7, 8], 2, 4,
          ["ancient_greece", "romans_britain"],
          ["Roman religion", "Jupiter", "Mars", "Juno", "Roman gods", "emperor cult",
           "Vestal Virgins", "augury", "syncretism", "Christianity",
           "religion", "ancient history"]),
    # Roman religion was pragmatic — adopt the gods of conquered peoples.
    # The emperor cult (emperors as gods) created the political conflict
    # with Christianity (Christians refused to sacrifice to the emperor).
    # How Rome's religious tolerance eventually broke down and Christianity
    # became the state religion — changing both Rome and Christianity forever.

    Topic("indigenous_spiritual_traditions", "Indigenous Spiritual Traditions — Animism, Dreamtime, and Sacred Land",
          "Religion", [2, 3], [6, 7, 8, 9], 3, 5,
          ["world_religions_overview"],
          ["indigenous", "animism", "Dreamtime", "Aboriginal", "Native American",
           "sacred", "land", "spirit", "oral tradition", "religion", "culture",
           "colonialism", "decolonisation"]),
    # Not a single religion but a cluster of worldviews sharing common features:
    # everything is alive and has spirit (animism), humans are part of nature
    # not above it, sacred knowledge is oral not written, place and land are
    # central to identity and religion. Australian Aboriginal Dreamtime.
    # How colonialism deliberately destroyed indigenous spiritual traditions
    # as a tool of cultural erasure. Why this matters today.

    Topic("religion_extinction_revival", "When Religions Die — and Sometimes Come Back",
          "Religion", [3], [8, 9], 4, 5,
          ["zoroastrianism", "norse_religion"],
          ["religion", "extinction", "revival", "neo-paganism", "Ásatrú",
           "Hellenism", "history", "culture", "identity", "modern"]),
    # Why religions disappear (conquest, conversion, cultural assimilation).
    # Modern revivals: Ásatrú (Norse religion practiced today), Hellenism
    # (worship of Greek gods), neo-druidry. Are these authentic continuations
    # or cultural constructions? What does it mean to revive a dead religion?
]


# ---------------------------------------------------------------------------
# Aerospace, Space, and the Rocket Age
# From the physics of flight to orbital mechanics to the Cold War race.
# Covers: how things fly, how rockets work, how you get to space,
# the military-industrial origins of the space programme, the Soviet
# parallel story, specific missions and vessels, modern era.
# Deliberately broad — connects physics, history, engineering, and
# geopolitics through one of the 20th century's defining threads.
# ---------------------------------------------------------------------------

_AEROSPACE = [

    # ==========================================================================
    # FLIGHT — THE PHYSICS
    # ==========================================================================

    Topic("how_wings_work", "How Wings Work — Lift, Drag, and the Aerofoil",
          "Aerospace", [2], [5, 6, 7], 2, 4,
          ["forces_magnets", "exp_bernoulli_flight"],
          ["flight", "wings", "lift", "drag", "aerofoil", "Bernoulli",
           "angle of attack", "physics", "aerospace"]),
    # The standard "Bernoulli" explanation (air over the top travels further
    # therefore faster therefore lower pressure) is a simplification —
    # it can't fully explain aerobatic flight upside down. The complete
    # explanation combines Bernoulli with Newtonian reaction: the wing
    # deflects air downward, reaction force pushes wing up.
    # Angle of attack: tilt the wing more and you get more lift — until
    # the stall point where flow separates and lift collapses suddenly.

    Topic("wing_types", "Wing Types — Delta, Swept, Variable Geometry, and Flying Wings",
          "Aerospace", [2, 3], [6, 7, 8, 9], 3, 5,
          ["how_wings_work"],
          ["wings", "delta wing", "swept wing", "variable geometry", "flying wing",
           "Concorde", "F-111", "B-2", "aircraft design", "aerospace", "tradeoffs"]),
    # Straight wings: maximum lift at low speed (good for light planes).
    # Swept wings: delay transonic shock waves — every modern jet airliner.
    # Delta wings: strong at supersonic speeds, poor takeoff/landing efficiency
    # — Concorde, Eurofighter, Space Shuttle.
    # Variable geometry (swing-wing): F-111, Tornado — sweep back for speed,
    # extend for landing. Complex and heavy; mostly abandoned.
    # Flying wings: no tail, maximum aerodynamic efficiency — B-2 Spirit.
    # The tradeoff is always the same: high-speed efficiency vs low-speed control.

    Topic("supersonic_transonic", "Going Through the Sound Barrier — Transonic, Supersonic, and Shock Waves",
          "Aerospace", [3], [7, 8, 9], 3, 5,
          ["how_wings_work", "waves_ks3"],
          ["supersonic", "transonic", "sound barrier", "shock wave", "Mach number",
           "Chuck Yeager", "X-1", "sonic boom", "wave drag", "aerospace"]),
    # At Mach ~0.8 (transonic) shock waves form on the wing surface — wave drag
    # increases dramatically. The "sound barrier" was a real engineering problem,
    # not just a speed limit. Chuck Yeager, Bell X-1 (1947) — rocket-powered,
    # dropped from a B-29. Why supersonic flight requires thin, swept, or delta wings.
    # Sonic boom: not just at the moment of breaking — a continuous cone of
    # compressed air follows the aircraft; you hear it as it passes overhead.

    Topic("concorde", "Concorde — The Supersonic Airliner and Why It Died",
          "Aerospace", [3], [7, 8, 9], 3, 5,
          ["supersonic_transonic", "wing_types"],
          ["Concorde", "supersonic", "British Airways", "Air France", "Mach 2",
           "ogival delta", "afterburner", "sonic boom ban", "economics", "aerospace"]),
    # Concorde flew at Mach 2.04 — London to New York in 3.5 hours.
    # The engineering: ogival delta wing, drooping nose for takeoff visibility,
    # four Olympus 593 engines with reheat (afterburner), kinetic heating
    # (the nose reached 127°C — the fuselage expanded 25cm in flight).
    # Why it ended: not the 2000 crash primarily — the economics were always
    # marginal, fuel crisis, supersonic boom ban over land severely limiting
    # routes. The broader lesson: supersonic passenger flight has been tried
    # and found economically difficult every time.

    Topic("hypersonic", "Hypersonic — Mach 5+ and the Return to Atmosphere",
          "Aerospace", [3], [8, 9], 4, 5,
          ["supersonic_transonic"],
          ["hypersonic", "Mach 5", "scramjet", "X-43", "plasma", "heat shield",
           "HGV", "hypersonic glide vehicle", "military", "space re-entry",
           "aerospace"]),
    # Above Mach 5 the air in front of the vehicle can't get out of the way —
    # it's compressed and heated to plasma temperatures.
    # Scramjet (supersonic combustion ramjet): unlike a ramjet, fuel burns in
    # supersonic airflow. The X-43A reached Mach 9.6 (2004). Challenge: you
    # need to reach Mach 4+ before a scramjet works — a rocket gets you there.
    # Military hypersonic glide vehicles (HGVs): launched by missile, glide
    # unpredictably at Mach 20+ — hard to intercept because trajectory changes.
    # The geopolitics: Russia (Avangard), China (DF-17), US all developing these.

    Topic("ramjet_pulsejet", "Ramjets and Pulsejets — Air-Breathing Engines That Have No Moving Parts",
          "Aerospace", [3], [7, 8, 9], 3, 5,
          ["how_engines_work"],
          ["ramjet", "pulsejet", "V-1", "jet engine", "combustion",
           "air-breathing", "SR-71", "aerospace", "how things work"]),
    # A ramjet is simply a tube: ram air in at the front, add fuel, ignite,
    # exhaust at the back. No compressor, no turbine — no moving parts.
    # Only works above ~300mph (you need the ram air pressure).
    # The V-1 flying bomb used a pulsejet — an interrupted combustion cycle
    # producing the characteristic buzz. Children in London learned the
    # silence meant the engine had cut out. SR-71 Blackbird used ramjet mode
    # above Mach 3 — the J58 engines were turbojets that transitioned to
    # ramjet operation at high speed.

    Topic("drones_uav", "Drones and UAVs — From V-1 to Predator to Delivery",
          "Aerospace", [2, 3], [6, 7, 8, 9], 3, 5,
          ["ramjet_pulsejet", "robotics_building"],
          ["drones", "UAV", "unmanned", "V-1", "Predator", "Reaper",
           "DJI", "autonomy", "military", "delivery", "surveillance",
           "aerospace", "ethics"]),
    # The V-1 was the first mass-produced UAV. Modern military drones
    # (Predator, Reaper) are flown by operators in Nevada attacking targets
    # in Afghanistan — the physical and psychological distance changes how
    # war is conducted. Commercial drones (DJI) now outsell military drones
    # by units. The geofencing question: who owns the airspace over your house?
    # Autonomous lethal drones (LAWS) — the ethics of removing a human from
    # the kill decision chain.

    # ==========================================================================
    # ROCKETS — THE PHYSICS AND HISTORY
    # ==========================================================================

    Topic("how_rockets_work", "How Rockets Work — Newton's Third Law in a Tube",
          "Aerospace", [2], [5, 6, 7], 2, 4,
          ["forces_motion_ks3"],
          ["rockets", "thrust", "Newton's third law", "propellant", "exhaust",
           "specific impulse", "rocket equation", "Tsiolkovsky", "aerospace",
           "physics"]),
    # A rocket carries both fuel AND oxidiser — it works in vacuum where
    # there's no air. Thrust = mass flow rate × exhaust velocity.
    # The Tsiolkovsky rocket equation: Δv = ve × ln(m0/mf).
    # The tyranny of the rocket equation: most of a rocket's mass is propellant.
    # To go twice as fast you need much more than twice the fuel.
    # Specific impulse: the efficiency measure of rocket engines.

    Topic("rocket_engine_types", "Rocket Engine Types — Solid, Liquid, and Hybrid",
          "Aerospace", [2, 3], [6, 7, 8, 9], 3, 5,
          ["how_rockets_work", "chemical_reactions"],
          ["rocket engines", "solid rocket", "liquid fuel", "cryogenic",
           "LOX", "kerosene", "hydrogen", "throttle", "restart", "SRB",
           "Merlin", "Raptor", "aerospace"]),
    # Solid: simple, storable, can't be throttled or shut down (SRBs on Shuttle).
    # Liquid: complex plumbing, cryogenic storage, but throttleable and restartable.
    # Kerosene+LOX (RP-1): SpaceX Merlin, Saturn V first stage — high thrust, dense.
    # Hydrogen+LOX: Space Shuttle main engines, SLS — highest Isp, but hydrogen
    # is tricky (boils, embrittles metals, very light so tanks are huge).
    # Methane+LOX: SpaceX Raptor — easier to handle than hydrogen, can be made
    # on Mars (Sabatier process from CO2+H2O). The next generation.
    # Nuclear thermal: uranium heats hydrogen propellant — 2× Isp of chemical,
    # never flown in crewed vehicles but actively being developed.

    Topic("multistage_rockets", "Staging — Why Rockets Drop Their Tanks",
          "Aerospace", [2, 3], [6, 7, 8], 3, 4,
          ["how_rockets_work"],
          ["staging", "multistage", "gravity loss", "delta-v", "mass fraction",
           "Saturn V", "Falcon 9", "staging ring", "aerospace"]),
    # Once propellant is burned, the empty tank is dead weight. Drop it.
    # Each stage is optimised for its regime: high-thrust lower stage,
    # efficient upper stage in vacuum. The Saturn V had three stages.
    # Staging explained why the Apollo mission looked so different at
    # launch vs landing: 3,000 tonnes off the pad, 6 tonnes on the Moon.

    # ==========================================================================
    # GETTING TO SPACE — THE ORBITAL MECHANICS
    # ==========================================================================

    Topic("atmosphere_layers", "The Atmosphere — From Ground to Space",
          "Aerospace", [2], [5, 6, 7], 2, 3,
          ["weather_climate", "earth_space_ks2"],
          ["atmosphere", "troposphere", "stratosphere", "mesosphere",
           "thermosphere", "Kármán line", "100km", "weather balloon",
           "orbital altitude", "space", "aerospace"]),
    # Troposphere (0–12km): weather happens here.
    # Stratosphere (12–50km): Concorde flew here; ozone layer.
    # Mesosphere (50–80km): where meteors burn up.
    # Thermosphere (80–700km): ISS orbits here (~400km). Temperature rises
    # to 2000°C but so few molecules there's almost no heat transfer —
    # you'd freeze, not burn.
    # Kármán line (100km): the conventional boundary of space.
    # Weather balloons reach ~35km (stratosphere) — much lower than "space."

    Topic("orbital_mechanics_basics", "How to Get to Space — Orbit Is Falling Sideways Fast Enough",
          "Aerospace", [2, 3], [6, 7, 8, 9], 3, 5,
          ["atmosphere_layers", "how_rockets_work", "pressure_buoyancy"],
          ["orbit", "orbital velocity", "7.8 km/s", "falling", "circular orbit",
           "ISS", "altitude vs speed", "gravity", "centripetal", "aerospace"]),
    # The key insight: orbit isn't about height, it's about speed.
    # At 7.8 km/s horizontal velocity, the Earth curves away beneath you
    # as fast as you fall — you're in perpetual free fall around the planet.
    # Why you need to go sideways, not just up.
    # Weather balloon vs orbital rocket: the balloon goes high but slowly —
    # it falls straight back down. The rocket goes fast enough to miss the Earth.

    Topic("apogee_perigee_inclination", "Orbital Elements — Apogee, Perigee, Inclination, and Orbital Planes",
          "Aerospace", [3], [7, 8, 9], 3, 5,
          ["orbital_mechanics_basics"],
          ["orbit", "apogee", "perigee", "inclination", "orbital plane",
           "eccentricity", "elliptical orbit", "Kepler", "aerospace"]),
    # Apogee: highest point of an orbit. Perigee: lowest.
    # Circular orbit: apogee = perigee. Elliptical: they differ.
    # Inclination: the angle of the orbital plane to the equator.
    # ISS: 51.6° inclination (allows both US and Russian launch sites to reach it).
    # Polar orbit: 90° — passes over every point on Earth, used for spy/weather satellites.
    # Sun-synchronous: slightly retrograde, always crosses the equator at the same
    # local solar time — ideal for optical imaging satellites.

    Topic("geostationary_lagrange", "Geostationary Orbit, Lagrange Points, and Where to Park a Satellite",
          "Aerospace", [3], [7, 8, 9], 3, 5,
          ["apogee_perigee_inclination"],
          ["geostationary", "GEO", "Clarke orbit", "Lagrange points", "L1", "L2",
           "L4", "L5", "JWST", "SOHO", "communications satellites", "aerospace"]),
    # Geostationary orbit: 35,786km altitude, orbital period exactly 24 hours —
    # satellite appears stationary over one point on Earth. Arthur C. Clarke
    # proposed this in 1945 ("Clarke orbit"). All TV broadcast satellites are here.
    # Limitation: only above the equator; polar regions have poor coverage; high
    # latency (~240ms round trip) too slow for live gaming.
    # Lagrange points: where gravitational forces of two bodies balance.
    # L1 (Earth-Sun): SOHO solar observatory — always faces the Sun.
    # L2 (Earth-Sun, opposite side): JWST — cold, stable, Earth always blocks the Sun.
    # L4 and L5: 60° ahead and behind Earth in its orbit — stable parking spots;
    # the Trojan asteroids cluster here.

    Topic("delta_v_manoeuvres", "Delta-V — The Currency of Space Travel",
          "Aerospace", [3], [8, 9], 4, 6,
          ["orbital_mechanics_basics", "how_rockets_work"],
          ["delta-v", "Hohmann transfer", "orbital manoeuvre", "burn",
           "space travel budget", "Mars", "gravity assist", "slingshot",
           "aerospace", "maths"]),
    # Every orbital manoeuvre costs delta-v — change in velocity.
    # Hohmann transfer: the most efficient way to move between two circular orbits —
    # two burns, one to raise the orbit, one to circularise at the new altitude.
    # Gravity assists (slingshot): steal velocity from a planet.
    # Voyager's grand tour: used Jupiter, Saturn, Uranus, Neptune gravity assists —
    # couldn't have been done any other way given 1970s rocket capability.
    # Going to Mars: ~3.6 km/s from LEO. Going to the Moon: ~3.1 km/s.
    # The counterintuitive result: it costs more delta-v to land on the Sun
    # than to escape the solar system entirely.

    Topic("reentry_heat_shields", "Re-Entry — Why Coming Back is Harder Than Going Up",
          "Aerospace", [3], [7, 8, 9], 3, 5,
          ["orbital_mechanics_basics", "heat_thermal_energy"],
          ["re-entry", "heat shield", "ablative", "plasma", "blackout",
           "Columbia", "angle of attack", "skip re-entry", "aerospace"]),
    # At orbital velocity (7.8 km/s) kinetic energy must be converted to heat.
    # You can't just rocket-brake — not enough propellant. Use the atmosphere.
    # The heat shield doesn't conduct heat away — it ablates (burns off slowly),
    # carrying heat with it. Columbia (2003): damaged leading edge tiles let
    # plasma enter the wing structure. The entry corridor: too steep and the
    # g-forces crush you; too shallow and you skip off the atmosphere like a
    # stone off water.

    # ==========================================================================
    # THE COLD WAR SPACE RACE
    # ==========================================================================

    Topic("ww2_rocket_programme", "V-2 and the German Rocket Programme — How the Space Age Began",
          "Aerospace", [3], [7, 8, 9], 4, 6,
          ["how_rockets_work", "ww2_global_conflict"],
          ["V-2", "Peenemünde", "Wernher von Braun", "forced labour", "Mittelwerk",
           "Operation Paperclip", "ICBM", "Cold War", "aerospace", "history",
           "ethics"]),
    # The V-2 was the first object to reach space (100km+) in 1944.
    # Built at Mittelwerk using concentration camp slave labour — more people
    # died building the V-2 than were killed by it. Wernher von Braun and
    # the German rocket engineers were brought to the US in Operation Paperclip;
    # the Soviets captured different engineers and hardware. Both sides built
    # their ICBM and space programmes on Nazi rocket technology.
    # The ethical question: do the ends (Moon landings) justify the origins?

    Topic("cold_war_icbm_programme", "ICBMs — Ballistic Missiles and the Logic of Nuclear Deterrence",
          "Aerospace", [3], [8, 9], 4, 6,
          ["ww2_rocket_programme", "cold_war_context"],
          ["ICBM", "ballistic missile", "nuclear deterrence", "MAD", "Minuteman",
           "Trident", "silos", "launch-on-warning", "Cold War", "aerospace",
           "geopolitics", "ethics"]),
    # The first ICBMs were simply modified V-2 descendants. By the 1960s
    # the US and USSR each had thousands of nuclear-tipped missiles.
    # MAD (Mutually Assured Destruction): deterrence works because no one
    # can win. Launch-on-warning: missiles detected by radar trigger automatic
    # launch — the system can misidentify a flock of geese (Stanislav Petrov, 1983).
    # The space race was inseparable from the missile race: the same rocket
    # that launched Sputnik could deliver a nuclear warhead to any city on Earth.

    Topic("space_race_origins", "Sputnik to Apollo — How the Cold War Created the Space Age",
          "Aerospace", [2, 3], [6, 7, 8, 9], 3, 5,
          ["cold_war_icbm_programme"],
          ["Sputnik", "Gagarin", "Apollo", "space race", "Kennedy", "Eisenhower",
           "NASA", "Korolev", "Cold War", "aerospace", "history"]),
    # Sputnik (1957) was a propaganda shock to the US — the Soviets could
    # reach space, which meant they could reach New York. NASA was created
    # in 1958 as the civilian answer to Sputnik. Kennedy's 1961 speech was
    # explicitly geopolitical — the Moon as a demonstration of American
    # technological superiority in a war fought with rockets not bullets.
    # The secret on the Soviet side: Sergei Korolev, the "Chief Designer"
    # whose name was classified. He died in 1966 — the Soviet programme
    # never recovered its momentum without him.

    Topic("soviet_space_programme", "The Soviet Space Programme — Firsts, Failures, and the Parallel Story",
          "Aerospace", [3], [7, 8, 9], 4, 5,
          ["space_race_origins"],
          ["Soviet Union", "Korolev", "Gagarin", "Vostok", "Luna", "Venera",
           "Soyuz", "N1", "space station", "Cold War", "aerospace", "history"]),
    # First satellite (Sputnik), first animal (Laika), first human (Gagarin),
    # first woman (Tereshkova), first spacewalk (Leonov), first Moon probe,
    # first soft landing on the Moon, first pictures from Venus surface.
    # The N1 Moon rocket: four consecutive launch failures destroyed the
    # launchpad each time. The Soviet lunar programme was officially denied
    # to exist until the 1990s.
    # Venera probes: the Soviets succeeded where the Americans didn't —
    # landing and surviving on Venus's crushing, 460°C, sulphuric acid atmosphere.
    # Venera 13 (1982) sent back colour photographs before dying after 127 minutes.

    Topic("star_wars_programme", "Star Wars — Reagan's Strategic Defence Initiative",
          "Aerospace", [3], [8, 9], 4, 6,
          ["cold_war_icbm_programme"],
          ["SDI", "Star Wars", "Reagan", "missile defence", "lasers",
           "X-ray laser", "nuclear pumped", "arms race", "Cold War",
           "aerospace", "geopolitics"]),
    # SDI (1983): a proposed system to intercept Soviet missiles with
    # ground- and space-based lasers and particle beams.
    # The physics: hitting a missile with a laser during its ~30-minute flight
    # trajectory is extraordinarily difficult. Most physicists said it was
    # impossible with 1980s technology. The nuclear-pumped X-ray laser
    # (detonate a nuclear bomb, use the X-ray pulse to pump a laser) worked
    # in tests but could only be used once.
    # Strategic effect regardless of feasibility: forced the Soviets to spend
    # heavily on countermeasures — some analysts argue this accelerated Soviet
    # economic collapse.

    # ==========================================================================
    # SPACE STATIONS AND HABITATION
    # ==========================================================================

    Topic("space_stations_history", "Space Stations — Salyut to Mir to the ISS",
          "Aerospace", [2, 3], [6, 7, 8, 9], 2, 4,
          ["orbital_mechanics_basics"],
          ["space station", "Salyut", "Skylab", "Mir", "ISS", "habitation",
           "microgravity", "long duration", "aerospace", "history"]),
    # Salyut 1 (1971) — Soviet, 3-person crew, 23 days. Three cosmonauts
    # died on re-entry when a valve failed and the cabin decompressed.
    # Skylab (1973) — US station built from Saturn V hardware; partly
    # destroyed by meteorite strike during assembly; repaired in orbit.
    # Mir (1986–2001) — continuous human presence in space, 15 years.
    # ISS (1998–present) — 16 nations, 73m length, continuously crewed
    # since November 2000. The largest structure ever assembled in space.

    Topic("life_in_space", "Living in Space — Microgravity, Bone Loss, and the Human Body",
          "Aerospace", [2, 3], [6, 7, 8, 9], 3, 4,
          ["space_stations_history", "human_body_ks2"],
          ["microgravity", "bone density", "muscle atrophy", "radiation",
           "psychological isolation", "space medicine", "long duration",
           "Mars mission", "aerospace", "biology"]),
    # In microgravity: fluid shifts to the head (puffy face), bones lose
    # density (1% per month), muscles atrophy, spine elongates (astronauts
    # are 2–5cm taller in space). Return to Earth is difficult after 6+ months.
    # Radiation: above the Van Allen belts, cosmic rays and solar particle
    # events are lethal without shielding. A Mars mission (2+ years) requires
    # solving radiation exposure.

    Topic("spacelab_experiments", "Spacelab and Space-Based Science — What Microgravity Research Gives Us",
          "Aerospace", [2, 3], [6, 7, 8], 3, 4,
          ["space_stations_history"],
          ["Spacelab", "science", "microgravity", "crystal growth",
           "protein folding", "materials", "combustion", "ISS research",
           "aerospace", "how things work"]),
    # Spacelab: ESA-built module flown in the Shuttle payload bay 1983–1998.
    # Microgravity research: protein crystals grow larger and more perfect
    # without gravity (pharmaceutical applications). Combustion without convection
    # produces spherical flames — reveals chemistry hidden on Earth.
    # Fluid dynamics without buoyancy. Long-duration human physiology.

    # ==========================================================================
    # SATELLITES AND APPLICATIONS
    # ==========================================================================

    Topic("satellites_types_uses", "Satellites — What They Do and Why We Can't Live Without Them",
          "Aerospace", [2], [5, 6, 7], 2, 4,
          ["geostationary_lagrange"],
          ["satellites", "GPS", "weather", "communications", "spy satellite",
           "Earth observation", "Starlink", "megaconstellation", "aerospace",
           "how things work"]),
    # GPS: 24+ satellites in medium Earth orbit (20,200km) — your phone
    # calculates position by measuring signal time from at least 4 satellites.
    # Accuracy requires relativistic corrections (both special and general
    # relativity — without them, GPS drifts 10km per day).
    # Weather satellites: geostationary for continuous imagery, polar for
    # global coverage. Without them, weather forecasting collapses.
    # Starlink and megaconstellations: thousands of LEO satellites providing
    # global internet — and cluttering the night sky for astronomers.

    Topic("space_debris_kessler", "Space Debris and Kessler Syndrome — Threatening Our Orbital Environment",
          "Aerospace", [3], [7, 8, 9], 4, 5,
          ["satellites_types_uses", "orbital_mechanics_basics"],
          ["space debris", "Kessler syndrome", "LEO", "collision cascade",
           "ASAT", "deorbit", "sustainability", "aerospace", "environment"]),
    # 27,000+ tracked debris objects above 10cm. A bolt at orbital velocity
    # hits with the energy of a hand grenade. Kessler syndrome: a cascade
    # of collisions makes low Earth orbit unusable.
    # ASAT (anti-satellite) weapons tests create debris fields — the 2007
    # Chinese ASAT test created 3,000+ tracked fragments.
    # The tragedy of the commons in space: no one owns the orbital environment
    # but everyone uses it.

    # ==========================================================================
    # MODERN ERA AND THE FUTURE
    # ==========================================================================

    Topic("space_shuttle_programme", "The Space Shuttle — A Reusable Spacecraft and Its Compromises",
          "Aerospace", [2, 3], [6, 7, 8, 9], 3, 5,
          ["multistage_rockets", "space_stations_history"],
          ["Space Shuttle", "reusable", "Columbia", "Challenger", "SRB",
           "SSME", "orbiter", "heat shield", "NASA", "aerospace", "history"]),
    # The Shuttle was the first partly reusable spacecraft — but reuse turned
    # out to be expensive. The orbiter required 11 months of maintenance between
    # flights. The heat shield tiles had to be inspected individually.
    # Challenger (1986): O-ring seals on the SRBs failed in cold weather.
    # Engineers at Thiokol recommended a launch delay; NASA management overruled.
    # Columbia (2003): foam strike on the leading edge during launch; NASA
    # management decided not to investigate further. Both disasters had warning
    # signs that were dismissed — a study in organisational failure.

    Topic("commercial_space_era", "The Commercial Space Era — SpaceX, Reusability, and New Players",
          "Aerospace", [3], [8, 9], 4, 5,
          ["multistage_rockets", "space_shuttle_programme"],
          ["SpaceX", "Falcon 9", "Starship", "reusability", "booster landing",
           "Blue Origin", "commercial", "cost reduction", "aerospace", "modern"]),
    # Falcon 9: first orbital rocket to land its booster vertically and refly it.
    # The economics: a new Falcon 9 costs ~$60M; a reflown booster costs ~$6M.
    # Reusability fundamentally changes the cost per kg to orbit.
    # Starship: fully reusable, aimed at cost of $10/kg to orbit (Shuttle was ~$60,000/kg).
    # The geopolitics: SpaceX now provides more lift capacity than all other
    # launch providers combined. NASA depends on a private company for ISS access.

    Topic("space_elevator", "Space Elevators — The Carbon Nanotube Dream",
          "Aerospace", [3], [8, 9], 4, 5,
          ["geostationary_lagrange", "how_rockets_work"],
          ["space elevator", "carbon nanotube", "tether", "geostationary",
           "climber", "cost per kg", "materials", "future", "aerospace"]),
    # A cable anchored at the equator, extending to geostationary altitude
    # (35,786km) and beyond — counterweight holds it taut by centrifugal force.
    # A "climber" (elevator car) powered by ground-based laser climbs to orbit —
    # no rocket required. Cost per kg: potentially $10–100 vs $2,000+ by rocket.
    # The problem: tensile strength required exceeds any known material by a
    # large margin. Carbon nanotubes in theory have the right properties —
    # but only at nanoscale; no one can make macroscopic nanotube cable.
    # Lunar elevator is more feasible (weaker gravity, L1 as anchor point).

    Topic("moon_programme_modern", "Back to the Moon — Artemis, China's Programme, and Why Now",
          "Aerospace", [3], [8, 9], 3, 5,
          ["space_race_origins", "commercial_space_era"],
          ["Moon", "Artemis", "Lunar Gateway", "China", "CNSA", "helium-3",
           "lunar resources", "geopolitics", "aerospace", "modern"]),
    # Why return to the Moon in 2026? Not just exploration:
    # Helium-3: rare on Earth, abundant in Moon's regolith — potential fusion fuel.
    # Water ice at the poles: rocket fuel (split into H2+O) and drinking water.
    # Staging point for Mars: lower gravity well, already in space.
    # Geopolitics: China's CNSA has a credible Moon programme; the US and China
    # are both establishing frameworks for claiming lunar resources.
    # The Outer Space Treaty (1967) says no nation can own the Moon —
    # but says nothing about resources extracted from it.

    Topic("mars_mission_challenges", "Going to Mars — Why It's So Much Harder Than the Moon",
          "Aerospace", [3], [8, 9], 4, 6,
          ["moon_programme_modern", "life_in_space", "delta_v_manoeuvres"],
          ["Mars", "transit time", "radiation", "landing", "EDL", "ISRU",
           "psychology", "isolation", "return trip", "Starship", "aerospace"]),
    # Distance: Moon is 3 days; Mars is 7–9 months minimum, launch windows
    # every 26 months, total mission 2–3 years.
    # Entry, Descent, and Landing (EDL): Mars has 1% of Earth's atmosphere —
    # enough to heat a spacecraft but not enough to brake it. The "seven minutes
    # of terror." Curiosity used a sky crane; humans need something far larger.
    # In-Situ Resource Utilisation (ISRU): make fuel and oxygen from CO2 and ice.
    # The psychological challenge: longer than any mission in history, no abort option.
    # Radiation: 300-600 mSv on a round trip (vs 50 mSv per year on ISS).
    # The deepest challenge: no one has died beyond low Earth orbit since 1972.

    Topic("probes_and_robotic_exploration", "Robotic Probes — Our Eyes in the Solar System",
          "Aerospace", [2, 3], [6, 7, 8, 9], 2, 4,
          ["delta_v_manoeuvres", "satellites_types_uses"],
          ["probes", "Voyager", "Pioneer", "Cassini", "New Horizons",
           "Curiosity", "Perseverance", "Venera", "Deep Space Network",
           "Pluto", "outer planets", "aerospace", "science"]),
    # Voyager 1 (launched 1977): now 24 billion km away — still operating.
    # Passed into interstellar space in 2012 (confirmed 2013). Powered by
    # plutonium RTGs that will go cold in the 2030s.
    # Cassini: 13 years at Saturn, discovered Enceladus has a subsurface
    # ocean venting into space. Deliberately crashed into Saturn (2017) to
    # avoid contaminating Enceladus.
    # Venera 13 (1982): landed on Venus, survived 127 minutes, sent colour photos.
    # New Horizons: first close flyby of Pluto (2015) — revealed heart-shaped
    # nitrogen ice plain, mountains of water ice 3km high.

    Topic("search_for_life_astrobiology", "Astrobiology — The Science of Looking for Life Elsewhere",
          "Aerospace", [3], [7, 8, 9], 4, 6,
          ["probes_and_robotic_exploration", "origin_of_life"],
          ["astrobiology", "habitable zone", "Europa", "Enceladus", "Titan",
           "biosignatures", "exoplanet atmospheres", "JWST", "SETI",
           "Drake equation", "Fermi paradox", "aerospace", "science"]),
    # Where to look: not just planets in the habitable zone.
    # Europa (Jupiter's moon): liquid ocean under ice shell, tidal heating —
    # possibly warmer than the habitable zone concept suggests.
    # Enceladus (Saturn's moon): water vapour venting from subsurface ocean,
    # organic compounds detected. Cassini flew through the plumes.
    # Titan (Saturn's moon): thick nitrogen atmosphere, liquid methane lakes
    # — could life exist using methane as solvent instead of water?
    # JWST: detecting atmospheric biosignatures on exoplanets — oxygen,
    # methane, water. The first hints of possible biological activity were
    # announced in 2025 for a super-Earth 124 light-years away.
]


CURRICULUM: list[Topic] = (
    _ENGLISH + _MATHS + _SCIENCE + _HISTORY + _GEOGRAPHY +
    _COMPUTING + _ART_MUSIC + _PSHE + _VOCATIONAL + _GRAND_NARRATIVES +
    _HOW_THINGS_ARE_MADE + _MATERIALS + _CONNECTIONS +
    _SOCIAL_PATTERNS + _CRITICAL_THINKING + _SOCIAL_INTELLIGENCE +
    _GROWING_UP + _VOCABULARY + _MANIPULATION + _POLITICAL_SYSTEMS +
    _EXPERIMENTS + _FILM +
    _MUSIC_DEEP + _PERFORMING_ARTS + _SPORT + _SPORTS_MEDICINE +
    _MODEL_PROGRESSIONS + _WORLD_RELIGIONS + _AEROSPACE
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
