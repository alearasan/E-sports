-- Tabla principal para almacenar información del partido
CREATE TABLE Matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league TEXT NOT NULL,      -- Liga del partido
    local_player TEXT NOT NULL,  -- Jugador local
    visitor_player TEXT NOT NULL, -- Jugador visitante
    local_team TEXT NOT NULL,     -- Equipo local
    visitor_team TEXT NOT NULL,   -- Equipo visitante
    local_score INTEGER NOT NULL, -- Puntuación del equipo local
    visitor_score INTEGER NOT NULL, -- Puntuación del equipo visitante
    match_date DATETIME NOT NULL -- Fecha y hora del partido
);

-- Tabla para almacenar eventos específicos del partido
CREATE TABLE Events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,    -- Relación con la tabla Matches
    event_type TEXT NOT NULL,     -- Tipo de evento (Corner, Goal, Yellow Card, etc.)
    minute INTEGER,               -- Minuto del evento (NULL si no aplica)
    team TEXT NOT NULL,           -- Equipo involucrado (local o visitor)
    FOREIGN KEY (match_id) REFERENCES Matches(id)
);

-- Tabla para almacenar estadísticas del partido
CREATE TABLE Statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,    -- Relación con la tabla Matches
    stat_type TEXT NOT NULL,      -- Tipo de estadística (e.g., "Attacks", "Ball Safe")
    local_value INTEGER NOT NULL, -- Valor para el equipo local
    visitor_value INTEGER NOT NULL, -- Valor para el equipo visitante
    FOREIGN KEY (match_id) REFERENCES Matches(id)
);
