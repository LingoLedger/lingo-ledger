import { test } from "node:test";
import assert from "node:assert/strict";
import { naatiSearchSteps, scoreTranslations, searchPractitioners, tokenF1, validateBrief, type Practitioner } from "../src/index.ts";

const good = {
  title: "Birth certificate for visa",
  source_lang: "en",
  target_lang: "es",
  purpose: "immigration",
  certifications: ["NAATI"],
};

test("valid brief passes", () => {
  assert.deepEqual(validateBrief(good), { ok: true, errors: [] });
});

test("missing field is reported", () => {
  const { purpose: _omit, ...rest } = good;
  assert.ok(validateBrief(rest).errors.includes("missing field: purpose"));
});

test("same languages rejected", () => {
  assert.equal(validateBrief({ ...good, target_lang: "en" }).ok, false);
});

test("unknown purpose and certification rejected", () => {
  const result = validateBrief({ ...good, purpose: "tax", certifications: ["MadeUp"] });
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((e) => e.includes("purpose")));
  assert.ok(result.errors.includes("unknown certifications: MadeUp"));
});

test("non-object input rejected", () => {
  assert.equal(validateBrief("nope").ok, false);
  assert.equal(validateBrief(null).ok, false);
});

test("tokenF1 identical and disjoint", () => {
  assert.equal(tokenF1("a b c", "a b c"), 1);
  assert.equal(tokenF1("x y", "a b"), 0);
});

test("scoreTranslations exact and partial", () => {
  const ex = [
    { source: "s1", reference: "the cat sat", domain: "legal", lang_pair: "en-es" },
    { source: "s2", reference: "go home", domain: "legal", lang_pair: "en-es" },
  ];
  const result = scoreTranslations(ex, ["the cat sat", "go away"]);
  assert.equal(result.exact_match, 0.5);
  assert.ok(result.token_f1 > 0 && result.token_f1 < 1);
});

test("scoreTranslations rejects mismatched lengths", () => {
  assert.throws(() => scoreTranslations([], ["x"]));
});


const pool: Practitioner[] = [
  { id: "p1", display_name: "Zed", scheme: "NAATI", language_pairs: [["en", "es"]], region: "AU", source_registry: "export" },
  { id: "p2", display_name: "Amy", scheme: "ITI", language_pairs: [["es", "en"]], region: "GB", source_registry: "export" },
  { id: "p3", display_name: "Bo", scheme: "ATA", language_pairs: [["en", "es"]], region: "US", source_registry: "export" },
  { id: "p4", display_name: "Cy", scheme: "NAATI", language_pairs: [["en", "fr"]], region: "AU", source_registry: "export" },
];

const search = {
  title: "Birth certificate for visa",
  source_lang: "en",
  target_lang: "es",
  purpose: "immigration",
  certifications: ["NAATI", "ITI"],
};

test("search matches accepted scheme and language pair, either direction, sorted by name", () => {
  const matches = searchPractitioners(search, pool);
  assert.deepEqual(matches.map((m) => m.id), ["p2", "p1"]);
  assert.equal(matches[1].matched_direction, "en->es");
  assert.equal(matches[0].matched_direction, "es->en");
});

test("search excludes schemes the brief does not accept", () => {
  assert.deepEqual(searchPractitioners({ ...search, certifications: ["ATA"] }, pool).map((m) => m.id), ["p3"]);
});

test("search rejects an invalid brief", () => {
  assert.throws(() => searchPractitioners({ ...search, purpose: "tax" }, pool), /invalid brief/);
});

test("naati steps name the directory and the fields to set", () => {
  const guide = naatiSearchSteps({ ...search, certifications: ["NAATI"], purpose: "immigration" });
  const text = guide.steps.join(" ");
  assert.equal(guide.url, "https://directory.naati.com.au/");
  assert.ok(text.includes("translate from en and translate into es"));
  assert.ok(text.includes("Immigration"));
});

test("naati steps reject a brief that does not accept NAATI", () => {
  assert.throws(() => naatiSearchSteps({ ...search, certifications: ["ATA"] }), /does not accept NAATI/);
});
