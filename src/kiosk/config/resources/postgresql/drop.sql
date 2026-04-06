-- Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- https://www.postgresql.org/docs/current/sql-dropindex.html
DROP INDEX IF EXISTS
    betreiber_kiosk_id_idx,
    betreiber_vorname_idx,
    betreiber_nachname_idx,
    produkt_kiosk_id_idx,
    kiosk_name_idx;

-- https://www.postgresql.org/docs/current/sql-droptable.html
DROP TABLE IF EXISTS
    betreiber,
    produkt,
    kiosk;

-- https://www.postgresql.org/docs/current/sql-droptype.html
DROP TYPE IF EXISTS
    geschlecht;
