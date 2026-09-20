/**
 * Shared RPC helpers for the ladder.
 *
 * A public RPC endpoint will refuse perfectly reasonable requests, because you
 * are sharing it with the world. That is not an exceptional condition and it is
 * not a bug in your code: an indexer that treats a rate limit or a "temporary
 * internal error" as a crash will not survive its first day.
 *
 * So every read in the ladder that is *meant* to succeed goes through
 * `withRetry`. The reads that are meant to fail — the deliberate breakages in
 * level 6 — deliberately do not.
 */

/**
 * Retry with exponential backoff.
 *
 * Note what this does NOT do: inspect the error. Provider error text is not a
 * stable interface, it differs between Alchemy, Infura, QuickNode and drpc, and
 * level 6 demonstrates a case where it is simply false. Retrying everything a
 * few times and then giving up is both simpler and more robust than trying to
 * classify failures you did not design.
 *
 * In production you would add a jitter term so that a fleet of workers recovering
 * from the same outage does not synchronise into a thundering herd.
 */
export async function withRetry<T>(operation: () => Promise<T>, attempts = 5): Promise<T> {
  for (let attempt = 1; ; attempt += 1) {
    try {
      return await operation();
    } catch (error) {
      if (attempt >= attempts) throw error;
      await new Promise((resolve) => setTimeout(resolve, 400 * 2 ** (attempt - 1)));
    }
  }
}
