-- upgrade --
CREATE UNIQUE INDEX "uid_exchangepai_exchang_a1ad50" ON "exchangepairprice" ("exchange_pair_id", "date");
-- downgrade --
DROP INDEX "uid_exchangepai_exchang_a1ad50";
