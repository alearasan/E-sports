-- Tabla principal para almacenar información del partido
CREATE TABLE Matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league TEXT,
    local_team TEXT,
    visitor_team TEXT,
    local_score INTEGER,
    visitor_score INTEGER,
    match_date DATETIME
);

-- Tabla para almacenar eventos específicos del partido
CREATE TABLE Events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,          -- Relación con la tabla Matches
    event_type TEXT,           -- Tipo de evento (Corner, Goal, Yellow Card, etc.)
    minute INTEGER,            -- Minuto del evento
    team TEXT,                 -- Equipo involucrado (local o visitor)
    FOREIGN KEY (match_id) REFERENCES Matches(id)
);
