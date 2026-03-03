CREATE TABLE IF NOT EXISTS dictionary_numbers (
    number TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS dictionary_words (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT    NOT NULL REFERENCES dictionary_numbers(number) ON DELETE CASCADE,
    word   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS stories (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    position INTEGER NOT NULL,
    sentence TEXT,
    word_0   TEXT NOT NULL,
    word_1   TEXT NOT NULL,
    word_2   TEXT NOT NULL,
    word_3   TEXT NOT NULL,
    word_4   TEXT NOT NULL
);
