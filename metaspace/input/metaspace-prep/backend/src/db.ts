import pg from "pg";

/**
 * Thin Postgres helper. Nothing exotic — but note two choices a Tech Lead may
 * poke at:
 *
 * 1. A POOL, not a client. Node is single-threaded but I/O is concurrent; a
 *    single client serialises every query behind the slowest one. Same reason
 *    you use an async engine + session factory in SQLAlchemy rather than one
 *    global connection.
 *
 * 2. numeric/int8 parsed as STRING, not Number. Postgres NUMERIC(78,0) holds
 *    uint256 values that blow past JavaScript's 2^53 safe-integer limit. The
 *    pg driver returns them as strings by default and you convert to BigInt
 *    yourself. If you ever see a balance that is "almost right", this is why.
 */
export const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL ?? "postgres://localhost:5432/metaspace",
  max: Number(process.env.PG_POOL_MAX ?? 10),
  idleTimeoutMillis: 30_000,
  // Fail fast rather than hanging a request forever on a dead node.
  connectionTimeoutMillis: 5_000,
});

export type Queryable = pg.Pool | pg.PoolClient;

/**
 * Run `fn` inside a transaction, rolling back on any throw.
 *
 * The indexer leans on this hard: a block's events and the checkpoint advance
 * must commit together. If they could commit separately you would either
 * re-process events (checkpoint lost) or skip them (checkpoint ahead) after a
 * crash. Atomicity is what turns "at least once" into "exactly once" at the
 * level the game cares about.
 */
export async function withTransaction<T>(fn: (tx: pg.PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await fn(client);
    await client.query("COMMIT");
    return result;
  } catch (err) {
    await client.query("ROLLBACK").catch(() => {});
    throw err;
  } finally {
    client.release();
  }
}
