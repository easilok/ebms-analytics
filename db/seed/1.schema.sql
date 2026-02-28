CREATE TABLE ocurrence (
    "id"  BIGSERIAL PRIMARY KEY,
    "sample_id" INTEGER NOT NULL,
    "occurrence_id" INTEGER NOT NULL UNIQUE,
    "location" VARCHAR(255) NOT NULL,
    "location_id" INTEGER NOT NULL,
    "country" VARCHAR(50),
    "date" DATE NOT NULL,
    "recorder_name" VARCHAR(255) NOT NULL,
    "identified_by" VARCHAR(255) NOT NULL,
    "accepted_species_name" VARCHAR(255) NOT NULL,
    "authority" VARCHAR(255),
    "family" VARCHAR(255) NOT NULL,
    "verification_status" boolean DEFAULT false,
    "verified_by" VARCHAR(255),
    "count_inside" INTEGER NOT NULL DEFAULT 0,
    "count_outside" INTEGER NOT NULL DEFAULT 0,
    "count" INTEGER GENERATED ALWAYS AS (count_inside + count_outside) STORED,
    "latitude_full" VARCHAR(255) NOT NULL,
    "longitude_full" VARCHAR(255) NOT NULL,
    "latitude" REAL,
    "longitude" REAL,
    "record_status" VARCHAR(50),
    "record_substatus" VARCHAR(50),
    "comments" TEXT,
    "occurrence_comment" TEXT,
    "created_at" timestamp default current_timestamp,
    "updated_at" timestamp default current_timestamp
);

CREATE TABLE session_detail (
    "id"  BIGSERIAL PRIMARY KEY,
    "fk_sample_id" INTEGER NOT NULL UNIQUE,
    "ambient_start_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "ambient_end_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "temp_min" REAL NOT NULL,
    "temp_max" REAL NOT NULL,
    "temp_mean" REAL NOT NULL,
    "precipitation_min" REAL,
    "precipitation_max" REAL,
    "precipitation_mean" REAL,
    "rel_hum_min" INTEGER NOT NULL,
    "rel_hum_max" INTEGER NOT NULL,
    "rel_hum_mean" INTEGER NOT NULL,
    "wind_speed_min" REAL NOT NULL,
    "wind_speed_max" REAL NOT NULL,
    "wind_speed_mean" REAL NOT NULL,
    "wind_dir_mean" REAL NOT NULL,
    "weather_condition_code" INTEGER NOT NULL,
    "created_at" timestamp default current_timestamp,
    "updated_at" timestamp default current_timestamp
);

CREATE TABLE gbif_occurrence (
    "id"  BIGSERIAL PRIMARY KEY,
    "occurrence_key" VARCHAR(255) NOT NULL UNIQUE,
    "location_id" INTEGER NOT NULL,
    "location" VARCHAR(255),
    "country" VARCHAR(100),
    "province" VARCHAR(100),
    "county" VARCHAR(100),
    "municipality" VARCHAR(100),
    "date" DATE NOT NULL,
    "recorded_by" VARCHAR(255)[] NOT NULL DEFAULT array[]::varchar[],
    "identified_by" VARCHAR(255)[] NOT NULL DEFAULT array[]::varchar[],
    "species" VARCHAR(255),
    "genus" VARCHAR(100),
    "name" VARCHAR(255),
    "family" VARCHAR(255) NOT NULL,
    "life_stage" VARCHAR(100),
    "count" INTEGER NOT NULL DEFAULT 0,
    "latitude" REAL,
    "longitude" REAL,
    "trap" VARCHAR(255),
    "event_time" VARCHAR(100),
    "event_start_time" VARCHAR(20),
    "event_end_time" VARCHAR(20),
    "name_authorship" VARCHAR(150),
    "year" integer GENERATED ALWAYS AS (date_part('year', "date")::int) STORED,
    "month" integer GENERATED ALWAYS AS (date_part('month', "date")::int) STORED,
    session_id bigint
        GENERATED ALWAYS AS (
        location_id::bigint * 100000
        + (date - DATE '1990-01-01')
    ) STORED,
    locality VARCHAR(255),
    country_code VARCHAR(5) DEFAULT 'PT',
    taxon_rank VARCHAR(10),
    sampling_effort VARCHAR(100),
    location_type VARCHAR(20) GENERATED ALWAYS AS (
        CASE WHEN location IS NOT NULL
            THEN 'Estação'
            ELSE 'Temporária'
        END
    ) STORED,
    is_station BOOLEAN GENERATED ALWAYS AS (
        location IS NOT NULL
    ) STORED,
    is_temporary BOOLEAN GENERATED ALWAYS AS (
        location IS NULL
    ) STORED,
    is_macro BOOLEAN GENERATED ALWAYS AS (
        family in (
            'Brahmaeidae', 'Cimeliidae', 'Cossidae', 'Drepanidae', 'Erebidae', 'Euteliidae', 'Geometridae',
            'Lasiocampidae', 'Limacodidae', 'Noctuidae', 'Nolidae', 'Notodontidae', 'Sphingidae', 'Saturniidae'
            )
    ) STORED,
    count_macro INTEGER GENERATED ALWAYS AS (
        CASE WHEN family in (
            'Brahmaeidae', 'Cimeliidae', 'Cossidae', 'Drepanidae', 'Erebidae', 'Euteliidae', 'Geometridae',
            'Lasiocampidae', 'Limacodidae', 'Noctuidae', 'Nolidae', 'Notodontidae', 'Sphingidae', 'Saturniidae'
        )
            THEN count
            ELSE 0
        END
    ) STORED,
    "created_at" timestamp default current_timestamp,
    "updated_at" timestamp default current_timestamp
);
