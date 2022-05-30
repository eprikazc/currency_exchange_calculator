-- upgrade --
CREATE TABLE IF NOT EXISTS "currency" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(3) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "exchangepairprice" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date" DATE NOT NULL,
    "price" DECIMAL(8,4) NOT NULL,
    "buy_currency_id" INT NOT NULL REFERENCES "currency" ("id") ON DELETE CASCADE,
    "sell_currency_id" INT NOT NULL REFERENCES "currency" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_exchangepai_date_8ff5f1" UNIQUE ("date", "sell_currency_id", "buy_currency_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
