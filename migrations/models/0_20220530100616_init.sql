-- upgrade --
CREATE TABLE IF NOT EXISTS "exchangepair" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "currency1" VARCHAR(3) NOT NULL,
    "currency2" VARCHAR(3) NOT NULL,
    CONSTRAINT "uid_exchangepai_currenc_9e764c" UNIQUE ("currency1", "currency2")
);
CREATE TABLE IF NOT EXISTS "exchangepairprice" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date" DATE NOT NULL,
    "price" DECIMAL(8,4) NOT NULL,
    "exchange_pair_id" INT NOT NULL REFERENCES "exchangepair" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
