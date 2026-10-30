import { test } from "node:test";
import assert from "node:assert/strict";
import { scoreTranslations, tokenF1, validateBrief } from "../src/index.ts";

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
