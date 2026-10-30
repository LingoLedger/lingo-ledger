/**
 * Lingo Ledger TypeScript API.
 *
 * Mirrors the Python package: project-brief validation and translation scoring.
 * Pure functions, no network access, no translator contact.
 */

export const PURPOSES = ["immigration", "court", "regulatory", "medical", "other"] as const;
export const CERTIFICATION_SCHEMES = ["NAATI", "CATTI", "ATA", "ITI", "sworn", "other"] as const;

export type Purpose = (typeof PURPOSES)[number];
export type CertificationScheme = (typeof CERTIFICATION_SCHEMES)[number];

/** A customer's project brief, submitted before any translator is contacted. */
export interface ProjectBrief {
  title: string;
  source_lang: string;
  target_lang: string;
  purpose: Purpose;
  certifications: CertificationScheme[];
}

/** One scored example. Field names match the JSONL format used by the Python CLI. */
export interface Example {
  source: string;
  reference: string;
  domain: string;
  lang_pair: string;
}

export interface BriefCheck {
  ok: boolean;
  errors: string[];
}

export interface Scores {
  exact_match: number;
  token_f1: number;
}

/** Check a brief's fields. Accepts unknown input so it can validate untrusted JSON. */
export function validateBrief(brief: unknown): BriefCheck {
  const errors: string[] = [];
  if (typeof brief !== "object" || brief === null || Array.isArray(brief)) {
    return { ok: false, errors: ["brief must be an object"] };
  }
  const b = brief as Record<string, unknown>;

  for (const key of ["title", "source_lang", "target_lang", "purpose", "certifications"]) {
    if (!(key in b)) errors.push(`missing field: ${key}`);
  }
  if (errors.length > 0) return { ok: false, errors };

  if (typeof b.title !== "string" || b.title.trim() === "") errors.push("title must not be empty");
  for (const key of ["source_lang", "target_lang"] as const) {
    const value = b[key];
    if (typeof value !== "string" || value.trim() === "") errors.push(`${key} must not be empty`);
  }
  if (b.source_lang === b.target_lang) errors.push("source_lang and target_lang must differ");
  if (!(PURPOSES as readonly unknown[]).includes(b.purpose)) {
    errors.push(`purpose must be one of: ${[...PURPOSES].sort().join(", ")}`);
  }
  if (!Array.isArray(b.certifications) || b.certifications.length === 0) {
    errors.push("certifications must be a non-empty list");
  } else {
    const unknown = b.certifications.filter(
      (c) => !(CERTIFICATION_SCHEMES as readonly unknown[]).includes(c),
    );
    if (unknown.length > 0) errors.push(`unknown certifications: ${unknown.join(", ")}`);
  }
  return { ok: errors.length === 0, errors };
}

/** Whitespace-token F1 between a hypothesis and a reference, in [0, 1]. */
export function tokenF1(hypothesis: string, reference: string): number {
  const hyp = countTokens(hypothesis);
  const ref = countTokens(reference);
  const hypTotal = [...hyp.values()].reduce((a, b) => a + b, 0);
  const refTotal = [...ref.values()].reduce((a, b) => a + b, 0);
  let overlap = 0;
  for (const [token, count] of hyp) {
    overlap += Math.min(count, ref.get(token) ?? 0);
  }
  if (overlap === 0) return 0;
  const precision = overlap / hypTotal;
  const recall = overlap / refTotal;
  return (2 * precision * recall) / (precision + recall);
}

/** Average exact match and token F1 over examples. Throws on mismatch or empty input. */
export function scoreTranslations(examples: Example[], hypotheses: string[]): Scores {
  if (examples.length !== hypotheses.length) {
    throw new Error("one hypothesis per example is required");
  }
  if (examples.length === 0) throw new Error("no examples to score");

  let exact = 0;
  let f1 = 0;
  examples.forEach((e, i) => {
    if (hypotheses[i].trim() === e.reference.trim()) exact += 1;
    f1 += tokenF1(hypotheses[i], e.reference);
  });
  return { exact_match: exact / examples.length, token_f1: f1 / examples.length };
}

function countTokens(text: string): Map<string, number> {
  const counts = new Map<string, number>();
  for (const token of text.toLowerCase().split(/\s+/).filter(Boolean)) {
    counts.set(token, (counts.get(token) ?? 0) + 1);
  }
  return counts;
}
